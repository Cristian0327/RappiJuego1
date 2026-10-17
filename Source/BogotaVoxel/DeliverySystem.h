#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/DataTable.h"
#include "GameFramework/SaveGame.h"
#include "Blueprint/UserWidget.h"
#include "UObject/Interface.h"
#include "Components/Button.h"
#include "DeliverySystem.generated.h"

class UStaticMesh;

UENUM(BlueprintType) enum class EDeliveryState:uint8 { Idle, Offered, Pickup, Dropoff };
UENUM(BlueprintType) enum class EDeliveryVehicle:uint8 { Bicycle, Motorcycle };
UENUM(BlueprintType) enum class EUpgradeEffect:uint8 { BikeCapacity, BikeDrain, BikeInfinite, Motorcycle, Turbo, MotoCapacity, MotoDrain, MotoRegen, MotoInfinite, Cargo };
USTRUCT(BlueprintType) struct FDeliveryUpgrade:public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FText Title;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 Price=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName Prerequisite;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) EUpgradeEffect Effect=EUpgradeEffect::BikeCapacity;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Magnitude=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 SortIndex=0;
};
USTRUCT(BlueprintType) struct FDeliveryShopTheme:public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 Category=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FText Title;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<UStaticMesh> FrontMesh;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<UStaticMesh> InteriorMesh;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FName> ProductMeshes;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FText> ProductNames;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 PurchaseBudget=22000;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float WidthMeters=20;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float DepthMeters=16;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="2")) float CounterDistanceMeters=2.75f;
};
USTRUCT(BlueprintType) struct FDeliveryOrder {
 GENERATED_BODY()
 UPROPERTY(BlueprintReadWrite) FGuid ID;
 UPROPERTY(BlueprintReadWrite) FName StoreID;
 UPROPERTY(BlueprintReadWrite) bool Grocery=false;
 UPROPERTY(BlueprintReadWrite) int32 StoreKind=0;
 UPROPERTY(BlueprintReadWrite) int32 GoodsCost=0;
 UPROPERTY(BlueprintReadWrite) FVector Pickup=FVector::ZeroVector;
 UPROPERTY(BlueprintReadWrite) FVector Dropoff=FVector::ZeroVector;
 UPROPERTY(BlueprintReadWrite) FText PickupName;
 UPROPERTY(BlueprintReadWrite) FText DropoffName;
 UPROPERTY(BlueprintReadWrite) float DistanceMeters=0;
 UPROPERTY(BlueprintReadWrite) int32 Reward=0;
 UPROPERTY(BlueprintReadWrite) float ExpiresAt=0;
};
USTRUCT(BlueprintType) struct FActiveDelivery {
 GENERATED_BODY()
 UPROPERTY(BlueprintReadWrite) FDeliveryOrder Order;
 UPROPERTY(BlueprintReadWrite) EDeliveryState State=EDeliveryState::Pickup;
 UPROPERTY(BlueprintReadWrite) int32 BasketCount=0;
 UPROPERTY(BlueprintReadWrite) bool Paid=false;
 UPROPERTY(BlueprintReadWrite) int32 Budget=0;
 UPROPERTY(BlueprintReadWrite) int32 GoodsPaid=0;
};
USTRUCT(BlueprintType) struct FDeliveryVehicleSpec:public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FText Title;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FText Description;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) bool Motorcycle=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 Price=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName Prerequisite;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 ModelIndex=0;
};
UCLASS(BlueprintType) class BOGOTAVOXEL_API UDeliverySave:public USaveGame {
 GENERATED_BODY()
public:
 UPROPERTY(SaveGame,BlueprintReadWrite) int32 Version=1;
 UPROPERTY(SaveGame,BlueprintReadWrite) int32 Balance=0;
 UPROPERTY(SaveGame,BlueprintReadWrite) TArray<FName> Purchased;
 UPROPERTY(SaveGame,BlueprintReadWrite) EDeliveryVehicle Vehicle=EDeliveryVehicle::Bicycle;
 UPROPERTY(SaveGame,BlueprintReadWrite) int32 BikeColor=0;
 UPROPERTY(SaveGame,BlueprintReadWrite) int32 MotoColor=0;
 UPROPERTY(SaveGame,BlueprintReadWrite) TArray<FName> OwnedModels;
 UPROPERTY(SaveGame,BlueprintReadWrite) FName BikeModel=TEXT("BikeCity");
 UPROPERTY(SaveGame,BlueprintReadWrite) FName MotoModel=TEXT("MotoStreet");
 UPROPERTY(SaveGame,BlueprintReadWrite) TMap<FName,int32> ModelColors;
};
UINTERFACE(BlueprintType) class BOGOTAVOXEL_API UDeliveryInteractable:public UInterface { GENERATED_BODY() };
class BOGOTAVOXEL_API IDeliveryInteractable {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable) bool CanDeliver(AActor* Rider,FGuid OrderID) const;
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable) void ReceiveDelivery(AActor* Rider,FGuid OrderID);
};
class UDeliveryComponent;
UCLASS(Blueprintable) class BOGOTAVOXEL_API ADeliveryPoint:public AActor {
 GENERATED_BODY()
public:
 ADeliveryPoint();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Customers") void UpdateCustomer(int32 Index,float Dt);
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Customers") TArray<TObjectPtr<class USkeletalMeshComponent>> WalkingCustomers;
 UPROPERTY() TArray<TObjectPtr<class UAnimSequence>> CustomerWalkClips;
 UPROPERTY() TArray<TObjectPtr<class UAnimSequence>> CustomerIdleClips;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Customers") TArray<int32> CustomerStops;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Customers") TArray<float> CustomerWaits;
 void UpdateCrowdCustomer(int32 Index,float Dt);
 UPROPERTY() TArray<FVector> CustomerPathStart;
 UPROPERTY() TArray<FVector> CustomerPathEnd;
 UPROPERTY() TArray<float> CustomerSpeeds;
 UPROPERTY() TArray<bool> CustomerUsesCane;
 UPROPERTY(BlueprintReadWrite) bool Grocery=false;
 UPROPERTY(BlueprintReadWrite) int32 StoreKind=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Theme") FName ThemeID;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Theme") TArray<FText> ThemeProductNames;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Theme") int32 PurchaseBudget=22000;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Theme") float HalfWidth=1000;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Theme") float HalfDepth=800;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Theme") float CounterDistanceMeters=2.75f;
 UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> StoreProducts;
 FGuid DisplayedOrder;
 void PresentOrder(FGuid OrderID,int32 Collected);
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="Delivery|Shop") FVector InteriorPosition(FVector Local) const;
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="Delivery|Shop") bool ContainsVisitor(FVector Position) const;
 UFUNCTION(BlueprintPure,Category="Delivery|Shop") FVector ProductPosition(int32 Index) const;
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="Delivery|Shop") FVector CheckoutPosition() const;
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="Delivery|Shop") int32 ItemCount() const;
 FString ItemName(int32 Index) const;
 void BuildStore();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery") FName PointID;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery") FText PlaceName;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) class UStaticMeshComponent* Sign;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) class UTextRenderComponent* Label;
};
UCLASS(Blueprintable) class BOGOTAVOXEL_API ADeliveryRecipient:public AActor,public IDeliveryInteractable {
 GENERATED_BODY()
public:
 ADeliveryRecipient();
 UFUNCTION(BlueprintCallable,Category="Delivery|Art") void InitializeAppearance(FName AppearanceRole);
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) class USkeletalMeshComponent* VoxelMesh;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) class UStaticMeshComponent* Marker;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) class UTextRenderComponent* Label;
 UPROPERTY(BlueprintReadWrite) FGuid OrderID;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") UDeliveryComponent* Delivery=nullptr;


};
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FDeliveryChanged);
UCLASS(Blueprintable,ClassGroup=(Delivery),meta=(BlueprintSpawnableComponent)) class BOGOTAVOXEL_API UDeliveryComponent:public UActorComponent {
 GENERATED_BODY()
public:
 UDeliveryComponent();
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 virtual void TickComponent(float Dt,ELevelTick Tick,FActorComponentTickFunction* Fn) override;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Balance") float OfferInterval=12;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Balance") float OfferLifetime=30;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Balance") float HoldDuration=2;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Balance") float InteractionRadius=250;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Balance") float BikeBaseSpeed=1100;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Balance") float BikeBoostSpeed=1450;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Balance") float MotoBoostSpeed=2200;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Balance") TObjectPtr<UDataTable> Upgrades;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery") TSubclassOf<ADeliveryRecipient> RecipientClass;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery") TSubclassOf<UUserWidget> PhoneClass;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") EDeliveryState State=EDeliveryState::Idle;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") FDeliveryOrder Order;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") TArray<FDeliveryOrder> Offers;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") TArray<FActiveDelivery> ActiveOrders;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") FGuid SelectedOffer;
 UFUNCTION(BlueprintImplementableEvent,BlueprintPure) int32 CargoCapacity(bool Motorcycle) const;
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable) bool SelectActiveOrder(int32 Index);
 const FDeliveryOrder* SelectedIncoming() const;
 UFUNCTION(BlueprintPure,Category="Delivery|Data") FDeliveryOrder GetSelectedOffer(bool& Found) const;
 UFUNCTION(BlueprintPure,Category="Delivery|Data") FDeliveryOrder FindOffer(FGuid ID,int32& Index) const;
 UFUNCTION(BlueprintPure,Category="Delivery|Data") int32 FindActiveOrderIndex(FGuid ID) const;
 UFUNCTION(BlueprintPure,Category="Delivery|Platform") class ABogotaPlayer* GetRider() const;

 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery|Orders") void StoreFocusedOrder();
 UFUNCTION(BlueprintCallable,Category="Delivery|Platform") void RestoreOrderMarkers();
 UPROPERTY(BlueprintReadWrite,Category="Delivery") int32 BikeColor=0;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") int32 MotoColor=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery") TObjectPtr<UDataTable> VehicleCatalog;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") TArray<FName> OwnedModels;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") FName BikeModel=TEXT("BikeCity");
 UPROPERTY(BlueprintReadWrite,Category="Delivery") FName MotoModel=TEXT("MotoStreet");
 UPROPERTY(BlueprintReadWrite,Category="Delivery") TMap<FName,int32> ModelColors;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") int32 Balance=0;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") TArray<FName> Purchased;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") EDeliveryVehicle Vehicle=EDeliveryVehicle::Bicycle;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") float Energy=100;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") float Capacity=100;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") float HoldProgress=0;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") bool BoostActive=false;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") bool InfiniteBoost=false;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") bool PhoneOpen=false;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") bool HasWaypoint=false;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") FVector Waypoint=FVector::ZeroVector;
 UPROPERTY(BlueprintReadWrite,Category="Delivery") FText StatusMessage;
 UPROPERTY(BlueprintAssignable) FDeliveryChanged OnChanged;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") void GenerateOffer();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") void CullExpiredOffers();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Lifecycle") void InitializeGameplay();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Orders") void EnterIdle();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Lifecycle") void UpdateMarketplace(float Dt);
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Lifecycle") float MarketRefreshRemaining=0;
 UFUNCTION(BlueprintPure,Category="Delivery|Map") TArray<FDeliveryOrder> GetAvailableResidentialRoutes() const;
 UFUNCTION(BlueprintPure,Category="Delivery|Orders") bool RouteAlreadyOffered(FVector Pickup,FVector Dropoff) const;
 UPROPERTY(Transient,BlueprintReadWrite,Category="Delivery|Orders") TArray<FDeliveryOrder> CandidateRoutes;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") bool SelectOffer(int32 Index);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") bool PaintVehicle(bool Motorcycle,int32 Color);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") bool BuyVehicle(FName ID);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") bool EquipVehicle(FName ID);
 UFUNCTION(BlueprintImplementableEvent,BlueprintPure,Category="Delivery") bool OwnsVehicle(FName ID) const;
 UFUNCTION(BlueprintImplementableEvent,BlueprintPure,Category="Delivery") int32 VisualStage(bool Motorcycle) const;
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery") bool AcceptOffer(FGuid ExpectedID);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") void IgnoreOffer();
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery") void BeginAction(bool PickupButton=false);
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery|Boost") void UpdateBoost(float Dt);
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery|Interaction") void AdvanceHeldAction();
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery") void EndAction();
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery") bool CollectOrder(FGuid ExpectedID);
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery") bool CompleteOrder(FGuid ExpectedID);
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery") bool PurchaseUpgrade(FName ID);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") bool SwitchVehicle();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") void TogglePhone();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") void SetWaypoint(FVector Location);
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery") void ClearWaypoint();
 TArray<FVector> NavigationRoute() const;
 FString NavigationInstruction() const;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") bool SaveProfile();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") void LoadProfile();
 UFUNCTION(BlueprintPure,Category="Delivery|Data") FString ProfileSlot() const;
 UFUNCTION(BlueprintPure,Category="Delivery|Data") FDeliveryVehicleSpec GetVehicleSpec(FName ID,bool& Found)const;
 UFUNCTION(BlueprintPure,Category="Delivery|Data") int32 GetModelColor(FName ID)const;
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery") void RebuildStats();
 UFUNCTION(BlueprintImplementableEvent,BlueprintPure,Category="Delivery") float GetTopSpeed() const;
 UFUNCTION(BlueprintPure,Category="Delivery") float OfferSecondsLeft() const;
 UFUNCTION(BlueprintPure,Category="Delivery") bool IsAtTarget() const;
 UFUNCTION(BlueprintPure,Category="Delivery") FVector GetOrderTarget() const;
 UFUNCTION(BlueprintImplementableEvent,BlueprintPure,Category="Delivery") bool Owns(FName ID) const;
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Delivery|Economy") int32 RewardForDistance(float Meters,float Multiplier);
 UFUNCTION(BlueprintPure,Category="Delivery") static int32 CalculatePay(float Meters,float Multiplier=1);
 UPROPERTY(BlueprintReadWrite,Category="Delivery") TObjectPtr<ADeliveryRecipient> Recipient;
 UPROPERTY() TObjectPtr<AActor> PickupMarker;
 UPROPERTY(BlueprintReadWrite) TObjectPtr<UUserWidget> PhoneWidget;
 UPROPERTY() TObjectPtr<class ASceneCapture2D> CityMapActor;
 UPROPERTY() TObjectPtr<class UTextureRenderTarget2D> CityMapTexture;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Developer") bool DeveloperMode=false;
 UFUNCTION(BlueprintCallable,Category="Delivery|Developer") void ToggleDeveloperMode();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Developer") void DeveloperKey(FKey Key);
 UPROPERTY(BlueprintReadWrite) TObjectPtr<ADeliveryPoint> InsideStore;
 UPROPERTY(BlueprintReadWrite) int32 BasketCount=0;
 UPROPERTY(BlueprintReadWrite) bool OrderPaid=false;
 UPROPERTY(BlueprintReadWrite) int32 OrderBudget=0;
 UPROPERTY(BlueprintReadWrite) int32 GoodsPaid=0;
 UFUNCTION(BlueprintPure,Category="Delivery|Shop") ADeliveryPoint* OrderStore() const;
 UFUNCTION(BlueprintCallable,Category="Delivery|Interaction") bool StoreDoorAction();
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="Delivery|Shop") bool ShopReady() const;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Shop") bool ShopCollect();
 UFUNCTION(BlueprintPure,Category="Delivery|Shop") FString ShoppingInstruction() const;
 UFUNCTION(BlueprintCallable,Category="Delivery|Art") void HideStoreProduct(int32 Index);
 UFUNCTION(BlueprintCallable,Category="Delivery|Platform") bool SpawnOrderRecipient();
 UFUNCTION(BlueprintCallable,Category="Delivery|Platform") void RemovePickupMarker();
 UFUNCTION(BlueprintPure,Category="Delivery|Data") FDeliveryUpgrade GetUpgradeSpec(FName ID,bool& Found) const;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery") void ExitStore();
 void PrepareCityMap();
 bool IsValidation() const {return bValidation;}
