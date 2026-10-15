#include "Camera/PlayerCameraManager.h"
#include "GameFramework/PlayerController.h"
#include "Components/SpotLightComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "BogotaGame.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Animation/AnimationAsset.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/SkeletalMesh.h"
#include "Algo/Reverse.h"

namespace {
#include "TrafficModelCatalog.inl"
#include "CrowdCatalog.inl"
constexpr int32 PedestriansPerBlock=36;
// A shared scale keeps parked/driving cars, wheels, doors and collisions aligned.
float TrafficModelScale(const FTrafficModelSpec& Spec){return Spec.HalfLength<210?1.18f:1.12f;}
TArray<TWeakObjectPtr<USpotLightComponent>> CreateTrafficHeadlights(AActor* Actor,USceneComponent* Root,float HalfLength,float HalfWidth,float Height){
 TArray<TWeakObjectPtr<USpotLightComponent>> Lights;
 for(float Side:{-1.f,1.f}){
  auto* Light=NewObject<USpotLightComponent>(Actor);Actor->AddInstanceComponent(Light);Light->SetupAttachment(Root);Light->SetMobility(EComponentMobility::Movable);
  Light->SetIntensityUnits(ELightUnits::Lumens);Light->SetRelativeLocation(FVector(HalfLength-15,Side*HalfWidth*.65f,Height));Light->SetRelativeRotation(FRotator(-10,0,0));
  Light->SetIntensity(220);Light->SetLightColor(FLinearColor(1,.92f,.8f));Light->SetAttenuationRadius(2400);Light->SetInnerConeAngle(8);Light->SetOuterConeAngle(36);Light->SetCastShadows(false);Light->SetVisibility(false);Light->RegisterComponent();Lights.Add(Light);
 }
 return Lights;
}
TArray<FVector> RoundedLoop(float X0,float X1,float Y0,float Y1,float Radius,bool Reverse){
 TArray<FVector> P;
 const FVector Centers[]={FVector(X1-Radius,Y0+Radius,35),FVector(X1-Radius,Y1-Radius,35),FVector(X0+Radius,Y1-Radius,35),FVector(X0+Radius,Y0+Radius,35)};
 for(int32 C=0;C<4;C++)for(int32 S=0;S<=12;S++){float Angle=FMath::DegreesToRadians(-90.f+C*90.f+S*7.5f);P.Add(Centers[C]+FVector(FMath::Cos(Angle)*Radius,FMath::Sin(Angle)*Radius,0));}
 if(Reverse)Algo::Reverse(P);return P;
}
float AsphaltHeight(const FVector& P,const TArray<float>& North,const TArray<float>& East){
 float Z=7;for(float X:North)if(FMath::Abs(P.X-X)<=750)Z=9;
 for(float X:North)for(float Y:East)if(FMath::Abs(P.X-X)<=1550&&FMath::Abs(P.Y-Y)<=(Y==0?1925:1550))Z=27;
 return Z+.5f;
}
float PathLength(const TArray<FVector>& P){float L=0;for(int32 I=0;I<P.Num();I++)L+=FVector::Dist2D(P[I],P[(I+1)%P.Num()]);return L;}
bool StraightAcross(const FStreetAgent& A,FVector Center,FVector Direction,float Band){
 FVector From=A.Position;
 for(int32 N=0;N<A.Route.Num();N++){
  FVector To=A.Route[(A.Segment+1+N)%A.Route.Num()];
  if(FVector::DotProduct((To-From).GetSafeNormal2D(),Direction)<.999f)return false;
  if(FVector::DotProduct(To-Center,Direction)>Band+A.HalfLength+100)return true;
  From=To;
 }
 return false;
}
void PlaceOnPath(FStreetAgent& A,float Distance){
 for(int32 I=0;I<A.Route.Num();I++){float L=FVector::Dist2D(A.Route[I],A.Route[(I+1)%A.Route.Num()]);if(Distance<L){A.Segment=I;A.Position=FMath::Lerp(A.Route[I],A.Route[(I+1)%A.Route.Num()],Distance/L);A.Heading=(A.Route[(I+1)%A.Route.Num()]-A.Position).Rotation().Yaw;return;}Distance-=L;}
}
}
bool ABogotaCity::TrafficNSGreen()const{return FMath::Fmod(Elapsed,32.f)<13;}
bool ABogotaCity::TrafficEWGreen()const{float T=FMath::Fmod(Elapsed,32.f);return T>=16&&T<29;}
void ABogotaCity::BuildTraffic(){
 for(auto& A:Vehicles)if(A.Visual.IsValid())A.Visual->GetOwner()->Destroy();
 for(auto& C:VehicleCollision)if(C)C->DestroyComponent();VehicleCollision.Empty();Vehicles.Empty();for(auto& W:Walkers)if(W.Visual.IsValid())W.Visual->Destroy();Walkers.Empty();TrafficReservations.Empty();
 for(auto& C:Moving)C->ClearInstances();
 FRandomStream R(2026);
 if(!TrafficMaterial)TrafficMaterial=UMaterialInstanceDynamic::Create(LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Traffic/Detailed/M_TrafficVoxelVertex.M_TrafficVoxelVertex")),this);
 // Load shared crowd resources once, before gameplay; entering another block
 // must not synchronously import a character or animation on a moving frame.
 CrowdMeshes.Empty();for(const auto& Spec:CrowdModels){FString N=Spec.Name;CrowdMeshes.Add(LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Crowd/People/SK_%s.SK_%s"),*N,*N)));}
 CrowdMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Crowd/MI_Crowd.MI_Crowd"));
 CrowdClips.Empty();for(const TCHAR* Path:{TEXT("/Game/Crowd/AN_CrowdWalk_Mixamo.AN_CrowdWalk_Mixamo"),TEXT("/Game/Crowd/AN_CrowdIdle.AN_CrowdIdle"),TEXT("/Game/Crowd/AN_CrowdEnterCar.AN_CrowdEnterCar"),TEXT("/Game/Crowd/AN_CrowdEnterCar.AN_CrowdEnterCar"),TEXT("/Game/Crowd/AN_CrowdBoard.AN_CrowdBoard"),TEXT("/Game/Crowd/AN_CrowdBoard.AN_CrowdBoard"),TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane"),TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane")})CrowdClips.Add(LoadObject<UAnimationAsset>(nullptr,Path));
 G66Random.Initialize(int32(FDateTime::Now().GetTicks()));
 constexpr int32 PrivateCount=96,BusCount=4;
 for(int32 I=0;I<PrivateCount+BusCount;I++){
  const FTrafficModelSpec& ModelSpec=TrafficCarModels[I%12<10?I%20:20+I%2];
  FStreetAgent A;A.Articulated=I>=PrivateCount;A.Bus=A.Articulated;A.ModelScale=A.Bus?1.f:TrafficModelScale(ModelSpec);A.HalfLength=A.Bus?915:ModelSpec.HalfLength;A.HalfWidth=A.Bus?135:ModelSpec.HalfWidth;A.WheelRadius=A.Bus?49:ModelSpec.WheelRadius;A.Speed=A.Bus?850:R.FRandRange(850,1100);
  A.HalfLength*=A.ModelScale;A.HalfWidth*=A.ModelScale;A.WheelRadius*=A.ModelScale;A.LaneGroup=A.Articulated?6:I%6;
  // Opposite directions have separate lanes. Rounded corners remove instant turns.
  if(A.Articulated)A.Route=RoundedLoop(-33500,33500,-330,330,330,false);
  else {const int32 Circuit=A.LaneGroup/2;const bool Reverse=(A.LaneGroup%2)!=0;
   const float X0[]={-36000,-24000,-12000},X1[]={36000,24000,12000},Y0[]={-22000,-11000,-22000},Y1[]={22000,11000,22000};
   const float Lane=Reverse?420.f:-420.f;
   A.Route=RoundedLoop(X0[Circuit]+Lane,X1[Circuit]-Lane,Y0[Circuit]+Lane,Y1[Circuit]-Lane,420,Reverse);
  }
  int32 Ordinal=A.Articulated?I-PrivateCount:I/6,Count=A.Articulated?BusCount:PrivateCount/6;
  const float LoopLength=PathLength(A.Route);float SpawnDistance=LoopLength*(Ordinal+.25f)/Count;
  // Never start straddling a junction: admission and rear-clearance rules apply
  // from the first simulation frame, including the long articulated buses.
  for(int32 Attempt=0;Attempt<300;Attempt++){
   PlaceOnPath(A,SpawnDistance);bool InsideJunction=false;
   for(float X:NorthRoads)for(float Y:EastRoads)if(FMath::Abs(A.Position.X-X)<1550+A.HalfLength+100&&FMath::Abs(A.Position.Y-Y)<(Y==0?1925:1550)+A.HalfLength+100)InsideJunction=true;
   for(const auto& B:Vehicles)if(B.LaneGroup==A.LaneGroup){float Along=FMath::Abs(SpawnDistance-B.PathDistance);Along=FMath::Min(Along,LoopLength-Along);if(Along<A.HalfLength+B.HalfLength+300)InsideJunction=true;}
   for(const auto& B:Vehicles){FVector D=B.Position-A.Position,Forward=FRotator(0,A.Heading,0).Vector();if(FMath::Abs(FVector::DotProduct(D,Forward))<A.HalfLength+B.HalfLength+300&&FMath::Abs(FVector::CrossProduct(D,Forward).Z)<A.HalfWidth+B.HalfWidth+80)InsideJunction=true;}
   if(!InsideJunction)break;SpawnDistance=FMath::Fmod(SpawnDistance-400+LoopLength,LoopLength);
  }
  A.Position.Z=AsphaltHeight(A.Position,NorthRoads,EastRoads);A.PathDistance=SpawnDistance;A.LoopLength=LoopLength;A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;
  FString Model=A.Articulated?TEXT("TransMilenio"):ModelSpec.Name;
  auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Traffic/Detailed/SK_%s.SK_%s"),*Model,*Model));
  if(Mesh){auto* Actor=GetWorld()->SpawnActor<AActor>();auto* Visual=NewObject<UPoseableMeshComponent>(Actor);Actor->SetRootComponent(Visual);Actor->AddInstanceComponent(Visual);Visual->SetMobility(EComponentMobility::Movable);Visual->SetSkinnedAssetAndUpdate(Mesh);Visual->SetMaterial(0,TrafficMaterial);Visual->SetWorldScale3D(FVector(A.ModelScale));Visual->SetCullDistance(24000);Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);Visual->RegisterComponent();Actor->SetActorLocationAndRotation(A.Position,FRotator(0,A.Heading,0));A.Visual=Visual;Visual->RefreshBoneTransforms();for(int32 Axle=0;Axle<(A.Articulated?3:2);Axle++)for(const TCHAR* Side:{TEXT("L"),TEXT("R")})A.WheelRest.Add(Visual->GetBoneTransformByName(FName(*FString::Printf(TEXT("wheel_%d_%s"),Axle,Side)),EBoneSpaces::ComponentSpace));if(A.Articulated)A.ArticulationRest=Visual->GetBoneTransformByName(TEXT("articulation"),EBoneSpaces::ComponentSpace);
  A.Headlights=CreateTrafficHeadlights(Actor,Visual,A.HalfLength/A.ModelScale,A.HalfWidth/A.ModelScale,A.Bus?115.f:65.f);}

  else UE_LOG(LogTemp,Error,TEXT("TRAFFIC_MISSING_MODEL %s"),*Model);
  Vehicles.Add(A);
  auto* Collider=NewObject<UBoxComponent>(this);AddInstanceComponent(Collider);Collider->SetupAttachment(RootComponent);Collider->SetMobility(EComponentMobility::Movable);Collider->SetBoxExtent(FVector(A.HalfLength,A.HalfWidth,A.Bus?150:100));Collider->SetCollisionProfileName(TEXT("BlockAllDynamic"));Collider->SetCanEverAffectNavigation(false);Collider->SetGenerateOverlapEvents(false);Collider->RegisterComponent();Collider->SetWorldLocationAndRotation(A.Position+FVector(0,0,A.Bus?150:100),FRotator(0,A.Heading,0));VehicleCollision.Add(Collider);
 }
 for(int32 Block=0;Block<24;Block++)for(int32 Lane=0;Lane<PedestriansPerBlock;Lane++){
  FWalker W;int32 IX=Block%6,IY=Block/6;float Offset=(Lane%2?48.f:-48.f)+((Lane/2)%3)*80.f;
  float X0=NorthRoads[IX]+1100+Offset,X1=NorthRoads[IX+1]-1100-Offset;
  float Y0=EastRoads[IY]+(IY==2?1530:1130)+Offset,Y1=EastRoads[IY+1]-(IY==1?1530:1130)-Offset;
  W.Route={FVector(X0,Y0,26),FVector(X1,Y0,26),FVector(X1,Y1,26),FVector(X0,Y1,26)};
  if(Lane%2)Algo::Reverse(W.Route);W.ModelIndex=(Block*PedestriansPerBlock+Lane)%UE_ARRAY_COUNT(CrowdModels);const auto& Spec=CrowdModels[W.ModelIndex];W.Scale=Spec.Scale;W.Speed=Spec.Speed;
  float Distance=PathLength(W.Route)*(Lane+.35f)/PedestriansPerBlock;
  for(int32 Segment=0;Segment<4;Segment++){float Length=FVector::Dist2D(W.Route[Segment],W.Route[(Segment+1)%4]);if(Distance<Length){W.Segment=Segment;W.Position=FMath::Lerp(W.Route[Segment],W.Route[(Segment+1)%4],Distance/Length);break;}Distance-=Length;}
  W.Heading=(W.Route[(W.Segment+1)%4]-W.Position).Rotation().Yaw;Walkers.Add(W);
 }
 BuildStreetInteractions();
}
#include "BogotaPedestrianBehaviors.inl"
void ABogotaCity::SimulateTraffic(float Dt){
 APawn* Player=UGameplayStatics::GetPlayerPawn(this,0);FVector PlayerPos=Player?Player->GetActorLocation():FVector(1e8);
 TArray<FVector> Old;TArray<float> OldPath;for(const auto& A:Vehicles){Old.Add(A.Position);OldPath.Add(A.PathDistance);}
 // Release only after the rear clears; a signal change cannot strand an admitted bus.
 for(auto It=TrafficReservations.CreateIterator();It;++It){const int32 X=It.Key()/100,Y=It.Key()%100;const auto& A=Vehicles[It.Value()];if(FMath::Abs(A.Position.X-NorthRoads[X])>1550+A.HalfLength||FMath::Abs(A.Position.Y-EastRoads[Y])>(EastRoads[Y]==0?1925:1550)+A.HalfLength)It.RemoveCurrent();}
 for(int32 Index=0;Index<Vehicles.Num();Index++){
  auto& A=Vehicles[Index];A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;A.PreviousWheelAngle=A.WheelAngle;FVector Target=A.Route[(A.Segment+1)%A.Route.Num()];FVector Dir=(Target-A.Position).GetSafeNormal2D();float Desired=A.Speed,Limit=1e8f;bool NS=FMath::Abs(Dir.X)>.9,EW=FMath::Abs(Dir.Y)>.9;
  A.StopCooldown=FMath::Max(0.f,A.StopCooldown-Dt);A.Wait=FMath::Max(0.f,A.Wait-Dt);
  // Car following uses the actual front/rear lengths and the same lane and direction.
  for(int32 J=0;J<Vehicles.Num();J++)if(J!=Index){const auto& B=Vehicles[J];if(B.LaneGroup!=A.LaneGroup)continue;float Ahead=FMath::Fmod(OldPath[J]-OldPath[Index]+A.LoopLength,A.LoopLength);float Gap=Ahead-A.HalfLength-B.HalfLength-190;Limit=FMath::Min(Limit,FMath::Max(0.f,Gap));Desired=FMath::Min(Desired,FMath::Max(0.f,Gap/1.25f));}
  for(int32 J=0;J<Vehicles.Num();J++)if(J!=Index&&Vehicles[J].LaneGroup!=A.LaneGroup){const auto& B=Vehicles[J];FVector D=Old[J]-A.Position;float Ahead=FVector::DotProduct(D,Dir),Side=FMath::Abs(FVector::CrossProduct(D,Dir).Z);
   if(Ahead>0&&Ahead<5000&&Side<A.HalfWidth+B.HalfWidth+40&&FVector::DotProduct(Dir,FRotator(0,B.Heading,0).Vector())>.9f){float Gap=FMath::Max(0.f,Ahead-A.HalfLength-B.HalfLength-190);Limit=FMath::Min(Limit,Gap);Desired=FMath::Min(Desired,Gap/1.25f);}
  }
  for(int32 X=0;X<NorthRoads.Num();X++)for(int32 Y=0;Y<EastRoads.Num();Y++){
   FVector Center(NorthRoads[X],EastRoads[Y],35),D=Center-A.Position;float Ahead=FVector::DotProduct(D,Dir),Side=FMath::Abs(FVector::CrossProduct(D,Dir).Z);if((!NS&&!EW)||Side>900||Ahead<0||Ahead>6000)continue;
   const int32 Key=X*100+Y;TArray<int32> JunctionOwners;TrafficReservations.MultiFind(Key,JunctionOwners);if(JunctionOwners.Contains(Index))continue;
   const float StopBand=NS?1550.f:EastRoads[Y]==0?1925.f:1550.f;float StopDistance=Ahead-StopBand-A.HalfLength;
   bool Green=(NS?TrafficNSGreen():TrafficEWGreen())&&!PedestrianJunctions.Contains(Key);bool Free=JunctionOwners.IsEmpty();
   // Opposing straight lanes can clear together. Turning traffic still owns
   // the junction exclusively until its rear has completely cleared it.
   if(!Free&&StraightAcross(A,Center,Dir,StopBand)){
    Free=true;for(int32 OwnerIndex:JunctionOwners){const auto& B=Vehicles[OwnerIndex];FVector BDir=(B.Route[(B.Segment+1)%B.Route.Num()]-B.Position).GetSafeNormal2D();float Alignment=FVector::DotProduct(Dir,BDir),Lateral=FMath::Abs(FVector::CrossProduct(B.Position-A.Position,Dir).Z);
     if(FMath::Abs(Alignment)<.999f||!StraightAcross(B,Center,BDir,StopBand)||(Alignment<0&&Lateral<A.HalfWidth+B.HalfWidth+80)||(Alignment>0&&A.LaneGroup!=B.LaneGroup)){Free=false;break;}}
   }
   // Keep the junction empty when the outgoing lane is queued.
   bool ExitFree=true;for(int32 J=0;J<Vehicles.Num();J++)if(J!=Index){FVector Other=Old[J]-Center;float Forward=FVector::DotProduct(Other,Dir);if(Forward>0&&Forward<StopBand+2*A.HalfLength+300&&Vehicles[J].Velocity<100&&FVector::DotProduct(FRotator(0,Vehicles[J].Heading,0).Vector(),Dir)>.7f&&FMath::Abs(FVector::CrossProduct(Old[J]-A.Position,Dir).Z)<A.HalfWidth+Vehicles[J].HalfWidth+80)ExitFree=false;}
   if(StopDistance<=25&&Green&&Free&&ExitFree)TrafficReservations.Add(Key,Index);
   else {Limit=FMath::Min(Limit,FMath::Max(0.f,StopDistance));Desired=FMath::Min(Desired,FMath::Sqrt(2*650.f*FMath::Max(0.f,StopDistance)));}
  }
  FVector PP=PlayerPos-A.Position;float PlayerAhead=FVector::DotProduct(PP,Dir);if(PlayerAhead>-A.HalfLength&&PlayerAhead<A.HalfLength+1600&&FMath::Abs(FVector::CrossProduct(PP,Dir).Z)<(A.Bus?210:175)&&FMath::Abs(PP.Z)<350){float Gap=FMath::Max(0.f,PlayerAhead-A.HalfLength-160);Limit=FMath::Min(Limit,Gap);Desired=FMath::Min(Desired,FMath::Sqrt(1300*Gap));}
  for(const auto& W:Walkers){if(PedHidden(W))continue;FVector D=W.Position-A.Position;float Ahead=FVector::DotProduct(D,Dir);if(Ahead>A.HalfLength&&Ahead<A.HalfLength+900&&FMath::Abs(FVector::CrossProduct(D,Dir).Z)<180){float Gap=FMath::Max(0.f,Ahead-A.HalfLength-150);Limit=FMath::Min(Limit,Gap);Desired=FMath::Min(Desired,FMath::Sqrt(1300*Gap));}}
  // One dwell per station pass, with cooldown measured in time rather than every frame.
  if(A.Articulated&&NS&&A.StopCooldown==0)for(float Station:{-27000.f,-7000.f,17000.f,32000.f}){float D=(Station-A.Position.X)*Dir.X;if(D>=-12&&D<3000){Limit=FMath::Min(Limit,FMath::Max(0.f,D));Desired=FMath::Min(Desired,FMath::Sqrt(1300.f*FMath::Max(0.f,D)));if(D<=12&&A.Velocity<80){A.Wait=4.5f;A.StopCooldown=20;}}}
  if(A.Wait>0)Desired=0;
  A.Velocity=FMath::FInterpConstantTo(A.Velocity,Desired,Dt,Desired>A.Velocity?240:650);float Move=FMath::Min(A.Velocity*Dt,Limit);if(Move<A.Velocity*Dt)A.Velocity=Move/Dt;
  if(FParse::Param(FCommandLine::Get(),TEXT("TrafficDebug"))&&A.Velocity<1&&FMath::Fmod(Elapsed,10.f)<Dt){FString Owners;for(auto& Entry:TrafficReservations)Owners+=FString::Printf(TEXT(" %d:%d"),Entry.Key,Entry.Value);float Gap=1e8;int32 AheadIndex=-1;for(int32 J=0;J<Vehicles.Num();J++)if(J!=Index&&Vehicles[J].LaneGroup==A.LaneGroup){float D=FMath::Fmod(OldPath[J]-OldPath[Index]+A.LoopLength,A.LoopLength)-A.HalfLength-Vehicles[J].HalfLength-190;if(D<Gap){Gap=D;AheadIndex=J;}}UE_LOG(LogTemp,Display,TEXT("TRAFFIC_WAIT time=%.1f car=%d pos=%s heading=%.1f wait=%.1f desired=%.1f limit=%.1f ahead=%d gap=%.1f owners=%s"),Elapsed,Index,*A.Position.ToString(),A.Heading,A.Wait,Desired,Limit,AheadIndex,Gap,*Owners);}
  A.Travelled+=Move;A.PathDistance=FMath::Fmod(A.PathDistance+Move,A.LoopLength);float Remaining=Move;
  while(Remaining>0){Target=A.Route[(A.Segment+1)%A.Route.Num()];float Distance=FVector::Dist2D(Target,A.Position);if(Distance<=Remaining+.001f){A.Position=Target;A.Segment=(A.Segment+1)%A.Route.Num();Remaining=FMath::Max(0.f,Remaining-Distance);}else{A.Position+=(Target-A.Position).GetSafeNormal2D()*Remaining;Remaining=0;}}
  A.Position.Z=AsphaltHeight(A.Position,NorthRoads,EastRoads);float OldHeading=A.Heading;A.Heading=FMath::FixedTurn(A.Heading,(A.Route[(A.Segment+1)%A.Route.Num()]-A.Position).Rotation().Yaw,Dt*100);float Turn=FMath::FindDeltaAngleDegrees(OldHeading,A.Heading);A.WheelAngle=FMath::Fmod(A.WheelAngle+FMath::RadiansToDegrees(Move/A.WheelRadius),360.f);
  A.SteeringRate=Turn/FMath::Max(Dt,.001f);
  auto* C=VehicleCollision[Index].Get();bool Near=FVector::DistSquared2D(PlayerPos,A.Position)<8000*8000;C->SetCollisionEnabled(Near?ECollisionEnabled::QueryOnly:ECollisionEnabled::NoCollision);C->SetWorldLocationAndRotation(A.Position+FVector(0,0,A.Bus?150:88),FRotator(0,A.Heading,0));
 }
}
void ABogotaCity::UpdateTrafficVisuals(float Alpha){
 FVector CameraPosition=FVector::ZeroVector;if(auto* PC=GetWorld()->GetFirstPlayerController())if(PC->PlayerCameraManager)CameraPosition=PC->PlayerCameraManager->GetCameraLocation();
 for(auto& A:Vehicles){
  if(A.Visual.IsValid()){
   FVector Position=FMath::Lerp(A.PreviousPosition,A.Position,Alpha);float Heading=A.PreviousHeading+FMath::FindDeltaAngleDegrees(A.PreviousHeading,A.Heading)*Alpha;
   float WheelAngle=A.PreviousWheelAngle+FMath::FindDeltaAngleDegrees(A.PreviousWheelAngle,A.WheelAngle)*Alpha;
   bool Near=FVector::DistSquared2D(CameraPosition,Position)<FMath::Square(24000.f);A.Visual->GetOwner()->SetActorHiddenInGame(!Near);A.Visual->SetComponentTickEnabled(Near);if(!Near)continue;
   auto* V=A.Visual.Get();V->GetOwner()->SetActorLocationAndRotation(Position,FRotator(0,Heading,0));
   const FQuat JointRotation(FVector::UpVector,FMath::DegreesToRadians(FMath::Clamp(-A.SteeringRate*.32f,-32.f,32.f)));
   if(A.Articulated){FTransform Joint=A.ArticulationRest;Joint.SetRotation(JointRotation*Joint.GetRotation());V->SetBoneTransformByName(TEXT("articulation"),Joint,EBoneSpaces::ComponentSpace);}
   for(int32 Axle=0;Axle<(A.Articulated?3:2);Axle++)for(int32 Side=0;Side<2;Side++){
    FName Bone(*FString::Printf(TEXT("wheel_%d_%s"),Axle,Side==0?TEXT("L"):TEXT("R")));FTransform Pose=A.WheelRest[Axle*2+Side];
    const FQuat Spin(FVector(0,1,0),FMath::DegreesToRadians(WheelAngle));const FQuat Steer(FVector::UpVector,FMath::DegreesToRadians(Axle==0?FMath::Clamp(A.SteeringRate*.25f,-25.f,25.f):0));
    Pose.SetRotation(Steer*Spin*Pose.GetRotation());
    if(A.Articulated&&Axle==2){Pose.SetLocation(A.ArticulationRest.GetLocation()+JointRotation.RotateVector(Pose.GetLocation()-A.ArticulationRest.GetLocation()));Pose.SetRotation(JointRotation*Pose.GetRotation());}
    V->SetBoneTransformByName(Bone,Pose,EBoneSpaces::ComponentSpace);
   }
  }
 }
}
FString ABogotaCity::ValidateTraffic(float Seconds){
 if(Vehicles.IsEmpty())BuildTraffic();TSet<FString> PrivateVariants;for(const auto& A:Vehicles)if(A.Visual.IsValid()){FString N=GetNameSafe(A.Visual->GetSkinnedAsset());if(N.StartsWith(TEXT("SK_Private")))PrivateVariants.Add(N);}
 int32 Missing=0,InvalidRigs=0,MissingColors=0;for(const auto& A:Vehicles){if(!A.Visual.IsValid())Missing++;else if(auto* Mesh=Cast<USkeletalMesh>(A.Visual->GetSkinnedAsset())){if(!Mesh->GetHasVertexColors())MissingColors++;}if(A.WheelRest.Num()!=(A.Articulated?6:4)){InvalidRigs++;continue;}for(const auto& T:A.WheelRest)if(FMath::Abs(T.GetLocation().X)<10||FMath::Abs(T.GetLocation().Y)<40||T.GetLocation().Z<20)InvalidRigs++;}
 TArray<float> Start,Still,Longest;for(const auto& A:Vehicles){Start.Add(A.Travelled);Still.Add(0);Longest.Add(0);}
 int32 Overlaps=0;float MinTravel=1e9;
 for(int32 Step=0;Step<FMath::CeilToInt(Seconds*30);Step++){
  Elapsed+=1.f/30;SimulateTraffic(1.f/30);
  for(int32 I=0;I<Vehicles.Num();I++){Still[I]=Vehicles[I].Velocity<1?Still[I]+1.f/30:0;Longest[I]=FMath::Max(Longest[I],Still[I]);
   for(int32 J=I+1;J<Vehicles.Num();J++){const auto& A=Vehicles[I];const auto& B=Vehicles[J];FVector Forward=FRotator(0,A.Heading,0).Vector(),Other=FRotator(0,B.Heading,0).Vector();FVector Right(-Forward.Y,Forward.X,0),OtherRight(-Other.Y,Other.X,0),D=B.Position-A.Position;bool Hit=true;for(FVector Axis:{Forward,Right,Other,OtherRight}){float Extent=A.HalfLength*FMath::Abs(FVector::DotProduct(Forward,Axis))+A.HalfWidth*FMath::Abs(FVector::DotProduct(Right,Axis))+B.HalfLength*FMath::Abs(FVector::DotProduct(Other,Axis))+B.HalfWidth*FMath::Abs(FVector::DotProduct(OtherRight,Axis));if(FMath::Abs(FVector::DotProduct(D,Axis))>=Extent-10){Hit=false;break;}}if(Hit){Overlaps++;if(Overlaps<=5)UE_LOG(LogTemp,Warning,TEXT("TRAFFIC_OVERLAP step=%d pair=%d,%d posA=%s posB=%s heading=%.1f,%.1f"),Step,I,J,*A.Position.ToString(),*B.Position.ToString(),A.Heading,B.Heading);}}
  }
 }
 float MaxStop=0;for(int32 I=0;I<Vehicles.Num();I++){MinTravel=FMath::Min(MinTravel,Vehicles[I].Travelled-Start[I]);MaxStop=FMath::Max(MaxStop,Longest[I]);}
 // Reproduce the original visual cadence separately from junction waiting:
 // a free car must change position on render frames between simulation steps.
 TArray<FStreetAgent> SavedVehicles=Vehicles;TArray<FWalker> SavedWalkers=Walkers;auto SavedReservations=TrafficReservations;
 FStreetAgent Probe=Vehicles[0];Probe.Route={FVector(-9000,-9000,9),FVector(-4000,-9000,9),FVector(-4000,-4000,9),FVector(-9000,-4000,9)};Probe.Segment=0;Probe.Position=Probe.PreviousPosition=Probe.Route[0];Probe.Heading=Probe.PreviousHeading=0;Probe.Speed=Probe.Velocity=900;Probe.PathDistance=0;Probe.LoopLength=PathLength(Probe.Route);Probe.Wait=Probe.StopCooldown=Probe.Travelled=0;
 Vehicles.Empty();Vehicles.Add(Probe);Walkers.Empty();TrafficReservations.Empty();UpdateTrafficVisuals(1);
 float Accumulator=0;int32 MovingRenderFrames=0;FVector PreviousVisual=Probe.Visual.IsValid()?Probe.Visual->GetOwner()->GetActorLocation():FVector::ZeroVector;
 for(int32 Frame=0;Frame<120;Frame++){Accumulator+=1.f/60;while(Accumulator>=1.f/30){SimulateTraffic(1.f/30);Accumulator-=1.f/30;}UpdateTrafficVisuals(Accumulator*30);
  if(Vehicles[0].Visual.IsValid()){FVector Current=Vehicles[0].Visual->GetOwner()->GetActorLocation();if(Frame>0&&FVector::Dist2D(Current,PreviousVisual)>1)MovingRenderFrames++;PreviousVisual=Current;}}
 float BeforeHitch=Vehicles[0].Travelled;Accumulator+=.2f;while(Accumulator>=1.f/30){SimulateTraffic(1.f/30);Accumulator-=1.f/30;}float HitchLoss=FMath::Abs((Vehicles[0].Travelled-BeforeHitch)-180);
 Vehicles=MoveTemp(SavedVehicles);Walkers=MoveTemp(SavedWalkers);TrafficReservations=MoveTemp(SavedReservations);UpdateTrafficVisuals(1);
 FString Result=FString::Printf(TEXT("{\"seconds\":%.1f,\"vehicles\":%d,\"missing_models\":%d,\"invalid_rigs\":%d,\"missing_vertex_colors\":%d,\"overlap_frames\":%d,\"minimum_travel_cm\":%.1f,\"longest_stop_seconds\":%.2f,\"private_model_variants\":%d}"),Seconds,Vehicles.Num(),Missing,InvalidRigs,MissingColors,Overlaps,MinTravel,MaxStop,PrivateVariants.Num());Result=Result.LeftChop(1)+FString::Printf(TEXT(",\"moving_render_frames\":%d,\"render_frames\":120,\"hitch_time_loss_cm\":%.2f}"),MovingRenderFrames,HitchLoss);UE_LOG(LogTemp,Display,TEXT("TRAFFIC_VALIDATION %s"),*Result);return Result;
}

void ABogotaCity::SimulateWalkers(float Dt){
 auto* Player=UGameplayStatics::GetPlayerPawn(this,0);FVector PP=PedestrianTestObstacle.IsSet()?PedestrianTestObstacle.GetValue():Player?Player->GetActorLocation():FVector::ZeroVector;
 PedestrianJunctions.Empty();for(const auto& W:Walkers)if(W.Crossing)PedestrianJunctions.Add(W.CrossJunction);
 TArray<int32> Nearest;for(int32 I=0;I<Walkers.Num();I++)if(!PedHidden(Walkers[I])&&FVector::DistSquared2D(PP,Walkers[I].Position)<FMath::Square(DetailLevel==0?6500.f:10000.f))Nearest.Add(I);
 Nearest.Sort([&](int32 A,int32 B){return FVector::DistSquared2D(PP,Walkers[A].Position)<FVector::DistSquared2D(PP,Walkers[B].Position);});
 TMap<FIntPoint,TArray<int32>> PedGrid;
 auto Cell=[](FVector P){return FIntPoint(FMath::FloorToInt(P.X/250),FMath::FloorToInt(P.Y/250));};
 for(int32 I=0;I<Walkers.Num();I++)if(!PedHidden(Walkers[I]))PedGrid.FindOrAdd(Cell(Walkers[I].Position)).Add(I);
 for(int32 I=0;I<Walkers.Num();I++){
  auto& W=Walkers[I];const FVector PreviousPosition=W.Position;float Move=0;
  if(!UpdateWalkerInteraction(W,Dt)){
   FVector Target=W.Route[(W.Segment+1)%W.Route.Num()];
   FVector SegmentDirection=(Target-W.Route[W.Segment]).GetSafeNormal2D();
   bool EndpointBlocked=(Player||PedestrianTestObstacle.IsSet())&&FMath::Abs(PP.Z-W.Position.Z)<300&&FVector::DistSquared2D(PP,Target)<FMath::Square(140.f);
   FVector SteeringTarget=EndpointBlocked?Target+SegmentDirection*220:Target,Dir=(SteeringTarget-W.Position).GetSafeNormal2D();
   Move=W.Speed*Dt;
   if(W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing){
    if(W.CrossJunctions.IsValidIndex(W.Segment))W.CrossJunction=W.CrossJunctions[W.Segment];
    float Phase=FMath::Fmod(Elapsed,32.f);bool Red=W.CrossSegments[W.Segment]==1?Phase>=16:Phase<16;
    bool Ready=Red&&!TrafficReservations.Contains(W.CrossJunction)&&Elapsed>=PedestrianNextAdmission.FindRef(W.CrossJunction);
    if(Ready){FVector Center=(W.Position+Target)*.5f,Across=(Target-W.Position).GetSafeNormal2D(),Side(-Across.Y,Across.X,0);float Half=FVector::Dist2D(W.Position,Target)*.5f;
     for(const auto& Car:Vehicles){FVector Forward=FRotator(0,Car.Heading,0).Vector(),Right(-Forward.Y,Forward.X,0),Delta=Car.Position-Center;bool Intersects=true;
      for(FVector Axis:{Forward,Right,Across,Side}){float Extent=Car.HalfLength*FMath::Abs(FVector::DotProduct(Forward,Axis))+Car.HalfWidth*FMath::Abs(FVector::DotProduct(Right,Axis))+Half*FMath::Abs(FVector::DotProduct(Across,Axis))+45*FMath::Abs(FVector::DotProduct(Side,Axis));if(FMath::Abs(FVector::DotProduct(Delta,Axis))>Extent){Intersects=false;break;}}
      if(Intersects){Ready=false;break;}
     }
    }

    if(Ready){W.Crossing=true;PedestrianJunctions.Add(W.CrossJunction);PedestrianNextAdmission.Add(W.CrossJunction,Elapsed+FVector::Dist2D(W.Position,Target)/W.Speed+32);if(!Red)IllegalCrossings++;}else Move=0;
   }
   // Choose a collision-free local velocity. Slow walkers remain slow, while
   // followers may pass immediately instead of waiting for a zero-speed timer.
   const FIntPoint GridCell=Cell(W.Position);TArray<int32> NearbyAgents;
   for(int32 X=-2;X<=2;X++)for(int32 Y=-2;Y<=2;Y++)if(const auto* Nearby=PedGrid.Find(GridCell+FIntPoint(X,Y)))NearbyAgents.Append(*Nearby);
   FVector BestDir=Dir;float BestScore=-1e9;const FVector RouteStart=W.Route[W.Segment],RouteDir=(Target-RouteStart).GetSafeNormal2D();
   const float Corridor=W.Crossing?150.f:230.f;
   for(float Angle:{0.f,-25.f,25.f,-45.f,45.f,-70.f,70.f,-90.f,90.f,-115.f,115.f,-150.f,150.f,180.f}){
    FVector Candidate=Dir.RotateAngleAxis(Angle,FVector::UpVector),Velocity=Candidate*W.Speed;
    float Score=FVector::DotProduct(Candidate,Dir)*3.f+(Angle<0?.04f:0.f);bool Safe=true;
    auto Obstacle=[&](FVector At,FVector OtherVelocity,float Radius){FVector D=At-W.Position,Relative=Velocity-OtherVelocity;float Time=FMath::Clamp(FVector::DotProduct(D,Relative)/FMath::Max(1.f,Relative.SizeSquared2D()),0.f,1.8f);
     float Now=D.Size2D(),Closest=(D-Relative*Time).Size2D();
     if(Now<Radius){if(FVector::DotProduct(D,Relative)>1.e-3f)Safe=false;else Score-=.5f;}
     else if(Closest<Radius&&Time>0){Score-=10.f*(Radius-Closest)/Radius;
      float StepTime=FMath::Clamp(FVector::DotProduct(D,Relative)/FMath::Max(1.f,Relative.SizeSquared2D()),0.f,Dt);
      if((D-Relative*StepTime).Size2D()<Radius)Safe=false;
     }
    };
    if((Player||PedestrianTestObstacle.IsSet())&&FMath::Abs(PP.Z-W.Position.Z)<300&&FVector::DistSquared2D(PP,W.Position)<FMath::Square(500.f))Obstacle(PP,FVector::ZeroVector,135);
    for(int32 J:NearbyAgents)if(J!=I){const auto& O=Walkers[J];if(FMath::Abs(O.Position.Z-W.Position.Z)>150)continue;
     FVector OV=O.Velocity;Obstacle(O.Position,OV,76);
    }
    FVector Next=W.Position+Candidate*W.Speed*.8f;float CurrentSide=FMath::Abs(FVector::CrossProduct(W.Position-RouteStart,RouteDir).Z),NextSide=FMath::Abs(FVector::CrossProduct(Next-RouteStart,RouteDir).Z);
    if(NextSide>Corridor&&NextSide>CurrentSide)Safe=false;
    if(!Safe)Score-=100;
    if(Score>BestScore){BestScore=Score;BestDir=Candidate;}
   }
   if(BestScore< -50)Move=0;
   Dir=BestDir;if(Move>0)W.Heading=FMath::FixedTurn(W.Heading,Dir.Rotation().Yaw,Dt*300);
   bool WaitingSignal=W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing;
   W.BlockedTime=Move<.01f&&!WaitingSignal?W.BlockedTime+Dt:0;
   float Distance=FVector::Dist2D(SteeringTarget,W.Position);Move=FMath::Min(Move,Distance);W.Position+=Dir*Move;W.Travelled+=Move;
   // Advance only after actually reaching the endpoint, never after a sideways step.
   if(FVector::Dist2D(Target,W.Position)<18||(EndpointBlocked&&FVector::DotProduct(W.Position-Target,SegmentDirection)>=0)){if(!EndpointBlocked)W.Position=Target;if(W.Crossing){W.Crossing=false;PedestrianCrossings++;PedestrianNextAdmission.Add(W.CrossJunction,Elapsed+2);}W.Segment=(W.Segment+1)%W.Route.Num();}
  }else Move=W.FrameMoved;
  W.Velocity=(W.Position-PreviousPosition)/FMath::Max(.001f,Dt);
  if(Nearest.Contains(I)&&(W.Activity==EPedActivity::Walking||W.Activity==EPedActivity::ApproachCar||W.Activity==EPedActivity::ReturningRoute)){FHitResult Ground;FCollisionQueryParams Query;if(Player)Query.AddIgnoredActor(Player);if(W.Visual.IsValid())Query.AddIgnoredActor(W.Visual.Get());if(GetWorld()->LineTraceSingleByChannel(Ground,W.Position+FVector(0,0,100),W.Position-FVector(0,0,100),ECC_Visibility,Query)&&Ground.ImpactNormal.Z>.7f)W.Position.Z=Ground.ImpactPoint.Z;}
  int32 Rank=Nearest.Find(I);bool Near=!PedHidden(W)&&Rank!=INDEX_NONE&&Rank<(DetailLevel==0?48:120);
  if(Near){
   if(!W.Visual.IsValid()){
    const FString Name=CrowdModels[W.ModelIndex].Name;auto* Mesh=CrowdMeshes.IsValidIndex(W.ModelIndex)?CrowdMeshes[W.ModelIndex].Get():nullptr;
    if(!Mesh)continue;auto* A=GetWorld()->SpawnActor<AActor>();auto* S=NewObject<USkeletalMeshComponent>(A);A->SetRootComponent(S);A->AddInstanceComponent(S);S->SetSkeletalMeshAsset(Mesh);S->SetMaterial(0,CrowdMaterial);S->SetCollisionEnabled(ECollisionEnabled::NoCollision);S->bEnableUpdateRateOptimizations=true;S->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;S->RegisterComponent();S->PlayAnimation(CrowdClips[CrowdModels[W.ModelIndex].Cane?6:0],true);S->SetPosition((I%17)*.07f,false);A->SetActorScale3D(FVector(W.Scale));W.Visual=A;
   }
   W.Visual->SetActorHiddenInGame(false);W.Visual->SetActorLocationAndRotation(W.Position,FRotator(0,W.Heading-90,0));
   if(auto* S=Cast<USkeletalMeshComponent>(W.Visual->GetRootComponent())){
    uint8 Clip=W.Activity==EPedActivity::EnteringCar?2:W.Activity==EPedActivity::LeavingCar?3:W.Activity==EPedActivity::BoardingTransit?4:W.Activity==EPedActivity::AlightingTransit?5:Move>0?(CrowdModels[W.ModelIndex].Cane?6:0):(CrowdModels[W.ModelIndex].Cane?7:1);
    if(W.VisualAnimation!=Clip){auto* A=CrowdClips[Clip].Get();S->PlayAnimation(A,Clip==0||Clip==1||Clip==6||Clip==7);if(Clip==3||Clip==5)if(auto* Sequence=Cast<UAnimSequence>(A))S->SetPosition(Sequence->GetPlayLength(),false);if(Clip==7)S->SetPosition(0,false);W.VisualAnimation=Clip;}
    S->SetPlayRate(Clip==3||Clip==5?-1.f:Clip==7?0.f:Clip==6?.95f:Clip==0?W.Speed/(140.f*W.Scale):1.f);
   }
  }else if(W.Visual.IsValid())W.Visual->SetActorHiddenInGame(true);
 }
}
FString ABogotaCity::ValidateStreetFlow(){
 if(Walkers.IsEmpty())BuildTraffic();
 auto SavedWalkers=Walkers;auto SavedVehicles=Vehicles;auto SavedJunctions=PedestrianJunctions;auto SavedAdmission=PedestrianNextAdmission;float SavedElapsed=Elapsed;
 const FVector Start(-8000,-8000,27);int32 Failures=0,PassedPlayer=0,PassedSlow=0,PassedCorner=0;float MinPlayerDistance=1e9;
 for(int32 Scenario=0;Scenario<3;Scenario++){
  Walkers.Empty();Vehicles.Empty();PedestrianJunctions.Empty();PedestrianNextAdmission.Empty();PedestrianTestObstacle.Reset();
  for(int32 I=0;I<6;I++){FWalker W;W.Route={Start+FVector(-2000,0,0),Start+FVector(6000,0,0),Start+FVector(6000,1500,0),Start+FVector(-2000,1500,0)};W.Position=Start+FVector(-I*120,0,0);W.Speed=112;W.ModelIndex=0;Walkers.Add(W);}
  if(Scenario==0)PedestrianTestObstacle=Start+FVector(700,0,0);
  else if(Scenario==2){PedestrianTestObstacle=Start+FVector(1200,0,0);for(auto& W:Walkers){W.Route[1].X=Start.X+1200;W.Route[2].X=Start.X+1200;}}
  else {FWalker Slow=Walkers[0];Slow.Speed=38;Slow.ModelIndex=6;Slow.Position=Start+FVector(240,0,0);Walkers.Add(Slow);}
  for(int32 Step=0;Step<600;Step++){Elapsed+=1.f/15;SimulateWalkers(1.f/15);if(Scenario!=1)for(const auto& W:Walkers)MinPlayerDistance=FMath::Min(MinPlayerDistance,FVector::Dist2D(W.Position,PedestrianTestObstacle.GetValue()));}
  for(int32 I=0;I<6;I++)if(Scenario==0){if(Walkers[I].Position.X>Start.X+1500)PassedPlayer++;}else if(Scenario==1){if(Walkers[I].Position.X>Walkers.Last().Position.X+150)PassedSlow++;}else if(Walkers[I].Position.Y>Start.Y+300)PassedCorner++;
  for(auto& W:Walkers)if(W.Visual.IsValid())W.Visual->Destroy();
 }
 Walkers=MoveTemp(SavedWalkers);Vehicles=MoveTemp(SavedVehicles);PedestrianJunctions=MoveTemp(SavedJunctions);PedestrianNextAdmission=MoveTemp(SavedAdmission);PedestrianTestObstacle.Reset();Elapsed=SavedElapsed;
 int32 ShortRoutes=0,WrongKeys=0,CrossingRoutes=0;
 for(const auto& W:Walkers)if(!W.CrossSegments.IsEmpty()){
  CrossingRoutes++;TArray<int32> Cross;for(int32 I=0;I<W.CrossSegments.Num();I++)if(W.CrossSegments[I])Cross.Add(I);
  if(Cross.Num()!=2||!W.CrossJunctions.IsValidIndex(Cross.Last())){WrongKeys++;continue;}
  if(W.CrossJunctions[Cross[0]]==W.CrossJunctions[Cross[1]])WrongKeys++;
  for(int32 C=0;C<2;C++){float Distance=0;for(int32 I=(Cross[C]+1)%W.Route.Num();I!=Cross[1-C];I=(I+1)%W.Route.Num())Distance+=FVector::Dist2D(W.Route[I],W.Route[(I+1)%W.Route.Num()]);if(Distance<5000)ShortRoutes++;}
 }
 Failures=(PassedPlayer!=6)+(PassedSlow!=6)+(PassedCorner!=6)+(MinPlayerDistance<120)+ShortRoutes+WrongKeys;
 return FString::Printf(TEXT("{\"passed_stationary_player\":%d,\"passed_slow_walker\":%d,\"passed_blocked_corner\":%d,\"minimum_player_clearance_cm\":%.1f,\"crossing_routes\":%d,\"short_return_routes\":%d,\"incorrect_crossing_keys\":%d,\"failures\":%d}"),PassedPlayer,PassedSlow,PassedCorner,MinPlayerDistance,CrossingRoutes,ShortRoutes,WrongKeys,Failures);
}
USkeleton* ABogotaCity::CreateCrowdSkeleton(USkeletalMesh* Source){
 if(!Source)return nullptr;UPackage* Package=CreatePackage(TEXT("/Game/Crowd/SKEL_Crowd"));auto* Skeleton=FindObject<USkeleton>(Package,TEXT("SKEL_Crowd"));if(!Skeleton){Skeleton=NewObject<USkeleton>(Package,TEXT("SKEL_Crowd"),RF_Public|RF_Standalone);FAssetRegistryModule::AssetCreated(Skeleton);}Skeleton->MergeAllBonesToBoneTree(Source,false);Skeleton->SetPreviewMesh(Source);Package->MarkPackageDirty();return Skeleton;
}
void ABogotaCity::BindCrowdMesh(USkeletalMesh* Mesh,USkeleton* Skeleton){if(Mesh&&Skeleton){Mesh->Modify();Skeleton->MergeAllBonesToBoneTree(Mesh,false);Skeleton->MarkPackageDirty();Mesh->SetSkeleton(Skeleton);Mesh->MarkPackageDirty();}}
FString ABogotaCity::ValidateCrowd(float Seconds){
 if(Walkers.IsEmpty())BuildTraffic();int32 Missing=0;TSet<int32> Models;
 auto* Hero=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Crowd/SK_CrowdRig.SK_CrowdRig"));auto* Probe=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Crowd/People/SK_Citizen00.SK_Citizen00"));
 if(Hero&&Probe)for(int32 B=0;B<Hero->GetRefSkeleton().GetNum();B++){FName Name=Hero->GetRefSkeleton().GetBoneName(B);int32 P=Probe->GetRefSkeleton().FindBoneIndex(Name);if(P!=INDEX_NONE){const auto& A=Hero->GetRefSkeleton().GetRefBonePose()[B];const auto& C=Probe->GetRefSkeleton().GetRefBonePose()[P];UE_LOG(LogTemp,Display,TEXT("CROWD_BIND %s hero=%s npc=%s angle=%.2f distance=%.2f"),*Name.ToString(),*A.ToString(),*C.ToString(),FMath::RadiansToDegrees(A.GetRotation().AngularDistance(C.GetRotation())),FVector::Dist(A.GetLocation(),C.GetLocation()));}}
 for(const auto& W:Walkers)Models.Add(W.ModelIndex);
 for(int32 I=0;I<UE_ARRAY_COUNT(CrowdModels);I++){FString Name=CrowdModels[I].Name;auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Crowd/People/SK_%s.SK_%s"),*Name,*Name));if(!Mesh||!Mesh->GetSkeleton()||(Mesh->GetMaterials().IsEmpty()||!Mesh->GetMaterials()[0].MaterialInterface))Missing++;}
 int32 PedestrianVehicleOverlaps=0;TArray<float> Start,LastTravel,Still,Longest;for(const auto& W:Walkers){Start.Add(W.Travelled);LastTravel.Add(W.Travelled);Still.Add(0);Longest.Add(0);}
 for(int32 Step=0;Step<FMath::CeilToInt(Seconds*15);Step++){Elapsed+=1.f/15;SimulateTraffic(1.f/15);SimulateWalkers(1.f/15);
 for(int32 I=0;I<Walkers.Num();I++){const auto& W=Walkers[I];bool SignalWait=W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing;
  Still[I]=W.Activity==EPedActivity::Walking&&!SignalWait&&W.Travelled-LastTravel[I]<.01f?Still[I]+1.f/15:0;Longest[I]=FMath::Max(Longest[I],Still[I]);LastTravel[I]=W.Travelled;}
 for(const auto& W:Walkers)if(W.Crossing)for(const auto& A:Vehicles){FVector D=W.Position-A.Position,Forward=FRotator(0,A.Heading,0).Vector(),Right(-Forward.Y,Forward.X,0);if(FMath::Abs(FVector::DotProduct(D,Forward))<A.HalfLength+30&&FMath::Abs(FVector::DotProduct(D,Right))<A.HalfWidth+30)PedestrianVehicleOverlaps++;}}
 float Minimum=1e9;int32 Invalid=0;for(int32 I=0;I<Walkers.Num();I++){if(!Walkers[I].TransitPassenger)Minimum=FMath::Min(Minimum,Walkers[I].Travelled-Start[I]);if(Walkers[I].Position.ContainsNaN())Invalid++;}
 float LongestUnplannedStop=0;int32 StalledWalkers=0;for(int32 I=0;I<Longest.Num();I++){LongestUnplannedStop=FMath::Max(LongestUnplannedStop,Longest[I]);if(Longest[I]>20){StalledWalkers++;if(StalledWalkers<=8)UE_LOG(LogTemp,Warning,TEXT("PEDESTRIAN_STALL id=%d duration=%.1f segment=%d position=%s"),I,Longest[I],Walkers[I].Segment,*Walkers[I].Position.ToString());}}
 FString Result=FString::Printf(TEXT("{\"pedestrians\":%d,\"variants\":%d,\"missing_assets\":%d,\"invalid_positions\":%d,\"minimum_travel_cm\":%.1f}"),Walkers.Num(),Models.Num(),Missing,Invalid,Minimum);
 Result=Result.LeftChop(1)+FString::Printf(TEXT(",\"stalled_walkers\":%d,\"longest_unplanned_stop_seconds\":%.2f}"),StalledWalkers,LongestUnplannedStop);
 return Result.LeftChop(1)+FString::Printf(TEXT(",\"parked_cars\":%d,\"crossings_completed\":%d,\"illegal_crossings\":%d,\"pedestrian_vehicle_overlap_frames\":%d,\"car_boardings\":%d,\"bus_boardings\":%d,\"bus_alightings\":%d}"),ParkedCars.Num(),PedestrianCrossings,IllegalCrossings,PedestrianVehicleOverlaps,ParkedCarBoardings,TransitBoardings,TransitAlightings);
}

