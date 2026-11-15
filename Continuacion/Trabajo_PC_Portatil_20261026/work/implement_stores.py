from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel')
h=p/'DeliverySystem.h';s=h.read_text(encoding='utf-8');s=s.replace(' UPROPERTY(BlueprintReadOnly) FGuid ID;',' UPROPERTY(BlueprintReadOnly) FGuid ID;\n UPROPERTY(BlueprintReadOnly) FName StoreID;\n UPROPERTY(BlueprintReadOnly) bool Grocery=false;\n UPROPERTY(BlueprintReadOnly) int32 GoodsCost=0;');s=s.replace(' ADeliveryPoint();',' ADeliveryPoint();\n virtual void BeginPlay() override;\n UPROPERTY(BlueprintReadOnly) bool Grocery=false;\n UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> StoreProducts;\n FVector InteriorPosition(FVector Local) const;\n FVector ProductPosition(int32 Index) const;\n FVector CheckoutPosition() const;\n void BuildStore();');s=s.replace(' void PrepareCityMap();',' UPROPERTY(BlueprintReadOnly) TObjectPtr<ADeliveryPoint> InsideStore;\n UPROPERTY(BlueprintReadOnly) int32 BasketCount=0;\n UPROPERTY(BlueprintReadOnly) bool OrderPaid=false;\n ADeliveryPoint* OrderStore() const;\n bool StoreDoorAction();\n bool ShopReady() const;\n bool ShopCollect();\n FString ShoppingInstruction() const;\n void ExitStore();\n void PrepareCityMap();');h.write_text(s,encoding='utf-8')
f=p/'DeliveryStores.cpp';f.write_text('''#include "DeliverySystem.h"
#include "BogotaGame.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/PointLightComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "EngineUtils.h"

void ADeliveryPoint::BeginPlay(){Super::BeginPlay();BuildStore();}
FVector ADeliveryPoint::InteriorPosition(FVector Local)const{return GetActorLocation()+FVector(0,0,-15000)+Local;}
FVector ADeliveryPoint::ProductPosition(int32 Index)const{
 const FVector Points[]={FVector(-250,0,100),FVector(250,80,100),FVector(0,260,100)};
 return InteriorPosition(Grocery?Points[FMath::Clamp(Index,0,2)]:FVector(100,240,115));
}
FVector ADeliveryPoint::CheckoutPosition()const{return InteriorPosition(FVector(270,-220,5));}
void ADeliveryPoint::BuildStore(){
 Grocery=FMath::RandBool();
 const TCHAR* Markets[]={TEXT("Mercado Don Lucho"),TEXT("La Canasta Verde"),TEXT("Mercadito La Vecina")};
 const TCHAR* Foods[]={TEXT("La Plancha del Barrio"),TEXT("Hamburguesas La Esquina"),TEXT("Parrilla Siete")};
 PlaceName=FText::FromString(Grocery?Markets[FMath::RandHelper(3)]:Foods[FMath::RandHelper(3)]);
 Sign->SetVisibility(false);Label->SetText(PlaceName);Label->SetRelativeLocation(FVector(80,0,340));Label->SetWorldSize(21);
 auto Mesh=[&](const TCHAR* Name,FVector Offset,bool Collision){
  auto* C=NewObject<UStaticMeshComponent>(this);AddInstanceComponent(C);C->SetupAttachment(RootComponent);C->SetRelativeLocation(Offset);
  C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/Delivery/Stores/%s.%s"),Name,Name)));C->SetCollisionProfileName(Collision?TEXT("BlockAll"):TEXT("NoCollision"));C->RegisterComponent();return C;
 };
 Mesh(Grocery?TEXT("SM_MarketFront"):TEXT("SM_RestaurantFront"),FVector::ZeroVector,false);
 Mesh(Grocery?TEXT("SM_MarketInterior"):TEXT("SM_RestaurantInterior"),FVector(0,0,-15000),true);
 Mesh(Grocery?TEXT("SM_Cashier"):TEXT("SM_Chef"),FVector(270,-50,-15000),true);
 const TCHAR* Goods[]={TEXT("SM_Milk"),TEXT("SM_Rice"),TEXT("SM_Apples")};
 for(int32 I=0;I<(Grocery?3:1);I++)StoreProducts.Add(Mesh(Grocery?Goods[I]:TEXT("SM_Burger"),ProductPosition(I)-GetActorLocation(),false));
 for(int32 X:{-250,250}){auto* L=NewObject<UPointLightComponent>(this);AddInstanceComponent(L);L->SetupAttachment(RootComponent);L->SetRelativeLocation(FVector(X,0,-14690));L->SetIntensity(7500);L->SetAttenuationRadius(1400);L->SetLightColor(FLinearColor(1,.87,.65));L->SetCastShadows(false);L->RegisterComponent();}
 auto Text=[&](const TCHAR* Value,FVector At,int32 Size){auto* T=NewObject<UTextRenderComponent>(this);AddInstanceComponent(T);T->SetupAttachment(RootComponent);T->SetRelativeLocation(At);T->SetRelativeRotation(FRotator(0,-90,0));T->SetHorizontalAlignment(EHTA_Center);T->SetWorldSize(Size);T->SetText(FText::FromString(Value));T->RegisterComponent();};
 Text(TEXT("CAJA / PEDIDOS"),FVector(270,-120,-14810),22);Text(TEXT("SALIDA"),FVector(0,-388,-14720),28);
}
ADeliveryPoint* UDeliveryComponent::OrderStore()const{for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)if(It->PointID==Order.StoreID)return *It;return nullptr;}
void UDeliveryComponent::ExitStore(){if(!InsideStore)return;auto* P=Cast<ABogotaPlayer>(GetOwner());if(P){P->SetActorLocation(InsideStore->GetActorLocation()+FVector(-160,0,100));P->GetCharacterMovement()->StopMovementImmediately();}InsideStore=nullptr;EndAction();}
bool UDeliveryComponent::StoreDoorAction(){
 auto* P=Cast<ABogotaPlayer>(GetOwner());if(!P||PhoneOpen)return false;
 if(InsideStore){if(FVector::Dist2D(P->GetActorLocation(),InsideStore->InteriorPosition(FVector(0,-340,0)))<170){ExitStore();return true;}return false;}
 for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It){if(FVector::Dist(P->GetActorLocation(),It->GetActorLocation()+FVector(0,0,90))<220){
  if(P->Riding){StatusMessage=FText::FromString(TEXT("Baja del vehículo con F antes de entrar."));return true;}
  InsideStore=*It;P->GetCharacterMovement()->StopMovementImmediately();P->SetActorLocation(It->InteriorPosition(FVector(0,-320,95)));P->SetActorRotation(FRotator(0,90,0));if(P->Controller)P->Controller->SetControlRotation(FRotator(-10,90,0));EndAction();return true;
 }}return false;
}
bool UDeliveryComponent::ShopReady()const{
 auto* P=Cast<ABogotaPlayer>(GetOwner());auto* Shop=OrderStore();return P&&!P->Riding&&Shop&&InsideStore==Shop&&BasketCount>=(Order.Grocery?3:1)&&FVector::Dist2D(P->GetActorLocation(),Shop->CheckoutPosition())<140;
}
bool UDeliveryComponent::ShopCollect(){
 auto* P=Cast<ABogotaPlayer>(GetOwner());auto* Shop=OrderStore();if(!P||P->Riding||InsideStore!=Shop||!Shop)return false;
 if(BasketCount<(Order.Grocery?3:1)){
  if(FVector::Dist2D(P->GetActorLocation(),Shop->ProductPosition(BasketCount))>160)return false;
  BasketCount++;StatusMessage=FText::FromString(ShoppingInstruction());Changed();return true;
 }
 return false;
}
FString UDeliveryComponent::ShoppingInstruction()const{
 if(State!=EDeliveryState::Pickup)return StatusMessage.ToString();
 if(!InsideStore)return TEXT("Llega al local, baja con F y pulsa E / B / Círculo en la puerta.");
 if(InsideStore!=OrderStore())return TEXT("Este no es el local del pedido. La salida está junto a la puerta.");
 const TCHAR* Goods[]={TEXT("leche"),TEXT("arroz"),TEXT("manzanas")};
 if(BasketCount<(Order.Grocery?3:1))return FString::Printf(TEXT("%d/%d · Busca %s. Mantén E / B / Círculo para recoger."),BasketCount,Order.Grocery?3:1,Order.Grocery?Goods[BasketCount]:TEXT("la hamburguesa en cocina"));
 return FString::Printf(TEXT("Ve a CAJA y mantén E / B / Círculo. Compra: $%d · cubre el cliente."),Order.GoodsCost);
}
''',encoding='utf-8')
f=p/'DeliverySystem.cpp';s=f.read_text(encoding='utf-8');s=s.replace('struct FPoint { FVector P;FString Name; };','struct FPoint { FVector P;FString Name;ADeliveryPoint* Shop; };');s=s.replace('It->PlaceName.ToString()});','It->PlaceName.ToString(),*It});');s=s.replace('FDeliveryOrder New;New.ID=FGuid::NewGuid();','FDeliveryOrder New;New.ID=FGuid::NewGuid();New.StoreID=Points[Pair.X].Shop->PointID;New.Grocery=Points[Pair.X].Shop->Grocery;New.GoodsCost=New.Grocery?18500:22000;');s=s.replace('Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ID==ID;});State=EDeliveryState::Pickup;','BasketCount=0;OrderPaid=false;Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ID==ID;});State=EDeliveryState::Pickup;');s=s.replace('return State==EDeliveryState::Pickup?Order.Pickup:Order.Dropoff;','if(State==EDeliveryState::Pickup&&InsideStore&&InsideStore==OrderStore())return BasketCount<(Order.Grocery?3:1)?InsideStore->ProductPosition(BasketCount):InsideStore->CheckoutPosition();return State==EDeliveryState::Pickup?Order.Pickup:Order.Dropoff;');s=s.replace(' if(bHolding)return;',' if(bHolding)return;\n if(StoreDoorAction())return;');s=s.replace('if(State!=EDeliveryState::Pickup||ID!=Order.ID||!IsAtTarget()||PhoneOpen)return false;','if(State!=EDeliveryState::Pickup||ID!=Order.ID||!IsAtTarget()||PhoneOpen)return false;\n if(ShopCollect())return true;\n if(!ShopReady())return false;');s=s.replace('Recipient->OrderID=Order.ID;','OrderPaid=true;Recipient->OrderID=Order.ID;');s=s.replace(' if(PhoneOpen)TogglePhone();\n EndAction();',' if(PhoneOpen)TogglePhone();\n ExitStore();\n EndAction();');f.write_text(s,encoding='utf-8')
f=p/'BogotaPlayer.cpp';s=f.read_text(encoding='utf-8');s=s.replace('if(Delivery&&Delivery->State==EDeliveryState::Pickup)Delivery->BeginAction(true);','if(Delivery&&Delivery->StoreDoorAction())return;if(Delivery&&Delivery->State==EDeliveryState::Pickup)Delivery->BeginAction(true);');s=s.replace('Riding?530.f:430.f','Delivery&&Delivery->InsideStore?220.f:Riding?530.f:430.f');f.write_text(s,encoding='utf-8')
f=p/'DeliveryUI.cpp';s=f.read_text(encoding='utf-8');s=s.replace('FString S=Delivery->StatusMessage.ToString();','FString S=Delivery->State==EDeliveryState::Pickup?Delivery->ShoppingInstruction():Delivery->StatusMessage.ToString();if(Delivery->InsideStore&&Delivery->State!=EDeliveryState::Pickup)S=TEXT("Acércate a la puerta y pulsa E / B / Círculo para salir.");');f.write_text(s,encoding='utf-8')
