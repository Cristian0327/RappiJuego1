#include "BogotaGame.h"
#include "DeliverySystem.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimationAsset.h"
#include "Animation/AnimSequence.h"
#include "DeliveryAnimInstance.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/IConsoleManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "HAL/PlatformMisc.h"

ABogotaPlayer::ABogotaPlayer(){
 Delivery=CreateDefaultSubobject<UDeliveryComponent>(TEXT("DeliveryGameplay"));
 PrimaryActorTick.bCanEverTick=true;GetCapsuleComponent()->InitCapsuleSize(34,90);
 bUseControllerRotationYaw=false;bUseControllerRotationPitch=false;bUseControllerRotationRoll=false;
 GetCharacterMovement()->bOrientRotationToMovement=true;GetCharacterMovement()->RotationRate=FRotator(0,600,0);GetCharacterMovement()->MaxWalkSpeed=390;GetCharacterMovement()->JumpZVelocity=430;GetCharacterMovement()->AirControl=.3;GetCharacterMovement()->MaxStepHeight=35;GetCharacterMovement()->BrakingDecelerationWalking=1800;
 static ConstructorHelpers::FObjectFinder<USkeletalMesh> CharacterMesh(TEXT("/Game/VoxelExplorer/SK_VoxelExplorer.SK_VoxelExplorer"));static ConstructorHelpers::FObjectFinder<UMaterialInterface> CharacterMaterial(TEXT("/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB.M_VoxelExplorerRuntimeRGB"));GetMesh()->SetSkeletalMeshAsset(CharacterMesh.Object);GetMesh()->SetMaterial(0,CharacterMaterial.Object);GetMesh()->SetRelativeLocation(FVector(0,0,-90));GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 static ConstructorHelpers::FObjectFinder<UAnimationAsset> I(TEXT("/Game/VoxelExplorer/AN_Idle.AN_Idle")),W(TEXT("/Game/VoxelExplorer/AN_Walk_InPlace.AN_Walk_InPlace")),P(TEXT("/Game/VoxelExplorer/AN_BikePedal.AN_BikePedal"));Idle=I.Object;Walk=W.Object;Pedal=P.Object;
 CameraBoom=CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));CameraBoom->SetupAttachment(RootComponent);CameraBoom->TargetArmLength=430;CameraBoom->SocketOffset=FVector(0,45,70);CameraBoom->bUsePawnControlRotation=true;CameraBoom->bEnableCameraLag=true;CameraBoom->CameraLagSpeed=8;CameraBoom->ProbeSize=12;
 Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));Camera->SetupAttachment(CameraBoom,USpringArmComponent::SocketName);Camera->FieldOfView=60;
 Bicycle=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BicycleFrame"));Bicycle->SetupAttachment(RootComponent);Bicycle->SetRelativeLocation(FVector(0,0,-90));Bicycle->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Bike(TEXT("/Game/World/SM_BicycleFrame.SM_BicycleFrame")),Wheel(TEXT("/Game/World/SM_BicycleWheel.SM_BicycleWheel"));Bicycle->SetStaticMesh(Bike.Object);
 FrontWheel=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FrontWheel"));RearWheel=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RearWheel"));
 for(auto* C:{FrontWheel.Get(),RearWheel.Get()}){C->SetupAttachment(Bicycle);C->SetStaticMesh(Wheel.Object);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetHiddenInGame(true);}
 static ConstructorHelpers::FObjectFinder<UStaticMesh> MotoCube(TEXT("/Engine/BasicShapes/Cube.Cube"));
 static ConstructorHelpers::FObjectFinder<UMaterialInterface> MotoBody(TEXT("/Game/World/M_Teal.M_Teal"));
 static ConstructorHelpers::FObjectFinder<UMaterialInterface> MotoDark(TEXT("/Game/World/M_Charcoal.M_Charcoal"));
 const FVector MotoPositions[]={FVector(5,0,-38),FVector(-25,0,-24),FVector(28,0,-20),FVector(48,0,-25),FVector(55,0,-14),FVector(-48,0,-28)};
 const FVector MotoSizes[]={FVector(56,30,28),FVector(50,34,12),FVector(35,32,26),FVector(14,34,36),FVector(10,28,10),FVector(12,30,12)};
 for(int32 Part=0;Part<6;Part++){auto* C=CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("VoxelMoto_%d"),Part));C->SetupAttachment(RootComponent);C->SetStaticMesh(MotoCube.Object);C->SetMaterial(0,Part==1?MotoDark.Object:MotoBody.Object);C->SetRelativeLocation(MotoPositions[Part]);C->SetRelativeScale3D(MotoSizes[Part]/100);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetHiddenInGame(true);MotorcycleParts.Add(C);}
 FrontWheel->SetRelativeLocation(FVector(62,0,33));RearWheel->SetRelativeLocation(FVector(-62,0,33));Bicycle->SetHiddenInGame(true,true);
 LeftPedal=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftPedal"));RightPedal=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightPedal"));
 static ConstructorHelpers::FObjectFinder<UStaticMesh> PedalCube(TEXT("/Engine/BasicShapes/Cube.Cube"));static ConstructorHelpers::FObjectFinder<UMaterialInterface> PedalMat(TEXT("/Game/World/M_Orange.M_Orange"));
 for(auto* PComp:{LeftPedal.Get(),RightPedal.Get()}){PComp->SetupAttachment(Bicycle);PComp->SetStaticMesh(PedalCube.Object);PComp->SetMaterial(0,PedalMat.Object);PComp->SetRelativeScale3D(FVector(.2,.13,.05));PComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);PComp->SetHiddenInGame(true);}
}
void ABogotaPlayer::BeginPlay(){Super::BeginPlay();Bicycle->SetHiddenInGame(true,true);if(auto* A=LoadObject<UAnimationAsset>(nullptr,TEXT("/Game/VoxelExplorer/AN_MixamoWalk.AN_MixamoWalk")))Walk=A;JumpClip=LoadObject<UAnimationAsset>(nullptr,TEXT("/Game/VoxelExplorer/AN_MixamoJump.AN_MixamoJump"));GetMesh()->SetRelativeRotation(FRotator(0,-90,0));MotoRide=LoadObject<UAnimationAsset>(nullptr,TEXT("/Game/VoxelExplorer/AN_MotoRide.AN_MotoRide"));City=Cast<ABogotaCity>(UGameplayStatics::GetActorOfClass(this,ABogotaCity::StaticClass()));if(auto* PC=Cast<APlayerController>(Controller)){PC->SetControlRotation(FRotator(-14,95,0));PC->SetViewTarget(this);}else if(Controller){Controller->SetControlRotation(FRotator(-14,95,0));}Camera->SetActive(true);Camera->Activate();if(UMaterialInterface* M=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB.M_VoxelExplorerRuntimeRGB")))GetMesh()->SetMaterial(0,M);GetMesh()->PlayAnimation(Idle,true);CurrentClip=Idle;if(auto* AnimClass=LoadClass<UAnimInstance>(nullptr,TEXT("/Game/Delivery/Animation/ABP_DeliveryRider.ABP_DeliveryRider_C")))GetMesh()->SetAnimInstanceClass(AnimClass);TestHarness=FParse::Param(FCommandLine::Get(),TEXT("BogotaTest"));UE_LOG(LogTemp,Display,TEXT("BOGOTA_CAMERA player=%s camera=%s active=%d loc=%s rot=%s city=%s mat=%s"),*GetActorLocation().ToString(),*Camera->GetName(),Camera->IsActive()?1:0,*Camera->GetComponentLocation().ToString(),*Camera->GetComponentRotation().ToString(),*GetNameSafe(City),*GetNameSafe(GetMesh()->GetMaterial(0)));}
void ABogotaPlayer::SetupPlayerInputComponent(UInputComponent* I){
 FInputKeyBinding CheatBinding(FInputChord(EKeys::AnyKey),IE_Pressed);CheatBinding.bConsumeInput=false;
 CheatBinding.KeyDelegate.GetDelegateWithKeyForManualSet().BindLambda([this](FKey Key){if(Delivery)Delivery->DeveloperKey(Key);});I->KeyBindings.Add(CheatBinding);
 Super::SetupPlayerInputComponent(I);I->BindAxis("MoveForward",this,&ABogotaPlayer::MoveForward);I->BindAxis("MoveRight",this,&ABogotaPlayer::MoveRight);I->BindAxis("Turn",this,&ABogotaPlayer::Turn);I->BindAxis("LookUp",this,&ABogotaPlayer::Look);
 I->BindAction("KeyboardAction",IE_Pressed,this,&ABogotaPlayer::KeyboardActionPressed);I->BindAction("KeyboardAction",IE_Released,this,&ABogotaPlayer::ActionReleased);
 I->BindAction("Interact",IE_Pressed,this,&ABogotaPlayer::ActionPressed);I->BindAction("Interact",IE_Released,this,&ABogotaPlayer::ActionReleased);I->BindAction("Pickup",IE_Pressed,this,&ABogotaPlayer::PickupPressed);I->BindAction("Pickup",IE_Released,this,&ABogotaPlayer::PickupReleased);I->BindAction("Phone",IE_Pressed,this,&ABogotaPlayer::PhonePressed);I->BindAction("Vehicle",IE_Pressed,this,&ABogotaPlayer::VehiclePressed);I->BindAction("Mount",IE_Pressed,this,&ABogotaPlayer::Interact);I->BindAction("Jump",IE_Pressed,this,&ABogotaPlayer::JumpOrBrake);I->BindAction("Jump",IE_Released,this,&ABogotaPlayer::StopJump);I->BindAction("Sprint",IE_Pressed,this,&ABogotaPlayer::StartSprint);I->BindAction("Sprint",IE_Released,this,&ABogotaPlayer::EndSprint);I->BindAction("Map",IE_Pressed,this,&ABogotaPlayer::PhonePressed);I->BindAction("Time",IE_Pressed,this,&ABogotaPlayer::SkipTime);I->BindAction("Quality",IE_Pressed,this,&ABogotaPlayer::ToggleQuality);auto& PauseBind=I->BindAction("Pause",IE_Pressed,this,&ABogotaPlayer::TogglePause);PauseBind.bExecuteWhenPaused=true;
}
void ABogotaPlayer::MoveForward_Implementation(float V){if(Delivery&&Delivery->PhoneOpen){ForwardInput=0;return;}ForwardInput=V;if(!Riding&&Controller){FRotator R(0,Controller->GetControlRotation().Yaw,0);AddMovementInput(FRotationMatrix(R).GetUnitAxis(EAxis::X),V);}}
void ABogotaPlayer::MoveRight_Implementation(float V){if(Delivery&&Delivery->PhoneOpen){SideInput=0;return;}SideInput=V;if(!Riding&&Controller){FRotator R(0,Controller->GetControlRotation().Yaw,0);AddMovementInput(FRotationMatrix(R).GetUnitAxis(EAxis::Y),V);}}
void ABogotaPlayer::Turn_Implementation(float V){if(!Delivery||!Delivery->PhoneOpen)AddControllerYawInput(V);}
void ABogotaPlayer::Look_Implementation(float V){if(!Delivery||!Delivery->PhoneOpen)AddControllerPitchInput(V);}
void ABogotaPlayer::StopForPhone_Implementation(){ForwardInput=0;SideInput=0;Sprint=false;BikeSpeed=0;GetCharacterMovement()->StopMovementImmediately();}
void ABogotaPlayer::ActionPressed(){if(!Delivery||Delivery->PhoneOpen)return;if(Delivery->State!=EDeliveryState::Idle){Delivery->BeginAction(false);return;}Interact();}
void ABogotaPlayer::KeyboardActionPressed(){if(Delivery&&Delivery->PhoneOpen)return;if(Delivery&&Delivery->State==EDeliveryState::Pickup){Delivery->BeginAction(true);return;}if(Delivery&&Delivery->State==EDeliveryState::Dropoff){ActionPressed();return;}if(Delivery&&Delivery->StoreDoorAction())return;ActionPressed();}
void ABogotaPlayer::ActionReleased_Implementation(){if(Delivery)Delivery->EndAction();}
void ABogotaPlayer::PickupPressed_Implementation(){if(Delivery)Delivery->BeginAction(true);}
void ABogotaPlayer::PickupReleased_Implementation(){if(Delivery)Delivery->EndAction();}
void ABogotaPlayer::PhonePressed_Implementation(){if(Delivery)Delivery->TogglePhone();}
void ABogotaPlayer::VehiclePressed_Implementation(){if(Delivery)Delivery->SwitchVehicle();}
void ABogotaPlayer::StartSprint_Implementation(){Sprint=true;}
void ABogotaPlayer::EndSprint_Implementation(){Sprint=false;}
void ABogotaPlayer::JumpOrBrake_Implementation(){if(Riding)BikeSpeed=0;else Jump();}
void ABogotaPlayer::StopJump_Implementation(){StopJumping();}
void ABogotaPlayer::ToggleMap(){FullMap=!FullMap;}
void ABogotaPlayer::SkipTime(){if(City)City->AdvanceTime();}
void ABogotaPlayer::ToggleQuality(){Quality=Quality==2?0:2;if(City)City->SetDetail(Quality);if(auto* C=IConsoleManager::Get().FindConsoleVariable(TEXT("r.Shadow.MaxResolution")))C->Set(Quality==0?1024:2048);}
void ABogotaPlayer::TogglePause(){if(Delivery)Delivery->EndAction();Sprint=false;Paused=!Paused;UGameplayStatics::SetGamePaused(this,Paused);}
 FString ABogotaPlayer::InteractionText()const{if(!Riding&&BikeSpeed<0)return TEXT("SUBIENDO A LA CICLA...");if(Riding)return TEXT("F  Bajar de la cicla     ESPACIO  Frenar");if(City)for(FVector B:City->ParkedBikes)if(FVector::DistSquared2D(B,GetActorLocation())<550*550)return TEXT("F  Subir a la cicla");return TEXT("Encuentra una cicla en el mapa");}
void ABogotaPlayer::Interact(){
  if(Delivery&&Delivery->PhoneOpen)return;
  if(!City)return;
  if(!Riding&&BikeSpeed<0)return;
 if(Riding){
  FVector Park=GetActorLocation()-FVector(0,0,90),DismountPoint=FVector::ZeroVector;bool FoundExit=false;
  FCollisionQueryParams Params;Params.AddIgnoredActor(this);
  for(float Radius:{130.f,190.f,260.f}){for(int32 Direction=0;Direction<8;Direction++){
   const float Angle=PI*.5f+Direction*PI*.25f;FVector Candidate=GetActorLocation()+GetActorForwardVector()*FMath::Cos(Angle)*Radius+GetActorRightVector()*FMath::Sin(Angle)*Radius;FHitResult Floor;
   if(!GetWorld()->LineTraceSingleByChannel(Floor,Candidate+FVector(0,0,100),Candidate-FVector(0,0,250),ECC_Visibility,Params)||Floor.ImpactNormal.Z<.6f)continue;
   Candidate=Floor.ImpactPoint+FVector(0,0,92);if(FMath::Abs(Candidate.Z-GetActorLocation().Z)>100)continue;
   if(GetWorld()->OverlapBlockingTestByChannel(Candidate,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(34,88),Params))continue;
   FHitResult Path;bool Blocked=GetWorld()->SweepSingleByChannel(Path,GetActorLocation(),Candidate,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(28,84),Params);if(Blocked&&!Path.bStartPenetrating)continue;
   DismountPoint=Candidate;FoundExit=true;break;
  }if(FoundExit)break;}if(!FoundExit){if(Delivery)Delivery->StatusMessage=FText::FromString(TEXT("Busca un espacio libre para bajar."));return;}
  City->ParkedBikes[BikeIndex]=Park;if(City->BikeActors[BikeIndex].IsValid()){City->BikeActors[BikeIndex]->SetActorLocationAndRotation(Park,GetActorRotation());City->BikeActors[BikeIndex]->SetActorHiddenInGame(false);}
  SetActorLocation(DismountPoint);Riding=false;BikeSpeed=0;GetMesh()->SetRelativeLocation(FVector(0,0,-90));GetCapsuleComponent()->SetCapsuleRadius(34);GetCharacterMovement()->bOrientRotationToMovement=true;Bicycle->SetHiddenInGame(true,true);
 }else{
  float Best=300;int32 Nearest=INDEX_NONE;for(int32 I=0;I<City->ParkedBikes.Num();I++){if(Delivery&&I!=0)continue;float D=FVector::Dist2D(GetActorLocation(),City->ParkedBikes[I]);if(D<Best){Best=D;Nearest=I;}}
  if(Nearest==INDEX_NONE)return;BikeIndex=Nearest;BikeSpeed=-.35f;CrankAngle=0;GetCharacterMovement()->StopMovementImmediately();SetActorLocation(City->ParkedBikes[Nearest]+FVector(0,0,90));if(City->BikeActors[Nearest].IsValid()){SetActorRotation(City->BikeActors[Nearest]->GetActorRotation());City->BikeActors[Nearest]->SetActorHiddenInGame(true);}
  GetCharacterMovement()->bOrientRotationToMovement=false;GetCapsuleComponent()->SetCapsuleRadius(67);GetMesh()->SetRelativeLocation(FVector(0,0,-90));Bicycle->SetHiddenInGame(false,true);
 }
}
void ABogotaPlayer::Tick(float Dt){
  Super::Tick(Dt);if(!City)City=Cast<ABogotaCity>(UGameplayStatics::GetActorOfClass(this,ABogotaCity::StaticClass()));
  if(!Riding&&BikeSpeed<0){BikeSpeed+=Dt;if(BikeSpeed>=0){Riding=true;BikeSpeed=0;if(!Cast<UDeliveryAnimInstance>(GetMesh()->GetAnimInstance()))GetMesh()->PlayAnimation(Idle,true);CurrentClip=Idle;}return;}
 if(Delivery){ADeliveryPoint* Entered=nullptr;for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)if(It->ContainsVisitor(GetActorLocation())){Entered=*It;break;}if(Entered!=Delivery->InsideStore){Delivery->EndAction();Delivery->InsideStore=Entered;if(Entered&&Riding)Interact();}}
 if(TestHarness)TickValidation(Dt);
 if(Riding){
  BikeSpeed=AdvanceDriveSpeed(Dt,Delivery?Delivery->GetTopSpeed():1100);AddActorWorldRotation(FRotator(0,SteeringAngle(Dt),0));GetCharacterMovement()->MaxWalkSpeed=FMath::Abs(BikeSpeed);AddMovementInput(GetActorForwardVector(),BikeSpeed<0?-1:1);
  WheelAngle+=GetVelocity().Size2D()/33*180/PI*Dt;FrontWheel->SetRelativeRotation(FRotator(WheelAngle,SideInput*18,0));RearWheel->SetRelativeRotation(FRotator(WheelAngle,0,0));
  CrankAngle+=GetVelocity().Size2D()/650*2*PI*Dt;LeftPedal->SetRelativeLocation(FVector(8+11*FMath::Cos(CrankAngle),13,33+11*FMath::Sin(CrankAngle)));RightPedal->SetRelativeLocation(FVector(8-11*FMath::Cos(CrankAngle),-13,33-11*FMath::Sin(CrankAngle)));
 }else GetCharacterMovement()->MaxWalkSpeed=WalkingSpeed();
  const bool Moto=Delivery&&Delivery->Vehicle==EDeliveryVehicle::Motorcycle;for(auto C:MotorcycleParts)C->SetHiddenInGame(!Riding||!Moto);if(Riding)Bicycle->SetVisibility(!Moto,false);else Bicycle->SetVisibility(true,false);
  FrontWheel->SetHiddenInGame(!Riding);RearWheel->SetHiddenInGame(!Riding);
  LeftPedal->SetHiddenInGame(!Riding||Moto);RightPedal->SetHiddenInGame(!Riding||Moto);
  float Speed=GetVelocity().Size2D();bool Airborne=!Riding&&GetCharacterMovement()->IsFalling();if(WasAirborne&&!Airborne)LandingTime=.18f;WasAirborne=Airborne;LandingTime=FMath::Max(0.f,LandingTime-Dt);
 const float WalkThreshold=CurrentClip==Walk?8.f:25.f;
 UAnimationAsset* Clip=Riding?(Moto&&MotoRide?MotoRide.Get():Pedal.Get()):((Airborne||LandingTime>0)&&JumpClip?JumpClip.Get():(Speed>WalkThreshold?Walk.Get():Idle.Get()));
 const bool UsesAnimBlueprint=Cast<UDeliveryAnimInstance>(GetMesh()->GetAnimInstance())!=nullptr;
 if(Clip&&Clip!=CurrentClip){if(!UsesAnimBlueprint)GetMesh()->PlayAnimation(Clip,Clip!=JumpClip);CurrentClip=Clip;}
 LocomotionRate=FMath::FInterpTo(LocomotionRate,Clip==Walk?GetWalkPlayRate(Speed):1.f,Dt,WalkRateResponse);
 if(!UsesAnimBlueprint)GetMesh()->SetPlayRate(Riding?1.f:LocomotionRate);
 if(!UsesAnimBlueprint&&Riding&&!Moto)if(auto* A=Cast<UAnimSequence>(Pedal))GetMesh()->SetPosition(FMath::Fmod(CrankAngle/(2*PI),1.f)*A->GetPlayLength(),false);
 if(!UsesAnimBlueprint&&Clip==JumpClip&&JumpClip){if(auto* JumpSequence=Cast<UAnimSequence>(JumpClip)){const float Length=JumpSequence->GetPlayLength();const float Phase=Airborne?FMath::GetMappedRangeValueClamped(FVector2D(GetCharacterMovement()->JumpZVelocity,-GetCharacterMovement()->JumpZVelocity),FVector2D(.30f,.70f),GetVelocity().Z):FMath::Lerp(.70f,1.f,FMath::Clamp(1.f-LandingTime/.18f,0.f,1.f));GetMesh()->SetPosition(FMath::Clamp(Phase*Length,0.f,Length),false);GetMesh()->SetPlayRate(0);}}

 UpdateCameraRig(Dt);
 // Keep the playable compact city bounded, without hard walls across roads.
 FVector P=GetActorLocation();if(Delivery&&Delivery->InsideStore&&P.Z<Delivery->InsideStore->GetActorLocation().Z-15500){Delivery->ExitStore();}
 if(P.Z<-500&&(!Delivery||!Delivery->InsideStore)){SetActorLocation(FVector(-6500,14000,150));GetCharacterMovement()->StopMovementImmediately();}
 if(FMath::Abs(P.X)>45500||P.Y<-32000||P.Y>39000){P.X=FMath::Clamp(P.X,-45000.,45000.);P.Y=FMath::Clamp(P.Y,-31500.,38500.);SetActorLocation(P);BikeSpeed=0;}
}
void ABogotaPlayer::UpdateCameraRig_Implementation(float Dt){
 CameraBoom->bEnableCameraLag=!(Delivery&&Delivery->InsideStore);
 CameraBoom->TargetArmLength=FMath::FInterpTo(CameraBoom->TargetArmLength,Delivery&&Delivery->InsideStore?240.f:Riding?670.f:570.f,Dt,3.f);
 Camera->SetFieldOfView(Delivery&&Delivery->InsideStore?78.f:60.f); CameraBoom->SocketOffset=FVector(0,Delivery&&Delivery->InsideStore?0.f:45.f,70); GetMesh()->SetOwnerNoSee(false);
}
float ABogotaPlayer::AdvanceDriveSpeed_Implementation(float Dt,float TopSpeed){return FMath::FInterpConstantTo(BikeSpeed,ForwardInput*TopSpeed,Dt,ForwardInput==0?350:600);}
float ABogotaPlayer::SteeringAngle_Implementation(float Dt)const{return SideInput*Dt*75.f*FMath::Clamp(FMath::Abs(BikeSpeed)/200.f,0.f,1.f)*(BikeSpeed<0?-1.f:1.f);}
float ABogotaPlayer::WalkingSpeed_Implementation()const{return Sprint?650.f:390.f;}
float ABogotaPlayer::GetWalkPlayRate_Implementation(float Speed)const{return FMath::Clamp(Speed/FMath::Max(1.f,WalkReferenceSpeed),MinimumWalkRate,FMath::Max(MinimumWalkRate,MaximumWalkRate));}
ABogotaGameMode::ABogotaGameMode(){DefaultPawnClass=ABogotaPlayer::StaticClass();HUDClass=ABogotaHUD::StaticClass();}
void ABogotaGameMode::BeginPlay(){Super::BeginPlay();if(!UGameplayStatics::GetActorOfClass(this,ABogotaCity::StaticClass()))GetWorld()->SpawnActor<ABogotaCity>();}

void ABogotaPlayer::TickValidation(float Dt){
 if(!City)return;TestTime+=Dt;
 auto Shot=[&](const TCHAR* Name){FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots")/Name,true,false);};
 if(TestStage==0&&TestTime>3){Shot(TEXT("01_Plaza.png"));TestStart=GetActorLocation();UE_LOG(LogTemp,Warning,TEXT("TEST walk start=%s mode=%d controller=%s"),*TestStart.ToString(),int32(GetCharacterMovement()->MovementMode),*GetNameSafe(Controller));TestStage++;}
 if(TestTime>3&&TestTime<6)AddMovementInput(FVector(1,0,0),1);
  if(TestStage==1&&TestTime>6){TestWalk=FVector::Dist2D(TestStart,GetActorLocation())>300;UE_LOG(LogTemp,Warning,TEXT("TEST walk end=%s velocity=%s distance=%f floor=%s input=%s"),*GetActorLocation().ToString(),*GetVelocity().ToString(),FVector::Dist2D(TestStart,GetActorLocation()),*GetNameSafe(GetCharacterMovement()->CurrentFloor.HitResult.GetComponent()),*GetLastMovementInputVector().ToString());SetActorLocation(City->ParkedBikes[0]+FVector(0,0,130));Interact();TestStart=GetActorLocation();TestStage++;}
  ForwardInput=TestTime>7&&TestTime<12?1:0;
  if(TestStage==2&&Riding)TestMount=true;
 if(TestStage==2&&TestTime>10){Shot(TEXT("02_Cicla.png"));TestStage++;}
 if(TestStage==3&&TestTime>13){TestRide=FVector::Dist2D(TestStart,GetActorLocation())>500;Interact();TestDismount=!Riding;City->AdvanceTime();City->AdvanceTime();City->AdvanceTime();TestStage++;}
 if(TestStage==4&&TestTime>16){Shot(TEXT("03_Noche.png"));TestStage++;}
 if(TestStage==5&&TestTime>18){FullMap=true;Shot(TEXT("04_Mapa.png"));TestStage++;}
 if(TestStage==6&&TestTime>22){
  const bool Pass=TestWalk&&TestMount&&TestRide&&TestDismount&&City->Vehicles.Num()==38&&City->Walkers.Num()==864&&GetMesh()->GetNumBones()==23;
  FString Report=FString::Printf(TEXT("{\"status\":\"%s\",\"walk\":%s,\"mount\":%s,\"cycle_movement\":%s,\"dismount\":%s,\"bones\":%d,\"vehicles\":%d,\"pedestrians\":%d,\"static_instances\":%d,\"hour_night\":%.2f,\"engine\":\"5.8.2\",\"target\":\"Windows PC\"}"),Pass?TEXT("PASS"):TEXT("FAIL"),TestWalk?TEXT("true"):TEXT("false"),TestMount?TEXT("true"):TEXT("false"),TestRide?TEXT("true"):TEXT("false"),TestDismount?TEXT("true"):TEXT("false"),GetMesh()->GetNumBones(),City->Vehicles.Num(),City->Walkers.Num(),City->StaticVoxelCount,City->Hour);
  FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/TEXT("playtest.json")));UE_LOG(LogTemp,Display,TEXT("BOGOTA_PLAYTEST %s"),*Report);TestStage++;FPlatformMisc::RequestExit(false);
 }
}


