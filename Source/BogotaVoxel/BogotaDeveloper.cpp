#include "BogotaGame.h"
#include "DeliverySystem.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/PlayerController.h"
#include "Components/CapsuleComponent.h"
#include "Components/BoxComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Json.h"
#include "Sound/SoundBase.h"
#include "Camera/PlayerCameraManager.h"

void ABogotaPlayer::BogDev(bool Enabled){
 if(!Delivery)return;if(Delivery->DeveloperMode!=Enabled){Delivery->ToggleDeveloperMode();if(Delivery->DeveloperMode!=Enabled)return;}
 if(!Delivery->DeveloperMode&&City)City->DeveloperRainOverride=-1;
 Delivery->StatusMessage=FText::FromString(Delivery->DeveloperMode?TEXT("DEV: BogRain 1/0/-1 · BogCar · F subir/bajar · WASD conducir · ESPACIO frenar"):TEXT("Modo normal. Progreso restaurado."));
}
void ABogotaPlayer::BogRain(int32 Mode){
 if(!City||!Delivery)return;if(Mode< -1||Mode>3){Delivery->StatusMessage=FText::FromString(TEXT("BogRain 2: leve · 1: lluvia · 3: tormenta · 0: despejado · -1: automático"));return;}if(!Delivery->DeveloperMode&&Mode!=-1){Delivery->StatusMessage=FText::FromString(TEXT("Activa primero BogDev 1 en la consola F10."));return;}
 City->DeveloperRainOverride=FMath::Clamp(Mode,-1,3);if(Mode>=0&&Mode!=3)City->HailIntensity=0;if(Mode>=0)City->RainIntensity=Mode==3?1.f:Mode==2?.25f:Mode==1?.7f:0.f;City->UpdateWeather(0);City->RefreshWorldLighting();
 Delivery->StatusMessage=FText::FromString(Mode<0?TEXT("Clima automático restaurado."):Mode==0?TEXT("DEV: lluvia desactivada."):Mode==2?TEXT("DEV: lluvia leve."):Mode==3?TEXT("DEV: tormenta con granizo y truenos."):TEXT("DEV: lluvia normal."));
}
void ABogotaPlayer::BogCar(int32 Index){
 if(!Delivery||!Delivery->DeveloperMode){if(Delivery)Delivery->StatusMessage=FText::FromString(TEXT("Activa BogDev 1 para usar los carros."));return;}
 if(Riding){Interact();if(Riding)return;}
 if(DeveloperCarIndex!=INDEX_NONE){if(!LeaveDeveloperCar()||Index<0)return;}
 EnterDeveloperCar(Index);
}
void ABogotaPlayer::SpawnPurpleBus(){
 if(!City||!Delivery)return;
 if(!Delivery->DeveloperMode){Delivery->StatusMessage=FText::FromString(TEXT("Escribe ESOYAM primero; luego PURPURA."));return;}
 if(DeveloperCarIndex!=INDEX_NONE){Delivery->StatusMessage=FText::FromString(TEXT("Baja del vehículo antes de escribir PURPURA."));return;}
 auto* PurpleMesh=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Traffic/Detailed/SK_TransMilenioG66.SK_TransMilenioG66"));if(!PurpleMesh)return;
 FVector Spawn;float Yaw=0,Best=1.e9f;bool Found=false;FCollisionQueryParams Q;Q.AddIgnoredActor(this);
 if(City->Vehicles.IsValidIndex(DeveloperPurpleBusIndex)&&City->VehicleCollision.IsValidIndex(DeveloperPurpleBusIndex))Q.AddIgnoredComponent(City->VehicleCollision[DeveloperPurpleBusIndex].Get());
 auto Candidate=[&](FVector At,float Heading){
  float Distance=FVector::DistSquared2D(At,GetActorLocation());if(Distance>=Best||Distance>FMath::Square(10000.f))return;
  for(float Road:City->NorthRoads)for(float Cross:City->EastRoads)if(FMath::Abs(At.X-Road)<2600&&FMath::Abs(At.Y-Cross)<2600)return;
  FHitResult Floor;if(!GetWorld()->LineTraceSingleByObjectType(Floor,FVector(At.X,At.Y,180),FVector(At.X,At.Y,-100),FCollisionObjectQueryParams(ECC_WorldStatic),Q)||Floor.ImpactNormal.Z<.7f||Floor.ImpactPoint.Z>60)return;
  At.Z=Floor.ImpactPoint.Z+.5f;if(GetWorld()->OverlapBlockingTestByChannel(At+FVector(0,0,150),FRotator(0,Heading,0).Quaternion(),ECC_Pawn,FCollisionShape::MakeBox(FVector(1000,180,140)),Q))return;
  for(int32 I=0;I<City->Vehicles.Num();I++){if(I==DeveloperPurpleBusIndex)continue;const auto& Other=City->Vehicles[I];FVector D=FRotator(0,-Heading,0).RotateVector(Other.Position-At);if(FMath::Abs(D.X)<1000+Other.HalfLength&&FMath::Abs(D.Y)<180+Other.HalfLength)return;}
  for(const auto& W:City->Walkers){if(W.Activity==EPedActivity::InsideTransit||W.Activity==EPedActivity::InsideCar)continue;FVector D=FRotator(0,-Heading,0).RotateVector(W.Position-At);if(FMath::Abs(D.X)<1000&&FMath::Abs(D.Y)<200)return;}
  Spawn=At;Yaw=Heading;Best=Distance;Found=true;
 };
 for(float Offset:{-2000.f,2000.f,-3500.f,3500.f,-5000.f,5000.f,-7500.f,7500.f}){
  for(float Road:City->EastRoads)Candidate(FVector(GetActorLocation().X+Offset,Road+330,0),0);
  for(float Road:City->NorthRoads)Candidate(FVector(Road+270,GetActorLocation().Y+Offset,0),-90);
 }
 if(!Found){Delivery->StatusMessage=FText::FromString(TEXT("MORADO: no hay espacio seguro cercano; acércate a una avenida."));return;}
 if(!City->Vehicles.IsValidIndex(DeveloperPurpleBusIndex)){
  FStreetAgent Bus;Bus.Bus=Bus.Articulated=true;Bus.DevParked=true;Bus.HalfLength=915;Bus.HalfWidth=135;Bus.WheelRadius=49;Bus.ModelScale=1;Bus.Speed=850;Bus.LaneGroup=-1;
  auto* Actor=GetWorld()->SpawnActor<AActor>();auto* Visual=NewObject<UPoseableMeshComponent>(Actor);Actor->SetRootComponent(Visual);Actor->AddInstanceComponent(Visual);Visual->SetMobility(EComponentMobility::Movable);Visual->SetSkinnedAssetAndUpdate(PurpleMesh);Visual->SetMaterial(0,City->TrafficMaterial);Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);Visual->RegisterComponent();Visual->RefreshBoneTransforms();Bus.Visual=Visual;
  for(float Side:{-1.f,1.f}){auto* Light=NewObject<::USpotLightComponent>(Actor);Actor->AddInstanceComponent(Light);Light->SetupAttachment(Visual);Light->SetMobility(EComponentMobility::Movable);Light->SetRelativeLocation(FVector(900,Side*88,115));Light->SetRelativeRotation(FRotator(-10,0,0));Light->SetIntensityUnits(ELightUnits::Lumens);Light->SetIntensity(220);Light->SetLightColor(FLinearColor(1,.92f,.8f));Light->SetAttenuationRadius(2400);Light->SetInnerConeAngle(8);Light->SetOuterConeAngle(36);Light->SetCastShadows(false);Light->SetVisibility(false);Light->RegisterComponent();Bus.Headlights.Add(Light);}
  for(int32 Axle=0;Axle<3;Axle++)for(const TCHAR* Side:{TEXT("L"),TEXT("R")})Bus.WheelRest.Add(Visual->GetBoneTransformByName(FName(*FString::Printf(TEXT("wheel_%d_%s"),Axle,Side)),EBoneSpaces::ComponentSpace));Bus.ArticulationRest=Visual->GetBoneTransformByName(TEXT("articulation"),EBoneSpaces::ComponentSpace);
  auto* Box=NewObject<UBoxComponent>(City);City->AddInstanceComponent(Box);Box->SetupAttachment(City->GetRootComponent());Box->SetMobility(EComponentMobility::Movable);Box->SetBoxExtent(FVector(915,135,150));Box->SetCollisionProfileName(TEXT("BlockAllDynamic"));Box->SetCanEverAffectNavigation(false);Box->RegisterComponent();City->VehicleCollision.Add(Box);DeveloperPurpleBusIndex=City->Vehicles.Add(Bus);
 }
 auto& Bus=City->Vehicles[DeveloperPurpleBusIndex];Bus.Position=Bus.PreviousPosition=Spawn;Bus.Heading=Bus.PreviousHeading=Yaw;Bus.Velocity=0;Bus.Visual->GetOwner()->SetActorLocationAndRotation(Spawn,FRotator(0,Yaw,0));City->VehicleCollision[DeveloperPurpleBusIndex]->SetWorldLocationAndRotation(Spawn+FVector(0,0,150),FRotator(0,Yaw,0));
 Delivery->StatusMessage=FText::FromString(FString::Printf(TEXT("MORADO: TransMilenio morado a %.0f m. Acércate y pulsa F para conducir."),FMath::Sqrt(Best)/100));
}
bool ABogotaPlayer::EnterDeveloperCar(int32 Index){
 if(!City||!Delivery||!Delivery->DeveloperMode||Delivery->PhoneOpen||DeveloperCarIndex!=INDEX_NONE||Riding||BikeSpeed<0)return false;
 int32 BestIndex=INDEX_NONE,Parked=INDEX_NONE;float Best=220;
 auto Distance=[&](FVector P,float H,float L,float W){FVector D=FRotator(0,-H,0).RotateVector(GetActorLocation()-P);return FVector2D(FMath::Max(0.f,float(FMath::Abs(D.X)-L)),FMath::Max(0.f,float(FMath::Abs(D.Y)-W))).Size();};
 if(Index>=0){if(!City->Vehicles.IsValidIndex(Index)||!City->Vehicles[Index].Visual.IsValid()){Delivery->StatusMessage=FText::FromString(FString::Printf(TEXT("Índice inválido. Usa BogCar 0 hasta %d."),City->Vehicles.Num()-1));return false;}BestIndex=Index;}
 else{
  for(int32 I=0;I<City->Vehicles.Num();I++){const auto& A=City->Vehicles[I];if(!A.Visual.IsValid())continue;float D=Distance(A.Position,A.Heading,A.HalfLength,A.HalfWidth);if(D<Best){Best=D;BestIndex=I;}}
  for(int32 I=0;I<City->ParkedCars.Num();I++){const auto& P=City->ParkedCars[I];if(!P.Visual.IsValid())continue;auto E=P.Visual->Bounds.BoxExtent;float D=Distance(P.Position,P.Heading,E.Y,E.X);if(D<Best){Best=D;BestIndex=INDEX_NONE;Parked=I;}}
 }
 if(Parked!=INDEX_NONE){
  auto& P=City->ParkedCars[Parked];auto* V=P.Visual.Get();auto E=V->Bounds.BoxExtent;
  FStreetAgent A;A.Position=A.PreviousPosition=P.Position;A.Heading=A.PreviousHeading=P.Heading;A.Visual=V;A.HalfLength=E.Y;A.HalfWidth=E.X;A.ModelScale=V->GetComponentScale().X;A.WheelRadius=33*A.ModelScale;A.Speed=900;A.LaneGroup=-1;A.DevParked=true;A.Headlights=P.Headlights;A.DoorRest=P.DoorRest;A.GroundPitch=V->GetOwner()->GetActorRotation().Pitch;A.GroundRoll=V->GetOwner()->GetActorRotation().Roll;
  for(int32 Axle=0;Axle<2;Axle++)for(const TCHAR* Side:{TEXT("L"),TEXT("R")})A.WheelRest.Add(V->GetBoneTransformByName(FName(*FString::Printf(TEXT("wheel_%d_%s"),Axle,Side)),EBoneSpaces::ComponentSpace));
  TArray<UBoxComponent*> Boxes;V->GetOwner()->GetComponents(Boxes);for(auto* B:Boxes)B->DestroyComponent();
  auto* Box=NewObject<UBoxComponent>(City);City->AddInstanceComponent(Box);Box->SetupAttachment(City->GetRootComponent());Box->SetMobility(EComponentMobility::Movable);Box->SetBoxExtent(FVector(A.HalfLength,A.HalfWidth,80));Box->SetCollisionProfileName(TEXT("BlockAllDynamic"));Box->SetCanEverAffectNavigation(false);Box->RegisterComponent();Box->SetWorldLocationAndRotation(A.Position+FVector(0,0,100),FRotator(0,A.Heading,0));City->VehicleCollision.Add(Box);
  BestIndex=City->Vehicles.Add(A);P.Visual.Reset();P.Headlights.Empty();P.Occupied=true;
  if(City->Walkers.IsValidIndex(P.Walker)){auto& W=City->Walkers[P.Walker];if(W.Activity==EPedActivity::InsideCar||W.Activity==EPedActivity::EnteringCar||W.Activity==EPedActivity::LeavingCar){W.Position=W.PreviousPosition=P.Door;W.Activity=EPedActivity::ReturningRoute;}W.ParkedCar=INDEX_NONE;}
 }
 if(BestIndex==INDEX_NONE){Delivery->StatusMessage=FText::FromString(TEXT("Acércate a un carro y pulsa F; BogCar N permite elegir uno por índice."));return false;}
 auto& A=City->Vehicles[BestIndex];A.PlayerControlled=true;A.DevParked=false;A.DoorOpen=A.VisualDoorOpen=0;City->ApplyVehicleDoors(A.Visual.Get(),A.Bus,0,0,A.DoorRest);A.Velocity=0;A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;
 for(auto It=City->TrafficReservations.CreateIterator();It;++It)if(It.Value()==BestIndex)It.RemoveCurrent();
 if(A.Bus){const float Stations[]={-27000.f,-7000.f,17000.f,32000.f};for(auto& W:City->Walkers)if(W.BusIndex==BestIndex){int32 Station=0;for(int32 I=1;I<4;I++)if(FMath::Abs(Stations[I]-A.Position.X)<FMath::Abs(Stations[Station]-A.Position.X))Station=I;W.BusIndex=INDEX_NONE;W.StationIndex=Station;W.Activity=EPedActivity::WaitingTransit;W.Position=W.PreviousPosition=FVector(Stations[Station]+650,0,110);W.NextInteraction=City->Elapsed+12;}}
 DeveloperCarIndex=BestIndex;if(City->VehicleCollision.IsValidIndex(BestIndex))City->VehicleCollision[BestIndex]->SetCollisionResponseToChannel(ECC_Camera,ECR_Ignore);ForwardInput=SideInput=0;GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);SetActorHiddenInGame(true);
 DeveloperCameraLength=CameraBoom->TargetArmLength;DeveloperCameraOffset=CameraBoom->SocketOffset;CameraBoom->TargetArmLength=FMath::Clamp(A.HalfLength*2.5f+300,850.f,2600.f);CameraBoom->SocketOffset=FVector(0,0,150);DeveloperLastHeading=A.Heading;
 if(auto* PC=Cast<APlayerController>(Controller))PC->SetControlRotation(FRotator(-12,A.Heading,0));UpdateDeveloperCarView(0);
 Delivery->StatusMessage=FText::FromString(TEXT("DEV: W/S acelerar y reversa · MOUSE dirigir · ESPACIO frenar · F bajar."));return true;
}
bool ABogotaPlayer::LeaveDeveloperCar(){
 if(DeveloperCarIndex==INDEX_NONE)return true;if(!City||!City->Vehicles.IsValidIndex(DeveloperCarIndex))return false;
 auto& A=City->Vehicles[DeveloperCarIndex];FVector Exit;bool Found=false;FCollisionQueryParams Q;Q.AddIgnoredActor(this);if(A.Visual.IsValid())Q.AddIgnoredActor(A.Visual->GetOwner());if(City->VehicleCollision.IsValidIndex(DeveloperCarIndex))Q.AddIgnoredComponent(City->VehicleCollision[DeveloperCarIndex].Get());
 for(float Extra:{90.f,150.f,240.f}){for(FVector Local:{FVector(0,A.HalfWidth+Extra,0),FVector(0,-A.HalfWidth-Extra,0),FVector(-A.HalfLength-Extra,0,0),FVector(A.HalfLength+Extra,0,0)}){
  FVector P=A.Position+FRotator(0,A.Heading,0).RotateVector(Local);FHitResult Ground;
  if(!GetWorld()->LineTraceSingleByObjectType(Ground,P+FVector(0,0,220),P-FVector(0,0,150),FCollisionObjectQueryParams(ECC_WorldStatic),Q)||Ground.ImpactNormal.Z<.7f||Ground.ImpactPoint.Z>A.Position.Z+150)continue;
  P=Ground.ImpactPoint+FVector(0,0,92);if(GetWorld()->OverlapBlockingTestByChannel(P,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(34,88),Q))continue;FHitResult Path;if(GetWorld()->SweepSingleByChannel(Path,A.Position+FVector(0,0,100),P,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(28,84),Q))continue;Exit=P;Found=true;break;
 }if(Found)break;}
 if(!Found){if(Delivery)Delivery->StatusMessage=FText::FromString(TEXT("No hay espacio seguro para bajar. Mueve el carro a una zona despejada."));return false;}
 A.PlayerControlled=false;A.DevParked=true;A.Velocity=0;if(City->VehicleCollision.IsValidIndex(DeveloperCarIndex))City->VehicleCollision[DeveloperCarIndex]->SetCollisionResponseToChannel(ECC_Camera,ECR_Block);DeveloperCarIndex=INDEX_NONE;ForwardInput=SideInput=0;SetActorLocation(Exit);ConsumeMovementInputVector();SetActorHiddenInGame(false);GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);GetCharacterMovement()->SetMovementMode(MOVE_Walking);CameraBoom->TargetArmLength=DeveloperCameraLength;CameraBoom->SocketOffset=DeveloperCameraOffset;
 if(Delivery)Delivery->StatusMessage=FText::FromString(TEXT("DEV: carro estacionado. F para volver a subir."));return true;
}
void ABogotaPlayer::UpdateDeveloperCarView(float Dt){
 if(!City||!City->Vehicles.IsValidIndex(DeveloperCarIndex))return;auto& A=City->Vehicles[DeveloperCarIndex];if(!A.Visual.IsValid())return;
 auto* Actor=A.Visual->GetOwner();const float Heading=Actor->GetActorRotation().Yaw;
 FVector Seat=Actor->GetActorLocation()+FRotator(0,Heading,0).RotateVector(FVector(A.HalfLength*(A.Bus?.7f:.3f),-A.HalfWidth*.25f,A.Bus?140:95));SetActorLocationAndRotation(Seat,FRotator(0,Heading,0));
 DeveloperLastHeading=Heading;
}
void ABogotaCity::SimulateDeveloperCar(int32 Index,float Dt){
 auto& A=Vehicles[Index];A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;A.PreviousWheelAngle=A.WheelAngle;A.SteeringRate=0;
 if(A.PlayerControlled){
  auto* P=Cast<ABogotaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));FVector2D Input=P?P->DeveloperDriveInput():FVector2D::ZeroVector;bool Brake=false;if(P)if(auto* PC=Cast<APlayerController>(P->GetController()))Brake=PC->IsInputKeyDown(EKeys::SpaceBar);
  if(P&&P->Delivery&&P->Delivery->PhoneOpen){Brake=true;A.Velocity=0;}
  float Desired=Brake?0:Input.X*(Input.X<0?500:1600);A.Velocity=FMath::FInterpConstantTo(A.Velocity,Desired,Dt,Brake?1400:Input.X==0?400:600);
  const float Turn=Input.Y*65*FMath::Clamp(FMath::Abs(A.Velocity)/600.f,0.f,1.f)*FMath::Sign(A.Velocity)*Dt;float Heading=A.Heading+Turn;
  FVector Target=A.Position+FRotator(0,Heading,0).Vector()*A.Velocity*Dt;FHitResult Ground;FCollisionQueryParams Q;if(P)Q.AddIgnoredActor(P);if(A.Visual.IsValid())Q.AddIgnoredActor(A.Visual->GetOwner());if(VehicleCollision.IsValidIndex(Index))Q.AddIgnoredComponent(VehicleCollision[Index].Get());
  bool Supported=GetWorld()->LineTraceSingleByObjectType(Ground,FVector(Target.X,Target.Y,180),FVector(Target.X,Target.Y,-100),FCollisionObjectQueryParams(ECC_WorldStatic),Q)&&Ground.ImpactNormal.Z>.7f&&Ground.ImpactPoint.Z<150;
  if(Supported)Target.Z=Ground.ImpactPoint.Z+.5f;FVector SupportedGround;FRotator SupportedRotation;Supported=Supported&&ResolveVehicleGround(A,Target,Heading,SupportedGround,SupportedRotation);FHitResult Hit;
  bool Blocked=!Supported||GetWorld()->SweepSingleByChannel(Hit,A.Position+FVector(0,0,105),Target+FVector(0,0,105),FRotator(0,Heading,0).Quaternion(),ECC_Pawn,FCollisionShape::MakeBox(FVector(A.HalfLength-3,A.HalfWidth-3,55)),Q);
  for(const auto& W:Walkers)if(!W.TransitPassenger&&W.Activity!=EPedActivity::InsideCar&&W.Activity!=EPedActivity::InsideTransit){FVector D=FRotator(0,-Heading,0).RotateVector(W.Position-Target);if(FMath::Abs(D.X)<A.HalfLength+50&&FMath::Abs(D.Y)<A.HalfWidth+50&&FMath::Abs(D.Z)<150){Blocked=true;break;}}
  if(!Blocked){float Move=FVector::Dist2D(A.Position,Target);A.Position=Target;A.Heading=Heading;A.Travelled+=Move;A.WheelAngle=FMath::Fmod(A.WheelAngle+FMath::RadiansToDegrees(A.Velocity*Dt/FMath::Max(10.f,A.WheelRadius)),360.f);A.SteeringRate=Turn/FMath::Max(.001f,Dt);}else A.Velocity=0;
 }
 if(VehicleCollision.IsValidIndex(Index)){auto* C=VehicleCollision[Index].Get();C->SetWorldLocationAndRotation(A.Position+FVector(0,0,100),FRotator(0,A.Heading,0));C->SetCollisionEnabled(ECollisionEnabled::QueryOnly);}
}