private:
 UPROPERTY() TObjectPtr<UDeliverySave> DeveloperBackup;
 UPROPERTY(Transient,BlueprintReadWrite,meta=(AllowPrivateAccess="true")) FString DeveloperSequence;
 UPROPERTY(Transient,BlueprintReadWrite,meta=(AllowPrivateAccess="true")) double DeveloperLastKey=0;
 UPROPERTY(BlueprintReadWrite,Category="Delivery",meta=(AllowPrivateAccess="true")) bool bHolding=false;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) bool bPickupButton=false;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) bool bExhausted=false;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) bool bHadBoost=false;
 UPROPERTY(BlueprintReadOnly,meta=(AllowPrivateAccess="true")) bool bValidation=false;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) float HoldStart=0;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) float RegenDelayRemaining=0;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Boost",meta=(AllowPrivateAccess="true")) float Drain=20;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Boost",meta=(AllowPrivateAccess="true")) float Regen=15;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) FGuid HeldOrder;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) EDeliveryState HeldState=EDeliveryState::Idle;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) float BikeEnergy=100;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) float MotoEnergy=100;
 float ValidationTime=0;
 int32 ValidationStage=0;
 int32 ArtPreparedStage=-1;
 TArray<FString> ValidationErrors;
 void ExpireOffer();


 void UpdateValidation(float Dt);
 void UpdateUsabilityValidation(float Dt);
 void HandleInputSuspended();
 UFUNCTION(BlueprintCallable,Category="Delivery|Platform") void DestroyMarkers();
 UFUNCTION(BlueprintCallable,Category="Delivery|Events") void Changed();
};

