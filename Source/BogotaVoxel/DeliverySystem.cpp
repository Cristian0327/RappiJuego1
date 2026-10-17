#include "DeliverySystem.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "BogotaGame.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/Font.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Animation/AnimationAsset.h"
#include "DeliveryAnimInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/SceneCapture2D.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Json.h"
#include "Framework/Application/SlateApplication.h"
#include "UnrealClient.h"
#include "EngineUtils.h"
#include "Misc/EngineVersion.h"

ADeliveryPoint::ADeliveryPoint(){PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickInterval=.033f;
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("DeliveryAnchor"));
 Sign=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VoxelShopSign"));Sign->SetupAttachment(RootComponent);Sign->SetRelativeLocation(FVector(160,0,220));Sign->SetRelativeScale3D(FVector(.2,1.5,.6));Sign->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));static ConstructorHelpers::FObjectFinder<UMaterialInterface> Teal(TEXT("/Game/World/M_Teal.M_Teal"));Sign->SetStaticMesh(Cube.Object);Sign->SetMaterial(0,Teal.Object);
 Label=CreateDefaultSubobject<UTextRenderComponent>(TEXT("DeliverySignText"));Label->SetupAttachment(RootComponent);Label->SetRelativeLocation(FVector(140,0,265));Label->SetRelativeRotation(FRotator(0,180,0));Label->SetText(FText::FromString(TEXT("REPARTOS")));Label->SetTextRenderColor(FColor(210,255,225));Label->SetHorizontalAlignment(EHTA_Center);Label->SetWorldSize(25);PlaceName=FText::FromString(TEXT("Tienda voxel"));
}

ADeliveryRecipient::ADeliveryRecipient(){
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
 VoxelMesh=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("VoxelCustomer"));VoxelMesh->SetupAttachment(RootComponent);VoxelMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 static ConstructorHelpers::FObjectFinder<USkeletalMesh> M(TEXT("/Game/VoxelExplorer/SK_VoxelExplorer.SK_VoxelExplorer"));
 static ConstructorHelpers::FObjectFinder<UMaterialInterface> Mat(TEXT("/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB.M_VoxelExplorerRuntimeRGB"));
 static ConstructorHelpers::FObjectFinder<UAnimationAsset> Anim(TEXT("/Game/VoxelExplorer/AN_Idle.AN_Idle"));
 VoxelMesh->SetSkeletalMeshAsset(M.Object);VoxelMesh->SetMaterial(0,Mat.Object);VoxelMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);VoxelMesh->SetAnimation(Anim.Object);
 Marker=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VoxelMarker"));Marker->SetupAttachment(RootComponent);Marker->SetRelativeLocation(FVector(0,0,260));Marker->SetRelativeScale3D(FVector(.35,.35,.35));Marker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));static ConstructorHelpers::FObjectFinder<UMaterialInterface> Yellow(TEXT("/Game/World/M_Yellow.M_Yellow"));Marker->SetStaticMesh(Cube.Object);Marker->SetMaterial(0,Yellow.Object);
 Label=CreateDefaultSubobject<UTextRenderComponent>(TEXT("CustomerLabel"));Label->SetupAttachment(RootComponent);Label->SetRelativeLocation(FVector(0,0,310));Label->SetWorldSize(32);Label->SetHorizontalAlignment(EHTA_Center);Label->SetText(FText::FromString(TEXT("CLIENTE")));Label->SetTextRenderColor(FColor(255,216,71));
}
void ADeliveryRecipient::InitializeAppearance(FName AppearanceRole){
 const FString Name=AppearanceRole.ToString();if(auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Delivery/People/SK_%s.SK_%s"),*Name,*Name))){VoxelMesh->SetSkeletalMeshAsset(Mesh);VoxelMesh->EmptyOverrideMaterials();VoxelMesh->SetRelativeScale3D(FVector(1,-1,1));VoxelMesh->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;
 if(auto* Class=LoadClass<UAnimInstance>(nullptr,*FString::Printf(TEXT("/Game/Delivery/Animation/ABP_%s.ABP_%s_C"),*Name,*Name)))VoxelMesh->SetAnimInstanceClass(Class);}
}



UDeliveryComponent::UDeliveryComponent(){PrimaryComponentTick.bCanEverTick=true;RecipientClass=ADeliveryRecipient::StaticClass();PhoneClass=UDeliveryPhoneWidget::StaticClass();}
void UDeliveryComponent::BeginPlay(){
 Super::BeginPlay();
 if(FSlateApplication::IsInitialized())FSlateApplication::Get().OnApplicationActivationStateChanged().AddWeakLambda(this,[this](bool Active){if(!Active)HandleInputSuspended();});
 bValidation=FParse::Param(FCommandLine::Get(),TEXT("DeliveryTest"))||FParse::Param(FCommandLine::Get(),TEXT("UsabilityTest"));
 if(!Upgrades)Upgrades=LoadObject<UDataTable>(nullptr,TEXT("/Game/Delivery/Data/DT_Upgrades.DT_Upgrades"));
 if(!VehicleCatalog)VehicleCatalog=LoadObject<UDataTable>(nullptr,TEXT("/Game/Delivery/Data/DT_Vehicles.DT_Vehicles"));
 InitializeGameplay();
 if(auto* P=Cast<ABogotaPlayer>(GetOwner()))if(auto* PC=Cast<APlayerController>(P->GetController())){
  PhoneWidget=CreateWidget<UUserWidget>(PC,PhoneClass);if(auto* Phone=Cast<UDeliveryPhoneWidget>(PhoneWidget)){Phone->Delivery=this;Phone->AddToViewport(5);}
 }
}
void UDeliveryComponent::EndPlay(const EEndPlayReason::Type Reason){if(FSlateApplication::IsInitialized())FSlateApplication::Get().OnApplicationActivationStateChanged().RemoveAll(this);EndAction();DestroyMarkers();if(CityMapActor)CityMapActor->Destroy();GetWorld()->GetTimerManager().ClearAllTimersForObject(this);if(PhoneWidget)PhoneWidget->RemoveFromParent();Super::EndPlay(Reason);}

void UDeliveryComponent::Changed(){OnChanged.Broadcast();}



int32 UDeliveryComponent::CalculatePay(float Meters,float Multiplier){if(!FMath::IsFinite(Meters)||!FMath::IsFinite(Multiplier))return 5000;return FMath::Clamp(FMath::RoundToInt(FMath::Lerp(5000.f,50000.f,FMath::Clamp((Meters-100)/800,0.f,1.f))*FMath::Clamp(Multiplier,.1f,2.f)),5000,50000);}
TArray<FDeliveryOrder> UDeliveryComponent::GetAvailableResidentialRoutes()const{
 TArray<FDeliveryOrder> Routes;auto* P=Cast<ABogotaPlayer>(GetOwner());if(!P||!P->City)return Routes;
 TArray<ADeliveryPoint*> Shops;for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)Shops.Add(*It);
 TArray<FVector> Homes;FCollisionQueryParams Params;Params.AddIgnoredActor(P);
 for(const auto& Building:P->City->MapFootprints){
  if(Building.Extent.X>4500||Building.Extent.Y>4500)continue;
  FVector Door=Building.Center+FVector(0,-Building.Extent.Y-150,0);bool Commercial=false;
  for(auto* Shop:Shops){FVector Local=Door-Shop->GetActorLocation();if(FMath::Abs(Local.X)<Shop->HalfWidth+180&&Local.Y>-180&&Local.Y<Shop->HalfDepth*2+180){Commercial=true;break;}}
  if(Commercial)continue;FHitResult Floor;
  if(!GetWorld()->LineTraceSingleByChannel(Floor,Door+FVector(0,0,500),Door-FVector(0,0,500),ECC_Visibility,Params)||Floor.ImpactNormal.Z<.8f)continue;
  Door.Z=Floor.ImpactPoint.Z+5;if(GetWorld()->OverlapBlockingTestByChannel(Door+FVector(0,0,95),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(70,88),Params))continue;
  if(!Homes.ContainsByPredicate([&](const FVector& H){return FVector::Dist2D(H,Door)<200;}))Homes.Add(Door);
 }
 const TCHAR* Customers[]={TEXT("Valeria"),TEXT("Don Luis"),TEXT("Camila"),TEXT("Andrea"),TEXT("Marta"),TEXT("Nicolas"),TEXT("Sara"),TEXT("Don Pedro")};
 for(auto* Shop:Shops){FVector Pickup=Shop->GetActorLocation();FHitResult Floor;FCollisionQueryParams ShopParams=Params;ShopParams.AddIgnoredActor(Shop);
  if(!GetWorld()->LineTraceSingleByChannel(Floor,Pickup+FVector(0,0,500),Pickup-FVector(0,0,500),ECC_Visibility,ShopParams))continue;
  Pickup.Z=Floor.ImpactPoint.Z+5;if(GetWorld()->OverlapBlockingTestByChannel(Pickup+FVector(0,0,95),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(70,88),ShopParams))continue;
  for(int32 I=0;I<Homes.Num();I++){FDeliveryOrder Route;Route.StoreID=Shop->PointID;Route.Grocery=Shop->Grocery;Route.StoreKind=Shop->StoreKind;Route.GoodsCost=Shop->PurchaseBudget;Route.Pickup=Pickup;Route.Dropoff=Homes[I];Route.PickupName=Shop->PlaceName;Route.DropoffName=FText::FromString(FString::Printf(TEXT("Casa de %s - %s"),Customers[I%8],*P->City->DistrictAt(Homes[I])));Route.DistanceMeters=FVector::Dist2D(Pickup,Homes[I])/100;Routes.Add(Route);}
 }
 UE_LOG(LogTemp,Display,TEXT("RESIDENTIAL_ROUTES houses=%d shops=%d candidates=%d"),Homes.Num(),Shops.Num(),Routes.Num());return Routes;
}

