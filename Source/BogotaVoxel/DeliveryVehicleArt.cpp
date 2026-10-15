#include "EngineUtils.h"
#include "DeliverySystem.h"
#include "BogotaGame.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/PointLightComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/SceneCapture2D.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace {
 FLinearColor Paint(int32 Index){const FLinearColor C[]={FLinearColor(.025,.65,.86),FLinearColor(1,.22,.025),FLinearColor(.94,.72,.025),FLinearColor(.72,.025,.055),FLinearColor(.79,.76,.64),FLinearColor(.035,.045,.06)};return C[FMath::Clamp(Index,0,5)];}
 void ApplyPaint(UStaticMeshComponent* C,int32 Index){if(!C||!C->GetStaticMesh())return;auto* Base=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Delivery/Art/M_VehiclePaint.M_VehiclePaint"));if(!Base)return;const auto& Slots=C->GetStaticMesh()->GetStaticMaterials();for(int32 I=0;I<Slots.Num();I++)if(Slots[I].MaterialSlotName.ToString().Contains(TEXT("Paint"))||GetNameSafe(Slots[I].MaterialInterface).Contains(TEXT("Paint"))){auto* M=UMaterialInstanceDynamic::Create(Base,C);M->SetVectorParameterValue(TEXT("PaintColor"),Paint(Index));C->SetMaterial(I,M);}}
 FString ModelMesh(UDeliveryComponent* D,bool Moto){FName ID=Moto?D->MotoModel:D->BikeModel;FString Prefix=Moto?TEXT("SM_Moto"):TEXT("SM_Bike");if(ID==TEXT("BikeCargo")||ID==TEXT("MotoCargo"))Prefix+=TEXT("Cargo");if(ID==TEXT("BikeBMX"))Prefix+=TEXT("BMX");if(ID==TEXT("MotoSport"))Prefix+=TEXT("Sport");return Prefix+FString::Printf(TEXT("Stage%d"),D->VisualStage(Moto));}
 UStaticMesh* ArtMesh(const FString& Name){return LoadObject<UStaticMesh>(nullptr,*(TEXT("/Game/Delivery/Art/")+Name+TEXT(".")+Name));}
}
void ABogotaPlayer::RefreshVehicleArt(){
 if(!Delivery)return;
 const bool Moto=Delivery->Vehicle==EDeliveryVehicle::Motorcycle;
 const int32 Color=Moto?Delivery->MotoColor:Delivery->BikeColor;
 const FString Key=ModelMesh(Delivery,Moto)+FString::FromInt(Color)+FString::FromInt(Delivery->Purchased.Num());
 if(Key!=VehicleArtKey){
  if(auto* VehicleMesh=ArtMesh(ModelMesh(Delivery,false))){Bicycle->SetStaticMesh(VehicleMesh);Bicycle->EmptyOverrideMaterials();ApplyPaint(Bicycle,Delivery->BikeColor);}
  if(!MotorcycleParts.IsEmpty())if(auto* VehicleMesh=ArtMesh(ModelMesh(Delivery,true))){auto* C=MotorcycleParts[0].Get();C->SetStaticMesh(VehicleMesh);C->SetRelativeLocation(FVector(0,0,-90));C->SetRelativeScale3D(FVector::OneVector);C->EmptyOverrideMaterials();ApplyPaint(C,Delivery->MotoColor);}
  if(Delivery->Owns(TEXT("BikePedals"))){auto* VehicleMesh=ArtMesh(TEXT("SM_LuxuryPedal"));if(VehicleMesh)for(auto* C:{LeftPedal.Get(),RightPedal.Get()}){C->SetStaticMesh(VehicleMesh);C->EmptyOverrideMaterials();C->SetRelativeScale3D(FVector::OneVector);}}
  const FVector TireScale=Moto?FVector(1,1.7,1):Delivery->BikeModel==TEXT("BikeBMX")?FVector(1,1.35,1):FVector::OneVector;FrontWheel->SetRelativeScale3D(TireScale);RearWheel->SetRelativeScale3D(TireScale);
  if(City)for(auto& Weak:City->BikeActors)if(auto* Parked=Cast<AStaticMeshActor>(Weak.Get())){
   auto* FrameMesh=Parked->GetStaticMeshComponent();FrameMesh->SetStaticMesh(ArtMesh(ModelMesh(Delivery,Moto)));FrameMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Parked->SetActorEnableCollision(false);FrameMesh->EmptyOverrideMaterials();ApplyPaint(FrameMesh,Color);
   for(int32 I=0;I<2;I++){FName WheelName(*FString::Printf(TEXT("GarageWheel%d"),I));UStaticMeshComponent* WheelComp=FindObject<UStaticMeshComponent>(Parked,*WheelName.ToString());if(!WheelComp){WheelComp=NewObject<UStaticMeshComponent>(Parked,WheelName);WheelComp->SetupAttachment(FrameMesh);WheelComp->RegisterComponent();WheelComp->SetStaticMesh(FrontWheel->GetStaticMesh());WheelComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);}WheelComp->SetRelativeLocation(FVector(I==0?62:-62,0,33));WheelComp->SetRelativeScale3D(TireScale);}
  }
  VehicleArtKey=Key;
 }
 auto Wear=[&](TObjectPtr<USkeletalMeshComponent>& C,const TCHAR* Name,const TCHAR* Upgrade){
  if(!C){C=NewObject<USkeletalMeshComponent>(this,Name);C->SetupAttachment(GetMesh());C->RegisterComponent();C->SetSkeletalMesh(LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Delivery/Art/SK_%s.SK_%s"),Name,Name)));C->SetLeaderPoseComponent(GetMesh());C->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
  C->SetHiddenInGame(!Delivery->Owns(Upgrade));C->SetOwnerNoSee(false);
 };
 Wear(CargoBackpack,TEXT("CargoBackpack"),TEXT("CargoBackpack"));Wear(CargoWaist,TEXT("CargoWaist"),TEXT("CargoWaist"));
 if(!CargoPanniers){CargoPanniers=NewObject<UStaticMeshComponent>(this,TEXT("CargoPanniers"));CargoPanniers->SetupAttachment(RootComponent);CargoPanniers->RegisterComponent();CargoPanniers->SetStaticMesh(ArtMesh(TEXT("SM_CargoPanniers")));CargoPanniers->SetRelativeLocation(FVector(0,0,-90));CargoPanniers->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
 CargoPanniers->SetHiddenInGame(!Moto||!Riding||!Delivery->Owns(TEXT("CargoPanniers")));
 if(City&&City->BikeActors.Num()>0)if(auto* Parked=Cast<AStaticMeshActor>(City->BikeActors[0].Get())){
  auto* C=FindObject<UStaticMeshComponent>(Parked,TEXT("ParkedPanniers"));if(!C){C=NewObject<UStaticMeshComponent>(Parked,TEXT("ParkedPanniers"));C->SetupAttachment(Parked->GetRootComponent());C->RegisterComponent();C->SetStaticMesh(ArtMesh(TEXT("SM_CargoPanniers")));C->SetCollisionEnabled(ECollisionEnabled::NoCollision);}C->SetVisibility(Moto&&Delivery->Owns(TEXT("CargoPanniers")));
 }
 if(!PhoneModel){PhoneModel=NewObject<UStaticMeshComponent>(this,TEXT("HeldVoxelPhone"));PhoneModel->SetupAttachment(GetMesh(),TEXT("hand_r"));PhoneModel->RegisterComponent();PhoneModel->SetStaticMesh(ArtMesh(TEXT("SM_UrbanPhoneVoxel")));PhoneModel->SetCollisionEnabled(ECollisionEnabled::NoCollision);PhoneModel->SetRelativeLocation(FVector(0,0,0));PhoneModel->SetRelativeRotation(FRotator(0,90,-20));PhoneModel->SetRelativeScale3D(FVector(1.4));}
 PhoneModel->SetHiddenInGame(!Delivery->PhoneOpen);
 if(!DeliveryVehiclePlaced)PlaceDeliveryVehicle();
 if(City)for(int32 I=0;I<City->BikeActors.Num();I++)if(City->BikeActors[I].IsValid()){City->BikeActors[I]->SetActorEnableCollision(false);City->BikeActors[I]->SetActorHiddenInGame(!DeliveryVehiclePlaced||I!=0||Riding||BikeSpeed<0);}
}
bool ABogotaPlayer::PlaceDeliveryVehicle(){
 if(DeliveryVehiclePlaced)return true;
 if(!City||City->ParkedBikes.IsEmpty()||City->BikeActors.IsEmpty()||!City->BikeActors[0].IsValid())return false;
 FCollisionQueryParams Params;Params.AddIgnoredActor(this);
 FVector ParkingOrigin=Delivery&&Delivery->InsideStore?Delivery->InsideStore->GetActorLocation()+FVector(0,-230,95):GetActorLocation();
 for(float Radius:{160.f,230.f,320.f,550.f,850.f})for(int32 I=0;I<8;I++){
  const float Angle=I*PI/4;FVector Candidate=ParkingOrigin+FVector(FMath::Cos(Angle)*Radius,FMath::Sin(Angle)*Radius,0);FHitResult Ground;
  if(!GetWorld()->LineTraceSingleByChannel(Ground,Candidate+FVector(0,0,250),Candidate-FVector(0,0,500),ECC_Visibility,Params)||Ground.ImpactNormal.Z<.6)continue;
  FVector Floor=Ground.ImpactPoint+FVector(0,0,3);bool InShop=false;for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)if(It->ContainsVisitor(Floor+FVector(0,0,95))){InShop=true;break;}if(InShop)continue;if(GetWorld()->OverlapBlockingTestByChannel(Floor+FVector(0,0,95),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(70,88),Params))continue;
  City->ParkedBikes[0]=Floor;City->BikeActors[0]->SetActorLocationAndRotation(Floor,GetActorRotation());BikeIndex=0;DeliveryVehiclePlaced=true;return true;
 }
 return false;
}
void ABogotaPlayer::FinishDeliveryRide(){
 StopForPhone();Riding=false;BikeSpeed=0;GetCapsuleComponent()->SetCapsuleRadius(34);GetCharacterMovement()->bOrientRotationToMovement=true;Bicycle->SetHiddenInGame(true,true);for(auto C:MotorcycleParts)C->SetHiddenInGame(true);
 if(City)for(auto& A:City->BikeActors)if(A.IsValid())A->SetActorHiddenInGame(true);
}
ADeliveryVehiclePreview::ADeliveryVehiclePreview(){
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("PreviewRoot"));
 Body=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));WheelA=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Front"));WheelB=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Rear"));
 for(auto* C:{Body,WheelA,WheelB}){C->SetupAttachment(RootComponent);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetVisibleInSceneCaptureOnly(true);}
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Wheel(TEXT("/Game/World/SM_BicycleWheel.SM_BicycleWheel"));WheelA->SetStaticMesh(Wheel.Object);WheelB->SetStaticMesh(Wheel.Object);WheelA->SetRelativeLocation(FVector(62,0,33));WheelB->SetRelativeLocation(FVector(-62,0,33));
 Capture=CreateDefaultSubobject<USceneCaptureComponent2D>(TEXT("WorkshopCamera"));Capture->SetupAttachment(RootComponent);Capture->SetRelativeLocation(FVector(260,-430,250));Capture->SetRelativeRotation((FVector(0,0,63)-FVector(260,-430,250)).Rotation());Capture->ProjectionType=ECameraProjectionMode::Orthographic;Capture->OrthoWidth=400;Capture->bCaptureEveryFrame=false;Capture->bCaptureOnMovement=false;Capture->PrimitiveRenderMode=ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList;Capture->CaptureSource=ESceneCaptureSource::SCS_FinalColorLDR;Capture->ShowFlags.SetAtmosphere(false);Capture->ShowFlags.SetFog(false);Capture->ShowFlags.SetMotionBlur(false);
 Capture->PostProcessSettings.bOverride_AutoExposureMethod=true;Capture->PostProcessSettings.AutoExposureMethod=EAutoExposureMethod::AEM_Manual;Capture->PostProcessSettings.bOverride_AutoExposureBias=true;Capture->PostProcessSettings.AutoExposureBias=7;
 // The preview is an actual voxel workshop, visible only to its dedicated camera.
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
 static ConstructorHelpers::FObjectFinder<UMaterialInterface> Concrete(TEXT("/Game/World/M_Concrete.M_Concrete")),Steel(TEXT("/Game/World/M_Steel.M_Steel")),Teal(TEXT("/Game/World/M_Teal.M_Teal")),Dark(TEXT("/Game/World/M_Charcoal.M_Charcoal")),Orange(TEXT("/Game/World/M_Orange.M_Orange")),White(TEXT("/Game/World/M_White.M_White")),Glow(TEXT("/Game/World/M_Glow.M_Glow"));
 int32 BlockIndex=0;
 auto Block=[&](FVector P,FVector Size,UMaterialInterface* Material){auto* C=CreateDefaultSubobject<UStaticMeshComponent>(FName(*FString::Printf(TEXT("GarageBlock%03d"),BlockIndex++)));C->SetupAttachment(RootComponent);C->SetStaticMesh(Cube.Object);C->SetRelativeLocation(P);C->SetRelativeScale3D(Size/100);C->SetMaterial(0,Material);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetVisibleInSceneCaptureOnly(true);C->SetCastShadow(false);};
 Block(FVector(0,0,-14),FVector(560,480,20),Dark.Object);
 for(int32 X=0;X<8;X++)for(int32 Y=0;Y<6;Y++)Block(FVector(-245+X*70,-195+Y*70,-2),FVector(68,68,6),(X+Y)%2?Concrete.Object:Steel.Object);
 for(int32 X=0;X<8;X++)for(int32 Z=0;Z<4;Z++)Block(FVector(-245+X*70,205,22+Z*44),FVector(68,16,42),Z==1?Teal.Object:Concrete.Object);
 Block(FVector(-285,0,84),FVector(16,420,180),Concrete.Object);
 Block(FVector(-276,0,66),FVector(4,420,42),Teal.Object);
 // Raised service pad and square safety markings leave breathing room around the model.
 Block(FVector(0,0,0),FVector(240,120,4),Dark.Object);
 for(int32 X=0;X<6;X++)Block(FVector(-110+X*44,-70,1),FVector(22,12,4),Orange.Object);
 Block(FVector(-185,115,64),FVector(116,60,12),Steel.Object);
 for(int32 X=0;X<2;X++)for(int32 Y=0;Y<2;Y++)Block(FVector(-232+X*94,92+Y*46,30),FVector(10,10,60),Dark.Object);
 Block(FVector(-185,191,111),FVector(116,10,68),Dark.Object);
 for(int32 X=0;X<4;X++){Block(FVector(-224+X*26,182,113),FVector(6,6,34),White.Object);Block(FVector(-224+X*26,182,131),FVector(16,6,8),Steel.Object);}
 Block(FVector(178,125,25),FVector(52,52,48),Orange.Object);Block(FVector(178,125,52),FVector(56,56,6),Dark.Object);Block(FVector(183,125,75),FVector(44,44,40),Teal.Object);
 Block(FVector(10,194,165),FVector(126,20,12),Dark.Object);Block(FVector(10,181,162),FVector(112,8,6),Glow.Object);
 Block(FVector(10,193,112),FVector(102,8,52),Teal.Object);
 for(int32 I=0;I<3;I++)Block(FVector(-20+I*30,186,112),FVector(12,6,28),White.Object);
 auto* Light=CreateDefaultSubobject<UPointLightComponent>(TEXT("WorkshopLight"));Light->SetupAttachment(RootComponent);Light->SetRelativeLocation(FVector(70,-130,260));Light->SetIntensity(12000);Light->SetAttenuationRadius(1000);Light->SetCastShadows(false);
}
void ADeliveryVehiclePreview::ShowVehicle(const FString& Name,int32 Color){
 const FString Key=Name+FString::FromInt(Color);if(Key==LastKey)return;
 if(!Target){Target=NewObject<UTextureRenderTarget2D>(this);Target->ClearColor=FLinearColor(.025,.04,.06,1);Target->InitAutoFormat(640,316);Capture->TextureTarget=Target;Capture->ShowOnlyActorComponents(this);}
 Body->SetStaticMesh(ArtMesh(Name));Body->EmptyOverrideMaterials();ApplyPaint(Body,Color);const bool Moto=Name.Contains(TEXT("Moto"));WheelA->SetRelativeScale3D(FVector(1,Moto?1.7:1,1));WheelB->SetRelativeScale3D(FVector(1,Moto?1.7:1,1));Capture->CaptureSceneDeferred();LastKey=Key;
}
void UDeliveryComponent::PrepareCityMap(){
 if(CityMapActor)return;
 CityMapActor=GetWorld()->SpawnActor<ASceneCapture2D>(FVector(0,0,40000),FRotator(-90,0,0));if(!CityMapActor)return;
 CityMapTexture=NewObject<UTextureRenderTarget2D>(this);CityMapTexture->ClearColor=FLinearColor(.02,.04,.05,1);CityMapTexture->InitAutoFormat(768,1152);
 auto* C=CityMapActor->GetCaptureComponent2D();C->TextureTarget=CityMapTexture;C->ProjectionType=ECameraProjectionMode::Orthographic;C->OrthoWidth=60000.f/.92f;C->bCaptureEveryFrame=false;C->bCaptureOnMovement=false;C->CaptureSource=ESceneCaptureSource::SCS_FinalColorLDR;C->ShowFlags.SetAtmosphere(false);C->ShowFlags.SetFog(false);C->ShowFlags.SetMotionBlur(false);C->HideActorComponents(GetOwner());
 if(Recipient)C->HideActorComponents(Recipient);if(PickupMarker)C->HideActorComponents(PickupMarker);if(auto* Rider=Cast<ABogotaPlayer>(GetOwner()))if(Rider->City)for(auto& V:Rider->City->BikeActors)if(V.IsValid())C->HideActorComponents(V.Get());C->CaptureSceneDeferred();
}
