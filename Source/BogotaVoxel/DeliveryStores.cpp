#include "DeliverySystem.h"
#include "BogotaGame.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Materials/MaterialInterface.h"
namespace {
#include "CrowdCatalog.inl"
}
#include "DeliveryAnimInstance.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Components/TextRenderComponent.h"
#include "Components/PointLightComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

void ADeliveryPoint::BeginPlay(){Super::BeginPlay();PrimaryActorTick.bCanEverTick=true;SetActorTickEnabled(true);BuildStore();}
void ADeliveryPoint::Tick(float Dt){
 Super::Tick(Dt);auto* Player=UGameplayStatics::GetPlayerPawn(this,0);if(!Player||FVector::DistSquared(Player->GetActorLocation(),InteriorPosition(FVector::ZeroVector))>FMath::Square(HalfDepth+1000.f))return;
 for(int32 I=0;I<WalkingCustomers.Num();I++)UpdateCrowdCustomer(I,Dt);
}

void ADeliveryPoint::UpdateCrowdCustomer(int32 I,float Dt){
 auto* Player=UGameplayStatics::GetPlayerPawn(this,0);
 if(!WalkingCustomers.IsValidIndex(I)||!CustomerPathStart.IsValidIndex(I))return;auto* C=WalkingCustomers[I].Get();if(!C)return;
 auto Rest=[&](){if(C->AnimationData.AnimToPlay!=CustomerIdleClips[I])C->PlayAnimation(CustomerIdleClips[I],true);if(CustomerUsesCane[I]){C->SetPosition(0,false);C->SetPlayRate(0);}else C->SetPlayRate(1);};
 // Query around the authored shop floor, never around the previous foot height.
 FHitResult Ground;FCollisionQueryParams GroundQuery;if(Player)GroundQuery.AddIgnoredActor(Player);FVector Foot=C->GetComponentLocation();const float Floor=GetActorLocation().Z+10;
 float GroundZ=Floor;
 if(GetWorld()->LineTraceSingleByObjectType(Ground,FVector(Foot.X,Foot.Y,Floor+65),FVector(Foot.X,Foot.Y,Floor-30),FCollisionObjectQueryParams(ECC_WorldStatic),GroundQuery)&&Ground.ImpactNormal.Z>.7f&&Ground.ImpactPoint.Z<=Floor+25)GroundZ=Ground.ImpactPoint.Z;
 auto At=C->GetRelativeLocation();At.Z=GroundZ-GetActorLocation().Z;C->SetRelativeLocation(At);

 if(CustomerWaits[I]>0){CustomerWaits[I]=FMath::Max(0.f,CustomerWaits[I]-Dt);Rest();return;}
 FVector From=C->GetRelativeLocation(),To=CustomerStops[I]?CustomerPathEnd[I]:CustomerPathStart[I];To.Z=From.Z;FVector Delta=To-From;float Dist=Delta.Size2D();
 if(Dist<4){CustomerStops[I]=1-CustomerStops[I];CustomerWaits[I]=4.f+I*2;Rest();return;}
 FVector Next=From+Delta.GetSafeNormal2D()*FMath::Min(Dist,Dt*CustomerSpeeds[I]);
 if(Player&&FVector::Dist2D(GetActorLocation()+Next,Player->GetActorLocation())<100){Rest();return;}
 FHitResult Block;FCollisionQueryParams Query;if(Player)Query.AddIgnoredActor(Player);
 if(GetWorld()->SweepSingleByChannel(Block,GetActorLocation()+From+FVector(0,0,95),GetActorLocation()+Next+FVector(0,0,95),FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(35,80),Query)){CustomerStops[I]=1-CustomerStops[I];CustomerWaits[I]=2;Rest();return;}
 if(C->AnimationData.AnimToPlay!=CustomerWalkClips[I])C->PlayAnimation(CustomerWalkClips[I],true);
 C->SetPlayRate(CustomerUsesCane[I]?.95f:CustomerSpeeds[I]/(140.f*C->GetRelativeScale3D().X));
 C->SetRelativeRotation(FMath::RInterpTo(C->GetRelativeRotation(),FRotator(0,Delta.Rotation().Yaw-90,0),Dt,5));C->SetRelativeLocation(Next);
}

