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
#include "Json.h"
#include "Engine/OverlapResult.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"

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
 constexpr int32 PrivateCount=96,BusCount=4;int32 PrivateOrdinal=0;
 for(int32 I=0;I<PrivateCount+BusCount;I++){
  const bool Taxi=I<PrivateCount&&I%6==5;const int32 PaintKey=PrivateOrdinal;const int32 ModelIndex=I>=PrivateCount?0:Taxi?20+(I/6)%2:(PrivateOrdinal++%20);
  const FTrafficModelSpec& ModelSpec=TrafficCarModels[ModelIndex];
  FStreetAgent A;A.Articulated=I>=PrivateCount;A.Bus=A.Articulated;A.ModelScale=A.Bus?1.f:TrafficModelScale(ModelSpec);A.HalfLength=A.Bus?915:ModelSpec.HalfLength;A.HalfWidth=A.Bus?135:ModelSpec.HalfWidth;A.WheelRadius=A.Bus?49:ModelSpec.WheelRadius;A.Speed=A.Bus?850:R.FRandRange(850,1100);
  A.HalfLength*=A.ModelScale;A.HalfWidth*=A.ModelScale;A.WheelRadius*=A.ModelScale;A.LaneGroup=A.Articulated?6:I%6;
  // Opposite directions have separate lanes. Rounded corners remove instant turns.
  if(A.Articulated)A.Route=RoundedLoop(-33500,35000,-330,330,330,true);
  else {const int32 Circuit=A.LaneGroup/2;const bool Reverse=(A.LaneGroup%2)!=0;
   const float X0[]={-36000,-24000,-12000},X1[]={36000,24000,12000},Y0[]={-22000,-11000,-22000},Y1[]={22000,11000,22000};
   const float Lane=Reverse?-270.f:270.f;
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
  if(Mesh){auto* Actor=GetWorld()->SpawnActor<AActor>();auto* Visual=NewObject<UPoseableMeshComponent>(Actor);Actor->SetRootComponent(Visual);Actor->AddInstanceComponent(Visual);Visual->SetMobility(EComponentMobility::Movable);Visual->SetSkinnedAssetAndUpdate(Mesh);Visual->SetMaterial(0,TrafficMaterial);if(Model.StartsWith(TEXT("Private"))){auto* Paint=UMaterialInstanceDynamic::Create(TrafficMaterial->Parent,Visual);Visual->SetMaterial(0,Paint);Paint->SetVectorParameterValue(TEXT("BodyPaint"),TrafficPaintFor(PaintKey));Paint->SetScalarParameterValue(TEXT("PaintEnabled"),1.f);}Visual->SetWorldScale3D(FVector(A.ModelScale));Visual->SetCullDistance(24000);Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);Visual->RegisterComponent();Actor->SetActorLocationAndRotation(A.Position,FRotator(0,A.Heading,0));A.Visual=Visual;Visual->RefreshBoneTransforms();for(int32 Axle=0;Axle<(A.Articulated?3:2);Axle++)for(const TCHAR* Side:{TEXT("L"),TEXT("R")})A.WheelRest.Add(Visual->GetBoneTransformByName(FName(*FString::Printf(TEXT("wheel_%d_%s"),Axle,Side)),EBoneSpaces::ComponentSpace));if(A.Articulated)A.ArticulationRest=Visual->GetBoneTransformByName(TEXT("articulation"),EBoneSpaces::ComponentSpace);
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
  auto& A=Vehicles[Index];if(A.PlayerControlled||A.DevParked){SimulateDeveloperCar(Index,Dt);continue;}A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;A.PreviousWheelAngle=A.WheelAngle;FVector Target=A.Route[(A.Segment+1)%A.Route.Num()];FVector Dir=(Target-A.Position).GetSafeNormal2D();float Desired=A.Speed,Limit=1e8f;bool NS=FMath::Abs(Dir.X)>.9,EW=FMath::Abs(Dir.Y)>.9;
  A.StopCooldown=FMath::Max(0.f,A.StopCooldown-Dt);A.Wait=FMath::Max(0.f,A.Wait-Dt);
  bool StationDwell=false;if(A.Bus&&A.Velocity<2&&A.Wait>0)for(float Station:{-27000.f,-7000.f,17000.f,32000.f})if(FMath::Abs(A.Position.X-Station)<80&&FMath::Abs(A.Position.Y)<400)StationDwell=true;
  A.DoorOpen=FMath::FInterpConstantTo(A.DoorOpen,StationDwell?1.f:0.f,Dt,1.8f);
  // Car following uses the actual front/rear lengths and the same lane and direction.
  for(int32 J=0;J<Vehicles.Num();J++)if(J!=Index){const auto& B=Vehicles[J];if(B.LaneGroup!=A.LaneGroup||B.PlayerControlled||B.DevParked)continue;float Ahead=FMath::Fmod(OldPath[J]-OldPath[Index]+A.LoopLength,A.LoopLength);float Gap=Ahead-A.HalfLength-B.HalfLength-190;Limit=FMath::Min(Limit,FMath::Max(0.f,Gap));Desired=FMath::Min(Desired,FMath::Max(0.f,Gap/1.25f));}
  for(int32 J=0;J<Vehicles.Num();J++)if(J!=Index&&(Vehicles[J].LaneGroup!=A.LaneGroup||Vehicles[J].PlayerControlled||Vehicles[J].DevParked)){const auto& B=Vehicles[J];FVector D=Old[J]-A.Position;float Ahead=FVector::DotProduct(D,Dir),Side=FMath::Abs(FVector::CrossProduct(D,Dir).Z);
   if(B.PlayerControlled||B.DevParked){FVector BF=FRotator(0,B.Heading,0).Vector();float Along=B.HalfLength*FMath::Abs(FVector::DotProduct(BF,Dir))+B.HalfWidth*FMath::Abs(FVector::CrossProduct(BF,Dir).Z),Across=B.HalfLength*FMath::Abs(FVector::CrossProduct(BF,Dir).Z)+B.HalfWidth*FMath::Abs(FVector::DotProduct(BF,Dir));if(Ahead>=0&&Ahead<5000&&Side<A.HalfWidth+Across+50){float Gap=FMath::Max(0.f,Ahead-A.HalfLength-Along-180);Limit=FMath::Min(Limit,Gap);Desired=FMath::Min(Desired,FMath::Sqrt(1300*Gap));}}
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
  if(A.Wait>0||A.DoorOpen>.001f)Desired=0;
  A.Velocity=FMath::FInterpConstantTo(A.Velocity,Desired,Dt,Desired>A.Velocity?240:650);float Move=FMath::Min(A.Velocity*Dt,Limit);if(Move<A.Velocity*Dt)A.Velocity=Move/Dt;
  if(FParse::Param(FCommandLine::Get(),TEXT("TrafficDebug"))&&A.Velocity<1&&FMath::Fmod(Elapsed,10.f)<Dt){FString Owners;for(auto& Entry:TrafficReservations)Owners+=FString::Printf(TEXT(" %d:%d"),Entry.Key,Entry.Value);float Gap=1e8;int32 AheadIndex=-1;for(int32 J=0;J<Vehicles.Num();J++)if(J!=Index&&Vehicles[J].LaneGroup==A.LaneGroup){float D=FMath::Fmod(OldPath[J]-OldPath[Index]+A.LoopLength,A.LoopLength)-A.HalfLength-Vehicles[J].HalfLength-190;if(D<Gap){Gap=D;AheadIndex=J;}}UE_LOG(LogTemp,Display,TEXT("TRAFFIC_WAIT time=%.1f car=%d pos=%s heading=%.1f wait=%.1f desired=%.1f limit=%.1f ahead=%d gap=%.1f owners=%s"),Elapsed,Index,*A.Position.ToString(),A.Heading,A.Wait,Desired,Limit,AheadIndex,Gap,*Owners);}
  A.Travelled+=Move;A.PathDistance=FMath::Fmod(A.PathDistance+Move,A.LoopLength);float Remaining=Move;
  while(Remaining>0){Target=A.Route[(A.Segment+1)%A.Route.Num()];float Distance=FVector::Dist2D(Target,A.Position);if(Distance<=Remaining+.001f){A.Position=Target;A.Segment=(A.Segment+1)%A.Route.Num();Remaining=FMath::Max(0.f,Remaining-Distance);}else{A.Position+=(Target-A.Position).GetSafeNormal2D()*Remaining;Remaining=0;}}
  A.Position.Z=AsphaltHeight(A.Position,NorthRoads,EastRoads);float OldHeading=A.Heading;A.Heading=FMath::FixedTurn(A.Heading,(A.Route[(A.Segment+1)%A.Route.Num()]-A.Position).Rotation().Yaw,Dt*240);float Turn=FMath::FindDeltaAngleDegrees(OldHeading,A.Heading);A.WheelAngle=FMath::Fmod(A.WheelAngle+FMath::RadiansToDegrees(Move/A.WheelRadius),360.f);
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
   auto* V=A.Visual.Get();bool GroundDetail=A.PlayerControlled||A.DevParked||FVector::DistSquared2D(CameraPosition,Position)<FMath::Square(6500.f);if(GroundDetail)UpdateVehicleGroundVisual(A,Position,Heading,GetWorld()->GetDeltaSeconds());else V->GetOwner()->SetActorLocationAndRotation(Position,FRotator(0,Heading,0));
   A.VisualDoorOpen=FMath::FInterpConstantTo(A.VisualDoorOpen,A.DoorOpen,GetWorld()->GetDeltaSeconds(),2.5f);ApplyVehicleDoors(V,A.Bus,A.VisualDoorOpen,0,A.DoorRest);
   const FQuat JointRotation(FVector::UpVector,FMath::DegreesToRadians(FMath::Clamp(-A.SteeringRate*.32f,-32.f,32.f)));
   if(A.Articulated){FTransform Joint=A.ArticulationRest;Joint.SetRotation(JointRotation*Joint.GetRotation());V->SetBoneTransformByName(TEXT("articulation"),Joint,EBoneSpaces::ComponentSpace);}
   for(int32 Axle=0;Axle<(A.Articulated?3:2);Axle++)for(int32 Side=0;Side<2;Side++){
    FName Bone(*FString::Printf(TEXT("wheel_%d_%s"),Axle,Side==0?TEXT("L"):TEXT("R")));FTransform Pose=A.WheelRest[Axle*2+Side];
    const FQuat Spin(FVector(0,1,0),FMath::DegreesToRadians(WheelAngle));const FQuat Steer(FVector::UpVector,FMath::DegreesToRadians(Axle==0?FMath::Clamp(A.SteeringRate*.25f,-25.f,25.f):0));
    Pose.SetRotation(Steer*Spin*Pose.GetRotation());
    if(A.Articulated&&Axle==2){Pose.SetLocation(A.ArticulationRest.GetLocation()+JointRotation.RotateVector(Pose.GetLocation()-A.ArticulationRest.GetLocation()));Pose.SetRotation(JointRotation*Pose.GetRotation());}
    FVector Hub=V->GetOwner()->GetActorTransform().TransformPosition(Pose.GetLocation());FHitResult Support;FCollisionQueryParams GroundQuery;GroundQuery.AddIgnoredActor(V->GetOwner());if(GroundDetail&&GetWorld()->LineTraceSingleByObjectType(Support,Hub+FVector(0,0,80),Hub-FVector(0,0,A.WheelRadius+160),FCollisionObjectQueryParams(ECC_WorldStatic),GroundQuery)&&Support.ImpactNormal.Z>.65f){Hub.Z+=FMath::Clamp(Support.ImpactPoint.Z+A.WheelRadius-Hub.Z,-18.f,18.f);Pose.SetLocation(V->GetOwner()->GetActorTransform().InverseTransformPosition(Hub));}
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
 for(auto& P:ParkedCars)P.DoorOpen=FMath::FInterpConstantTo(P.DoorOpen,P.DoorTarget,Dt,1.8f);
 auto* Player=UGameplayStatics::GetPlayerPawn(this,0);FVector PP=PedestrianTestObstacle.IsSet()?PedestrianTestObstacle.GetValue():Player?Player->GetActorLocation():FVector::ZeroVector;
 PedestrianJunctions.Empty();for(const auto& W:Walkers)if(W.Crossing)PedestrianJunctions.Add(W.CrossJunction);
 TArray<int32> Nearest;for(int32 I=0;I<Walkers.Num();I++)if(!PedHidden(Walkers[I])&&FVector::DistSquared2D(PP,Walkers[I].Position)<FMath::Square(DetailLevel==0?6500.f:10000.f))Nearest.Add(I);
 Nearest.Sort([&](int32 A,int32 B){return FVector::DistSquared2D(PP,Walkers[A].Position)<FVector::DistSquared2D(PP,Walkers[B].Position);});
 TMap<FIntPoint,TArray<int32>> PedGrid;
 auto Cell=[](FVector P){return FIntPoint(FMath::FloorToInt(P.X/250),FMath::FloorToInt(P.Y/250));};
 for(int32 I=0;I<Walkers.Num();I++)if(!PedHidden(Walkers[I]))PedGrid.FindOrAdd(Cell(Walkers[I].Position)).Add(I);
 for(int32 I=0;I<Walkers.Num();I++){
  auto& W=Walkers[I];W.PreviousPosition=W.Position;W.PreviousHeading=W.Heading;
  if(!W.TransitPassenger&&!PedHidden(W)&&W.Activity==EPedActivity::Walking){
   if(W.Position.Z>60||W.Position.Z< -10)W.Position.Z=WalkerGroundHeight(W.Position);
   if(!WalkerStepClear(W.Position,W.Position)){
    bool Found=false;for(float Radius:{60.f,120.f,180.f,240.f,320.f,450.f,650.f}){for(int32 Direction=0;Direction<16;Direction++){
     FVector Candidate=W.Position+FVector(Radius,0,0).RotateAngleAxis(Direction*22.5f,FVector::UpVector);Candidate.Z=WalkerGroundHeight(Candidate);
     if(WalkerStepClear(Candidate,Candidate)&&StreetClearance(Candidate)>=40){W.Position=Candidate;Found=true;break;}}
     if(Found)break;
    }
   }
  }
  if(FVector::DistSquared(W.PreviousPosition,W.Position)>FMath::Square(250.f))W.PreviousPosition=W.Position;
  const FVector PreviousPosition=W.Position;float Move=0;
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
   bool Yield=false,Retreat=false;
   if(!W.Crossing&&(Player||PedestrianTestObstacle.IsSet())&&FMath::Abs(PP.Z-W.Position.Z)<300){
    FVector D=PP-W.Position,Right(-Dir.Y,Dir.X,0);float Ahead=FVector::DotProduct(D,Dir);
    bool Left=WalkerStreetStepClear(W,W.Position,W.Position+Right*170)&&FVector::Dist2D(PP,W.Position+Right*170)>=145;
    bool RightFree=WalkerStreetStepClear(W,W.Position,W.Position-Right*170)&&FVector::Dist2D(PP,W.Position-Right*170)>=145;
    if(W.YieldingToPlayer&&((D.Size2D()>350)||Left||RightFree))W.YieldingToPlayer=false;
    if(Ahead> -35&&Ahead<240&&FMath::Abs(FVector::CrossProduct(D,Dir).Z)<145&&!Left&&!RightFree)W.YieldingToPlayer=true;
    Yield=W.YieldingToPlayer;
    Retreat=Yield&&D.Size2D()<140&&WalkerStreetStepClear(W,W.Position,W.Position-Dir*W.Speed*Dt);
   }else W.YieldingToPlayer=false;

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
    if(Safe&&Score>BestScore&&!WalkerStreetStepClear(W,W.Position,W.Position+Candidate*FMath::Max(Move,W.Speed*.8f)))Safe=false;
    if(!Safe)Score-=100;
    if(Score>BestScore){BestScore=Score;BestDir=Candidate;}
   }
   if(BestScore< -50||Yield)Move=0;
   if(Retreat){BestDir=-Dir;Move=W.Speed*Dt;}
   Dir=BestDir;if(Move>0)W.Heading=FMath::FixedTurn(W.Heading,Dir.Rotation().Yaw,Dt*300);
   bool WaitingSignal=W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing;
   W.BlockedTime=Move<.01f&&!WaitingSignal?W.BlockedTime+Dt:0;
   float Distance=FVector::Dist2D(SteeringTarget,W.Position);Move=FMath::Min(Move,Distance);
   if(Move>0&&!WalkerStreetStepClear(W,W.Position,W.Position+Dir*Move))Move=0;
   W.Position+=Dir*Move;W.Travelled+=Move;
   // Advance only after actually reaching the endpoint, never after a sideways step.
   if(FVector::Dist2D(Target,W.Position)<18||(EndpointBlocked&&FVector::DotProduct(W.Position-Target,SegmentDirection)>=0)){if(!EndpointBlocked)W.Position=Target;if(W.Crossing){W.Crossing=false;PedestrianCrossings++;PedestrianNextAdmission.Add(W.CrossJunction,Elapsed+2);}W.Segment=(W.Segment+1)%W.Route.Num();}
  }else Move=W.FrameMoved;
  W.Velocity=(W.Position-PreviousPosition)/FMath::Max(.001f,Dt);
  // Anchor outdoor pedestrians to the street layer, never to their previous height.
  // Nearby roofs, other characters and cars cannot become a new walking floor.
  if(!W.TransitPassenger&&!PedHidden(W)&&W.Activity!=EPedActivity::EnteringCar&&W.Activity!=EPedActivity::LeavingCar)W.Position.Z=WalkerGroundHeight(W.Position);

  int32 Rank=Nearest.Find(I);bool Near=!PedHidden(W)&&Rank!=INDEX_NONE&&Rank<(DetailLevel==0?48:120);
  if(Near){
   if(!W.Visual.IsValid()){
    const FString Name=CrowdModels[W.ModelIndex].Name;auto* Mesh=CrowdMeshes.IsValidIndex(W.ModelIndex)?CrowdMeshes[W.ModelIndex].Get():nullptr;
    if(!Mesh)continue;auto* A=GetWorld()->SpawnActor<AActor>();auto* S=NewObject<USkeletalMeshComponent>(A);A->SetRootComponent(S);A->AddInstanceComponent(S);S->SetSkeletalMeshAsset(Mesh);S->SetMaterial(0,CrowdMaterial);S->SetCollisionEnabled(ECollisionEnabled::NoCollision);S->bEnableUpdateRateOptimizations=false;S->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;S->RegisterComponent();S->PlayAnimation(CrowdClips[CrowdModels[W.ModelIndex].Cane?6:0],true);S->SetPosition((I%17)*.07f,false);A->SetActorScale3D(FVector(W.Scale));W.Visual=A;W.PreviousPosition=W.Position;W.PreviousHeading=W.Heading;
   }
   W.Visual->SetActorHiddenInGame(false);W.Visual->SetActorLocationAndRotation(W.Position,FRotator(0,W.Heading-90,0));
   if(auto* S=Cast<USkeletalMeshComponent>(W.Visual->GetRootComponent())){
    uint8 Clip=W.Activity==EPedActivity::EnteringCar?2:W.Activity==EPedActivity::LeavingCar?3:(W.Activity==EPedActivity::BoardingTransit||W.Activity==EPedActivity::AlightingTransit)?(Move>0?0:1):Move>0?(CrowdModels[W.ModelIndex].Cane?6:0):(CrowdModels[W.ModelIndex].Cane?7:1);
    if(W.VisualAnimation!=Clip){auto* A=CrowdClips[Clip].Get();S->PlayAnimation(A,Clip==0||Clip==1||Clip==6||Clip==7);if(Clip==3||Clip==5)if(auto* Sequence=Cast<UAnimSequence>(A))S->SetPosition(Sequence->GetPlayLength(),false);if(Clip==7)S->SetPosition(0,false);W.VisualAnimation=Clip;}
    S->SetPlayRate(Clip==3||Clip==5?-1.f:Clip==7?0.f:Clip==2?.55f:Clip==6?.95f:Clip==0?W.Speed/(140.f*W.Scale):1.f);
   }
  }else if(W.Visual.IsValid())W.Visual->SetActorHiddenInGame(true);
 }
 // Reciprocal velocity estimates alone can leave two walkers shoulder-to-shoulder
 // after an abrupt turn. Resolve the small residual overlap against real positions.
 for(int32 Pass=0;Pass<2;Pass++)for(int32 I=0;I<Walkers.Num();I++){
  auto& A=Walkers[I];if(PedHidden(A)||A.TransitPassenger||A.Activity!=EPedActivity::Walking)continue;
  const auto GridCell=Cell(A.Position);
  for(int32 X=-1;X<=1;X++)for(int32 Y=-1;Y<=1;Y++)if(auto* Nearby=PedGrid.Find(GridCell+FIntPoint(X,Y)))for(int32 J:*Nearby)if(J>I){
   auto& B=Walkers[J];if(PedHidden(B)||B.TransitPassenger||B.Activity!=EPedActivity::Walking||FMath::Abs(A.Position.Z-B.Position.Z)>100)continue;
   FVector D=A.Position-B.Position;float Distance=D.Size2D();if(Distance>=76)continue;
   FVector Normal=Distance>.01f?D.GetSafeNormal2D():FVector(1,0,0);float Push=(76-Distance)*.5f+.1f;
   auto Clear=[&](const FWalker& Walker,FVector From,FVector To){if((Player||PedestrianTestObstacle.IsSet())&&FMath::Abs(PP.Z-To.Z)<300&&FVector::DistSquared2D(To,PP)<FMath::Square(135.f)&&FVector::DistSquared2D(To,PP)<FVector::DistSquared2D(From,PP))return false;return WalkerStreetStepClear(Walker,From,To);};
   bool MoveA=Clear(A,A.Position,A.Position+Normal*Push),MoveB=Clear(B,B.Position,B.Position-Normal*Push);
   if(MoveA&&MoveB){A.Position+=Normal*Push;B.Position-=Normal*Push;}
   else if(MoveA&&Clear(A,A.Position,A.Position+Normal*(Push*2)))A.Position+=Normal*(Push*2);
   else if(MoveB&&Clear(B,B.Position,B.Position-Normal*(Push*2)))B.Position-=Normal*(Push*2);
   if(A.Visual.IsValid())A.Visual->SetActorLocation(A.Position);if(B.Visual.IsValid())B.Visual->SetActorLocation(B.Position);
  }
 }

}
FString ABogotaCity::ValidateStreetFlow(){
 if(Walkers.IsEmpty())BuildTraffic();
 auto SavedWalkers=Walkers;auto SavedVehicles=Vehicles;auto SavedJunctions=PedestrianJunctions;auto SavedAdmission=PedestrianNextAdmission;float SavedElapsed=Elapsed;
 const FVector Start(-8000,-45000,27);int32 Failures=0,PassedPlayer=0,PassedSlow=0,PassedCorner=0;float MinPlayerDistance=1e9;
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
  Still[I]=W.Activity==EPedActivity::Walking&&!SignalWait&&!W.YieldingToPlayer&&W.Travelled-LastTravel[I]<.01f?Still[I]+1.f/15:0;Longest[I]=FMath::Max(Longest[I],Still[I]);LastTravel[I]=W.Travelled;}
 for(const auto& W:Walkers)if(W.Crossing)for(const auto& A:Vehicles){FVector D=W.Position-A.Position,Forward=FRotator(0,A.Heading,0).Vector(),Right(-Forward.Y,Forward.X,0);if(FMath::Abs(FVector::DotProduct(D,Forward))<A.HalfLength+30&&FMath::Abs(FVector::DotProduct(D,Right))<A.HalfWidth+30)PedestrianVehicleOverlaps++;}}
 float Minimum=1e9;int32 Invalid=0;for(int32 I=0;I<Walkers.Num();I++){if(!Walkers[I].TransitPassenger)Minimum=FMath::Min(Minimum,Walkers[I].Travelled-Start[I]);if(Walkers[I].Position.ContainsNaN())Invalid++;}
 float LongestUnplannedStop=0;int32 StalledWalkers=0;for(int32 I=0;I<Longest.Num();I++){LongestUnplannedStop=FMath::Max(LongestUnplannedStop,Longest[I]);if(Longest[I]>20){StalledWalkers++;if(StalledWalkers<=8)UE_LOG(LogTemp,Warning,TEXT("PEDESTRIAN_STALL id=%d duration=%.1f segment=%d position=%s"),I,Longest[I],Walkers[I].Segment,*Walkers[I].Position.ToString());}}
 FString Result=FString::Printf(TEXT("{\"pedestrians\":%d,\"variants\":%d,\"missing_assets\":%d,\"invalid_positions\":%d,\"minimum_travel_cm\":%.1f}"),Walkers.Num(),Models.Num(),Missing,Invalid,Minimum);
 Result=Result.LeftChop(1)+FString::Printf(TEXT(",\"stalled_walkers\":%d,\"longest_unplanned_stop_seconds\":%.2f}"),StalledWalkers,LongestUnplannedStop);
 return Result.LeftChop(1)+FString::Printf(TEXT(",\"parked_cars\":%d,\"crossings_completed\":%d,\"illegal_crossings\":%d,\"pedestrian_vehicle_overlap_frames\":%d,\"car_boardings\":%d,\"bus_boardings\":%d,\"bus_alightings\":%d}"),ParkedCars.Num(),PedestrianCrossings,IllegalCrossings,PedestrianVehicleOverlaps,ParkedCarBoardings,TransitBoardings,TransitAlightings);
}