class UCanvasPanel;
class UBorder;
class UTextBlock;
class UProgressBar;
class UWidget;
class UButton;
class UDeliveryPhoneWidget;
UCLASS() class BOGOTAVOXEL_API ADeliveryVehiclePreview:public AActor {
 GENERATED_BODY()
public:
 ADeliveryVehiclePreview();
 UPROPERTY() class UStaticMeshComponent* Body=nullptr;
 UPROPERTY() class UStaticMeshComponent* WheelA=nullptr;
 UPROPERTY() class UStaticMeshComponent* WheelB=nullptr;
 UPROPERTY() class USceneCaptureComponent2D* Capture=nullptr;
 UPROPERTY() class UTextureRenderTarget2D* Target=nullptr;
 void ShowVehicle(const FString& MeshName,int32 Color);
 FString LastKey;
};
UCLASS() class BOGOTAVOXEL_API UDeliveryChoiceButton:public UButton {
 GENERATED_BODY()
public:
 UPROPERTY() UDeliveryPhoneWidget* Phone=nullptr;
 int32 Choice=0;
 UFUNCTION() void Choose();
};
UCLASS(Blueprintable) class BOGOTAVOXEL_API UDeliveryMapWidget:public UUserWidget {
 GENERATED_BODY()
public:
 UPROPERTY(BlueprintReadWrite) UDeliveryComponent* Delivery=nullptr;
 UPROPERTY(BlueprintReadWrite) bool FullMap=false;
 UPROPERTY(BlueprintReadWrite) FVector2D MapCursor=FVector2D(.5,.5);
 virtual int32 NativePaint(const FPaintArgs& Args,const FGeometry& Geometry,const FSlateRect& Culling,FSlateWindowElementList& Elements,int32 Layer,const FWidgetStyle& Style,bool Enabled) const override;
 virtual FReply NativeOnMouseButtonDown(const FGeometry& Geometry,const FPointerEvent& Event) override;
};
UCLASS(Blueprintable) class BOGOTAVOXEL_API UDeliveryPhoneWidget:public UUserWidget {
 GENERATED_BODY()
public:
 friend class UDeliveryComponent;
 UPROPERTY(BlueprintReadWrite) UDeliveryComponent* Delivery=nullptr;
 virtual void NativeConstruct() override;
 // Editor-only template creation skips dynamic app contents.
 bool AuthoringPhoneTemplate=false;
 void AuthorAppLayouts();
 virtual TSharedRef<SWidget> RebuildWidget() override;
 virtual void NativeTick(const FGeometry& Geometry,float Dt) override;
 virtual FReply NativeOnPreviewKeyDown(const FGeometry& Geometry,const FKeyEvent& Event) override;
 virtual FReply NativeOnKeyUp(const FGeometry& Geometry,const FKeyEvent& Event) override;
 virtual void NativeDestruct() override;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void OpenHome();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void OpenMap();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void OpenOrders();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void OpenShop();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void AcceptPressed();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void AcceptReleased();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void IgnorePressed();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void BuySelected();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void SelectPrevious();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void SelectNext();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void ClearPoint();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void SwitchPressed();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void ClosePressed();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void GarageBike();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void GarageMoto();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void NextColor();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void PaintSelected();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void OpenCatalog();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void OpenActiveOrders();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void OpenCargo();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void BuyModel();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void EquipModel();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Phone") void SelectEntry(int32 Index);
private:
 UPROPERTY() UCanvasPanel* Root=nullptr;
 UPROPERTY() UBorder* PhoneShade=nullptr;
 UPROPERTY() TArray<TObjectPtr<class UTexture2D>> PhoneTextures;
 UPROPERTY() UBorder* Frame=nullptr;
 UPROPERTY() UCanvasPanel* Screen=nullptr;
 UPROPERTY() UDeliveryMapWidget* MiniMap=nullptr;
 UPROPERTY() UDeliveryMapWidget* MainMap=nullptr;
 UPROPERTY() UTextBlock* Header=nullptr;
 UPROPERTY() UTextBlock* Details=nullptr;
 UPROPERTY() UTextBlock* Notice=nullptr;
 UPROPERTY() UTextBlock* PhoneHints=nullptr;
 UPROPERTY() UTextBlock* EnergyText=nullptr;
 UPROPERTY() UProgressBar* EnergyBar=nullptr;
 UPROPERTY() UProgressBar* HoldBar=nullptr;
 UPROPERTY() UButton* AcceptButton=nullptr;
 UPROPERTY() class UImage* PhoneArt=nullptr;
 UPROPERTY() class UImage* PreviewArt=nullptr;
 UPROPERTY() TArray<UDeliveryChoiceButton*> Choices;
 UPROPERTY() UButton* ModelBuyButton=nullptr;
 UPROPERTY() UButton* ModelEquipButton=nullptr;
 UPROPERTY() UTextBlock* PageTitle=nullptr;
 UPROPERTY() UTextBlock* SelectionTitle=nullptr;
 UPROPERTY() ADeliveryVehiclePreview* VehiclePreview=nullptr;
 UPROPERTY() TArray<UWidget*> AppControls;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) TArray<FName> UpgradeIDs;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) int32 Page=0;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) int32 Selection=0;
 float OpenAlpha=0;
 bool LastOpen=false;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) bool PreviewMoto=false;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) int32 PaintSelection=0;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) int32 OrderSelection=0;
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) int32 CatalogSelection=0;
 int32 LayoutIndex=0;
 bool BuildingLayout=false;
 void ApplyVoxelTheme();
 FName NextLayoutName();
 UPROPERTY(BlueprintReadWrite,meta=(AllowPrivateAccess="true")) TArray<FName> ModelIDs;
 UDeliveryChoiceButton* AddChoice(const FString& Text,int32 Index,FVector2D Pos,FVector2D Size);
 class UImage* AddArt(const FString& Name,FVector2D Pos,FVector2D Size);
 UButton* AddButton(const FString& Text,FVector2D Pos,FVector2D Size);
 UTextBlock* AddText(const FString& Text,FVector2D Pos,FVector2D Size,int32 FontSize);
public:
 UFUNCTION(BlueprintCallable,Category="Delivery|Phone") void BuildPage(int32 NewPage);
 UFUNCTION(BlueprintCallable,Category="Delivery|Phone") void RefreshText();
};