FVector ADeliveryPoint::ProductPosition(int32 Index)const{
 const FVector Points[]={FVector(-HalfWidth+250,0,105),FVector(HalfWidth-250,0,105),FVector(0,HalfDepth-200,105)};
 const uint32 Seed=DisplayedOrder.IsValid()?GetTypeHash(DisplayedOrder):0;
 const int32 Slot=(int32(Seed%3)+(Seed&8?2:1)*FMath::Clamp(Index,0,2))%3;
 return InteriorPosition(StoreKind!=1?Points[Slot]:FVector(180,CounterDistanceMeters*100-65-HalfDepth,105));
}
void ADeliveryPoint::PresentOrder(FGuid OrderID,int32 Collected){
 DisplayedOrder=OrderID;
 for(int32 I=0;I<StoreProducts.Num();I++)if(auto* Product=StoreProducts[I].Get()){
  FVector Position=ProductPosition(I);if(StoreKind==1)Position+=FVector(0,65,5);
  Product->SetWorldLocation(Position);Product->SetVisibility(I>=Collected);
 }
}


void ADeliveryPoint::BuildStore(){
 for(auto C:WalkingCustomers)if(C)C->DestroyComponent();WalkingCustomers.Empty();CustomerWalkClips.Empty();CustomerIdleClips.Empty();CustomerStops.Empty();CustomerWaits.Empty();CustomerPathStart.Empty();CustomerPathEnd.Empty();CustomerSpeeds.Empty();CustomerUsesCane.Empty();
 StoreKind=FCrc::StrCrc32(*PointID.ToString())%5;Grocery=StoreKind==0;
 const TCHAR* Markets[]={TEXT("Mercado Don Lucho"),TEXT("La Canasta Verde"),TEXT("Mercadito La Vecina")};
 const TCHAR* Foods[]={TEXT("La Plancha del Barrio"),TEXT("Hamburguesas La Esquina"),TEXT("Parrilla Siete")};
 const TCHAR* Others[]={TEXT("Circuito 7 / Tecnología"),TEXT("Droguería Buen Vecino"),TEXT("Flores de la Sabana")};
 PlaceName=FText::FromString(StoreKind==0?Markets[FMath::RandHelper(3)]:StoreKind==1?Foods[FMath::RandHelper(3)]:Others[StoreKind-2]);
 auto* Themes=LoadObject<UDataTable>(nullptr,TEXT("/Game/Delivery/Data/DT_StoreThemes.DT_StoreThemes"));const FDeliveryShopTheme* Theme=nullptr;
 if(Themes){if(!ThemeID.IsNone())Theme=Themes->FindRow<FDeliveryShopTheme>(ThemeID,TEXT("StoreTheme"));if(!Theme){TArray<FName> Choices;for(FName ID:Themes->GetRowNames())if(auto* Row=Themes->FindRow<FDeliveryShopTheme>(ID,TEXT("ThemeChoice")))if(Row->Category==StoreKind)Choices.Add(ID);Choices.Sort(FNameLexicalLess());if(!Choices.IsEmpty()){ThemeID=Choices[(FCrc::StrCrc32(*PointID.ToString())/5)%Choices.Num()];Theme=Themes->FindRow<FDeliveryShopTheme>(ThemeID,TEXT("Theme"));}}}
 if(Theme){StoreKind=Theme->Category;Grocery=StoreKind==0;PlaceName=Theme->Title;ThemeProductNames=Theme->ProductNames;PurchaseBudget=Theme->PurchaseBudget;HalfWidth=Theme->WidthMeters*50;HalfDepth=Theme->DepthMeters*50;CounterDistanceMeters=Theme->CounterDistanceMeters;}
 Sign->SetVisibility(false);Label->SetVisibility(false);Label->SetText(PlaceName);
 auto Mesh=[&](const TCHAR* Name,FVector Offset,bool Collision){
  auto* C=NewObject<UStaticMeshComponent>(this);AddInstanceComponent(C);C->SetupAttachment(RootComponent);C->SetRelativeLocation(Offset);C->SetRelativeScale3D(FVector(1,-1,1));
  C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/Delivery/Stores/%s.%s"),Name,Name)));C->SetCollisionProfileName(Collision?TEXT("BlockAll"):TEXT("NoCollision"));C->RegisterComponent();return C;
 };
 const TCHAR* Fronts[]={TEXT("SM_MarketFront_Voxel"),TEXT("SM_RestaurantFront_Voxel"),TEXT("SM_TechFront_Voxel"),TEXT("SM_PharmacyFront_Voxel"),TEXT("SM_FloristFront_Voxel")};
 Mesh(Theme&&Theme->FrontMesh?*Theme->FrontMesh->GetName():Fronts[StoreKind],FVector::ZeroVector,true);
 const TCHAR* Interiors[]={TEXT("SM_MarketInterior_Voxel"),TEXT("SM_RestaurantInterior_Voxel"),TEXT("SM_TechInterior_Voxel"),TEXT("SM_PharmacyInterior_Voxel"),TEXT("SM_FloristInterior_Voxel")};
 Mesh(Theme&&Theme->InteriorMesh?*Theme->InteriorMesh->GetName():Interiors[StoreKind],FVector(0,0,-15000),true);
 const TCHAR* Staff[]={TEXT("Cashier"),TEXT("Chef"),TEXT("TechClerk"),TEXT("Pharmacist"),TEXT("Florist")};
 auto Person=[&](const TCHAR* Name,FVector Position,float Yaw,float Phase){
  auto* C=NewObject<USkeletalMeshComponent>(this);AddInstanceComponent(C);C->SetupAttachment(RootComponent);C->SetRelativeLocation(Position);C->SetRelativeRotation(FRotator(0,Yaw,0));C->SetRelativeScale3D(FVector(1,-1,1));
  C->SetSkeletalMesh(LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Delivery/People/SK_%s.SK_%s"),Name,Name)));
  C->SetCollisionProfileName(TEXT("NoCollision"));C->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;C->bEnableUpdateRateOptimizations=false;C->SetCastShadow(false);C->RegisterComponent();
  if(auto* A=LoadObject<UAnimSequence>(nullptr,*FString::Printf(TEXT("/Game/Delivery/People/A_%s_Work.A_%s_Work"),Name,Name))){C->PlayAnimation(A,true);C->SetPosition(Phase,false);}
  if(auto* Class=LoadClass<UAnimInstance>(nullptr,*FString::Printf(TEXT("/Game/Delivery/Animation/ABP_%s.ABP_%s_C"),Name,Name)))C->SetAnimInstanceClass(Class);
  if(FString(Name).StartsWith(TEXT("Customer"))){WalkingCustomers.Add(C);CustomerStops.Add(WalkingCustomers.Num()%2);CustomerWaits.Add(Phase);CustomerIdleClips.Add(LoadObject<UAnimSequence>(nullptr,*FString::Printf(TEXT("/Game/Delivery/People/A_%s_Work.A_%s_Work"),Name,Name)));CustomerWalkClips.Add(LoadObject<UAnimSequence>(nullptr,*FString::Printf(TEXT("/Game/Delivery/People/A_%s_Walk.A_%s_Walk"),Name,Name)));}
 };
 Person(Staff[StoreKind],FVector(270,CounterDistanceMeters*100+75-HalfDepth,-15000),0,0);
 // Replace the former two repeated customers with a quiet, varied population.
 const uint32 CustomerSeed=FCrc::StrCrc32(*PointID.ToString());const int32 CustomerCount=4*HalfWidth*HalfDepth/10000.f<120?1:2;
 for(int32 I=0;I<CustomerCount;I++){
  const int32 BusinessProfiles[]={24,25,34,35,46,47,48,49};const int32 StudentProfiles[]={0,15,40,41,42,43,44,45};
  const int32 Profile=I==0&&StoreKind==2?BusinessProfiles[CustomerSeed%8]:I==0&&StoreKind==1?StudentProfiles[CustomerSeed%8]:(CustomerSeed+I*13)%UE_ARRAY_COUNT(CrowdModels);const auto& Spec=CrowdModels[Profile];FString Name=Spec.Name;
  auto* C=NewObject<USkeletalMeshComponent>(this);AddInstanceComponent(C);C->SetupAttachment(RootComponent);
  const float X=(I==0?-1.f:1.f)*FMath::Min(430.f,HalfWidth*.4f);float StartY=FMath::Min(850.f,HalfDepth*2-450),EndY=StoreKind==1?FMath::Max(200.f,CounterDistanceMeters*100-175):HalfDepth*2-500;
  if(FMath::Abs(EndY-StartY)<180)StartY=FMath::Max(180.f,EndY-300);
  FVector From(X,StartY,10),To(X,EndY,10);C->SetRelativeLocation(FVector(X,StartY-HalfDepth,10-15000));C->SetRelativeRotation(FRotator(0,-90,0));C->SetRelativeScale3D(FVector(Spec.Scale));
  C->SetSkeletalMeshAsset(LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Crowd/People/SK_%s.SK_%s"),*Name,*Name)));C->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Crowd/MI_Crowd.MI_Crowd")));C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;C->bEnableUpdateRateOptimizations=false;C->RegisterComponent();
  auto* Walk=LoadObject<UAnimSequence>(nullptr,Spec.Cane?TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane"):TEXT("/Game/Crowd/AN_CrowdWalk_Mixamo.AN_CrowdWalk_Mixamo"));auto* Idle=LoadObject<UAnimSequence>(nullptr,Spec.Cane?TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane"):TEXT("/Game/Crowd/AN_CrowdIdle.AN_CrowdIdle"));
  WalkingCustomers.Add(C);CustomerWalkClips.Add(Walk);CustomerIdleClips.Add(Idle);CustomerStops.Add(1);CustomerWaits.Add(2.f+I*3);CustomerPathStart.Add(From);CustomerPathEnd.Add(To);CustomerSpeeds.Add(Spec.Cane?Spec.Speed:65.f);CustomerUsesCane.Add(Spec.Cane);C->PlayAnimation(Idle,true);if(Spec.Cane){C->SetPlayRate(0);C->SetPosition(0,false);}
 }
 const TCHAR* Goods[5][3]={{TEXT("SM_Milk"),TEXT("SM_Rice"),TEXT("SM_Apples")},{TEXT("SM_Burger"),TEXT("SM_Burger"),TEXT("SM_Burger")},{TEXT("SM_Headphones"),TEXT("SM_Keyboard"),TEXT("SM_PhoneBox")},{TEXT("SM_FirstAid"),TEXT("SM_Medicine"),TEXT("SM_FirstAid")},{TEXT("SM_Bouquet"),TEXT("SM_Bouquet"),TEXT("SM_Bouquet")}};
 for(int32 I=0;I<ItemCount();I++){FVector Stock=ProductPosition(I)-GetActorLocation();if(StoreKind==1)Stock+=FVector(0,65,5);Stock.Y-=HalfDepth;Stock.Z-=15000;const FString Product=Theme&&Theme->ProductMeshes.IsValidIndex(I)?Theme->ProductMeshes[I].ToString():FString(Goods[StoreKind][I]);StoreProducts.Add(Mesh(*Product,Stock,false));}
 for(float X:{-HalfWidth*.55f,HalfWidth*.55f})for(float Y:{-HalfDepth*.72f,-HalfDepth*.24f,HalfDepth*.24f,HalfDepth*.72f}){
  auto* L=NewObject<UPointLightComponent>(this);AddInstanceComponent(L);L->SetupAttachment(RootComponent);L->SetRelativeLocation(FVector(X,Y,-14480));L->SetIntensityUnits(ELightUnits::Lumens);L->SetIntensity(1800);L->SetAttenuationRadius(1400);L->SetLightColor(StoreKind==1?FLinearColor(1,.86,.65):FLinearColor(.91,.97,1));L->SetCastShadows(false);L->MaxDrawDistance=5000;L->MaxDistanceFadeRange=1000;L->RegisterComponent();
 }
 // Storefronts and interiors contain no text; interactions remain in the player's HUD.
 TArray<USceneComponent*> Parts;GetComponents<USceneComponent>(Parts);for(auto* C:Parts)if(C!=RootComponent&&C->GetAttachParent()==RootComponent){auto At=C->GetRelativeLocation();if(At.Z<-10000){At.Z+=15000;At.Y+=HalfDepth;C->SetRelativeLocation(At);}}
}
ADeliveryPoint* UDeliveryComponent::OrderStore()const{for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)if(It->PointID==Order.StoreID)return *It;return nullptr;}


