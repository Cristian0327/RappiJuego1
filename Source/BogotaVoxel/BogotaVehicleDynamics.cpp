#include "BogotaGame.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Math/RotationMatrix.h"
#include "Json.h"
#include "DeliverySystem.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraActor.h"
#include "UnrealClient.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

bool ABogotaCity::ResolveVehicleGround(const FStreetAgent& A,FVector At,float Heading,FVector& Ground,FRotator& Rotation) const{
 if(A.WheelRest.Num()<4)return false;const int32 Rear=A.Articulated?4:2;if(!A.WheelRest.IsValidIndex(Rear+1))return false;
 FVector Local[4]={A.WheelRest[0].GetLocation()*A.ModelScale,A.WheelRest[1].GetLocation()*A.ModelScale,A.WheelRest[Rear].GetLocation()*A.ModelScale,A.WheelRest[Rear+1].GetLocation()*A.ModelScale};float Height[4];FCollisionQueryParams Q(SCENE_QUERY_STAT(VehicleSuspension),false);if(A.Visual.IsValid())Q.AddIgnoredActor(A.Visual->GetOwner());
 for(int32 I=0;I<4;I++){FVector XY=At+FRotator(0,Heading,0).RotateVector(Local[I]);FHitResult Hit;if(!GetWorld()->LineTraceSingleByObjectType(Hit,FVector(XY.X,XY.Y,At.Z+160),FVector(XY.X,XY.Y,At.Z-220),FCollisionObjectQueryParams(ECC_WorldStatic),Q)||Hit.ImpactNormal.Z<.65f)return false;Height[I]=Hit.ImpactPoint.Z;}
 float WheelBase=FMath::Abs((Local[0].X+Local[1].X-Local[2].X-Local[3].X)*.5f),Track=(Local[1].Y+Local[3].Y-Local[0].Y-Local[2].Y)*.5f;
 float SlopeX=((Height[0]+Height[1]-Height[2]-Height[3])*.5f)/FMath::Max(50.f,WheelBase),SlopeY=((Height[1]+Height[3]-Height[0]-Height[2])*.5f)/(FMath::Abs(Track)>50?Track:50);
 if(FMath::Abs(SlopeX)>.4f||FMath::Abs(SlopeY)>.4f)return false;
 FVector Normal=FRotator(0,Heading,0).RotateVector(FVector(-SlopeX,-SlopeY,1).GetSafeNormal());Rotation=FRotationMatrix::MakeFromXZ(FRotator(0,Heading,0).Vector(),Normal).Rotator();Ground=At;Ground.Z=(Height[0]+Height[1]+Height[2]+Height[3])*.25f+.5f;return true;
}
void ABogotaCity::UpdateVehicleGroundVisual(FStreetAgent& A,FVector At,float Heading,float Dt){
 FVector Ground;FRotator Rotation;bool Supported=ResolveVehicleGround(A,At,Heading,Ground,Rotation);
 float Offset=Supported?Ground.Z-At.Z:0,Pitch=Supported?Rotation.Pitch:0,Roll=Supported?Rotation.Roll:0;
 A.GroundOffset=FMath::FInterpTo(A.GroundOffset,Offset,Dt,8);A.GroundPitch=FMath::FInterpTo(A.GroundPitch,Pitch,Dt,8);A.GroundRoll=FMath::FInterpTo(A.GroundRoll,Roll,Dt,8);
 A.Visual->GetOwner()->SetActorLocationAndRotation(At+FVector(0,0,A.GroundOffset),FRotator(A.GroundPitch,Heading,A.GroundRoll));
}
void ABogotaCity::ApplyVehicleDoors(UPoseableMeshComponent* Visual,bool Bus,float Left,float Right,TMap<FName,FTransform>& Rest){
 if(!Visual)return;
 auto Pose=[&](FName Bone,float Amount,float Side){if(Visual->GetBoneIndex(Bone)==INDEX_NONE)return;if(!Rest.Contains(Bone))Rest.Add(Bone,Visual->GetBoneTransformByName(Bone,EBoneSpaces::ComponentSpace));FTransform T=Rest[Bone];
  if(Bus)T.AddToTranslation(FVector(Side*50*Amount,-8*Amount,0));else T.SetRotation(FQuat(FVector::UpVector,FMath::DegreesToRadians(Side*65*Amount))*T.GetRotation());Visual->SetBoneTransformByName(Bone,T,EBoneSpaces::ComponentSpace);};
 if(Bus){Pose(TEXT("bus_door_a"),Left,-1);Pose(TEXT("bus_door_b"),Left,1);}else{for(FName Bone:{FName(TEXT("door_L")),FName(TEXT("door_R"))}){if(Visual->GetBoneIndex(Bone)==INDEX_NONE)continue;if(!Rest.Contains(Bone))Rest.Add(Bone,Visual->GetBoneTransformByName(Bone,EBoneSpaces::ComponentSpace));bool IsLeft=Rest[Bone].GetLocation().Y<0;Pose(Bone,IsLeft?Left:Right,IsLeft?1:-1);}}
}
void ABogotaCity::UpdateParkedDoors(float Dt){for(auto& P:ParkedCars)if(P.Visual.IsValid()){P.VisualDoorOpen=FMath::FInterpConstantTo(P.VisualDoorOpen,P.DoorOpen,Dt,2.5f);FVector DoorLocal=FRotator(0,-P.Heading,0).RotateVector(P.Door-P.Position);ApplyVehicleDoors(P.Visual.Get(),false,DoorLocal.Y<0?P.VisualDoorOpen:0,DoorLocal.Y>=0?P.VisualDoorOpen:0,P.DoorRest);}}

