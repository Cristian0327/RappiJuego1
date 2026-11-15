#pragma once

#include "Subsystems/WorldSubsystem.h"
#include "BogotaTwoWheelHandling.generated.h"

class ACharacter;
class UCharacterMovementComponent;
class USceneComponent;
class UPointLightComponent;
class UStaticMesh;
class UStaticMeshComponent;
class UPoseableMeshComponent;
enum class EVisibilityBasedAnimTickOption : uint8;

UCLASS()
class UBogotaTwoWheelHandling : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;
    virtual void Deinitialize() override;
    virtual void OnWorldBeginPlay(UWorld& World) override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

    UFUNCTION(BlueprintPure, Category="Bogota|Vehicle")
    bool IsDrifting() const;
    uint32 GetDriftBoostCount() const { return DriftBoostCount; }
    int32 GetDriftTier() const;

    UFUNCTION(BlueprintPure, Category="Bogota|Movement")
    float GetFootStamina() const { return FootStamina; }

private:
    UFUNCTION()
    void OnMovement(float DeltaTime, FVector OldLocation, FVector OldVelocity);

    void ClearDrift();
    void RestorePose(UWorld* World, ELevelTick TickType, float DeltaTime);
    void UpdatePose(UWorld* World, ELevelTick TickType, float DeltaTime);
    void UpdateVehicleSteering(ACharacter& Character, bool Mounted, bool Motorcycle);
    void ClearVehicleSteering();
    void UpdateRiderPose(ACharacter& Character, const FVector& Inside, float Alpha, bool Motorcycle);
    void ClearDriftLeg();
    void UpdateFootStamina(ACharacter& Character, const UCharacterMovementComponent& Movement, float DeltaTime);

    TWeakObjectPtr<ACharacter> Rider;
    FVector DriftDirection = FVector::ZeroVector;
    float DriftSide = 1.f;
    float DriftCharge = 0.f;
    uint32 DriftBoostCount = 0;
    float BoostRemaining = 0.f;
    float BoostSpeed = 0.f;
    float Lean = 0.f;
    float SlideYaw = 0.f;
    float PedalSway = 0.f;
    float PedalPhase = 0.f;
    float FrontSteer = 0.f;
    float MouseSteer = 0.f;
    float PreviousLookYaw = 0.f;
    float WeightShift = 0.f;
    float HopAge = 0.f;
    float DriftPoseAlpha = 0.f;
    bool bWaitForRelease = false;
    bool bTrackingLook = false;
    TMap<TWeakObjectPtr<USceneComponent>, FTransform> RestPose;
    TWeakObjectPtr<UPointLightComponent> TireGlow;
    TWeakObjectPtr<UStaticMeshComponent> OriginalBike;
    TWeakObjectPtr<UStaticMeshComponent> SplitFrame;
    TWeakObjectPtr<UStaticMeshComponent> SplitSteering;
    TWeakObjectPtr<UStaticMesh> OriginalBikeModel;
    TWeakObjectPtr<UPoseableMeshComponent> DriftRiderMesh;
    EVisibilityBasedAnimTickOption PreviousRiderTickOption{};
    bool bPreviousRiderVisibility = true;
    float FootStamina = 100.f;
    float RecoveryDelay = 0.f;
    bool bExhausted = false;
    bool bDrifting = false;
};
