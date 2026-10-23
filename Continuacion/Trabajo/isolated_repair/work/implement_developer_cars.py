from pathlib import Path
p=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1/Source/BogotaVoxel/BogotaDeveloper.cpp')
p.write_text(r'''#include "BogotaGame.h"
#include "DeliverySystem.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/PlayerController.h"
#include "Components/CapsuleComponent.h"
#include "Components/BoxComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Json.h"

void ABogotaPlayer::BogDev(bool Enabled){
 if(!Delivery)return;if(Delivery->DeveloperMode!=Enabled)Delivery->ToggleDeveloperMode();
 if(!Delivery->DeveloperMode&&City)City->DeveloperRainOverride=-1;
 Delivery->StatusMessage=FText::FromString(Delivery->DeveloperMode?TEXT("DEV: BogRain 1/0/-1 · BogCar · F subir/bajar · WASD conducir · ESPACIO frenar"):TEXT("Modo normal. Progreso restaurado."));
}
void ABogotaPlayer::BogRain(int32 Mode){
 if(!City||!Delivery)return;if(!Delivery->DeveloperMode&&Mode!=-1){Delivery->StatusMessage=FText::FromString(TEXT("Activa primero BogDev 1 en la consola F10."));return;}
 City->DeveloperRainOverride=FMath::Clamp(Mode,-1,1);if(Mode>=0)City->RainIntensity=Mode==1?1.f:0.f;City->UpdateWeather(0);City->RefreshWorldLighting();
 Delivery->StatusMessage=FText::FromString(Mode<0?TEXT("Clima automático restaurado."):Mode==0?TEXT("DEV: lluvia desactivada."):TEXT("DEV: lluvia activada."));
}
void ABogotaPlayer::BogCar(int32 Index){
 if(!Delivery||!Delivery->DeveloperMode){if(Delivery)Delivery->StatusMessage=FText::FromString(TEXT("Activa BogDev 1 para usar los carros."));return;}
 if(DeveloperCarIndex!=INDEX_NONE){if(!LeaveDeveloperCar()||Index<0)return;}
 EnterDeveloperCar(Index);
}
FVector2D ABogotaPlayer::DeveloperDriveInput()const{
 if(!Delivery||Delivery->PhoneOpen||!Delivery->DeveloperMode||Paused)return FVector2D::ZeroVector;
 return FVector2D(ForwardInput,SideInput);
}
bool ABogotaPlayer::EnterDeveloperCar(int32 Index){
 if(!City||!Delivery||!Delivery->DeveloperMode||Delivery->PhoneOpen||DeveloperCarIndex!=INDEX_NONE||Riding||BikeSpeed<0)return false;
 int32 BestIndex=INDEX_NONE,Parked=INDEX_NONE;float Best=220;
 auto Distance=[&](FVector P,float H,float L,float W){FVector D=FRotator(0,-H,0).RotateVector(GetActorLocation()-P);return FVector2D(FMath::Max(0.f,float(FMath::Abs(D.X)-L)),FMath::Max(0.f,float(FMath::Abs(D.Y)-W))).Size();};
 if(Index>=0){if(!City->Vehicles.IsValidIndex(Index)||!City->Vehicles[Index].Visual.IsValid())return false;BestIndex=Index;}
 else{
  for(int32 I=0;I<City->Vehicles.Num();I++){const auto& A=City->Vehicles[I];if(!A.Visual.IsValid())continue;float D=Distance(A.Position,A.Heading,A.HalfLength,A.HalfWidth);if(D<Best){Best=D;BestIndex=I;}}
  for(int32 I=0;I<City->ParkedCars.Num();I++){const auto& P=City->ParkedCars[I];if(!P.Visual.IsValid())continue;auto E=P.Visual->Bounds.BoxExtent;float D=Distance(P.Position,P.Heading,E.Y,E.X);if(D<Best){Best=D;BestIndex=INDEX_NONE;Parked=I;}}
 }
 if(Parked!=INDEX_NONE){
  auto& P=City->ParkedCars[Parked];auto* V=P.Visual.Get();auto E=V->Bounds.BoxExtent;
  FStreetAgent A;A.Position=A.PreviousPosition=P.Position;A.Heading=A.PreviousHeading=P.Heading;A.Visual=V;A.HalfLength=E.Y;A.HalfWidth=E.X;A.ModelScale=V->GetComponentScale().X;A.WheelRadius=33*A.ModelScale;A.Speed=900;A.LaneGroup=-1;A.DevParked=true;A.Headlights=P.Headlights;
  for(int32 Axle=0;Axle<2;Axle++)for(const TCHAR* Side:{TEXT("L"),TEXT("R")})A.WheelRest.Add(V->GetBoneTransformByName(FName(*FString::Printf(TEXT("wheel_%d_%s"),Axle,Side)),EBoneSpaces::ComponentSpace));
  TArray<UBoxComponent*> Boxes;V->GetOwner()->GetComponents(Boxes);for(auto* B:Boxes)B->DestroyComponent();
  auto* Box=NewObject<UBoxComponent>(City);City->AddInstanceComponent(Box);Box->SetupAttachment(City->GetRootComponent());Box->SetMobility(EComponentMobility::Movable);Box->SetBoxExtent(FVector(A.HalfLength,A.HalfWidth,80));Box->SetCollisionProfileName(TEXT("BlockAllDynamic"));Box->SetCanEverAffectNavigation(false);Box->RegisterComponent();Box->SetWorldLocationAndRotation(A.Position+FVector(0,0,100),FRotator(0,A.Heading,0));City->VehicleCollision.Add(Box);
  BestIndex=City->Vehicles.Add(A);P.Visual.Reset();P.Headlights.Empty();P.Occupied=true;
  if(City->Walkers.IsValidIndex(P.Walker)){auto& W=City->Walkers[P.Walker];if(W.Activity==EPedActivity::InsideCar||W.Activity==EPedActivity::EnteringCar||W.Activity==EPedActivity::LeavingCar){W.Position=W.PreviousPosition=P.Door;W.Activity=EPedActivity::ReturningRoute;}W.ParkedCar=INDEX_NONE;}
 }
 if(BestIndex==INDEX_NONE){Delivery->StatusMessage=FText::FromString(TEXT("Acércate a un carro y pulsa F; BogCar N permite elegir uno por índice."));return false;}
 auto& A=City->Vehicles[BestIndex];A.PlayerControlled=true;A.DevParked=false;A.Velocity=0;A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;
 for(auto It=City->TrafficReservations.CreateIterator();It;++It)if(It.Value()==BestIndex)It.RemoveCurrent();
 DeveloperCarIndex=BestIndex;ForwardInput=SideInput=0;GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);SetActorHiddenInGame(true);
 DeveloperCameraLength=CameraBoom->TargetArmLength;DeveloperCameraOffset=CameraBoom->SocketOffset;CameraBoom->TargetArmLength=FMath::Clamp(A.HalfLength*2.5f+300,850.f,2600.f);CameraBoom->SocketOffset=FVector(0,0,150);DeveloperLastHeading=A.Heading;
 if(auto* PC=Cast<APlayerController>(Controller))PC->SetControlRotation(FRotator(-12,A.Heading,0));UpdateDeveloperCarView(0);
 Delivery->StatusMessage=FText::FromString(TEXT("DEV: WASD conducir · ESPACIO frenar · F bajar · BogCar N cambiar."));return true;
}
bool ABogotaPlayer::LeaveDeveloperCar(){
 if(DeveloperCarIndex==INDEX_NONE)return true;if(!City||!City->Vehicles.IsValidIndex(DeveloperCarIndex))return false;
 auto& A=City->Vehicles[DeveloperCarIndex];FVector Exit;bool Found=false;FCollisionQueryParams Q;Q.AddIgnoredActor(this);if(A.Visual.IsValid())Q.AddIgnoredActor(A.Visual->GetOwner());if(City->VehicleCollision.IsValidIndex(DeveloperCarIndex))Q.AddIgnoredComponent(City->VehicleCollision[DeveloperCarIndex].Get());
 for(float Extra:{90.f,150.f,240.f}){for(FVector Local:{FVector(0,A.HalfWidth+Extra,0),FVector(0,-A.HalfWidth-Extra,0),FVector(-A.HalfLength-Extra,0,0),FVector(A.HalfLength+Extra,0,0)}){
  FVector P=A.Position+FRotator(0,A.Heading,0).RotateVector(Local);FHitResult Ground;
  if(!GetWorld()->LineTraceSingleByObjectType(Ground,P+FVector(0,0,220),P-FVector(0,0,150),FCollisionObjectQueryParams(ECC_WorldStatic),Q)||Ground.ImpactNormal.Z<.7f||Ground.ImpactPoint.Z>A.Position.Z+150)continue;
  P=Ground.ImpactPoint+FVector(0,0,92);if(GetWorld()->OverlapBlockingTestByChannel(P,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(34,88),Q))continue;Exit=P;Found=true;break;
 }if(Found)break;}
 if(!Found){if(Delivery)Delivery->StatusMessage=FText::FromString(TEXT("No hay espacio seguro para bajar. Mueve el carro a una zona despejada."));return false;}
 A.PlayerControlled=false;A.DevParked=true;A.Velocity=0;DeveloperCarIndex=INDEX_NONE;ForwardInput=SideInput=0;SetActorLocation(Exit);SetActorHiddenInGame(false);GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);GetCharacterMovement()->SetMovementMode(MOVE_Walking);CameraBoom->TargetArmLength=DeveloperCameraLength;CameraBoom->SocketOffset=DeveloperCameraOffset;
 if(Delivery)Delivery->StatusMessage=FText::FromString(TEXT("DEV: carro estacionado. F para volver a subir."));return true;
}
void ABogotaPlayer::UpdateDeveloperCarView(float Dt){
 if(!City||!City->Vehicles.IsValidIndex(DeveloperCarIndex))return;auto& A=City->Vehicles[DeveloperCarIndex];if(!A.Visual.IsValid())return;
 auto* Actor=A.Visual->GetOwner();const float Heading=Actor->GetActorRotation().Yaw;
 FVector Seat=Actor->GetActorLocation()+FRotator(0,Heading,0).RotateVector(FVector(A.HalfLength*(A.Bus?.7f:.3f),-A.HalfWidth*.25f,A.Bus?140:95));SetActorLocationAndRotation(Seat,FRotator(0,Heading,0));
 if(auto* PC=Cast<APlayerController>(Controller)){auto R=PC->GetControlRotation();R.Yaw+=FMath::FindDeltaAngleDegrees(DeveloperLastHeading,Heading);PC->SetControlRotation(R);}DeveloperLastHeading=Heading;
}
void ABogotaCity::SimulateDeveloperCar(int32 Index,float Dt){
 auto& A=Vehicles[Index];A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;A.PreviousWheelAngle=A.WheelAngle;A.SteeringRate=0;
 if(A.PlayerControlled){
  auto* P=Cast<ABogotaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));FVector2D Input=P?P->DeveloperDriveInput():FVector2D::ZeroVector;bool Brake=false;if(P)if(auto* PC=Cast<APlayerController>(P->GetController()))Brake=PC->IsInputKeyDown(EKeys::SpaceBar);
  float Desired=Brake?0:Input.X*(Input.X<0?500:1600);A.Velocity=FMath::FInterpConstantTo(A.Velocity,Desired,Dt,Brake?1400:Input.X==0?400:600);
  const float Turn=Input.Y*65*FMath::Clamp(FMath::Abs(A.Velocity)/600.f,0.f,1.f)*FMath::Sign(A.Velocity)*Dt;float Heading=A.Heading+Turn;
  FVector Target=A.Position+FRotator(0,Heading,0).Vector()*A.Velocity*Dt;FHitResult Ground;FCollisionQueryParams Q;if(P)Q.AddIgnoredActor(P);if(A.Visual.IsValid())Q.AddIgnoredActor(A.Visual->GetOwner());if(VehicleCollision.IsValidIndex(Index))Q.AddIgnoredComponent(VehicleCollision[Index].Get());
  bool Supported=GetWorld()->LineTraceSingleByObjectType(Ground,FVector(Target.X,Target.Y,180),FVector(Target.X,Target.Y,-100),FCollisionObjectQueryParams(ECC_WorldStatic),Q)&&Ground.ImpactNormal.Z>.7f&&Ground.ImpactPoint.Z<150;
  if(Supported)Target.Z=Ground.ImpactPoint.Z+.5f;FHitResult Hit;
  bool Blocked=!Supported||GetWorld()->SweepSingleByChannel(Hit,A.Position+FVector(0,0,105),Target+FVector(0,0,105),FRotator(0,Heading,0).Quaternion(),ECC_Pawn,FCollisionShape::MakeBox(FVector(A.HalfLength,A.HalfWidth,55)),Q);
  if(!Blocked){float Move=FVector::Dist2D(A.Position,Target);A.Position=Target;A.Heading=Heading;A.Travelled+=Move;A.WheelAngle=FMath::Fmod(A.WheelAngle+FMath::RadiansToDegrees(A.Velocity*Dt/FMath::Max(10.f,A.WheelRadius)),360.f);A.SteeringRate=Turn/FMath::Max(.001f,Dt);}else A.Velocity=0;
 }
 if(VehicleCollision.IsValidIndex(Index)){auto* C=VehicleCollision[Index].Get();C->SetWorldLocationAndRotation(A.Position+FVector(0,0,100),FRotator(0,A.Heading,0));C->SetCollisionEnabled(ECollisionEnabled::QueryOnly);}
}
''',encoding='utf-8')