FString ABogotaCity::ValidateVehicleDynamics(){
 auto Report=MakeShared<FJsonObject>();auto Checks=MakeShared<FJsonObject>();auto Check=[&](const TCHAR* Name,bool Passed){Checks->SetBoolField(Name,Passed);UE_LOG(LogTemp,Display,TEXT("VEHICLE_DYNAMICS %s %s"),Name,Passed?TEXT("PASS"):TEXT("FAIL"));};
 int32 CurbCount=0,StreetCount=0,TiltedCount=0;for(const auto& P:ParkedCars){if(P.CurbParked)CurbCount++;else StreetCount++;if(P.Visual.IsValid()&&P.CurbParked&&FMath::Abs(P.Visual->GetOwner()->GetActorRotation().Roll)>1.5f)TiltedCount++;}Check(TEXT("mixed_curb_and_street_parking"),CurbCount==4&&StreetCount==8);Check(TEXT("curb_parked_cars_follow_terrain"),TiltedCount>=3);
 FStreetAgent Probe=Vehicles[0];FTransform SavedTransform=Probe.Visual->GetOwner()->GetActorTransform();auto* Ramp=GetWorld()->SpawnActor<AStaticMeshActor>();Ramp->SetMobility(EComponentMobility::Movable);Ramp->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));Ramp->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Ramp->GetStaticMeshComponent()->SetCollisionObjectType(ECC_WorldStatic);Ramp->SetActorLocation(FVector(90000,90000,-50));Ramp->SetActorScale3D(FVector(20,20,1));
 FVector At(90000,90000,20),Ground;FRotator Rotation;bool Flat=ResolveVehicleGround(Probe,At,0,Ground,Rotation);Check(TEXT("four_wheels_on_flat_ground"),Flat&&FMath::Abs(Rotation.Roll)<.1f&&FMath::Abs(Rotation.Pitch)<.1f);
 Ramp->SetActorRotation(FRotator(0,0,8));bool Sloped=ResolveVehicleGround(Probe,At,0,Ground,Rotation);Check(TEXT("body_leans_on_cross_slope"),Sloped&&FMath::Abs(FMath::FindDeltaAngleDegrees(Rotation.Roll,8))<1&&FMath::Abs(Rotation.Pitch)<1);
 Probe.GroundPitch=Probe.GroundRoll=Probe.GroundOffset=0;for(int32 I=0;I<120;I++)UpdateVehicleGroundVisual(Probe,At,0,1.f/60);Check(TEXT("parked_vehicle_retains_ground_lean"),FMath::Abs(Probe.Visual->GetOwner()->GetActorRotation().Roll)>5);Probe.Visual->GetOwner()->SetActorTransform(SavedTransform);
 Check(TEXT("unsupported_wheels_rejected"),!ResolveVehicleGround(Probe,At+FVector(3000,0,0),0,Ground,Rotation));Ramp->Destroy();
 auto* CarVisual=Vehicles[0].Visual.Get();TMap<FName,FTransform> CarRest;ApplyVehicleDoors(CarVisual,false,0,0,CarRest);FTransform Wheel=CarVisual->GetBoneTransformByName(TEXT("wheel_0_L"),EBoneSpaces::ComponentSpace);FName LeftBone=CarRest[FName(TEXT("door_L"))].GetLocation().Y<0?FName(TEXT("door_L")):FName(TEXT("door_R"));FTransform Door=CarVisual->GetBoneTransformByName(LeftBone,EBoneSpaces::ComponentSpace);ApplyVehicleDoors(CarVisual,false,1,0,CarRest);Check(TEXT("car_door_hinge_moves"),CarVisual->GetBoneIndex(TEXT("door_L"))!=INDEX_NONE&&FMath::Abs(FMath::FindDeltaAngleDegrees(Door.Rotator().Yaw,CarVisual->GetBoneTransformByName(LeftBone,EBoneSpaces::ComponentSpace).Rotator().Yaw))>60);Check(TEXT("opening_door_preserves_wheel_pose"),Wheel.Equals(CarVisual->GetBoneTransformByName(TEXT("wheel_0_L"),EBoneSpaces::ComponentSpace),.01f));ApplyVehicleDoors(CarVisual,false,0,0,CarRest);
 auto* BusVisual=Vehicles[96].Visual.Get();TMap<FName,FTransform> BusRest;ApplyVehicleDoors(BusVisual,true,0,0,BusRest);FVector Closed=BusVisual->GetBoneTransformByName(TEXT("bus_door_a"),EBoneSpaces::ComponentSpace).GetLocation();Check(TEXT("bus_door_faces_platform"),Closed.Y<0);ApplyVehicleDoors(BusVisual,true,1,0,BusRest);Check(TEXT("bus_door_slides_open"),BusVisual->GetBoneIndex(TEXT("bus_door_a"))!=INDEX_NONE&&FVector::Dist(Closed,BusVisual->GetBoneTransformByName(TEXT("bus_door_a"),EBoneSpaces::ComponentSpace).GetLocation())>45);ApplyVehicleDoors(BusVisual,true,0,0,BusRest);
 auto SavedVehicles=Vehicles;auto SavedWalkers=Walkers;auto SavedReservations=TrafficReservations;auto SavedJunctions=PedestrianJunctions;int32 SavedBoardings=TransitBoardings,SavedAlightings=TransitAlightings;float SavedElapsed=Elapsed;Vehicles.Empty();Walkers.Empty();TrafficReservations.Empty();PedestrianJunctions.Empty();int32 Boarded=0,Alighted=0,ClosedWait=0;float MaximumStep=0;
 for(float Side:{-1.f,1.f}){
  FStreetAgent Bus=SavedVehicles[96];Bus.Position=FVector(-27000,Side*330,9);Bus.Heading=Side>0?0:180;Bus.Wait=4;Bus.Velocity=0;Bus.PlayerControlled=Bus.DevParked=false;Bus.DoorOpen=0;Vehicles={Bus};FWalker Passenger;Passenger.TransitPassenger=true;Passenger.Activity=EPedActivity::WaitingTransit;Passenger.StationIndex=0;Passenger.Position=FVector(-26350,0,110);Passenger.Speed=110;UpdateWalkerInteraction(Passenger,1.f/30);FVector Waiting=Passenger.Position;for(int32 I=0;I<20;I++)UpdateWalkerInteraction(Passenger,1.f/30);if(Passenger.Position.Equals(Waiting,.01f))ClosedWait++;
  Vehicles[0].DoorOpen=1;for(int32 I=0;I<600&&Passenger.Activity!=EPedActivity::InsideTransit;I++){FVector Previous=Passenger.Position;UpdateWalkerInteraction(Passenger,1.f/30);MaximumStep=FMath::Max(MaximumStep,float(FVector::Dist2D(Previous,Passenger.Position)));}if(Passenger.Activity==EPedActivity::InsideTransit)Boarded++;
  Vehicles[0].Position.X=-7000;Vehicles[0].Wait=4;UpdateWalkerInteraction(Passenger,1.f/30);for(int32 I=0;I<300&&Passenger.Activity!=EPedActivity::WaitingTransit;I++)UpdateWalkerInteraction(Passenger,1.f/30);if(Passenger.Activity==EPedActivity::WaitingTransit)Alighted++;
 }
 Check(TEXT("passenger_waits_for_open_door"),ClosedWait==2);Check(TEXT("walks_into_bus_both_directions"),Boarded==2);Check(TEXT("walks_out_at_next_station"),Alighted==2);Check(TEXT("boarding_has_no_position_jump"),MaximumStep<4);
 FStreetAgent Gate=SavedVehicles[96];Gate.Route={FVector(-27000,330,9),FVector(-17000,330,9),FVector(-17000,-330,9),FVector(-27000,-330,9)};Gate.Position=Gate.PreviousPosition=Gate.Route[0];Gate.Segment=0;Gate.Heading=0;Gate.Velocity=0;Gate.Wait=0;Gate.StopCooldown=20;Gate.PathDistance=0;Gate.LoopLength=21320;Gate.DoorOpen=1;Gate.PlayerControlled=Gate.DevParked=false;Vehicles={Gate};bool SafeGate=true;for(int32 I=0;I<40;I++){SimulateTraffic(1.f/30);if(Vehicles[0].DoorOpen>.001f&&Vehicles[0].Velocity>.01f)SafeGate=false;}Check(TEXT("bus_cannot_depart_with_open_door"),SafeGate&&Vehicles[0].DoorOpen<.001f);
 Vehicles=MoveTemp(SavedVehicles);Walkers=MoveTemp(SavedWalkers);TrafficReservations=MoveTemp(SavedReservations);PedestrianJunctions=MoveTemp(SavedJunctions);TransitBoardings=SavedBoardings;TransitAlightings=SavedAlightings;Elapsed=SavedElapsed;
 Report->SetObjectField(TEXT("checks"),Checks);Report->SetNumberField(TEXT("maximum_boarding_step_cm"),MaximumStep);Report->SetNumberField(TEXT("boarding_directions"),Boarded);FString Result;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Result));return Result;
}