bool UDeliveryComponent::RouteAlreadyOffered(FVector Pickup,FVector Dropoff)const{
 for(const auto& O:Offers)if(O.Pickup.Equals(Pickup,1)&&O.Dropoff.Equals(Dropoff,1))return true;
 for(const auto& O:ActiveOrders)if(O.Order.Pickup.Equals(Pickup,1)&&O.Order.Dropoff.Equals(Dropoff,1))return true;
 return false;
}








float UDeliveryComponent::OfferSecondsLeft()const{return State==EDeliveryState::Offered?FMath::Max(0.f,Order.ExpiresAt-GetWorld()->GetTimeSeconds()):0;}
void UDeliveryComponent::ExpireOffer(){if(State==EDeliveryState::Offered){Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ID==Order.ID;});StatusMessage=FText::FromString(TEXT("Oferta vencida. Consulta las otras rutas."));EnterIdle();}}


FVector UDeliveryComponent::GetOrderTarget()const{if(State==EDeliveryState::Pickup&&InsideStore&&InsideStore==OrderStore())return BasketCount<(Order.StoreKind==1?1:3)?InsideStore->ProductPosition(BasketCount):InsideStore->CheckoutPosition();return State==EDeliveryState::Pickup?Order.Pickup:Order.Dropoff;}
bool UDeliveryComponent::IsAtTarget()const{return (State==EDeliveryState::Pickup||State==EDeliveryState::Dropoff)&&GetOwner()&&FVector::Dist2D(GetOwner()->GetActorLocation(),GetOrderTarget())<=InteractionRadius&&FMath::Abs(GetOwner()->GetActorLocation().Z-GetOrderTarget().Z)<180&&GetOwner()->GetVelocity().Size2D()<150;}




void UDeliveryComponent::DestroyMarkers(){if(Recipient){Recipient->Destroy();Recipient=nullptr;}if(PickupMarker){PickupMarker->Destroy();PickupMarker=nullptr;}}









void UDeliveryComponent::ToggleDeveloperMode(){
 if(DeveloperMode)if(auto* Rider=Cast<ABogotaPlayer>(GetOwner()))if(Rider->DeveloperCarIndex!=INDEX_NONE&&!Rider->LeaveDeveloperCar())return;
 if(PhoneOpen)TogglePhone();
 ExitStore();
 EndAction();BoostActive=false;DestroyMarkers();ActiveOrders.Empty();Offers.Empty();EnterIdle();
 if(!DeveloperMode){
  DeveloperBackup=NewObject<UDeliverySave>(this);auto* S=DeveloperBackup.Get();
  S->Balance=Balance;S->Purchased=Purchased;S->Vehicle=Vehicle;S->BikeColor=BikeColor;S->MotoColor=MotoColor;S->OwnedModels=OwnedModels;S->BikeModel=BikeModel;S->MotoModel=MotoModel;S->ModelColors=ModelColors;
  DeveloperMode=true;Balance=100000000;
  if(Upgrades)Purchased=Upgrades->GetRowNames();if(VehicleCatalog)OwnedModels=VehicleCatalog->GetRowNames();
 }else{
  auto* S=DeveloperBackup.Get();if(S){Balance=S->Balance;Purchased=S->Purchased;Vehicle=S->Vehicle;BikeColor=S->BikeColor;MotoColor=S->MotoColor;OwnedModels=S->OwnedModels;BikeModel=S->BikeModel;MotoModel=S->MotoModel;ModelColors=S->ModelColors;}
  DeveloperMode=false;DeveloperBackup=nullptr;if(auto* Rider=GetRider())if(Rider->City)Rider->City->DeveloperRainOverride=-1;
 }
 RebuildStats();Energy=Capacity;BikeEnergy=100;MotoEnergy=100;GenerateOffer();
 StatusMessage=FText::FromString(DeveloperMode?TEXT("MODO DESARROLLADOR: todo desbloqueado. ESOYAM para salir."):TEXT("Modo normal: progreso restaurado."));Changed();
}

void UDeliveryComponent::TickComponent(float Dt,ELevelTick Tick,FActorComponentTickFunction* Fn){
 Super::TickComponent(Dt,Tick,Fn);UpdateBoost(Dt);
 if(!bValidation)UpdateMarketplace(Dt);
 if(auto* Rider=Cast<ABogotaPlayer>(GetOwner()))Rider->RefreshVehicleArt();
 if(PickupMarker&&State==EDeliveryState::Pickup)PickupMarker->SetActorLocation(GetOrderTarget()+FVector(0,0,130));
 AdvanceHeldAction();

 if(bValidation)UpdateValidation(Dt);
 else {static const bool ResumeTest=FParse::Param(FCommandLine::Get(),TEXT("UsabilityResumeTest"));if(ResumeTest)UpdateUsabilityValidation(Dt);}
}