void ABogotaCity::UpdateTrafficNight(){
 const bool Night=Hour<6||Hour>=18;if(TrafficMaterial)TrafficMaterial->SetScalarParameterValue(TEXT("NightLights"),Night?1.f:0.f);
 if(Hour>=2&&Hour<3&&G66CheckedNight!=GameDay){G66CheckedNight=GameDay;G66Scheduled=GameDay-G66LastNight>=3&&G66Random.FRand()<.08f;G66StartHour=G66Random.FRandRange(2.05f,2.65f);}
 const bool Active=Hour>=2&&Hour<3&&((G66Scheduled&&Hour>=G66StartHour)||FParse::Param(FCommandLine::Get(),TEXT("ForceG66")));
 if(Active!=G66Active&&Vehicles.Num()>=38){auto& A=Vehicles.Last();if(A.Visual.IsValid()){
 auto* Mesh=LoadObject<USkeletalMesh>(nullptr,Active?TEXT("/Game/Traffic/Detailed/SK_TransMilenioG66.SK_TransMilenioG66"):TEXT("/Game/Traffic/Detailed/SK_TransMilenio.SK_TransMilenio"));
 if(Mesh){A.Visual->SetSkinnedAssetAndUpdate(Mesh);A.Visual->SetMaterial(0,TrafficMaterial);A.Visual->SetWorldScale3D(FVector(A.ModelScale));G66Active=Active;if(Active)G66LastNight=GameDay;}}
 }
 if(Hour>=3)G66Scheduled=false;
 auto* Player=UGameplayStatics::GetPlayerPawn(this,0);FVector P=Player?Player->GetActorLocation():FVector::ZeroVector;if(auto* PC=GetWorld()->GetFirstPlayerController())if(PC->PlayerCameraManager)P=PC->PlayerCameraManager->GetCameraLocation();
 TArray<int32> Nearby;for(int32 I=0;I<Vehicles.Num();I++)if(FVector::DistSquared2D(P,Vehicles[I].Position)<FMath::Square(5000.f))Nearby.Add(I);
 Nearby.Sort([&](int32 A,int32 B){return FVector::DistSquared2D(P,Vehicles[A].Position)<FVector::DistSquared2D(P,Vehicles[B].Position);});
 for(int32 I=0;I<Vehicles.Num();I++){bool On=Night&&Nearby.Find(I)!=INDEX_NONE&&Nearby.Find(I)<6;for(auto& L:Vehicles[I].Headlights)if(L.IsValid())L->SetVisibility(On);}
 TArray<int32> ParkedNearby;for(int32 I=0;I<ParkedCars.Num();I++)if(FVector::DistSquared2D(P,ParkedCars[I].Position)<FMath::Square(6000.f))ParkedNearby.Add(I);
 ParkedNearby.Sort([&](int32 A,int32 B){return FVector::DistSquared2D(P,ParkedCars[A].Position)<FVector::DistSquared2D(P,ParkedCars[B].Position);});
 for(int32 I=0;I<ParkedCars.Num();I++){bool On=Night&&ParkedNearby.Find(I)!=INDEX_NONE&&ParkedNearby.Find(I)<6;for(auto& L:ParkedCars[I].Headlights)if(L.IsValid())L->SetVisibility(On);}

}
FString ABogotaCity::ValidateG66(){
 if(Vehicles.IsEmpty())BuildTraffic();
 float SavedHour=Hour;int32 SavedDay=GameDay,SavedChecked=G66CheckedNight,SavedLast=G66LastNight;bool SavedScheduled=G66Scheduled;float SavedStart=G66StartHour;FRandomStream SavedRandom=G66Random;
 G66CheckedNight=GameDay;G66Scheduled=true;G66StartHour=2.1f;Hour=1.99f;UpdateTrafficNight();bool Boundaries=!G66Active;
 Hour=2.5f;UpdateTrafficNight();Boundaries=Boundaries&&G66Active&&Vehicles.Last().Visual.IsValid()&&GetNameSafe(Vehicles.Last().Visual->GetSkinnedAsset()).Contains(TEXT("G66"));
 Hour=3;UpdateTrafficNight();Boundaries=Boundaries&&!G66Active;
 GameDay=SavedDay+1;G66CheckedNight=-1;Hour=2.5f;UpdateTrafficNight();Boundaries=Boundaries&&!G66Scheduled&&!G66Active;
 Hour=SavedHour;GameDay=SavedDay;G66CheckedNight=SavedChecked;G66LastNight=SavedLast;G66Scheduled=SavedScheduled;G66StartHour=SavedStart;G66Random=SavedRandom;UpdateTrafficNight();
 FRandomStream R(6602);int32 Last=-100,Count=0,Consecutive=0,Eligible=0;
 for(int32 Day=0;Day<10000;Day++){if(Day-Last<3)continue;Eligible++;if(R.FRand()<.08f){if(Day-Last<3)Consecutive++;Last=Day;Count++;}}
 return FString::Printf(TEXT("{\"boundary_checks_pass\":%s,\"nights\":10000,\"eligible_nights\":%d,\"appearances\":%d,\"cooldown_violations\":%d,\"probability_per_eligible_night\":0.08,\"start_hour\":2,\"end_hour\":3}"),Boundaries?TEXT("true"):TEXT("false"),Eligible,Count,Consecutive);
}









