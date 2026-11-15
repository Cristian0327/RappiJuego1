#pragma once

#include "Subsystems/WorldSubsystem.h"
#include "Styling/SlateBrush.h"
#include "BogotaRobbery.generated.h"

class APlayerController;
class ASkeletalMeshActor;
class UAudioComponent;
class UPrimitiveComponent;
class UCharacterMovementComponent;
class UGameViewportClient;
class UNativeWidgetHost;
class SWidget;
class UAnimSequence;
class FReply;
class STextBlock;
class SImage;
struct FSlateBrush;
struct FCollisionQueryParams;
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FBogotaRobberyResolved, bool, bRayas, bool, bEscaped);

UCLASS()
class UBogotaRobbery : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;
    virtual TStatId GetStatId() const override;
    virtual void Tick(float DeltaTime) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category="Bogota|Robbery")
    bool StartEncounter(bool bRayas);

    UPROPERTY(BlueprintAssignable, Category="Bogota|Robbery")
    FBogotaRobberyResolved OnEncounterResolved;

    UFUNCTION(BlueprintPure, Category="Bogota|Robbery")
    static int32 CalculateBalanceLoss(int32 Balance);

    UFUNCTION(BlueprintPure, Category="Bogota|Robbery")
    int32 ServiceRescueQuote() const;

    UFUNCTION(BlueprintPure, Category="Bogota|Robbery")
    bool IsRobberyPromptActive() const;

    UFUNCTION(BlueprintCallable, Category="Bogota|Robbery")
    void PayServiceRescue();

    void ObservePickup(UObject* Delivery, bool bCheckedOut, bool bOutside, double Hour);

    void StartPreview(const FString& Variant);
    void CancelPreview();

private:
    enum class EPhase : uint8 { Approach, Prompt, Retreat, ForcedDismount, VehicleApproach, VehicleMount, VehicleEscape };
    bool SpawnEncounter(bool bRayas);
    void AdvancePrompt();
    void ReadDeveloperCode();
    FString DeveloperCode;
    double LastDeveloperKey = 0.;
    bool ShowPromptIcon(APlayerController* Controller);
    TSharedPtr<SImage> PromptIcon;
    TSharedPtr<FSlateBrush> PromptBrush;
    FSlateBrush EncounterPanel;
    int32 PromptArt = INDEX_NONE;
    void Show(const FString& Message);

    TWeakObjectPtr<UGameViewportClient> OverlayViewport;
    TSharedPtr<SWidget> Overlay;
    TSharedPtr<STextBlock> PromptText;
    void FinishPrompt(bool bEscaped);
    void PlayClip(const TCHAR* Clip, bool bLoop);
    void PlayRobberySound(ASkeletalMeshActor& Actor);
    TWeakObjectPtr<UAudioComponent> RobberyVoice;

    bool BeginVehicleEscape();
    void TickVehicleEscape(float DeltaTime);
    void StartRetreat();
    bool CanStealVehicle(const UObject* Delivery) const;
    void PlanEscape(APlayerController& Controller, const FVector& Start, const FCollisionQueryParams& Params);
    FVector AdvanceEscape(APlayerController& Controller, const FVector& Current, double Speed,
        float DeltaTime, const FCollisionQueryParams& Params);
    bool CanFinishEscape(APlayerController& Controller, AActor& Actor, AActor* Vehicle,
        float DeltaTime, const FCollisionQueryParams& Params);
    bool TrackGrabPosition(float DeltaTime);
    void UpdateRescuePanel();
    void RemoveRescuePanel();
    FReply PayRescue();
    UAnimSequence* FindClip(const TCHAR* Clip) const;

    TWeakObjectPtr<AActor> RetainedVehicle;
    TWeakObjectPtr<UObject> RescueDelivery;
    TWeakObjectPtr<UNativeWidgetHost> RescueTile;
    UPROPERTY(Transient)
    TObjectPtr<UAnimSequence> VehicleMountClip;
    UPROPERTY(Transient)
    TObjectPtr<UAnimSequence> VehicleRideClip;
    TWeakObjectPtr<UNativeWidgetHost> RescuePage;
    FText RescueStatus;
    FVector RescuePoint = FVector::ZeroVector;
    FVector MountFrom = FVector::ZeroVector;
    FVector MountTo = FVector::ZeroVector;
    FRotator RescueHeading = FRotator::ZeroRotator;
    float MountSeconds = 0.f;
    int32 RescueCost = 0;
    bool bRescuePaid = false;
    bool bVehicleWasHidden = false;
    bool bVehicleHadCollision = false;


    TWeakObjectPtr<UObject> PickupCandidate;
    TWeakObjectPtr<UObject> EncounterDelivery;
    int32 ProtectedPickups = 0;
    double PickupExpires = 0.;
    double LastStreetObservation = -1.;
    bool bDismountRequested = false;
    float RetreatElapsed = 0.f;
    float ActivePlaySeconds = 0.f;
    TArray<FVector> EscapeRoute;
    TWeakObjectPtr<UPrimitiveComponent> EscapeBuilding;
    int32 EscapeInstance = INDEX_NONE;
    int32 EscapeWaypoint = 0;
    float EscapeReplanTime = 0.f;
    float FootstepTime = 0.f;
    float OutOfSightTime = 0.f;
    bool bMovementLocked = false;
    TWeakObjectPtr<UCharacterMovementComponent> FrozenWalkingMovement;
    uint8 PreviousMovementMode = 0;
    bool bPreviousWaypoint = false;
    FVector PreviousWaypoint = FVector::ZeroVector;
    TWeakObjectPtr<class UInputComponent> MountInputGuard;
    void LockMovement(APlayerController& Controller);
    void ReleaseMovement();

    TWeakObjectPtr<ASkeletalMeshActor> Thief;
    TWeakObjectPtr<APawn> Player;
    bool bRayasEncounter = false;
    const TCHAR* GetCharacterName() const { return bRayasEncounter ? TEXT("Rayas") : TEXT("Hornets"); }
    FVector Origin = FVector::ZeroVector;
    EPhase Phase = EPhase::Approach;
    float TimeLeft = 0.f;
    bool bGameplayEncounter = false;

    int32 Step = 0;
    int32 Errors = 0;
    int32 Prompt = INDEX_NONE;
};

