#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "Subsystems/WorldSubsystem.h"
#include "Components/SlateWrapperTypes.h"
#include "BogotaAudio.generated.h"

class UUserWidget;

class UAudioComponent;
class UFMODAudioComponent;
class USkeletalMeshComponent;
class ACharacter;
class UPrimitiveComponent;
class USoundWave;

UCLASS()
class UBogotaAudioLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="Bogota|Audio")
    static void PlayReaction(AActor* Speaker, int32 Reaction);
    static void PlayRobberyFootstep(AActor& Walker);

    UFUNCTION(BlueprintCallable, Category="Bogota|Audio", meta=(WorldContext="WorldContext"))
    static void PlayMissionFinish(const UObject* WorldContext);
};

UCLASS()
class UBogotaAudioSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;
    virtual bool IsTickableWhenPaused() const override { return true; }
    virtual void OnWorldBeginPlay(UWorld& World) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    struct FTrafficSource
    {
        TWeakObjectPtr<UAudioComponent> Loop;
        TWeakObjectPtr<UFMODAudioComponent> FmodLoop;
        TWeakObjectPtr<UAudioComponent> Tires;
        FVector LastPosition = FVector::ZeroVector;
        float Speed = 0.f;
        float PreviousSpeed = 0.f;
        float NextHorn = 0.f;
        float QueuedTime = 0.f;
        float NextDetail = 0.f;
        float NextOcclusion = 0.f;
        float OcclusionGain = 1.f;
        float SmoothedGain = 0.f;
        bool AtStop = false;
        bool DoorsOpen = false;
        bool Closing = false;
    };

    USoundWave* Clip(FName Name) const;
    void UpdateTraffic(UWorld& World, const FVector& Listener, float DeltaTime, bool ManualHorn);
    void UpdatePedestrianSteps(UWorld& World, const FVector& Listener, float DeltaTime);
    void UpdateConversation(UWorld& World, const FVector& Listener);
    void UpdateAtmosphere(AActor& Listener, float DeltaTime, float RainAmount, float NightWeight, float ParkWeight);
    void UpdateDelivery(UWorld& World, UObject* Delivery, const FVector& Listener);
    void UpdateWorldFoley(APawn& Pawn, UObject* Delivery, float Dt, float RainAmount,
        float NightWeight, const FVector* ParkPoint, float ParkDistance, float VehicleSpeed, bool Mounted);

    UPROPERTY() TObjectPtr<UAudioComponent> Ride;
    UPROPERTY() TObjectPtr<UAudioComponent> Freewheel;
    UPROPERTY() TObjectPtr<UAudioComponent> Chain;
    UPROPERTY() TObjectPtr<UAudioComponent> Skid;
    UPROPERTY() TObjectPtr<UAudioComponent> Interior;
    UPROPERTY() TObjectPtr<UAudioComponent> Station;
    UPROPERTY() TObjectPtr<UAudioComponent> CanopyRain;
    UPROPERTY() TObjectPtr<UAudioComponent> WetWheels;
    UPROPERTY() TObjectPtr<UAudioComponent> Drain;
    TWeakObjectPtr<UFMODAudioComponent> FmodRide;
    struct FAtmosphereLayer
    {
        TWeakObjectPtr<UFMODAudioComponent> Loop;
        float Volume = 0.f;
    };
    TMap<FName, FAtmosphereLayer> Atmosphere;
    TWeakObjectPtr<USkeletalMeshComponent> ConversationReply;
    float NextConversation = 0.f;
    float ReplyTime = 0.f;
    UPROPERTY() TObjectPtr<UAudioComponent> Rain;
    UPROPERTY() TObjectPtr<UAudioComponent> Menu;
    UPROPERTY() TMap<FName, TObjectPtr<USoundWave>> Sounds;
    TWeakObjectPtr<AActor> Weather;
    TWeakObjectPtr<AActor> Graphics;
    TWeakObjectPtr<UClass> TwoWheelerClass;
    TWeakObjectPtr<UClass> TrafficClass;
    TWeakObjectPtr<UClass> ServiceClass;
    TMap<TWeakObjectPtr<AActor>, FTrafficSource> TrafficSources;
    TMap<TWeakObjectPtr<ACharacter>, float> PedestrianStepDistances;
    TArray<FVector> ParkPoints;
    TArray<FVector> StationPoints;
    TArray<TWeakObjectPtr<AActor>> StationActors;
    TArray<TWeakObjectPtr<AActor>> CrossingSignals;
    TArray<TWeakObjectPtr<AActor>> LandmarkBells;
    TArray<TWeakObjectPtr<AActor>> LocalEmitters;
    TWeakObjectPtr<UPrimitiveComponent> WheelContact;
    TWeakObjectPtr<AActor> FoleyShop;
    TWeakObjectPtr<AActor> AnnouncedPlatform;
    TMap<TWeakObjectPtr<AActor>, bool> PlatformDoorsOpen;
    TWeakObjectPtr<AActor> GreetedRecipient;
    TWeakObjectPtr<AActor> StyledRecipient;
    FGuid StyledOrder;
    FGuid LastPhoneSelection;
    TMap<FGuid, FName> RecipientRoles;
    int32 NextRecipient = 0;
    TWeakObjectPtr<AActor> LastShop;
    TWeakObjectPtr<UObject> LastDelivery;
    TWeakObjectPtr<APawn> PreviousPawn;
    FVector PreviousLocation = FVector::ZeroVector;
    FText LastShopStatus;
    int32 LastBasket = 0;
    int32 LastDeliveryState = 0;
    float NextShopVoice = 0.f;
    float NextHorn = 0.f;
    float TrafficUpdateAge = 0.f;
    float UpdateRemaining = 0.f;
    float RideSpeed = 0.f;
    float StepDistance = 0.f;
    float NextParkDetail = 0.f;
    float NextParkBird = 0.f;
    float NextEffort = 0.f;
    float NextWheelDetail = 0.f;
    float NextLocalDetail = 0.f;
    float SpeechUntil = 0.f;
    float NextCrossingCue = 0.f;
    float NextLandmarkBell = 0.f;
    float NextStationVoice = 0.f;
    float PreviousVerticalSpeed = 0.f;
    double LastRealTime = 0.;
    bool WasMounted = false;
    bool WasBraking = false;
    bool WasInCabin = false;
    bool WasPhoneOpen = false;
    bool WasOnGround = false;
    bool PlayedBoostCue = false;
    bool PendingHorn = false;
    bool bBellWasDown = false;
    uint32 LastDriftBoostCount = 0;
    TWeakObjectPtr<UUserWidget> HiddenPhone;
    ESlateVisibility PreviousPhoneVisibility = ESlateVisibility::Visible;
    bool Ready = false;
};