void UDeliveryComponent::UpdateValidation(float Dt){
 if(FParse::Param(FCommandLine::Get(),TEXT("UsabilityTest"))){UpdateUsabilityValidation(Dt);return;}
 ValidationTime+=Dt;auto* P=Cast<ABogotaPlayer>(GetOwner());if(!P||!P->City)return;
 if(ValidationStage==0&&FParse::Param(FCommandLine::Get(),TEXT("CargoVisual"))){for(FName ID:{FName(TEXT("CargoBackpack")),FName(TEXT("CargoWaist")),FName(TEXT("CargoPanniers")),FName(TEXT("Motorcycle"))})Purchased.AddUnique(ID);ValidationStage=37;ValidationTime=2;}
 if(ValidationStage==39)P->MoveForward(1.f);
 auto CaptureUI=[&](const FString& Name){FTimerHandle CaptureTimer;GetWorld()->GetTimerManager().SetTimer(CaptureTimer,[Name](){FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/")+Name,true,false);},.65f,false);};
 auto Check=[&](bool OK,const TCHAR* Name){if(!OK)ValidationErrors.Add(Name);UE_LOG(LogTemp,Display,TEXT("DELIVERY_TEST %s %s"),Name,OK?TEXT("PASS"):TEXT("FAIL"));};
 if(ValidationStage>=16&&ValidationStage<22&&ArtPreparedStage!=ValidationStage){
  if(State!=EDeliveryState::Pickup&&State!=EDeliveryState::Dropoff){State=EDeliveryState::Idle;Offers.Empty();GenerateOffer();SelectOffer(0);AcceptOffer(Order.ID);}
  const TCHAR* Models[]={TEXT("BikeCity"),TEXT("BikeCargo"),TEXT("BikeBMX"),TEXT("MotoStreet"),TEXT("MotoCargo"),TEXT("MotoSport")};
  P->SetDeliveryDriveInput(0,false);P->GetCharacterMovement()->StopMovementImmediately();if(P->Riding)P->Interact();Check(!P->Riding,TEXT("dismount_before_variant"));Check(EquipVehicle(Models[ValidationStage-16]),TEXT("equip_variant_before_mount"));P->RefreshVehicleArt();P->SetActorLocation(P->City->ParkedBikes[0]+FVector(0,0,130));P->Interact();ArtPreparedStage=ValidationStage;
 }
 if(ValidationStage==0&&FParse::Param(FCommandLine::Get(),TEXT("WheelStartupProbe"))){
  if(ValidationTime>1&&ArtPreparedStage!=0){CaptureUI(TEXT("StartupWheels.png"));ArtPreparedStage=0;}
  if(ValidationTime>3){const bool Hidden=P->FrontWheel->bHiddenInGame&&P->RearWheel->bHiddenInGame;UE_LOG(LogTemp,Display,TEXT("WHEEL_STARTUP_RESULT %s front_hidden=%d rear_hidden=%d riding=%d"),Hidden?TEXT("PASS"):TEXT("FAIL"),P->FrontWheel->bHiddenInGame,P->RearWheel->bHiddenInGame,P->Riding);FPlatformMisc::RequestExit(false);}return;
 }
 if(ValidationStage==0&&ValidationTime>3){
  Check(P->FrontWheel->bHiddenInGame&&P->RearWheel->bHiddenInGame&&P->Bicycle->bHiddenInGame,TEXT("startup_vehicle_parts_hidden"));
  Check(!P->Riding&&P->City->BikeActors[0].IsValid()&&!P->City->BikeActors[0]->IsHidden(),TEXT("vehicle_available_without_order"));Check(Upgrades&&Upgrades->GetRowNames().Num()==13,TEXT("upgrade_table"));Check(CalculatePay(0)==5000&&CalculatePay(500)==27500&&CalculatePay(900)==50000&&CalculatePay(10000)==50000,TEXT("distance_pay"));
  Check(P->City->MapFootprints.Num()>50,TEXT("map_reads_actual_baked_city_buildings"));
  TSet<FName> SeenThemes;
  for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It){auto* Shop=*It;SeenThemes.Add(Shop->ThemeID);bool Clear=true;FVector C=Shop->GetActorLocation()+FVector(0,Shop->HalfDepth,0);for(const auto& Foot:P->City->MapFootprints)if(FMath::Abs(C.X-Foot.Center.X)<Shop->HalfWidth+Foot.Extent.X&&FMath::Abs(C.Y-Foot.Center.Y)<Shop->HalfDepth+Foot.Extent.Y){Clear=false;break;}Check(Clear,TEXT("store_does_not_overlap_city_buildings"));Check(!Shop->ThemeID.IsNone(),TEXT("store_theme_table_loaded"));Check(Shop->ThemeProductNames.Num()==Shop->ItemCount(),TEXT("theme_products_match_order_basket"));
   TArray<UStaticMeshComponent*> Components;Shop->GetComponents(Components);for(auto* Cmp:Components)if(Cmp->GetStaticMesh())for(int32 Slot=0;Slot<Cmp->GetNumMaterials();Slot++)Check(Cmp->GetMaterial(Slot)!=nullptr,TEXT("store_material_slot_loaded"));
  }
  Check(SeenThemes.Num()==13,TEXT("thirteen_distinct_store_themes"));
  const float SavedBikeSpeed=P->BikeSpeed,SavedThrottle=P->ForwardInput,SavedSteer=P->SideInput;const bool SavedSprint=P->Sprint;
  P->BikeSpeed=500;P->ForwardInput=1;P->SideInput=1;Check(FMath::IsNearlyEqual(P->AdvanceDriveSpeed(.1f,1000),560.f),TEXT("blueprint_vehicle_acceleration"));Check(FMath::IsNearlyEqual(P->SteeringAngle(.1f),7.5f),TEXT("blueprint_vehicle_forward_steering"));
  P->BikeSpeed=-500;Check(FMath::IsNearlyEqual(P->SteeringAngle(.1f),-7.5f),TEXT("blueprint_vehicle_reverse_steering"));P->BikeSpeed=0;Check(FMath::IsNearlyZero(P->SteeringAngle(.1f)),TEXT("blueprint_vehicle_no_turn_at_rest"));
  P->Sprint=false;Check(FMath::IsNearlyEqual(P->WalkingSpeed(),390.f),TEXT("blueprint_walking_speed"));P->Sprint=true;Check(FMath::IsNearlyEqual(P->WalkingSpeed(),650.f),TEXT("blueprint_running_speed"));
  P->BikeSpeed=SavedBikeSpeed;P->ForwardInput=SavedThrottle;P->SideInput=SavedSteer;P->Sprint=SavedSprint;
  UpdateMarketplace(.1f);Check(Offers.Num()==6&&State==EDeliveryState::Idle&&!SelectedIncoming(),TEXT("blueprint_marketplace_refills_without_selecting"));
  const float BeforeRefresh=MarketRefreshRemaining;UpdateMarketplace(.5f);Check(FMath::IsNearlyEqual(MarketRefreshRemaining,BeforeRefresh-.5f),TEXT("blueprint_marketplace_countdown"));
  Offers.Pop();MarketRefreshRemaining=0;UpdateMarketplace(.1f);Check(Offers.Num()==6,TEXT("blueprint_marketplace_periodic_refill"));
  for(auto& Expired:Offers)Expired.ExpiresAt=GetWorld()->GetTimeSeconds()-1;UpdateMarketplace(.1f);bool FreshOffers=Offers.Num()==6;for(const auto& Fresh:Offers)FreshOffers&=Fresh.ExpiresAt>GetWorld()->GetTimeSeconds();Check(FreshOffers,TEXT("blueprint_marketplace_replaces_expired_offers"));
  GenerateOffer();Check(State==EDeliveryState::Idle,TEXT("offer_generation_waits_for_selection"));
  BeginAction();Check(!bHolding&&!SelectedIncoming(),TEXT("holding_action_without_selection_does_not_accept"));HoldStart=GetWorld()->GetTimeSeconds()-HoldDuration-1;AdvanceHeldAction();Check(ActiveOrders.IsEmpty(),TEXT("unselected_hold_cannot_create_order"));
  UpdateMarketplace(OfferInterval+1);BeginAction();AdvanceHeldAction();Check(!bHolding&&ActiveOrders.IsEmpty()&&!SelectedIncoming(),TEXT("market_refresh_does_not_select_or_accept"));Check(SelectOffer(0),TEXT("explicit_first_offer_selection"));Check(Offers.Num()==6,TEXT("six_simultaneous_offers"));for(const auto& Offer:Offers){bool AtHouse=false;for(const auto& Home:P->City->MapFootprints)if(FMath::Abs(Offer.Dropoff.X-Home.Center.X)<1&&FMath::Abs(Offer.Dropoff.Y-(Home.Center.Y-Home.Extent.Y-150))<1)AtHouse=true;Check(AtHouse,TEXT("destination_is_residential_door"));for(TActorIterator<ADeliveryPoint> Shop(GetWorld());Shop;++Shop)Check(FVector::Dist2D(Offer.Dropoff,Shop->GetActorLocation())>250,TEXT("destination_is_not_shop_branch"));}FGuid FirstOffer=Order.ID;Check(SelectOffer(4)&&Order.ID!=FirstOffer,TEXT("choose_different_offer"));BeginAction();Check(SelectOffer(2)&&HoldProgress==0,TEXT("changing_offer_cancels_hold"));IgnoreOffer();Check(Offers.Num()==5&&State==EDeliveryState::Idle,TEXT("ignored_offer_removed_without_accepting"));Check(SelectOffer(0),TEXT("select_after_ignore"));BeginAction();ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==1&&ValidationTime>1){EndAction();Check(State==EDeliveryState::Offered&&HoldProgress==0,TEXT("release_cancels_hold"));BeginAction();ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==2&&ValidationTime>2.2){
  Check(State==EDeliveryState::Pickup,TEXT("hold_accept"));Check(!AcceptOffer(Order.ID),TEXT("duplicate_accept_rejected"));P->SetActorLocation(Order.Pickup+FVector(0,0,100));P->GetCharacterMovement()->StopMovementImmediately();Check(!CollectOrder(Order.ID),TEXT("cannot_collect_outside_store"));P->SetActorLocation(OrderStore()->InteriorPosition(FVector(0,-300,95)));InsideStore=OrderStore();Check(InsideStore->ContainsVisitor(P->GetActorLocation()),TEXT("enter_store_at_street_level"));
  for(int32 I=0;I<InsideStore->ItemCount();I++){P->SetActorLocation(InsideStore->ProductPosition(I)+FVector(0,-90,0));P->GetCharacterMovement()->StopMovementImmediately();Check(CollectOrder(Order.ID),TEXT("collect_shopping_item"));}
  P->SetActorLocation(InsideStore->CheckoutPosition()+FVector(0,0,90));P->GetCharacterMovement()->StopMovementImmediately();BeginAction(true);ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==3&&ValidationTime>2.2){
  Check(State==EDeliveryState::Dropoff&&Recipient&&OrderPaid&&OrderBudget==0&&GoodsPaid==Order.GoodsCost&&Balance==0,TEXT("checkout_uses_customer_budget_not_wallet"));ExitStore();P->SetActorLocation(Order.Dropoff+FVector(0,0,100));P->GetCharacterMovement()->StopMovementImmediately();FGuid ID=Order.ID;int32 Expected=Order.Reward;BeginAction();Check(ActiveOrders.IsEmpty()&&State==EDeliveryState::Idle&&Balance==Expected,TEXT("delivery_pays"));Check(Offers.Num()==6,TEXT("completion_replenishes_offers"));P->RefreshVehicleArt();Check(!P->Riding&&!P->City->BikeActors[0]->IsHidden(),TEXT("vehicle_available_after_delivery"));Check(!CompleteOrder(ID)&&Balance==Expected,TEXT("double_pay_prevented"));
  P->Riding=true;P->SetDeliveryDriveInput(1,true);Energy=100;UpdateBoost(1);Check(BoostActive&&FMath::IsNearlyEqual(Energy,80)&&FMath::IsNearlyEqual(GetTopSpeed(),BikeBoostSpeed),TEXT("boost_drains_and_accelerates"));UpdateBoost(5);Check(Energy==0&&!BoostActive,TEXT("boost_exhaustion"));P->SetDeliveryDriveInput(0,false);UpdateBoost(2);Check(Energy>0,TEXT("passive_energy_regeneration"));P->Riding=false;
  Balance=10000000;Check(PurchaseUpgrade(TEXT("BikePedals"))&&FMath::IsNearlyEqual(Capacity,110),TEXT("pedals_ten_percent"));int32 Before=Balance;Check(!PurchaseUpgrade(TEXT("BikePedals"))&&Balance==Before,TEXT("double_purchase_prevented"));Check(!PurchaseUpgrade(TEXT("MotoSportEngine")),TEXT("prerequisite_enforced"));
  for(const TCHAR* Upgrade:{TEXT("BikeFrame"),TEXT("BikeGears"),TEXT("BikeMotor"),TEXT("Motorcycle")})Check(PurchaseUpgrade(Upgrade),Upgrade);
  Check(InfiniteBoost,TEXT("bike_infinite"));P->GetCharacterMovement()->StopMovementImmediately();Check(SwitchVehicle(),TEXT("moto_unlock"));Check(FMath::IsNearlyEqual(GetTopSpeed(),BikeBoostSpeed),TEXT("moto_base_equals_bike_boost"));
  for(const TCHAR* Upgrade:{TEXT("MotoTurbo"),TEXT("MotoAero"),TEXT("MotoDisplacement"),TEXT("MotoInjection"),TEXT("MotoSportEngine")})Check(PurchaseUpgrade(Upgrade),Upgrade);
  Check(InfiniteBoost,TEXT("moto_infinite"));
  Check(VehicleCatalog&&VehicleCatalog->GetRowNames().Num()==6,TEXT("six_vehicle_catalog"));
  for(const TCHAR* Model:{TEXT("BikeCargo"),TEXT("BikeBMX"),TEXT("MotoCargo"),TEXT("MotoSport")})Check(BuyVehicle(Model),Model);
  Check(EquipVehicle(TEXT("MotoSport")),TEXT("equip_owned_variant"));int32 PaintBalance=Balance;Check(PaintVehicle(true,3)&&Balance==PaintBalance-2000&&MotoColor==3,TEXT("paint_changes_color_and_charges"));Check(PaintVehicle(true,3)&&Balance==PaintBalance-2000,TEXT("same_paint_not_charged_twice"));Check(!PaintVehicle(true,99),TEXT("invalid_paint_rejected"));
  Check(SaveProfile(),TEXT("save_game_writes"));auto* Saved=Cast<UDeliverySave>(UGameplayStatics::LoadGameFromSlot(TEXT("VoxelDelivery_Automation"),0));Check(Saved&&Saved->Balance==Balance&&Saved->Purchased.Num()==10&&Saved->Vehicle==EDeliveryVehicle::Motorcycle&&Saved->MotoModel==TEXT("MotoSport")&&Saved->ModelColors.FindRef(TEXT("MotoSport"))==3&&Saved->OwnedModels.Num()==4,TEXT("save_game_roundtrip"));SetWaypoint(FVector(100,200,0));Check(HasWaypoint&&Waypoint.X==100,TEXT("manual_waypoint"));ClearWaypoint();TogglePhone();Check(PhoneOpen,TEXT("phone_opens"));TogglePhone();Check(!PhoneOpen,TEXT("phone_closes"));GenerateOffer();SelectOffer(0);Order.ExpiresAt=GetWorld()->GetTimeSeconds()-.1f;for(auto& O:Offers)if(O.ID==Order.ID)O.ExpiresAt=Order.ExpiresAt;Check(!AcceptOffer(Order.ID),TEXT("expired_offer_cannot_accept"));ExpireOffer();Check(State==EDeliveryState::Idle,TEXT("expired_offer_resets"));
  TogglePhone();ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==4&&ValidationTime>.5){
  if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget))UI->OpenShop();CaptureUI(TEXT("DeliveryShop.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==5&&ValidationTime>1){
  if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget))UI->OpenMap();SetWaypoint(FVector(10000,5000,0));CaptureUI(TEXT("DeliveryMap.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==6&&ValidationTime>1){
  TogglePhone();ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==7&&ValidationTime>1){
  FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/DeliveryHUD.png"),true,false);ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==8&&ValidationTime>1){
  if(State!=EDeliveryState::Pickup&&State!=EDeliveryState::Dropoff){State=EDeliveryState::Idle;Offers.Empty();GenerateOffer();SelectOffer(0);AcceptOffer(Order.ID);}P->SetActorLocation(P->City->ParkedBikes[0]+FVector(0,0,130));P->GetCharacterMovement()->StopMovementImmediately();P->Interact();ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==9&&ValidationTime>1){
  UE_LOG(LogTemp,Display,TEXT("RIDER_POSE actor=%s handL=%s handR=%s pelvis=%s"),*P->GetActorRotation().ToString(),*P->GetActorTransform().InverseTransformPosition(P->GetMesh()->GetSocketLocation(TEXT("hand_l"))).ToString(),*P->GetActorTransform().InverseTransformPosition(P->GetMesh()->GetSocketLocation(TEXT("hand_r"))).ToString(),*P->GetActorTransform().InverseTransformPosition(P->GetMesh()->GetSocketLocation(TEXT("pelvis"))).ToString());Check(P->Riding,TEXT("motorcycle_mount"));Check(!P->FrontWheel->bHiddenInGame&&!P->RearWheel->bHiddenInGame,TEXT("mounted_wheels_visible"));Check(!P->MotorcycleParts.IsEmpty()&&P->MotorcycleParts[0]&&P->MotorcycleParts[0]->GetStaticMesh()&&P->MotorcycleParts[0]->GetStaticMesh()->GetName().Contains(TEXT("MotoSportStage")),TEXT("imported_voxel_motorcycle"));FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/DeliveryMotorcycle.png"),true,false);ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==10&&ValidationTime>1){
  P->PhonePressed();P->MoveForward(1.f);P->MoveRight(1.f);P->StartSprint();
  Check(PhoneOpen&&P->ForwardInput==0&&P->SideInput==0&&!P->Sprint,TEXT("rider_blueprint_phone_blocks_drive_and_boost"));
  FRotator ViewBefore=P->GetControlRotation();P->Turn(1.f);P->Look(1.f);Check(P->GetControlRotation().Equals(ViewBefore),TEXT("rider_blueprint_phone_blocks_camera_input"));
  ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==11&&ValidationTime>1){
  if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget)){
   const TCHAR* Buttons[]={TEXT("HomeMap"),TEXT("HomeOrders"),TEXT("HomeWorkshop"),TEXT("HomeCargo"),TEXT("HomeVehicles")};
   const int32 ExpectedPages[]={1,2,3,6,4};
   Check(UI->GetWidgetFromName(TEXT("DesignerHome"))!=nullptr,TEXT("designer_home_loaded"));
   auto* PixelFont=LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font"));
   auto* PhoneHeader=Cast<UTextBlock>(UI->GetWidgetFromName(TEXT("Header")));
   Check(PixelFont&&PixelFont->GetInternalCompositeFont().DefaultTypeface.Fonts.Num()>0&&PixelFont->GetInternalCompositeFont().DefaultTypeface.Fonts[0].Font.HasFont()&&PhoneHeader&&PhoneHeader->GetFont().FontObject==PixelFont,TEXT("phone_pixel_font_saved_and_loaded"));
   for(int32 I=0;I<5;I++){
    auto* Button=Cast<UButton>(UI->GetWidgetFromName(Buttons[I]));Check(Button!=nullptr,Buttons[I]);
    if(Button){Button->OnClicked.Broadcast();auto* Title=Cast<UTextBlock>(UI->GetWidgetFromName(TEXT("PageTitle")));Check(Title&&!Title->GetText().IsEmpty()&&UI->Page==ExpectedPages[I],TEXT("blueprint_launcher_opens_expected_app"));}
   }
   const int32 GarageWallet=Balance,OriginalPaint=MotoColor;
   UI->OpenCatalog();UI->GarageMoto();UI->SelectEntry(5);UI->BuyModel();UI->EquipModel();
   Check(MotoModel==TEXT("MotoSport")&&Vehicle==EDeliveryVehicle::Motorcycle&&Balance==GarageWallet,TEXT("phone_blueprint_equips_owned_vehicle_without_charge"));
   UI->SelectEntry(102);UI->PaintSelected();Check(MotoColor==2&&ModelColors.FindRef(TEXT("MotoSport"))==2,TEXT("phone_blueprint_applies_selected_paint"));
   UI->SelectEntry(100+OriginalPaint);UI->PaintSelected();Balance=GarageWallet;
   UI->OpenShop();UI->GarageBike();UI->SelectEntry(0);UI->BuySelected();Check(Balance==GarageWallet,TEXT("phone_blueprint_owned_upgrade_not_charged_twice"));
   UI->SelectEntry(-1);UI->BuySelected();Check(Balance==GarageWallet,TEXT("phone_blueprint_invalid_upgrade_selection_safe"));
   UI->OpenCatalog();UI->SelectEntry(-1);UI->BuyModel();UI->EquipModel();Check(Balance==GarageWallet,TEXT("phone_blueprint_invalid_model_selection_safe"));
   UI->GarageMoto();UI->SwitchPressed();Check(Vehicle==EDeliveryVehicle::Motorcycle,TEXT("phone_blueprint_switch_uses_preview_vehicle"));
   UI->OpenHome();
  }CaptureUI(TEXT("UrbanHome.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==12&&ValidationTime>1){
  DestroyMarkers();ActiveOrders.Empty();Offers.Empty();State=EDeliveryState::Idle;GenerateOffer();Check(Offers.Num()==6,TEXT("market_refills_six"));if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget)){UI->OpenOrders();UI->SelectEntry(0);UI->SelectNext();Check(SelectedOffer==Offers[1].ID,TEXT("phone_blueprint_next_offer"));UI->SelectPrevious();Check(SelectedOffer==Offers[0].ID,TEXT("phone_blueprint_previous_offer"));UI->SelectPrevious();Check(SelectedOffer==Offers[0].ID,TEXT("phone_blueprint_offer_lower_bound"));for(int32 N=0;N<8;N++)UI->SelectNext();Check(SelectedOffer==Offers.Last().ID,TEXT("phone_blueprint_offer_upper_bound"));UI->SelectEntry(0);}CaptureUI(TEXT("UrbanOrders.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==13&&ValidationTime>1){
  if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget)){UI->OpenCatalog();UI->GarageMoto();}CaptureUI(TEXT("UrbanCatalog.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==14&&ValidationTime>1){
  if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget)){UI->OpenShop();UI->GarageMoto();UI->SelectEntry(8);UI->SelectEntry(103);}CaptureUI(TEXT("UrbanWorkshop.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==15&&ValidationTime>1){
  TogglePhone();P->GetCharacterMovement()->StopMovementImmediately();ValidationStage++;ValidationTime=0;
 }else if(ValidationStage>=16&&ValidationStage<22&&ValidationTime>1.2){
  const TCHAR* Models[]={TEXT("BikeCity"),TEXT("BikeCargo"),TEXT("BikeBMX"),TEXT("MotoStreet"),TEXT("MotoCargo"),TEXT("MotoSport")};const int32 I=ValidationStage-16;
  P->SetDeliveryDriveInput(0,false);P->GetCharacterMovement()->StopMovementImmediately();Check(P->Riding,Models[I]);FVector Hands=(P->GetActorTransform().InverseTransformPosition(P->GetMesh()->GetSocketLocation(TEXT("hand_l")))+P->GetActorTransform().InverseTransformPosition(P->GetMesh()->GetSocketLocation(TEXT("hand_r"))))*.5;Check(FMath::Abs(Hands.X-36)<3&&FMath::Abs(Hands.Y)<3,TEXT("hands_align_handlebar"));if(auto* Anim=Cast<UDeliveryAnimInstance>(P->GetMesh()->GetAnimInstance()))UE_LOG(LogTemp,Display,TEXT("ANIM_MOUNT_DIAGNOSTIC mounted=%d motorcycle=%d walking=%d hands=%s pedal=%f"),Anim->Mounted,Anim->Motorcycle,Anim->Walking,*Hands.ToString(),Anim->PedalTime);FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/FString::Printf(TEXT("Screenshots/Riding_%s.png"),Models[I]),true,false);ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==22&&ValidationTime>1){
  int32 OriginalBalance=Balance;auto OriginalPurchased=Purchased;auto OriginalModels=OwnedModels;auto OriginalColors=ModelColors;FName OriginalModel=MotoModel;
  for(TCHAR C:FString(TEXT("ESOYAM")))DeveloperKey(FKey(FName(*FString::Chr(C))));
  Check(DeveloperMode&&Balance==100000000&&Purchased.Num()==Upgrades->GetRowNames().Num()&&OwnedModels.Num()==VehicleCatalog->GetRowNames().Num(),TEXT("developer_code_unlocks_catalog"));
  auto* BeforeDev=Cast<UDeliverySave>(UGameplayStatics::LoadGameFromSlot(TEXT("VoxelDelivery_Automation"),0));Balance=9000;PaintVehicle(true,1);Check(SaveProfile(),TEXT("developer_save_suppressed"));
  auto* AfterDev=Cast<UDeliverySave>(UGameplayStatics::LoadGameFromSlot(TEXT("VoxelDelivery_Automation"),0));Check(BeforeDev&&AfterDev&&BeforeDev->Balance==AfterDev->Balance&&BeforeDev->ModelColors.OrderIndependentCompareEqual(AfterDev->ModelColors),TEXT("developer_does_not_change_saved_profile"));
  for(TCHAR C:FString(TEXT("ESOYAM")))DeveloperKey(FKey(FName(*FString::Chr(C))));
  Check(!DeveloperMode&&Balance==OriginalBalance&&Purchased==OriginalPurchased&&OwnedModels==OriginalModels&&MotoModel==OriginalModel&&ModelColors.OrderIndependentCompareEqual(OriginalColors),TEXT("developer_exit_restores_progress"));

  ValidationStage++;ValidationTime=0;
 }else if(ValidationStage>=23&&ValidationStage<=35&&ValidationTime>1.2){
  P->FinishDeliveryRide();ExitStore();if(PhoneOpen)TogglePhone();const FName ThemeNames[]={TEXT("MarketLocal"),TEXT("MarketFresh"),TEXT("BurgerGrill"),TEXT("QuickMeals"),TEXT("TechRetail"),TEXT("TechComponents"),TEXT("Pharmacy"),TEXT("Florist"),TEXT("Bakery"),TEXT("Cafe"),TEXT("Hardware"),TEXT("PetShop"),TEXT("Pizza")};TArray<ADeliveryPoint*> ThemeShops;for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)if(It->ThemeID==ThemeNames[ValidationStage-23])ThemeShops.Add(*It);
  Check(!ThemeShops.IsEmpty(),TEXT("store_category_exists"));for(ADeliveryPoint* Shop:ThemeShops){
   P->SetActorLocation(Shop->InteriorPosition(FVector(0,-300,95)));InsideStore=Shop;P->GetCharacterMovement()->StopMovementImmediately();Check(Shop->ContainsVisitor(P->GetActorLocation()),TEXT("walk_in_store_at_street_level"));FHitResult DoorHit;FCollisionQueryParams DoorParams;DoorParams.AddIgnoredActor(P);Check(!GetWorld()->SweepSingleByChannel(DoorHit,Shop->GetActorLocation()+FVector(0,-120,95),Shop->InteriorPosition(FVector(0,120-Shop->HalfDepth,95)),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(34,88),DoorParams),TEXT("doorway_has_continuous_walkable_entry"));if(DoorHit.bBlockingHit)UE_LOG(LogTemp,Warning,TEXT("DOOR_BLOCKED theme=%s shop=%s actor=%s component=%s item=%d position=%s start=%d"),*Shop->ThemeID.ToString(),*Shop->PointID.ToString(),*GetNameSafe(DoorHit.GetActor()),*GetNameSafe(DoorHit.GetComponent()),DoorHit.Item,*DoorHit.ImpactPoint.ToString(),DoorHit.bStartPenetrating);
   // Flood connected standing positions with a capsule: verify actual walkable aisles, not teleport-only tests.
   TArray<FVector> Reachable;TArray<FIntPoint> Queue;TSet<FIntPoint> Visited;Queue.Add(FIntPoint(0,-FMath::RoundToInt(Shop->HalfDepth/50)+2));Visited.Add(Queue[0]);FCollisionQueryParams WalkParams;WalkParams.AddIgnoredActor(P);
   for(int32 Q=0;Q<Queue.Num();Q++){auto Cell=Queue[Q];FVector Here=Shop->InteriorPosition(FVector(Cell.X*50,Cell.Y*50,95));Reachable.Add(Here);
    for(auto Step:TArray<FIntPoint>{FIntPoint(1,0),FIntPoint(-1,0),FIntPoint(0,1),FIntPoint(0,-1)}){auto Next=Cell+Step;if(Visited.Contains(Next)||FMath::Abs(Next.X)>FMath::FloorToInt((Shop->HalfWidth-35)/50)||FMath::Abs(Next.Y)>FMath::FloorToInt((Shop->HalfDepth-35)/50))continue;FVector There=Shop->InteriorPosition(FVector(Next.X*50,Next.Y*50,95));FHitResult Hit;
     if(!GetWorld()->SweepSingleByChannel(Hit,Here,There,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(34,88),WalkParams)){Visited.Add(Next);Queue.Add(Next);}else if(Q==0)UE_LOG(LogTemp,Warning,TEXT("AISLE_ENTRY_BLOCKED theme=%s shop=%s actor=%s component=%s item=%d position=%s"),*Shop->ThemeID.ToString(),*Shop->PointID.ToString(),*GetNameSafe(Hit.GetActor()),*GetNameSafe(Hit.GetComponent()),Hit.Item,*Hit.ImpactPoint.ToString());
    }
   }
   for(int32 I=0;I<Shop->ItemCount();I++){bool Access=Reachable.ContainsByPredicate([&](const FVector& V){return FVector::Dist2D(V,Shop->ProductPosition(I))<140;});Check(Access,TEXT("walkable_path_from_door_to_product"));if(!Access)UE_LOG(LogTemp,Warning,TEXT("WALKABILITY_BLOCKED theme=%s product=%d reachable=%d target=%s"),*Shop->ThemeID.ToString(),I,Reachable.Num(),*Shop->ProductPosition(I).ToString());}
   Check(Reachable.ContainsByPredicate([&](const FVector& V){return FVector::Dist2D(V,Shop->CheckoutPosition())<120;}),TEXT("walkable_path_to_checkout"));
   FHitResult Floor;FCollisionQueryParams Params;Params.AddIgnoredActor(P);Params.bTraceComplex=true;Params.bReturnFaceIndex=true;Check(GetWorld()->LineTraceSingleByChannel(Floor,Shop->InteriorPosition(FVector(0,0,120)),Shop->InteriorPosition(FVector(0,0,-50)),ECC_Visibility,Params),TEXT("interior_has_walkable_floor"));
   int32 FloorSection=INDEX_NONE;auto* FloorMaterial=Floor.Component.IsValid()?Floor.Component->GetMaterialFromCollisionFaceIndex(Floor.FaceIndex,FloorSection):nullptr;
   const FString FloorMaterialName=GetNameSafe(FloorMaterial);Check(FloorMaterialName.StartsWith(TEXT("ENV_ivory"))||FloorMaterialName.StartsWith(TEXT("ENV_tile"))||FloorMaterialName.StartsWith(TEXT("ENV_cream")),TEXT("floor_uses_blender_palette"));
   if(auto* FloorMesh=Cast<UStaticMeshComponent>(Floor.Component.Get()))Check(FloorMesh->GetStaticMesh()&&FloorMesh->GetStaticMesh()->GetStaticMaterials().Num()<50,TEXT("interior_has_no_legacy_material_slot_accumulation"));
   P->SetActorLocation(Shop->InteriorPosition(FVector(0,-220,95)));Check(Shop->StoreProducts.Num()==Shop->ItemCount(),TEXT("store_has_correct_products"));for(auto Product:Shop->StoreProducts)Check(Product->GetStaticMesh()!=nullptr,TEXT("voxel_product_imported"));
   TArray<USkeletalMeshComponent*> People;Shop->GetComponents<USkeletalMeshComponent>(People);Check(People.Num()==3,TEXT("one_employee_two_customers"));
   Check(Shop->WalkingCustomers.Num()==2,TEXT("two_walking_customers"));
   Check(Shop->CounterDistanceMeters>=6.f,TEXT("service_counter_inside_store"));
   for(auto* Person:People)if(!Shop->WalkingCustomers.Contains(Person))Check(Shop->ContainsVisitor(Person->GetComponentLocation()+FVector(0,0,95)),TEXT("employee_stays_inside_store"));
   for(int32 N=0;N<Shop->WalkingCustomers.Num();N++){
    auto* C=Shop->WalkingCustomers[N].Get();Check(Shop->CustomerWalkClips[N]!=nullptr,TEXT("customer_walk_clip_loaded"));
    const float FarStop=Shop->StoreKind==1?Shop->CounterDistanceMeters*100-175:Shop->HalfDepth*2-500;
    FVector AisleStart=Shop->GetActorLocation()+FVector(N==0?-430:430,FMath::Min(850.f,Shop->HalfDepth*2-450),95);
    FVector AisleEnd=Shop->GetActorLocation()+FVector(N==0?-430:430,FarStop,95);FHitResult AisleHit;
    Check(!GetWorld()->SweepSingleByChannel(AisleHit,AisleStart,AisleEnd,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(25,80),WalkParams),TEXT("customer_aisle_clear_of_furniture"));
    if(AisleHit.bBlockingHit)UE_LOG(LogTemp,Warning,TEXT("CUSTOMER_AISLE_BLOCKED theme=%s lane=%d actor=%s component=%s point=%s start=%s end=%s"),*Shop->ThemeID.ToString(),N,*GetNameSafe(AisleHit.GetActor()),*GetNameSafe(AisleHit.GetComponent()),*AisleHit.ImpactPoint.ToString(),*AisleStart.ToString(),*AisleEnd.ToString());
    FVector Start=C->GetRelativeLocation();Shop->CustomerWaits[N]=0;Shop->CustomerStops[N]=Start.Y<(FMath::Min(850.f,Shop->HalfDepth*2-450)+Shop->HalfDepth*2-500)*.5f?1:0;Shop->Tick(.25f);
    Check(FVector::Dist2D(Start,C->GetRelativeLocation())>1,TEXT("customer_advances_in_aisle"));
    FVector SavedPlayer=P->GetActorLocation();P->SetActorLocation(C->GetComponentLocation()+FVector(0,0,95));Start=C->GetRelativeLocation();Shop->CustomerWaits[N]=0;Shop->Tick(.25f);Check(C->GetRelativeLocation().Equals(Start,1),TEXT("customer_yields_to_player"));P->SetActorLocation(SavedPlayer);
   }
   for(auto* Person:People){Check(Person->GetSkeletalMeshAsset()!=nullptr&&Person->GetNumBones()>=16,TEXT("npc_has_imported_rig"));Check(Person->IsPlaying()||Cast<UDeliveryAnimInstance>(Person->GetAnimInstance())!=nullptr,TEXT("npc_animation_playing"));auto* RenderData=Person->GetSkeletalMeshAsset()?Person->GetSkeletalMeshAsset()->GetResourceForRendering():nullptr;Check(RenderData&&RenderData->LODRenderData.Num()>0&&RenderData->LODRenderData[0].RenderSections.Num()==1,TEXT("npc_single_render_section"));Check(Person->VisibilityBasedAnimTickOption==EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered,TEXT("offscreen_npc_animation_culled"));}
   DestroyMarkers();Order=FDeliveryOrder();Order.ID=FGuid::NewGuid();Order.StoreID=Shop->PointID;Order.StoreKind=Shop->StoreKind;Order.Pickup=Shop->GetActorLocation();Order.Dropoff=Shop->GetActorLocation()+FVector(-300,0,0);Order.GoodsCost=32000;State=EDeliveryState::Pickup;BasketCount=0;OrderPaid=false;OrderBudget=32000;GoodsPaid=0;int32 WalletBefore=Balance;
   P->SetActorLocation(Shop->CheckoutPosition()+FVector(0,0,90));P->GetCharacterMovement()->StopMovementImmediately();CollectOrder(Order.ID);Check(Shop->StoreKind==1?(OrderPaid&&OrderBudget==0&&State==EDeliveryState::Dropoff):(!OrderPaid&&OrderBudget==32000&&GoodsPaid==0&&State==EDeliveryState::Pickup),TEXT("ready_meal_pays_at_counter_other_goods_require_collection"));
   for(int32 I=BasketCount;I<Shop->ItemCount();I++){P->SetActorLocation(Shop->ProductPosition(I)+FVector(0,-80,0));P->GetCharacterMovement()->StopMovementImmediately();Check(CollectOrder(Order.ID),TEXT("each_category_product_collects"));}
   P->SetActorLocation(Shop->CheckoutPosition()+FVector(0,0,90));P->GetCharacterMovement()->StopMovementImmediately();Check((OrderPaid||CollectOrder(Order.ID))&&OrderBudget==0&&GoodsPaid==32000&&Balance==WalletBefore,TEXT("each_category_pays_from_budget"));Check(!CollectOrder(Order.ID),TEXT("checkout_cannot_charge_twice"));
   P->SetActorLocation(Shop->InteriorPosition(FVector(0,-220,95)));P->GetCharacterMovement()->StopMovementImmediately();
   CaptureUI(FString::Printf(TEXT("Store_%s.png"),*Shop->ThemeID.ToString()));
  }ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==36&&ValidationTime>1.2){
  P->FinishDeliveryRide();ExitStore();DestroyMarkers();ActiveOrders.Empty();State=EDeliveryState::Idle;Offers.Empty();P->SetActorLocation(FVector(-6500,14000,130));P->GetCharacterMovement()->StopMovementImmediately();Balance=5000000;
  Check(CargoCapacity(false)==1&&CargoCapacity(true)==1,TEXT("base_one_order_capacity"));Check(PurchaseUpgrade(TEXT("CargoBackpack"))&&CargoCapacity(false)==2,TEXT("backpack_adds_order_slot"));
  GenerateOffer();Check(AcceptOffer(Offers[0].ID),TEXT("accept_first_batch_order"));FGuid First=Order.ID;int32 BudgetOne=OrderBudget;
  Check(SelectOffer(0)&&AcceptOffer(Offers[0].ID),TEXT("accept_second_batch_order"));FGuid Second=Order.ID;Check(ActiveOrders.Num()==2&&Order.ID!=First,TEXT("two_independent_order_ids"));Check(!AcceptOffer(Offers[0].ID),TEXT("reject_order_when_capacity_full"));
  BasketCount=1;StoreFocusedOrder();Check(SelectActiveOrder(0)&&Order.ID==First&&BasketCount==0&&OrderBudget==BudgetOne,TEXT("switch_preserves_separate_budgets"));Check(SelectActiveOrder(1)&&Order.ID==Second&&BasketCount==1,TEXT("switch_preserves_partial_basket"));
  Check(PurchaseUpgrade(TEXT("CargoWaist"))&&CargoCapacity(false)==3,TEXT("waist_adds_third_slot"));Check(PurchaseUpgrade(TEXT("CargoPanniers"))&&CargoCapacity(true)==5&&CargoCapacity(false)==3,TEXT("panniers_moto_only"));Vehicle=EDeliveryVehicle::Motorcycle;
  for(int32 I=0;I<3;I++)Check(AcceptOffer(Offers[0].ID),TEXT("fill_moto_cargo_slots"));Check(ActiveOrders.Num()==5&&!AcceptOffer(Offers[0].ID),TEXT("moto_limit_five"));Check(!SwitchVehicle()&&!EquipVehicle(TEXT("BikeCity")),TEXT("cannot_switch_to_overloaded_bicycle"));
  // Complete every independently accepted order through collection, checkout and handover.
  int32 ExpectedWallet=Balance;int32 AttemptsRemaining=ActiveOrders.Num();while(!ActiveOrders.IsEmpty()&&AttemptsRemaining-->0){
   SelectActiveOrder(0);auto* Shop=OrderStore();Check(Shop!=nullptr,TEXT("batch_store_exists"));if(!Shop)break;InsideStore=Shop;
   for(int32 I=BasketCount;I<Shop->ItemCount();I++){P->SetActorLocation(Shop->ProductPosition(I)+FVector(0,-80,0));Check(CollectOrder(Order.ID),TEXT("batch_collect_independent_products"));}
   P->SetActorLocation(Shop->CheckoutPosition()+FVector(0,0,90));Check((OrderPaid||CollectOrder(Order.ID))&&OrderBudget==0&&OrderPaid,TEXT("batch_checkout_independent_budget"));
   ExitStore();FGuid Done=Order.ID;ExpectedWallet+=Order.Reward;int32 Remaining=ActiveOrders.Num()-1;P->SetActorLocation(Order.Dropoff+FVector(0,0,95));Check(CompleteOrder(Done)&&Balance==ExpectedWallet&&ActiveOrders.Num()==Remaining,TEXT("batch_delivery_pays_only_its_reward"));Check(!CompleteOrder(Done),TEXT("batch_duplicate_delivery_rejected"));if(Remaining)Check(State==EDeliveryState::Pickup||State==EDeliveryState::Dropoff,TEXT("batch_keeps_other_orders_active"));
  }
  Check(ActiveOrders.IsEmpty(),TEXT("last_batch_delivery_clears_orders"));P->RefreshVehicleArt();Check(P->City&&P->City->BikeActors[0].IsValid()&&!P->City->BikeActors[0]->IsHidden(),TEXT("vehicle_remains_after_last_delivery"));const FVector ParkBefore=P->City->ParkedBikes[0];P->PlaceDeliveryVehicle();Check(P->City->ParkedBikes[0].Equals(ParkBefore),TEXT("existing_vehicle_not_teleported"));Check(P->CargoBackpack&&P->CargoBackpack->GetSkeletalMeshAsset()&&P->CargoWaist&&P->CargoWaist->GetSkeletalMeshAsset()&&P->CargoPanniers&&P->CargoPanniers->GetStaticMesh(),TEXT("cargo_models_loaded"));Check(P->JumpClip&&P->Walk&&P->Walk->GetName()==TEXT("AN_MixamoWalk"),TEXT("main_mixamo_walk_jump_loaded"));
  SaveProfile();auto* SavedCargo=Cast<UDeliverySave>(UGameplayStatics::LoadGameFromSlot(TEXT("VoxelDelivery_Automation"),0));Check(SavedCargo&&SavedCargo->Purchased.Contains(TEXT("CargoPanniers")),TEXT("cargo_upgrades_saved"));
  TogglePhone();if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget))UI->OpenCargo();CaptureUI(TEXT("CargoShop.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==37&&ValidationTime>1.2){
  if(PhoneOpen)TogglePhone();ExitStore();Vehicle=EDeliveryVehicle::Motorcycle;P->SetActorLocation(FVector(0,11000,95));GenerateOffer();AcceptOffer(Offers[0].ID);P->RefreshVehicleArt();
  if(P->City&&P->City->ParkedBikes.IsValidIndex(0)){P->SetActorLocation(P->City->ParkedBikes[0]+FVector(0,-100,95));P->Interact();}CaptureUI(TEXT("CargoMounted.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==38&&ValidationTime>1.2){
  Check(P->Riding&&!InsideStore&&FVector::Dist(P->Camera->GetComponentLocation(),P->GetActorLocation())>300,TEXT("mounted_camera_outside_character"));
  Check(P->CargoBackpack->GetSkeletalMeshAsset()->GetBounds().BoxExtent.GetMax()<100&&P->CargoWaist->GetSkeletalMeshAsset()->GetBounds().BoxExtent.GetMax()<100&&P->CargoPanniers->GetStaticMesh()->GetBounds().BoxExtent.GetMax()<100,TEXT("cargo_dimensions_match_character"));
  P->FinishDeliveryRide();Check(P->FrontWheel->bHiddenInGame&&P->RearWheel->bHiddenInGame,TEXT("dismounted_wheels_hidden"));P->GetCharacterMovement()->StopMovementImmediately();if(auto* PC=Cast<APlayerController>(P->GetController()))PC->SetControlRotation(FRotator(-14,145,0));CaptureUI(TEXT("MainWalking.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==39&&ValidationTime>1.2){
  if(auto* Live=Cast<UDeliveryAnimInstance>(P->GetMesh()->GetAnimInstance())){
   auto* Probe=NewObject<UDeliveryAnimInstance>(P->GetMesh(),Live->GetClass());FDeliveryMotionInput Motion;Motion.HasRider=true;Motion.Speed=390;Motion.TargetWalkRate=1;Motion.JumpLength=2;Motion.PedalLength=4;Motion.CrankAngle=PI/2;
   Probe->UpdateMotion(Motion,.1f);Check(Probe->Walking&&!Probe->Mounted&&!Probe->Jumping&&FMath::IsNearlyEqual(Probe->PedalTime,1.f),TEXT("animation_blueprint_walk_and_pedal_phase"));
   Motion.Speed=12;Probe->UpdateMotion(Motion,.1f);Check(Probe->Walking,TEXT("animation_blueprint_walk_hysteresis"));Motion.Speed=0;Probe->UpdateMotion(Motion,.1f);Check(!Probe->Walking,TEXT("animation_blueprint_stops_at_rest"));
   Motion.Falling=true;Motion.VerticalSpeed=Motion.JumpVelocity;Probe->UpdateMotion(Motion,.1f);Check(Probe->Jumping&&FMath::IsNearlyEqual(Probe->JumpTime,.6f),TEXT("animation_blueprint_jump_takeoff_phase"));
   Motion.VerticalSpeed=-Motion.JumpVelocity;Probe->UpdateMotion(Motion,.1f);Check(FMath::IsNearlyEqual(Probe->JumpTime,1.4f),TEXT("animation_blueprint_jump_descent_phase"));
   Motion.Riding=true;Motion.Moto=true;Probe->UpdateMotion(Motion,.1f);Check(Probe->Mounted&&Probe->Motorcycle&&!Probe->Jumping,TEXT("animation_blueprint_vehicle_suppresses_jump"));
  }
  Check(Cast<UDeliveryAnimInstance>(P->GetMesh()->GetAnimInstance())!=nullptr,TEXT("main_animation_blueprint_active"));Check(P->GetVelocity().Size2D()>100&&P->CurrentClip==P->Walk,TEXT("main_walk_plays_while_moving"));Check(FMath::IsNearlyEqual(P->GetWalkPlayRate(390),1.f)&&P->GetWalkPlayRate(1000)<=1.65f&&P->LocomotionRate<=1.66f,TEXT("walk_cadence_matches_speed_without_overcranking"));P->GetCharacterMovement()->StopMovementImmediately();P->JumpOrBrake();CaptureUI(TEXT("MainJump.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==40&&ValidationTime>.18){
  Check(P->GetCharacterMovement()->IsFalling()&&P->CurrentClip==P->JumpClip,TEXT("jump_clip_plays_airborne"));CaptureUI(TEXT("MainJump.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==41&&ValidationTime>1.2){
  ExitStore();Check(!InsideStore,TEXT("store_exit_restores_street"));
  auto Report=MakeShared<FJsonObject>();Report->SetStringField(TEXT("status"),ValidationErrors.IsEmpty()?TEXT("PASS"):TEXT("FAIL"));TArray<TSharedPtr<FJsonValue>> Errors;for(const auto& E:ValidationErrors)Errors.Add(MakeShared<FJsonValueString>(E));Report->SetArrayField(TEXT("failures"),Errors);Report->SetStringField(TEXT("engine"),FEngineVersion::Current().ToString());FString JSON;auto Writer=TJsonWriterFactory<>::Create(&JSON);FJsonSerializer::Serialize(Report,Writer);FFileHelper::SaveStringToFile(JSON,*(FPaths::ProjectSavedDir()/TEXT("delivery_test.json")));UE_LOG(LogTemp,Display,TEXT("DELIVERY_TEST_RESULT %s"),*JSON);ValidationStage++;FPlatformMisc::RequestExit(false);
 }
}


bool UDeliveryComponent::SpawnOrderRecipient(){
 FActorSpawnParameters Params;Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 Recipient=GetWorld()->SpawnActor<ADeliveryRecipient>(RecipientClass,Order.Dropoff,FRotator(0,180,0),Params);
 if(!Recipient)return false;Recipient->OrderID=Order.ID;Recipient->Delivery=this;const FName Roles[]={TEXT("CustomerStudent"),TEXT("CustomerOffice"),TEXT("CustomerNeighbor")};Recipient->InitializeAppearance(Roles[Order.ID.A%3]);return true;
}
void UDeliveryComponent::RemovePickupMarker(){if(PickupMarker){PickupMarker->Destroy();PickupMarker=nullptr;}}

FDeliveryUpgrade UDeliveryComponent::GetUpgradeSpec(FName ID,bool& Found)const{const auto* Row=Upgrades?Upgrades->FindRow<FDeliveryUpgrade>(ID,TEXT("BlueprintData")):nullptr;Found=Row!=nullptr;return Row?*Row:FDeliveryUpgrade();}

FDeliveryOrder UDeliveryComponent::GetSelectedOffer(bool& Found) const {const auto* P=SelectedIncoming();Found=P!=nullptr;return P?*P:FDeliveryOrder();}


FDeliveryOrder UDeliveryComponent::FindOffer(FGuid ID,int32& Index)const{Index=Offers.IndexOfByPredicate([&](const FDeliveryOrder& O){return O.ID==ID;});return Offers.IsValidIndex(Index)?Offers[Index]:FDeliveryOrder();}
int32 UDeliveryComponent::FindActiveOrderIndex(FGuid ID)const{return ActiveOrders.IndexOfByPredicate([&](const FActiveDelivery& O){return O.Order.ID==ID;});}
ABogotaPlayer* UDeliveryComponent::GetRider()const{return Cast<ABogotaPlayer>(GetOwner());}






FString UDeliveryComponent::ProfileSlot()const{return bValidation?TEXT("VoxelDelivery_Automation"):TEXT("VoxelDelivery_Profile_v1");}
FDeliveryVehicleSpec UDeliveryComponent::GetVehicleSpec(FName ID,bool& Found)const{const auto* Row=VehicleCatalog?VehicleCatalog->FindRow<FDeliveryVehicleSpec>(ID,TEXT("BlueprintData")):nullptr;Found=Row!=nullptr;return Row?*Row:FDeliveryVehicleSpec();}
int32 UDeliveryComponent::GetModelColor(FName ID)const{return FMath::Clamp(ModelColors.FindRef(ID),0,5);}


void UDeliveryComponent::HandleInputSuspended(){
 // UI-consumed key presses are absent from PlayerInput's pressed-key flush.
 // Cancel the interaction itself when Windows deactivates the game.
 EndAction();BoostActive=false;
 if(auto* P=Cast<ABogotaPlayer>(GetOwner())){P->StopForPhone();P->StopJump();}
}