FString ABogotaPlayer::ValidateDeveloperTools(){
 auto R=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Checks;auto Check=[&](const TCHAR* Name,bool OK){auto V=MakeShared<FJsonObject>();V->SetStringField(TEXT("id"),Name);V->SetBoolField(TEXT("passed"),OK);Checks.Add(MakeShared<FJsonValueObject>(V));UE_LOG(LogTemp,Display,TEXT("DEV_NPC_CHECK %s %s"),Name,OK?TEXT("PASS"):TEXT("FAIL"));};
 auto* PC=Cast<APlayerController>(Controller);int32 Balance=Delivery->Balance;PC->ConsoleCommand(TEXT("BogRain 1"));Check(TEXT("rain_requires_developer_mode"),City->DeveloperRainOverride==-1);
 PC->ConsoleCommand(TEXT("BogDev 1"));Check(TEXT("developer_console_command"),Delivery->DeveloperMode);
 PC->ConsoleCommand(TEXT("BogRain 1"));Check(TEXT("rain_on_immediately"),City->DeveloperRainOverride==1&&City->RainIntensity>.69f);
 PC->ConsoleCommand(TEXT("BogRain 0"));Check(TEXT("rain_off_immediately"),City->DeveloperRainOverride==0&&City->RainIntensity<.01f);
 PC->ConsoleCommand(TEXT("BogRain -1"));Check(TEXT("rain_automatic"),City->DeveloperRainOverride==-1);
 PC->ConsoleCommand(TEXT("BogCar 0"));Check(TEXT("enter_traffic_car"),DeveloperCarIndex==0&&IsHidden()&&GetCapsuleComponent()->GetCollisionEnabled()==ECollisionEnabled::NoCollision);
 Check(TEXT("camera_ignores_own_car"),City->VehicleCollision[0]->GetCollisionResponseToChannel(ECC_Camera)==ECR_Ignore);
 FVector Before=City->Vehicles[0].Position;MoveForward(.8f);MoveRight(0);MoveRight(.4f);Check(TEXT("blueprint_inputs_reach_developer_car"),DeveloperDriveInput().X>.7f&&DeveloperDriveInput().Y>.3f);MoveRight(0);
 FRotator SavedMouseAim=PC->GetControlRotation();PC->SetControlRotation(FRotator(-12,GetActorRotation().Yaw+25,0));Check(TEXT("mouse_steers_right"),DeveloperDriveInput().Y>.45f&&DeveloperDriveInput().Y<.55f);PC->SetControlRotation(FRotator(-12,GetActorRotation().Yaw-25,0));Check(TEXT("mouse_steers_left"),DeveloperDriveInput().Y<-.45f&&DeveloperDriveInput().Y>-.55f);PC->SetControlRotation(SavedMouseAim);
 for(int32 I=0;I<60;I++){City->SimulateTraffic(1.f/30);City->UpdateTrafficVisuals(1);UpdateDeveloperCarView(1.f/30);}Check(TEXT("car_drives_from_input"),FVector::Dist2D(Before,City->Vehicles[0].Position)>200);
 Delivery->TogglePhone();City->Vehicles[0].Velocity=700;City->SimulateTraffic(1.f/30);Check(TEXT("phone_stops_developer_car"),City->Vehicles[0].Velocity==0);Delivery->TogglePhone();
 ForwardInput=SideInput=0;
 auto SavedPeople=City->Walkers;City->Walkers.Empty();FWalker Pedestrian;FVector Direction=FRotator(0,City->Vehicles[0].Heading,0).Vector();FVector PedestrianStart=City->Vehicles[0].Position+Direction*(City->Vehicles[0].HalfLength+130);Pedestrian.Position=PedestrianStart;City->Walkers.Add(Pedestrian);City->Vehicles[0].Velocity=0;ForwardInput=.8f;
 for(int32 I=0;I<60;I++){City->SimulateTraffic(1.f/30);City->UpdateTrafficVisuals(1);UpdateDeveloperCarView(1.f/30);}ForwardInput=0;
 Check(TEXT("developer_car_stops_for_pedestrian"),FVector::DotProduct(PedestrianStart-City->Vehicles[0].Position,Direction)>=City->Vehicles[0].HalfLength+45);City->Walkers=MoveTemp(SavedPeople);
 auto& TestCar=City->Vehicles[0];TestCar.Velocity=0;FVector Forward=FRotator(0,TestCar.Heading,0).Vector(),WallPosition=TestCar.Position+Forward*(TestCar.HalfLength+350);
 auto* Wall=GetWorld()->SpawnActor<AStaticMeshActor>();Wall->SetMobility(EComponentMobility::Movable);Wall->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Wall->SetActorLocationAndRotation(WallPosition+FVector(0,0,180),FRotator(0,TestCar.Heading,0));Wall->SetActorScale3D(FVector(.6,(TestCar.HalfWidth*4+600)/100,4));
 ForwardInput=.8f;for(int32 I=0;I<90;I++){City->SimulateTraffic(1.f/30);City->UpdateTrafficVisuals(1);UpdateDeveloperCarView(1.f/30);}ForwardInput=0;
 Check(TEXT("developer_car_cannot_drive_through_wall"),FVector::DotProduct(WallPosition-TestCar.Position,Forward)-TestCar.HalfLength-30>=-5);Wall->Destroy();
 auto* BlockExit=GetWorld()->SpawnActor<AStaticMeshActor>();BlockExit->SetMobility(EComponentMobility::Movable);BlockExit->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));BlockExit->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));BlockExit->SetActorLocationAndRotation(TestCar.Position+FVector(0,0,180),FRotator(0,TestCar.Heading,0));BlockExit->SetActorScale3D(FVector((TestCar.HalfLength+400)/50,(TestCar.HalfWidth+400)/50,4));
 Check(TEXT("blocked_exit_keeps_player_inside"),!LeaveDeveloperCar()&&DeveloperCarIndex==0&&IsHidden());BlockExit->Destroy();
 auto* ThinWall=GetWorld()->SpawnActor<AStaticMeshActor>();ThinWall->SetMobility(EComponentMobility::Movable);ThinWall->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));ThinWall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));FVector Right=FRotator(0,TestCar.Heading,0).RotateVector(FVector(0,1,0));ThinWall->SetActorLocationAndRotation(TestCar.Position+Right*(TestCar.HalfWidth+45)+FVector(0,0,180),FRotator(0,TestCar.Heading,0));ThinWall->SetActorScale3D(FVector((TestCar.HalfLength*3+500)/100,.1,4));
 bool LeftCar=LeaveDeveloperCar();Check(TEXT("exit_does_not_cross_thin_wall"),LeftCar&&FVector::DotProduct(GetActorLocation()-TestCar.Position,Right)<TestCar.HalfWidth+35);ThinWall->Destroy();
 Check(TEXT("safe_exit_restores_walking"),LeftCar&&!IsHidden()&&GetCharacterMovement()->MovementMode==MOVE_Walking);Check(TEXT("exit_restores_car_camera_collision"),City->VehicleCollision[0]->GetCollisionResponseToChannel(ECC_Camera)==ECR_Block);
 int32 Entered=0,Exited=0;for(int32 Index:{1,4,5,16,32,60,96,97,98,99}){BogCar(Index);if(DeveloperCarIndex==Index)Entered++;
 if(Index==96){FVector Start=City->Vehicles[Index].Position;ForwardInput=.7f;for(int32 Step=0;Step<45;Step++){City->SimulateTraffic(1.f/30);City->UpdateTrafficVisuals(1);UpdateDeveloperCarView(1.f/30);}Check(TEXT("bus_is_drivable"),FVector::Dist2D(Start,City->Vehicles[Index].Position)>100);ForwardInput=0;}
 if(LeaveDeveloperCar())Exited++;}
 Check(TEXT("varied_cars_taxis_and_buses_enter"),Entered==10);Check(TEXT("varied_cars_taxis_and_buses_exit"),Exited==10);
 int32 Expected=City->Vehicles.Num();if(!City->ParkedCars.IsEmpty()){SetActorLocation(City->ParkedCars[0].Door+FVector(0,0,92));Interact();Check(TEXT("F_enters_parked_car"),DeveloperCarIndex==Expected);if(DeveloperCarIndex==Expected){FVector Start=City->Vehicles[Expected].Position;ForwardInput=.6f;SideInput=0;for(int32 Step=0;Step<45;Step++){City->SimulateTraffic(1.f/30);City->UpdateTrafficVisuals(1);UpdateDeveloperCarView(1.f/30);}ForwardInput=0;Check(TEXT("parked_car_is_drivable"),FVector::Dist2D(Start,City->Vehicles[Expected].Position)>100);}Check(TEXT("F_exits_parked_car"),LeaveDeveloperCar());}
 auto SavedTraffic=City->Vehicles;auto SavedWalkers=City->Walkers;auto SavedReservations=City->TrafficReservations;auto SavedPedJunctions=City->PedestrianJunctions;
 City->Vehicles.Empty();City->Walkers.Empty();City->TrafficReservations.Empty();City->PedestrianJunctions.Empty();
 FStreetAgent Obstacle=SavedTraffic[0];Obstacle.Position=Obstacle.PreviousPosition=FVector(1000,-4000,9);Obstacle.Heading=0;Obstacle.PlayerControlled=false;Obstacle.DevParked=true;Obstacle.Velocity=0;City->Vehicles.Add(Obstacle);
 FStreetAgent Follower=SavedTraffic[1];Follower.Route={FVector(1000,-5500,9),FVector(1000,-1000,9),FVector(3000,-1000,9),FVector(3000,-5500,9)};Follower.Position=Follower.PreviousPosition=Follower.Route[0];Follower.Segment=0;Follower.Heading=90;Follower.Speed=Follower.Velocity=900;Follower.PathDistance=0;Follower.LoopLength=13000;Follower.LaneGroup=77;Follower.DevParked=Follower.PlayerControlled=false;City->Vehicles.Add(Follower);
 for(int32 I=0;I<180;I++)City->SimulateTraffic(1.f/30);
 Check(TEXT("traffic_stops_for_perpendicular_parked_car"),City->Vehicles[1].Position.Y<Obstacle.Position.Y-Obstacle.HalfWidth-Follower.HalfLength-100&&City->Vehicles[1].Velocity<5);
 City->Vehicles=MoveTemp(SavedTraffic);City->Walkers=MoveTemp(SavedWalkers);City->TrafficReservations=MoveTemp(SavedReservations);City->PedestrianJunctions=MoveTemp(SavedPedJunctions);City->UpdateTrafficVisuals(1);
 BogDev(false);Check(TEXT("developer_exit_restores_balance"),!Delivery->DeveloperMode&&Delivery->Balance==Balance&&City->DeveloperRainOverride==-1);
 BogDev(true);BogRain(1);for(TCHAR C:FString(TEXT("ESOYAM")))Delivery->DeveloperKey(FKey(FName(*FString::Chr(C))));Check(TEXT("legacy_developer_exit_restores_auto_weather"),!Delivery->DeveloperMode&&City->DeveloperRainOverride==-1);
 auto TypeCode=[&](const TCHAR* Code){for(TCHAR C:FString(Code))Delivery->DeveloperKey(FKey(FName(*FString::Chr(C))));};
 TypeCode(TEXT("ESOYAM"));TypeCode(TEXT("LLUVIA"));Check(TEXT("typed_rain_code"),Delivery->DeveloperMode&&City->DeveloperRainOverride==1&&City->RainIntensity>.69f);
 TypeCode(TEXT("SOLEADO"));Check(TEXT("typed_clear_code"),City->DeveloperRainOverride==0&&City->RainIntensity<.01f);
 TypeCode(TEXT("CICLO"));Check(TEXT("typed_auto_weather_code"),City->DeveloperRainOverride==-1);
 SetActorLocation(City->Vehicles[2].Position+FRotator(0,City->Vehicles[2].Heading,0).RotateVector(FVector(0,City->Vehicles[2].HalfWidth+100,92)));TypeCode(TEXT("CARRO"));Check(TEXT("typed_enter_car_code"),DeveloperCarIndex!=INDEX_NONE);TypeCode(TEXT("CARRO"));Check(TEXT("typed_exit_car_code"),DeveloperCarIndex==INDEX_NONE);
 TypeCode(TEXT("LLOVIZNA"));Check(TEXT("typed_light_rain"),City->DeveloperRainOverride==2&&FMath::IsNearlyEqual(City->RainIntensity,.25f));
 TypeCode(TEXT("GRANIZO"));Check(TEXT("typed_hail_storm"),City->DeveloperRainOverride==3&&City->RainIntensity>.99f);
 int32 ThunderBefore=City->ThunderEvents,FlashBefore=City->LightningEvents;for(int32 Step=0;Step<600;Step++)City->UpdateWeather(1.f/30);
 Check(TEXT("storm_has_hail"),City->HailMesh&&City->HailDrops.Num()==200&&City->HailIntensity>.99f);
 Check(TEXT("storm_lightning_and_delayed_thunder"),City->LightningEvents>FlashBefore&&City->ThunderEvents>ThunderBefore&&LoadObject<USoundBase>(nullptr,TEXT("/Game/World/Audio/S_Thunder.S_Thunder")));
 FVector RoofEye=PC->PlayerCameraManager->GetCameraLocation();auto* WeatherRoof=GetWorld()->SpawnActor<AStaticMeshActor>();WeatherRoof->SetMobility(EComponentMobility::Movable);WeatherRoof->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));WeatherRoof->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));WeatherRoof->SetActorLocation(RoofEye+FVector(0,0,500));WeatherRoof->SetActorScale3D(FVector(50,50,1));City->RainOrigin=FVector(1e9);City->UpdateWeather(1.f/30);
 int32 CoveredHail=0,HailLeaks=0;for(int32 I=0;I<City->HailFloors.Num();I++){if(City->HailFloors[I]>=RoofEye.Z+549)CoveredHail++;FTransform T;City->HailMesh->GetInstanceTransform(I,T);if(!T.GetScale3D().IsNearlyZero()&&City->HailDrops[I].Z<City->HailFloors[I]+10)HailLeaks++;}
 Check(TEXT("hail_roof_occlusion"),CoveredHail==200&&HailLeaks==0);WeatherRoof->Destroy();
 TypeCode(TEXT("SOLEADO"));City->UpdateWeather(0);Check(TEXT("clear_stops_hail_and_lightning"),City->HailIntensity==0&&City->LightningFlash==0&&City->ThunderDelay<0);
 TypeCode(TEXT("MORADO"));Check(TEXT("typed_purple_bus_spawn"),City->Vehicles.IsValidIndex(DeveloperPurpleBusIndex)&&GetNameSafe(City->Vehicles[DeveloperPurpleBusIndex].Visual->GetSkinnedAsset()).Contains(TEXT("G66")));
 int32 FleetCount=City->Vehicles.Num();TypeCode(TEXT("MORADO"));Check(TEXT("purple_code_reuses_single_bus"),City->Vehicles.Num()==FleetCount);
 BogCar(DeveloperPurpleBusIndex);Check(TEXT("purple_bus_is_enterable"),DeveloperCarIndex==DeveloperPurpleBusIndex);LeaveDeveloperCar();
 TypeCode(TEXT("ESOYAM"));Check(TEXT("typed_exit_developer_code"),!Delivery->DeveloperMode);
 TSharedPtr<FJsonObject> Dynamics;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(City->ValidateVehicleDynamics()),Dynamics);R->SetObjectField(TEXT("vehicle_dynamics"),Dynamics);
 TSharedPtr<FJsonObject> DynamicWeather;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(City->ValidateDynamicWeather()),DynamicWeather);R->SetObjectField(TEXT("dynamic_weather"),DynamicWeather);
 R->SetArrayField(TEXT("checks"),Checks);TSharedPtr<FJsonObject> Ped;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(City->ValidatePedestrianPresentation()),Ped);R->SetObjectField(TEXT("pedestrians"),Ped);
 FString Result;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Result));return Result;
}