void ABogotaCity::TickVehicleDynamicsVisualCheck(){
 static int32 Stage=0;static float Lean=0;static ACameraActor* View=nullptr;auto* Player=Cast<ABogotaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));if(!Player)return;auto* PC=Cast<APlayerController>(Player->GetController());if(!PC)return;
 auto CameraAt=[&](FVector At,FVector Target){if(!View)View=GetWorld()->SpawnActor<ACameraActor>();View->SetActorLocationAndRotation(At,(Target-At).Rotation());PC->SetViewTarget(View);};
 if(Elapsed>3&&Stage==0){Player->BogDev(true);Player->BogCar(4);auto& A=Vehicles[4];float Best=0;FVector Where(780,-6000,27);for(float X:{650.f,750.f,850.f,950.f,1050.f,1150.f}){FVector Ground;FRotator R;if(ResolveVehicleGround(A,FVector(X,-6000,27),-90,Ground,R)&&FMath::Abs(R.Roll)>Best){Best=FMath::Abs(R.Roll);Where=FVector(X,-6000,27);}}A.Position=A.PreviousPosition=Where;A.Heading=A.PreviousHeading=-90;A.Velocity=0;CameraAt(Where+FVector(650,850,380),Where+FVector(0,0,100));Stage=1;}
 if(Elapsed>8&&Stage==1){Lean=FMath::Abs(Vehicles[4].Visual->GetOwner()->GetActorRotation().Roll);FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/Carro_Inclinado.png"),false,false);Stage=2;}
 if(Elapsed>9&&Stage==2){Player->LeaveDeveloperCar();auto& P=ParkedCars[0];Player->SetActorLocation(P.Door+FVector(0,500,92));auto& W=Walkers[P.Walker];W.Position=W.PreviousPosition=P.Door;W.Activity=EPedActivity::ApproachCar;W.ActionTime=0;W.ResumePosition=P.Door+FVector(0,400,0);P.Occupied=false;P.DoorTarget=P.DoorOpen=P.VisualDoorOpen=0;FVector Cam=P.Position+FVector(P.Door.X>P.Position.X?850.f:-850.f,550,350);CameraAt(Cam,P.Position+FVector(0,0,95));Stage=3;}
 if(Elapsed>9.7f&&Stage==3){FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/NPC_Abre_Carro.png"),false,false);Stage=4;}
 if(Elapsed>10.5f&&Stage==4){FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/NPC_Entra_Carro.png"),false,false);Stage=5;}
 if(Elapsed>13&&Stage==5){auto& Bus=Vehicles[96];Bus.Position=Bus.PreviousPosition=FVector(17000,330,9);Bus.Heading=Bus.PreviousHeading=0;Bus.Velocity=0;Bus.Wait=12;Bus.StopCooldown=20;Bus.DoorOpen=Bus.VisualDoorOpen=0;for(int32 I=0;I<Bus.Route.Num();I++){auto D=Bus.Route[(I+1)%Bus.Route.Num()]-Bus.Route[I];if(D.X>1000&&FMath::Abs(Bus.Route[I].Y-330)<1)Bus.Segment=I;}for(int32 I=Walkers.Num()-4;I<Walkers.Num()-1;I++)if(Walkers[I].TransitPassenger&&Walkers[I].StationIndex==2){Walkers[I].StationIndex=0;Walkers[I].Activity=EPedActivity::WaitingTransit;Walkers[I].BusIndex=INDEX_NONE;Walkers[I].Position=Walkers[I].PreviousPosition=FVector(-26350,0,110);}auto& W=Walkers.Last();W.TransitPassenger=true;W.StationIndex=2;W.BusIndex=INDEX_NONE;W.Activity=EPedActivity::WaitingTransit;W.Position=W.PreviousPosition=FVector(17650,0,110);W.NextInteraction=0;W.ActionTime=0;Player->SetActorLocation(FVector(18150,0,202));CameraAt(FVector(18000,-1500,700),FVector(17380,240,180));Stage=6;}
 if(Elapsed>15.5f&&Stage==6){FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/NPC_Sube_Transmilenio.png"),false,false);Stage=7;}
 if(Elapsed>18&&Stage==7){FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/Transmilenio_Puerta_Abierta.png"),false,false);Stage=8;}
 if(Elapsed>21){FString Report=FString::Printf(TEXT("{\"curb_lean_degrees\":%.3f,\"bus_door_open\":%.3f,\"passenger_inside\":%s}"),Lean,Vehicles[96].DoorOpen,Walkers.Last().Activity==EPedActivity::InsideTransit?TEXT("true"):TEXT("false"));FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/TEXT("vehicle_dynamics_visual_validation.json")));FGenericPlatformMisc::RequestExit(false);}
}