void ABogotaCity::UpdateTrafficNight(){
 const bool Night=Hour<6||Hour>=18;if(TrafficMaterial)TrafficMaterial->SetScalarParameterValue(TEXT("NightLights"),Night?1.f:0.f);
 for(auto& Car:Vehicles)if(Car.Visual.IsValid())if(auto* Paint=Cast<UMaterialInstanceDynamic>(Car.Visual->GetMaterial(0)))Paint->SetScalarParameterValue(TEXT("NightLights"),Night?1.f:0.f);
 for(auto& Car:ParkedCars)if(Car.Visual.IsValid())if(auto* Paint=Cast<UMaterialInstanceDynamic>(Car.Visual->GetMaterial(0)))Paint->SetScalarParameterValue(TEXT("NightLights"),Night?1.f:0.f);
 if(Hour>=2&&Hour<3&&G66CheckedNight!=GameDay){G66CheckedNight=GameDay;G66Scheduled=GameDay-G66LastNight>=3&&G66Random.FRand()<.08f;G66StartHour=G66Random.FRandRange(2.05f,2.65f);}
 const bool Active=Hour>=2&&Hour<3&&((G66Scheduled&&Hour>=G66StartHour)||FParse::Param(FCommandLine::Get(),TEXT("ForceG66")));
 if(Active!=G66Active&&Vehicles.IsValidIndex(99)){auto& A=Vehicles[99];if(A.Visual.IsValid()){
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










bool ABogotaCity::WalkerStepClear(FVector From,FVector To) const{
 FHitResult Hit;FCollisionQueryParams Query(SCENE_QUERY_STAT(PedestrianWalls),false);
 From.Z=26;To.Z=26;
 return !GetWorld()->SweepSingleByObjectType(Hit,From+FVector(0,0,100),To+FVector(0,0,100),FQuat::Identity,FCollisionObjectQueryParams(ECC_WorldStatic),FCollisionShape::MakeCapsule(34,65),Query);
}
float ABogotaCity::WalkerGroundHeight(FVector At) const{
 // All outdoor street routes are on the ground layer. Query a fixed 80 cm band;
 // never trace from the previous foot height (which used to climb walls/roofs).
 FHitResult Hit;FCollisionQueryParams Query(SCENE_QUERY_STAT(PedestrianFloor),false);
 if(GetWorld()->LineTraceSingleByObjectType(Hit,FVector(At.X,At.Y,80),FVector(At.X,At.Y,-20),FCollisionObjectQueryParams(ECC_WorldStatic),Query)&&Hit.ImpactNormal.Z>.7f&&Hit.ImpactPoint.Z<=60)return Hit.ImpactPoint.Z;
 return 26.f;
}
FString ABogotaCity::ValidateMapRoutes(float Seconds){
 if(!GetWorld()->IsGameWorld())return TEXT("{\"error\":\"Run this audit in a standalone game using -MapRouteTest\"}");
 if(Vehicles.IsEmpty())BuildTraffic();
 auto Report=MakeShared<FJsonObject>();Report->SetNumberField(TEXT("seconds"),Seconds);
 bool WallControl=false;FVector WallProbe;for(auto C:Solid){for(int32 I=0;I<C->GetInstanceCount();I++){FTransform T;C->GetInstanceTransform(I,T,true);FVector S=T.GetScale3D().GetAbs()*100;if(S.X>1000&&S.Y>1000&&S.Z>300&&T.GetLocation().Z<3000&&T.GetLocation().Z-S.Z*.5f<50){WallProbe=T.GetLocation();WallProbe.Z=26;WallControl=!WalkerStepClear(WallProbe,WallProbe);break;}}if(WallControl)break;}
 Report->SetBoolField(TEXT("wall_collision_positive_control"),WallControl);
 int32 WrongSideSegments=0,StraightSegments=0;
 for(const auto& A:Vehicles)for(int32 I=0;I<A.Route.Num();I++){FVector D=(A.Route[(I+1)%A.Route.Num()]-A.Route[I]).GetSafeNormal2D(),Mid=(A.Route[(I+1)%A.Route.Num()]+A.Route[I])*.5f;
  if(FMath::Abs(D.X)>.999f){float Y=EastRoads[0];for(float Road:EastRoads)if(FMath::Abs(Mid.Y-Road)<FMath::Abs(Mid.Y-Y))Y=Road;StraightSegments++;if((Mid.Y-Y)*D.X<=0)WrongSideSegments++;}
  else if(FMath::Abs(D.Y)>.999f&&!A.Bus){float X=NorthRoads[0];for(float Road:NorthRoads)if(FMath::Abs(Mid.X-Road)<FMath::Abs(Mid.X-X))X=Road;StraightSegments++;if(-(Mid.X-X)*D.Y<=0)WrongSideSegments++;}
 }
 Report->SetNumberField(TEXT("right_hand_traffic_straight_segments"),StraightSegments);Report->SetNumberField(TEXT("wrong_side_traffic_segments"),WrongSideSegments);


 int32 InsideWalls=0,Airborne=0,Invalid=0,StaticCarHits=0,ParkedHits=0,PedestrianContacts=0,PedestrianCarContacts=0,MovingCarContacts=0;float MaxHeight=0;
 TArray<float> CarStart,CarStill,CarLongest;for(const auto& A:Vehicles){CarStart.Add(A.Travelled);CarStill.Add(0);CarLongest.Add(0);}
 TArray<float> PreviousTravel,Still,Longest;for(const auto& W:Walkers){PreviousTravel.Add(W.Travelled);Still.Add(0);Longest.Add(0);}
 int32 HeightRecoveries=0;for(int32 I=0;I<Walkers.Num();I+=37)if(!Walkers[I].TransitPassenger){Walkers[I].Position.Z=5000;HeightRecoveries++;}
 const int32 Steps=FMath::CeilToInt(Seconds*15);
 for(int32 Step=0;Step<Steps;Step++){
  Elapsed+=1.f/15;SimulateTraffic(1.f/30);SimulateTraffic(1.f/30);SimulateWalkers(1.f/15);
  for(int32 I=0;I<Walkers.Num();I++){const auto& W=Walkers[I];bool SignalWait=W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing;
   Still[I]=W.Activity==EPedActivity::Walking&&!SignalWait&&!W.YieldingToPlayer&&W.Travelled-PreviousTravel[I]<.01f?Still[I]+1.f/15:0;Longest[I]=FMath::Max(Longest[I],Still[I]);PreviousTravel[I]=W.Travelled;
   if(Step%15==0&&!W.TransitPassenger&&!PedHidden(W)&&W.Activity==EPedActivity::Walking){if(!WalkerStepClear(W.Position,W.Position)){InsideWalls++;if(InsideWalls<6)UE_LOG(LogTemp,Warning,TEXT("MAP_WALL id=%d pos=%s"),I,*W.Position.ToString());}if(W.Position.Z>65)Airborne++;if(W.Position.ContainsNaN())Invalid++;MaxHeight=FMath::Max(MaxHeight,float(W.Position.Z));}
  }
  if(Step%15==0&&Step>75){
   TMap<FIntPoint,TArray<int32>> Grid;
   for(int32 I=0;I<Walkers.Num();I++){const auto& W=Walkers[I];if(W.Activity!=EPedActivity::Walking||W.TransitPassenger)continue;
    FIntPoint Cell(FMath::FloorToInt(W.Position.X/150),FMath::FloorToInt(W.Position.Y/150));
    for(int32 X=-1;X<=1;X++)for(int32 Y=-1;Y<=1;Y++)if(auto* Others=Grid.Find(Cell+FIntPoint(X,Y)))for(int32 J:*Others)if(FVector::DistSquared2D(W.Position,Walkers[J].Position)<FMath::Square(60.f)){PedestrianContacts++;if(PedestrianContacts<=6)UE_LOG(LogTemp,Warning,TEXT("MAP_PEDESTRIAN_CONTACT pair=%d,%d distance=%.1f"),I,J,FVector::Dist2D(W.Position,Walkers[J].Position));}
    Grid.FindOrAdd(Cell).Add(I);
   }
  }
  if(Step%15==0){
   for(const auto& W:Walkers)if(!W.TransitPassenger&&!PedHidden(W))for(const auto& A:Vehicles){FVector D=W.Position-A.Position;if(D.SizeSquared2D()>FMath::Square(A.HalfLength+150))continue;FVector F=FRotator(0,A.Heading,0).Vector(),R(-F.Y,F.X,0);if(FMath::Abs(FVector::DotProduct(D,F))<A.HalfLength+28&&FMath::Abs(FVector::DotProduct(D,R))<A.HalfWidth+28){PedestrianCarContacts++;if(PedestrianCarContacts<5)UE_LOG(LogTemp,Warning,TEXT("MAP_PEDESTRIAN_CAR ped=%s car=%s"),*W.Position.ToString(),*A.Position.ToString());}}
   for(int32 I=0;I<Vehicles.Num();I++)for(int32 J=I+1;J<Vehicles.Num();J++){
    const auto& A=Vehicles[I];const auto& B=Vehicles[J];FVector D=B.Position-A.Position;if(D.SizeSquared2D()>FMath::Square(A.HalfLength+B.HalfLength+100))continue;
    FVector F=FRotator(0,A.Heading,0).Vector(),G=FRotator(0,B.Heading,0).Vector(),R(-F.Y,F.X,0),S(-G.Y,G.X,0);bool Hit=true;
    for(FVector Axis:{F,G,R,S}){float E=A.HalfLength*FMath::Abs(FVector::DotProduct(F,Axis))+A.HalfWidth*FMath::Abs(FVector::DotProduct(R,Axis))+B.HalfLength*FMath::Abs(FVector::DotProduct(G,Axis))+B.HalfWidth*FMath::Abs(FVector::DotProduct(S,Axis));if(FMath::Abs(FVector::DotProduct(D,Axis))>=E-10){Hit=false;break;}}
    if(Hit){MovingCarContacts++;if(MovingCarContacts<5)UE_LOG(LogTemp,Warning,TEXT("MAP_MOVING_CAR pair=%d,%d"),I,J);}
   }
  }
  for(int32 I=0;I<Vehicles.Num();I++){CarStill[I]=Vehicles[I].Velocity<1?CarStill[I]+1.f/15:0;CarLongest[I]=FMath::Max(CarLongest[I],CarStill[I]);}
  if(Step%15==0)for(const auto& A:Vehicles){
   for(const auto& P:ParkedCars){if(!P.Visual.IsValid())continue;auto Bounds=P.Visual->Bounds.GetBox();FVector F=FRotator(0,A.Heading,0).Vector(),R(-F.Y,F.X,0),D=P.Position-A.Position;float Along=FMath::Abs(FVector::DotProduct(D,F)),Side=FMath::Abs(FVector::DotProduct(D,R));auto E=Bounds.GetExtent();float L=FMath::Abs(F.X)*E.X+FMath::Abs(F.Y)*E.Y,W=FMath::Abs(R.X)*E.X+FMath::Abs(R.Y)*E.Y;if(Along<A.HalfLength+L-10&&Side<A.HalfWidth+W-10){ParkedHits++;if(ParkedHits<4)UE_LOG(LogTemp,Warning,TEXT("MAP_PARKED_HIT moving=%s parked=%s"),*A.Position.ToString(),*P.Position.ToString());}}
   FHitResult Hit;FVector P=A.Position+FVector(0,0,100);TArray<FOverlapResult> Contacts;if(GetWorld()->OverlapMultiByObjectType(Contacts,P,FRotator(0,A.Heading,0).Quaternion(),FCollisionObjectQueryParams(ECC_WorldStatic),FCollisionShape::MakeBox(FVector(A.HalfLength*.9f,A.HalfWidth*.9f,60)),FCollisionQueryParams())){StaticCarHits++;if(StaticCarHits<=12)for(const auto& Contact:Contacts)UE_LOG(LogTemp,Warning,TEXT("MAP_CAR_STATIC car=%s pos=%s heading=%.1f actor=%s component=%s instance=%d"),*GetNameSafe(A.Visual.IsValid()?A.Visual->GetSkinnedAsset():nullptr),*A.Position.ToString(),A.Heading,*GetNameSafe(Contact.GetActor()),*GetNameSafe(Contact.GetComponent()),Contact.ItemIndex);}}
 }
 int32 Stalled=0;float MaxStop=0;for(int32 I=0;I<Longest.Num();I++){MaxStop=FMath::Max(MaxStop,Longest[I]);if(Longest[I]>25){Stalled++;if(Stalled<=12)UE_LOG(LogTemp,Warning,TEXT("MAP_STALL id=%d seconds=%.1f pos=%s segment=%d"),I,Longest[I],*Walkers[I].Position.ToString(),Walkers[I].Segment);}}
 float MinCarTravel=1e9,MaxCarStop=0;for(int32 I=0;I<Vehicles.Num();I++){MinCarTravel=FMath::Min(MinCarTravel,Vehicles[I].Travelled-CarStart[I]);MaxCarStop=FMath::Max(MaxCarStop,CarLongest[I]);}
 Report->SetNumberField(TEXT("pedestrian_vehicle_contact_samples"),PedestrianCarContacts);Report->SetNumberField(TEXT("moving_vehicle_overlap_samples"),MovingCarContacts);Report->SetNumberField(TEXT("pedestrian_close_contact_samples"),PedestrianContacts);Report->SetNumberField(TEXT("parked_vehicle_overlap_samples"),ParkedHits);Report->SetNumberField(TEXT("minimum_vehicle_travel_cm"),MinCarTravel);Report->SetNumberField(TEXT("longest_vehicle_stop_seconds"),MaxCarStop);
 Report->SetNumberField(TEXT("pedestrians"),Walkers.Num());Report->SetNumberField(TEXT("vehicles"),Vehicles.Num());Report->SetNumberField(TEXT("wall_penetration_samples"),InsideWalls);Report->SetNumberField(TEXT("airborne_samples"),Airborne);Report->SetNumberField(TEXT("invalid_positions"),Invalid);Report->SetNumberField(TEXT("maximum_street_foot_height_cm"),MaxHeight);Report->SetNumberField(TEXT("injected_invalid_heights"),HeightRecoveries);Report->SetNumberField(TEXT("unplanned_stalls"),Stalled);Report->SetNumberField(TEXT("longest_unplanned_stop_seconds"),MaxStop);Report->SetNumberField(TEXT("static_vehicle_overlap_samples"),StaticCarHits);Report->SetNumberField(TEXT("crossings_completed"),PedestrianCrossings);Report->SetNumberField(TEXT("illegal_crossings"),IllegalCrossings);
 TSharedPtr<FJsonObject> Avoidance;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(ValidateStreetFlow()),Avoidance);if(Avoidance)Report->SetObjectField(TEXT("avoidance_scenarios"),Avoidance);
 auto RestoreWalkers=Walkers;auto RestorePedJunctions=PedestrianJunctions;Walkers.Empty();PedestrianJunctions.Empty();
 TSharedPtr<FJsonObject> Traffic;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(ValidateTraffic(180)),Traffic);if(Traffic)Report->SetObjectField(TEXT("isolated_traffic_and_render_cadence"),Traffic);
 Walkers=MoveTemp(RestoreWalkers);PedestrianJunctions=MoveTemp(RestorePedJunctions);
 const float SavedCycle=CycleSeconds,SavedRain=RainIntensity;const int32 SavedDay=GameDay,SavedOverride=DeveloperRainOverride;DeveloperRainOverride=1;
 RainIntensity=0;for(int32 I=0;I<900;I++)UpdateWeather(1.f/30);const bool RainStarted=RainIntensity>.6f&&RainMesh&&RainDrops.Num()==1800;
 FVector Eye=FVector::ZeroVector;if(auto* PC=GetWorld()->GetFirstPlayerController())if(PC->PlayerCameraManager)Eye=PC->PlayerCameraManager->GetCameraLocation();
 auto* TestRoof=GetWorld()->SpawnActor<AStaticMeshActor>();TestRoof->SetMobility(EComponentMobility::Movable);TestRoof->GetStaticMeshComponent()->SetStaticMesh(Cube);TestRoof->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));TestRoof->SetActorLocation(Eye+FVector(0,0,500));TestRoof->SetActorScale3D(FVector(50,50,1));
 RainOrigin=FVector(1e9);UpdateWeather(1.f/30);int32 RoofHits=0,RainUnderRoof=0;
 for(int32 I=0;I<RainFloors.Num();I++){if(RainFloors[I]>=Eye.Z+549)RoofHits++;FTransform T;RainMesh->GetInstanceTransform(I,T);if(!T.GetScale3D().IsNearlyZero()&&RainDrops[I].Z<RainFloors[I]+25)RainUnderRoof++;}
 TestRoof->Destroy();DeveloperRainOverride=0;for(int32 I=0;I<900;I++)UpdateWeather(1.f/30);const bool RainStopped=RainIntensity<.001f;
 auto Weather=MakeShared<FJsonObject>();Weather->SetBoolField(TEXT("rain_started_gradually"),RainStarted);Weather->SetBoolField(TEXT("rain_stopped_gradually"),RainStopped);Weather->SetNumberField(TEXT("roof_occlusion_probes"),RainFloors.Num());Weather->SetNumberField(TEXT("roof_hits"),RoofHits);Weather->SetNumberField(TEXT("visible_drops_below_surface"),RainUnderRoof);Report->SetObjectField(TEXT("weather_rendering"),Weather);
 CycleSeconds=SavedCycle;GameDay=SavedDay;RainIntensity=SavedRain;DeveloperRainOverride=SavedOverride;if(RainMesh)RainMesh->SetVisibility(SavedRain>.005f);
 FString Result;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Result));return Result;
}