bool UDeliveryComponent::StoreDoorAction(){return false;}


FString UDeliveryComponent::ShoppingInstruction()const{
 if(State!=EDeliveryState::Pickup)return StatusMessage.ToString();
 if(!InsideStore)return TEXT("Llega al local, baja con F y entra caminando por la puerta.");
 if(InsideStore!=OrderStore())return TEXT("Este no es el local del pedido. La salida está junto a la puerta.");
 const TCHAR* Goods[]={TEXT("leche"),TEXT("arroz"),TEXT("manzanas")};
 if(BasketCount<(Order.StoreKind==1?1:3))return FString::Printf(TEXT("%d/%d · Busca %s. Mantén E / B / Círculo para recoger."),BasketCount,Order.StoreKind==1?1:3,*InsideStore->ItemName(BasketCount));
 return FString::Printf(TEXT("Ve a CAJA y mantén E / B / Círculo. Compra: $%d · cubre el cliente."),Order.GoodsCost);
}

FString ADeliveryPoint::ItemName(int32 Index)const{
 if(ThemeProductNames.IsValidIndex(Index))return ThemeProductNames[Index].ToString();
 const TCHAR* Names[5][3]={{TEXT("leche"),TEXT("arroz"),TEXT("manzanas")},{TEXT("pedido listo en el mostrador"),TEXT("hamburguesa"),TEXT("hamburguesa")},{TEXT("audífonos"),TEXT("teclado"),TEXT("celular sellado")},{TEXT("botiquín"),TEXT("medicamento sellado"),TEXT("kit de primeros auxilios")},{TEXT("ramo rojo"),TEXT("ramo mixto"),TEXT("ramo de regalo")}};
 return Names[StoreKind][FMath::Clamp(Index,0,2)];
}

void UDeliveryComponent::HideStoreProduct(int32 Index){if(auto* Shop=OrderStore())if(Shop->StoreProducts.IsValidIndex(Index)&&Shop->StoreProducts[Index])Shop->StoreProducts[Index]->SetVisibility(false);}