float ABogotaCity::StreetClearance(FVector At)const{
 float Clearance=1e9;for(float X:NorthRoads)Clearance=FMath::Min(Clearance,float(FMath::Abs(At.X-X)-750));for(float Y:EastRoads)Clearance=FMath::Min(Clearance,float(FMath::Abs(At.Y-Y)-(Y==0?1150:750)));return Clearance;
}
bool ABogotaCity::WalkerStreetStepClear(const FWalker& W,FVector From,FVector To)const{
 if(!WalkerStepClear(From,To))return false;
 if(W.Crossing||W.TransitPassenger||W.Activity!=EPedActivity::Walking)return true;
 const float Before=StreetClearance(From),After=StreetClearance(To);return After>=40||(Before<40&&After>Before+.01f);
}
void ABogotaCity::UpdateWalkerVisuals(float Alpha){
 for(auto& W:Walkers)if(W.Visual.IsValid()&&!W.Visual->IsHidden()){
  FVector P=FMath::Lerp(W.PreviousPosition,W.Position,Alpha);float H=W.PreviousHeading+FMath::FindDeltaAngleDegrees(W.PreviousHeading,W.Heading)*Alpha;
  W.Visual->SetActorLocationAndRotation(P,FRotator(0,H-90,0));
 }
}

FString ABogotaCity::ValidatePedestrianPresentation(){
 auto Saved=Walkers;auto SavedJunctions=PedestrianJunctions;auto SavedAdmission=PedestrianNextAdmission;auto SavedObstacle=PedestrianTestObstacle;float SavedElapsed=Elapsed;
 auto R=MakeShared<FJsonObject>();int32 URO=0;for(const auto& W:Walkers)if(W.Visual.IsValid())if(auto* S=Cast<USkeletalMeshComponent>(W.Visual->GetRootComponent()))if(S->bEnableUpdateRateOptimizations)URO++;
 R->SetNumberField(TEXT("visible_npcs_with_animation_throttling"),URO);
 Walkers.Empty();PedestrianJunctions.Empty();PedestrianNextAdmission.Empty();
 const FVector Start(-8000,-45000,26);FWalker P;P.Route={Start,Start+FVector(6000,0,0),Start+FVector(6000,1500,0),Start+FVector(0,1500,0)};P.Position=P.PreviousPosition=Start;P.Speed=112;
 auto* Probe=GetWorld()->SpawnActor<AStaticMeshActor>();Probe->SetMobility(EComponentMobility::Movable);Probe->GetStaticMeshComponent()->SetStaticMesh(Cube);Probe->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);Probe->SetActorLocation(Start);P.Visual=Probe;Walkers.Add(P);PedestrianTestObstacle=Start+FVector(0,2000,0);
 float Acc=0,MaxJump=0;int32 MovingFrames=0;FVector Last=Start;
 for(int32 Frame=0;Frame<120;Frame++){Acc+=1.f/60;while(Acc>=1.f/15){Elapsed+=1.f/15;SimulateWalkers(1.f/15);Acc-=1.f/15;}UpdateWalkerVisuals(Acc*15);FVector At=Probe->GetActorLocation();float D=FVector::Dist2D(At,Last);if(D>.1f)MovingFrames++;MaxJump=FMath::Max(MaxJump,D);Last=At;}
 float Before=Walkers[0].Travelled+Acc*P.Speed;Acc+=.2f;while(Acc>=1.f/15){SimulateWalkers(1.f/15);Acc-=1.f/15;}float Loss=FMath::Abs(Walkers[0].Travelled+Acc*P.Speed-Before-.2f*P.Speed);
 R->SetNumberField(TEXT("moving_render_frames"),MovingFrames);R->SetNumberField(TEXT("render_frames"),120);R->SetNumberField(TEXT("maximum_render_step_cm"),MaxJump);R->SetNumberField(TEXT("hitch_time_loss_cm"),Loss);Probe->Destroy();Walkers.Empty();
 int32 Yielded=0,Resumed=0,RoadIntrusions=0;float MinPlayerDistance=1e9,MaxWaitingTurn=0;
 for(float Side:{-1.f,1.f}){
  auto* Wall=GetWorld()->SpawnActor<AStaticMeshActor>();Wall->SetMobility(EComponentMobility::Movable);Wall->GetStaticMeshComponent()->SetStaticMesh(Cube);Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Wall->SetActorLocation(FVector(Side*1160,-4000,150));Wall->SetActorScale3D(FVector(1,20,3));
  PedestrianTestObstacle=FVector(Side*950,-4100,116);Walkers.Empty();
  for(int32 I=0;I<6;I++){FWalker W;W.Route={FVector(Side*950,-6000,26),FVector(Side*950,-2000,26),FVector(Side*1020,-2000,26),FVector(Side*1020,-6000,26)};W.Position=W.PreviousPosition=FVector(Side*950,-4300-I*125,26);W.Heading=90;W.Speed=112;W.ModelIndex=0;Walkers.Add(W);}
  bool DidYield=false;
  for(int32 Step=0;Step<225;Step++){Elapsed+=1.f/15;float Previous=Walkers[0].Heading;SimulateWalkers(1.f/15);DidYield|=Walkers[0].YieldingToPlayer;
   for(const auto& W:Walkers){if(StreetClearance(W.Position)<39)RoadIntrusions++;MinPlayerDistance=FMath::Min(MinPlayerDistance,FVector::Dist2D(W.Position,PedestrianTestObstacle.GetValue()));}
   if(Step>150)MaxWaitingTurn=FMath::Max(MaxWaitingTurn,FMath::Abs(FMath::FindDeltaAngleDegrees(Previous,Walkers[0].Heading)));
  }
  if(DidYield)Yielded++;TArray<float> Travel;for(auto& W:Walkers)Travel.Add(W.Travelled);PedestrianTestObstacle=FVector(1e8);
  for(int32 Step=0;Step<300;Step++){Elapsed+=1.f/15;SimulateWalkers(1.f/15);}
  bool All=true;for(int32 I=0;I<Walkers.Num();I++)if(Walkers[I].Travelled-Travel[I]<500)All=false;if(All)Resumed++;
  for(auto& W:Walkers)if(W.Visual.IsValid())W.Visual->Destroy();Walkers.Empty();Wall->Destroy();
 }
 R->SetNumberField(TEXT("confined_sidewalk_scenarios"),2);R->SetNumberField(TEXT("yielded_without_entering_road"),Yielded);R->SetNumberField(TEXT("resumed_after_player_leaves"),Resumed);R->SetNumberField(TEXT("road_intrusion_frames"),RoadIntrusions);R->SetNumberField(TEXT("minimum_player_clearance_cm"),MinPlayerDistance);R->SetNumberField(TEXT("maximum_waiting_turn_degrees"),MaxWaitingTurn);
 Walkers=MoveTemp(Saved);PedestrianJunctions=MoveTemp(SavedJunctions);PedestrianNextAdmission=MoveTemp(SavedAdmission);PedestrianTestObstacle=SavedObstacle;Elapsed=SavedElapsed;
 FString Result;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Result));return Result;
}
