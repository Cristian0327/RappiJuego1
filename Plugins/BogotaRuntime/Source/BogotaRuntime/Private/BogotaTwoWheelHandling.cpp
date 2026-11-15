#include "BogotaTwoWheelHandling.h"

#include "Components/LineBatchComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogBogotaHandling, Log, All);

namespace
{
bool DriftHeld(const APlayerController* Controller)
{
    return Controller && Controller->IsInputKeyDown(EKeys::SpaceBar);
}

bool IsSet(const UObject* Object, FName Name)
{
    if (!Object) return false;
    const auto* Property = FindFProperty<FBoolProperty>(Object->GetClass(), Name);
    return Property && Property->GetPropertyValue_InContainer(Object);
}

const UObject* DeliveryOf(const ACharacter& Character)
{
    const auto* Property = FindFProperty<FObjectPropertyBase>(Character.GetClass(), TEXT("Delivery"));
    return Property ? Property->GetObjectPropertyValue_InContainer(&Character) : nullptr;
}

float RiderAxis(const ACharacter& Character, FName Name)
{
    const auto* Property = FindFProperty<FNumericProperty>(Character.GetClass(), Name);
    if (!Property || !Property->IsFloatingPoint()) return 0.f;
    return static_cast<float>(Property->GetFloatingPointPropertyValue(Property->ContainerPtrToValuePtr<void>(&Character)));
}

bool IsMotorcycle(const ACharacter& Character)
{
    const UObject* Delivery = DeliveryOf(Character);
    const auto* Vehicle = Delivery ? FindFProperty<FByteProperty>(Delivery->GetClass(), TEXT("Vehicle")) : nullptr;
    return Vehicle && Vehicle->GetPropertyValue_InContainer(Delivery) == 1;
}

UStaticMeshComponent* MeshPart(ACharacter& Character, FName Name)
{
    const auto* Property = FindFProperty<FObjectPropertyBase>(Character.GetClass(), Name);
    return Property ? Cast<UStaticMeshComponent>(Property->GetObjectPropertyValue_InContainer(&Character)) : nullptr;
}

int32 DriftTier(float Charge)
{
    if (Charge >= 3.2f) return 3;
    if (Charge >= 1.75f) return 2;
    return Charge >= .65f ? 1 : 0;
}
}

bool UBogotaTwoWheelHandling::DoesSupportWorldType(EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

void UBogotaTwoWheelHandling::OnWorldBeginPlay(UWorld& World)
{
    Super::OnWorldBeginPlay(World);
    FWorldDelegates::OnWorldPreActorTick.AddUObject(this, &UBogotaTwoWheelHandling::RestorePose);
    FWorldDelegates::OnWorldPostActorTick.AddUObject(this, &UBogotaTwoWheelHandling::UpdatePose);
}

void UBogotaTwoWheelHandling::Deinitialize()
{
    RestorePose(GetWorld(), LEVELTICK_All, 0.f);
    ClearVehicleSteering();
    ClearDriftLeg();
    FWorldDelegates::OnWorldPreActorTick.RemoveAll(this);
    FWorldDelegates::OnWorldPostActorTick.RemoveAll(this);
    if (ACharacter* Character = Rider.Get())
        Character->OnCharacterMovementUpdated.RemoveDynamic(this, &UBogotaTwoWheelHandling::OnMovement);
    Rider.Reset();
    ClearDrift();
    Super::Deinitialize();
}

void UBogotaTwoWheelHandling::Tick(float DeltaTime)
{
    const APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    ACharacter* Character = Controller ? Cast<ACharacter>(Controller->GetPawn()) : nullptr;
    if (Character == Rider.Get()) return;
    if (ACharacter* Previous = Rider.Get())
        Previous->OnCharacterMovementUpdated.RemoveDynamic(this, &UBogotaTwoWheelHandling::OnMovement);
    ClearVehicleSteering();
    ClearDriftLeg();
    Rider = Character;
    if (auto* Light = TireGlow.Get()) Light->DestroyComponent();
    TireGlow.Reset();
    ClearDrift();
    BoostRemaining = Lean = SlideYaw = PedalSway = PedalPhase = FrontSteer = WeightShift = 0.f;
    bWaitForRelease = false;
    bTrackingLook = false;
    MouseSteer = 0.f;
    DriftPoseAlpha = 0.f;
    FootStamina = 100.f;
    RecoveryDelay = 0.f;
    bExhausted = false;
    if (Character)
        Character->OnCharacterMovementUpdated.AddUniqueDynamic(this, &UBogotaTwoWheelHandling::OnMovement);
}

void UBogotaTwoWheelHandling::ClearDrift()
{
    bDrifting = false;
    DriftCharge = 0.f;
    DriftDirection = FVector::ZeroVector;
}

int32 UBogotaTwoWheelHandling::GetDriftTier() const
{
    return IsDrifting() ? DriftTier(DriftCharge) : 0;
}

void UBogotaTwoWheelHandling::RestorePose(UWorld* World, ELevelTick TickType, float)
{
    if (World != GetWorld() || TickType != LEVELTICK_All) return;
    for (const auto& Pair : RestPose)
        if (auto* Part = Pair.Key.Get()) Part->SetRelativeTransform(Pair.Value);
    RestPose.Reset();
}

void UBogotaTwoWheelHandling::ClearVehicleSteering()
{
    if (auto* Part = SplitFrame.Get()) Part->DestroyComponent();
    if (auto* Part = SplitSteering.Get()) Part->DestroyComponent();
    if (auto* Part = OriginalBike.Get()) Part->SetVisibility(true);
    OriginalBike.Reset();
    OriginalBikeModel.Reset();
    SplitFrame.Reset();
    SplitSteering.Reset();
}

void UBogotaTwoWheelHandling::UpdateVehicleSteering(ACharacter& Character, bool Mounted, bool Motorcycle)
{
    auto* Source = Mounted ? MeshPart(Character, Motorcycle ? TEXT("MotoFrame") : TEXT("Bicycle")) : nullptr;
    UStaticMesh* Model = Source ? Source->GetStaticMesh() : nullptr;
    if (Source != OriginalBike.Get() || Model != OriginalBikeModel.Get())
    {
        ClearVehicleSteering();
        if (!Model) return;
        OriginalBike = Source;
        OriginalBikeModel = Model;
        const FString Base = Model->GetName();
        auto LoadPart = [&Base](const TCHAR* Suffix)
        {
            const FString Name = Base + Suffix;
            return LoadObject<UStaticMesh>(nullptr, *FString::Printf(TEXT("/Game/Delivery/Art/Steering/%s.%s"), *Name, *Name));
        };
        auto* FrameMesh = LoadPart(TEXT("_Frame"));
        auto* FrontMesh = LoadPart(TEXT("_Steering"));
        if (!FrameMesh || !FrontMesh) return;
        auto MakePart = [&Character, Source](UStaticMesh* Mesh, const TCHAR* Name)
        {
            auto* Part = NewObject<UStaticMeshComponent>(&Character, MakeUniqueObjectName(&Character,
                UStaticMeshComponent::StaticClass(), FName(Name)));
            Part->SetupAttachment(Source);
            Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Part->SetStaticMesh(Mesh);
            Part->RegisterComponent();
            return Part;
        };
        SplitFrame = MakePart(FrameMesh, TEXT("BogotaArticulatedFrame"));
        SplitSteering = MakePart(FrontMesh, TEXT("BogotaHandlebar"));
        UE_LOG(LogBogotaHandling, Display, TEXT("Articulated steering: %s"), *Base);
    }
    auto* Frame = SplitFrame.Get();
    auto* Front = SplitSteering.Get();
    if (!Frame || !Front || !Source) return;
    Source->SetVisibility(false);
    Frame->SetHiddenInGame(Source->bHiddenInGame);
    Front->SetHiddenInGame(Source->bHiddenInGame);
    for (auto* Part : {Frame, Front})
    {
        const auto& Slots = Part->GetStaticMesh()->GetStaticMaterials();
        for (int32 Index = 0; Index < Slots.Num(); ++Index)
        {
            const int32 OriginalIndex = Source->GetMaterialIndex(Slots[Index].MaterialSlotName);
            if (OriginalIndex != INDEX_NONE && Part->GetMaterial(Index) != Source->GetMaterial(OriginalIndex))
                Part->SetMaterial(Index, Source->GetMaterial(OriginalIndex));
        }
    }
    const FVector Head = Motorcycle ? FVector(50, 0, 98) : FVector(38, 0, 77);
    const FVector Axis = (Head - FVector(62, 0, 33)).GetSafeNormal();
    const FQuat Turn(Axis, FMath::DegreesToRadians(FrontSteer));
    Front->SetRelativeLocationAndRotation(Head - Turn.RotateVector(Head), Turn);
}

void UBogotaTwoWheelHandling::ClearDriftLeg()
{
    if (auto* Pose = DriftRiderMesh.Get())
    {
        if (auto* Source = Cast<USkeletalMeshComponent>(Pose->GetAttachParent()))
        {
            Source->SetVisibility(bPreviousRiderVisibility);
            Source->VisibilityBasedAnimTickOption = PreviousRiderTickOption;
        }
        Pose->DestroyComponent();
    }
    DriftRiderMesh.Reset();
}

void UBogotaTwoWheelHandling::UpdateRiderPose(ACharacter& Character, const FVector& Inside, float Alpha, bool Motorcycle)
{
    auto* Source = Character.GetMesh();
    if (!Source || !Source->GetSkinnedAsset())
    {
        ClearDriftLeg();
        return;
    }
    auto* Pose = DriftRiderMesh.Get();
    if (!Pose)
    {
        Pose = NewObject<UPoseableMeshComponent>(&Character);
        Pose->SetupAttachment(Source);
        Pose->SetSkinnedAssetAndUpdate(Source->GetSkinnedAsset());
        Pose->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Pose->SetVisibility(false);
        for (int32 Index = 0; Index < Source->GetNumMaterials(); ++Index)
            Pose->SetMaterial(Index, Source->GetMaterial(Index));
        Pose->RegisterComponent();
        DriftRiderMesh = Pose;
        bPreviousRiderVisibility = Source->IsVisible();
        PreviousRiderTickOption = Source->VisibilityBasedAnimTickOption;
        Source->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    }
    Pose->CopyPoseFromSkeletalComponent(Source);

    if (Alpha >= .025f)
    {
        const FName Left = TEXT("foot_l");
        const FName Right = TEXT("foot_r");
        const bool UseLeft = FVector::DotProduct(Source->GetSocketLocation(Left) -
            Source->GetSocketLocation(Right), Inside) > 0.;
        const FName Thigh = UseLeft ? TEXT("thigh_l") : TEXT("thigh_r");
        const FName Calf = UseLeft ? TEXT("calf_l") : TEXT("calf_r");
        const FName Foot = UseLeft ? Left : Right;
        const int32 ThighIndex = Pose->GetBoneIndex(Thigh);
        const int32 CalfIndex = Pose->GetBoneIndex(Calf);
        const int32 FootIndex = Pose->GetBoneIndex(Foot);
        auto& Bones = Pose->BoneSpaceTransforms;
        if (!Bones.IsValidIndex(ThighIndex) || !Bones.IsValidIndex(CalfIndex) || !Bones.IsValidIndex(FootIndex))
        {
            ClearDriftLeg();
            return;
        }

        const FTransform HipTransform = Source->GetSocketTransform(Thigh);
        const FTransform KneeTransform = Source->GetSocketTransform(Calf);
        const FTransform FootTransform = Source->GetSocketTransform(Foot);
        const FVector Hip = HipTransform.GetLocation();
        const FVector Knee = KneeTransform.GetLocation();
        const FVector Ankle = FootTransform.GetLocation();
        const double Upper = FVector::Distance(Hip, Knee);
        const double Lower = FVector::Distance(Knee, Ankle);
        const FVector Forward = Character.GetActorForwardVector();
        // Use a fixed direction from the hip so the extended foot stops following the crank.
        const FVector Extension = Inside * (Motorcycle ? .78 : 1.05) + Forward * .08 - FVector::UpVector;
        const FVector Axis = Extension.GetSafeNormal();
        if (Upper < 1. || Lower < 1. || Axis.IsNearlyZero())
        {
            ClearDriftLeg();
            return;
        }
        // Both segments point along the same line at full extension.
        const FQuat HipGoal = FQuat::FindBetweenVectors(Knee - Hip, Axis) * HipTransform.GetRotation();
        const FQuat KneeGoal = FQuat::FindBetweenVectors(Ankle - Knee, Axis) * KneeTransform.GetRotation();
        const FQuat Parent = Source->GetSocketQuaternion(Source->GetParentBone(Thigh));
        const FQuat NewHip = FQuat::Slerp(HipTransform.GetRotation(), HipGoal, Alpha);
        Bones[ThighIndex].SetRotation(Parent.Inverse() * NewHip);
        const FQuat NewCalf = FQuat::Slerp(KneeTransform.GetRotation(), KneeGoal, Alpha);
        Bones[CalfIndex].SetRotation(NewHip.Inverse() * NewCalf);
        // Align the actual ankle-to-toe direction from this rig with the extended leg.
        const FName Toe = UseLeft ? TEXT("ball_l") : TEXT("ball_r");
        const FVector ToeDirection = (Source->GetSocketLocation(Toe) - Ankle).GetSafeNormal();
        const FQuat FootGoal = FQuat::FindBetweenNormals(ToeDirection, Axis) * FootTransform.GetRotation();
        Bones[FootIndex].SetRotation(NewCalf.Inverse() * FQuat::Slerp(FootTransform.GetRotation(), FootGoal, Alpha));
    }

    // The split front mesh carries the actual steering transform, including chassis lean.
    if (const auto* Front = SplitSteering.Get())
    {
        const FTransform Steering = Front->GetComponentTransform();
        for (const bool Left : {true, false})
        {
            const FName UpperArm = Left ? TEXT("upperarm_l") : TEXT("upperarm_r");
            const FName Forearm = Left ? TEXT("lowerarm_l") : TEXT("lowerarm_r");
            const FName Hand = Left ? TEXT("hand_l") : TEXT("hand_r");
            const int32 UpperIndex = Pose->GetBoneIndex(UpperArm);
            const int32 ForeIndex = Pose->GetBoneIndex(Forearm);
            const int32 HandIndex = Pose->GetBoneIndex(Hand);
            auto& Bones = Pose->BoneSpaceTransforms;
            if (!Bones.IsValidIndex(UpperIndex) || !Bones.IsValidIndex(ForeIndex) ||
                !Bones.IsValidIndex(HandIndex)) continue;
            const FTransform Shoulder = Source->GetSocketTransform(UpperArm);
            const FTransform Elbow = Source->GetSocketTransform(Forearm);
            const FTransform Wrist = Source->GetSocketTransform(Hand);
            FVector Upper = Elbow.GetLocation() - Shoulder.GetLocation();
            FVector Lower = Wrist.GetLocation() - Elbow.GetLocation();
            // The grip centers are shared by the authored bike and motorcycle stages.
            const FVector Grip = Steering.TransformPosition(FVector(36., Left ? -24. : 24., 111.));
            const FVector Reach = Grip - Shoulder.GetLocation();
            if (Upper.IsNearlyZero() || Lower.IsNearlyZero() || Reach.IsNearlyZero()) continue;
            // Allow small rig tolerances so the far hand can stay on the grip in a turn.
            const double Stretch = FMath::Clamp((Reach.Size() + .01) / (Upper.Size() + Lower.Size()), 1., 1.08);
            Upper *= Stretch;
            Lower *= Stretch;
            Bones[ForeIndex].ScaleTranslation(Stretch);
            Bones[HandIndex].ScaleTranslation(Stretch);
            const double Length = FMath::Clamp(Reach.Size(), FMath::Abs(Upper.Size() - Lower.Size()) + .01,
                Upper.Size() + Lower.Size() - .01);
            const FVector Direction = Reach.GetSafeNormal();
            FVector Bend = FVector::VectorPlaneProject(Upper, Direction).GetSafeNormal();
            if (Bend.IsNearlyZero()) Bend = FVector::VectorPlaneProject(-FVector::UpVector, Direction).GetSafeNormal();
            const double Along = (Upper.SizeSquared() - Lower.SizeSquared() + Length * Length) / (2. * Length);
            const FVector NewUpper = Direction * Along + Bend * FMath::Sqrt(FMath::Max(0., Upper.SizeSquared() - Along * Along));
            const FQuat UpperRotation = FQuat::FindBetweenVectors(Upper, NewUpper) * Shoulder.GetRotation();
            const FQuat ForeRotation = FQuat::FindBetweenVectors(Lower, Direction * Length - NewUpper) * Elbow.GetRotation();
            Bones[UpperIndex].SetRotation(Source->GetSocketQuaternion(Source->GetParentBone(UpperArm)).Inverse() * UpperRotation);
            Bones[ForeIndex].SetRotation(UpperRotation.Inverse() * ForeRotation);
            const FQuat SteeringTurn((FVector(Motorcycle ? 50 : 38, 0, Motorcycle ? 98 : 77) -
                FVector(62, 0, 33)).GetSafeNormal(), FMath::DegreesToRadians(FrontSteer));
            const FQuat WorldTurn = Steering.GetRotation() * SteeringTurn * Steering.GetRotation().Inverse();
            Bones[HandIndex].SetRotation(ForeRotation.Inverse() * WorldTurn * Wrist.GetRotation());
        }
    }
    Pose->MarkRefreshTransformDirty();
    Pose->RefreshBoneTransforms();
    Pose->SetVisibility(bPreviousRiderVisibility);
    Pose->SetHiddenInGame(Source->bHiddenInGame);
    Source->SetVisibility(false);
}

void UBogotaTwoWheelHandling::UpdatePose(UWorld* World, ELevelTick TickType, float DeltaTime)
{
    if (World != GetWorld() || TickType != LEVELTICK_All) return;
    ACharacter* Character = Rider.Get();
    if (!Character) return;
    const bool Mounted = IsSet(Character, TEXT("Riding")) && !IsSet(Character, TEXT("RoadActive"));
    // Riding stays true through the authored dismount until FinishTwoWheelTransition.
    const auto* Transition = FindFProperty<FIntProperty>(Character->GetClass(), TEXT("TransitionState"));
    const bool Transitioning = Transition && Transition->GetPropertyValue_InContainer(Character) != 0;
    const bool UseRiderPose = Mounted && !Transitioning;
    const bool Sliding = UseRiderPose && IsDrifting();
    const bool Bicycle = Mounted && !IsMotorcycle(*Character);
    DriftPoseAlpha = UseRiderPose ? FMath::FInterpConstantTo(DriftPoseAlpha, Sliding ? 1.f : 0.f, DeltaTime, Sliding ? 6.f : 4.5f) : 0.f;
    if (!UseRiderPose) ClearDriftLeg();
    const float Speed = Character->GetVelocity().Size2D();
    const auto* Controller = Cast<APlayerController>(Character->GetController());
    const bool CanSteer = Mounted && Controller && !IsSet(DeliveryOf(*Character), TEXT("PhoneOpen"));
    if (CanSteer)
    {
        const float Yaw = Controller->GetControlRotation().Yaw;
        const float Delta = bTrackingLook ? FMath::FindDeltaAngleDegrees(PreviousLookYaw, Yaw) : 0.f;
        const float Aim = FMath::Abs(Delta) < 80.f ?
            FMath::Clamp(Delta / FMath::Max(1.f, 110.f * DeltaTime), -1.f, 1.f) : 0.f;
        MouseSteer = FMath::FInterpTo(MouseSteer, Aim, DeltaTime, FMath::Abs(Aim) > .02f ? 17.f : 5.f);
        PreviousLookYaw = Yaw;
    }
    else MouseSteer = 0.f;
    bTrackingLook = CanSteer;
    const float KeyboardSteer = CanSteer ? RiderAxis(*Character, TEXT("SideInput")) : 0.f;
    const float Steering = FMath::Clamp(FMath::Abs(KeyboardSteer) > .05f ? KeyboardSteer : MouseSteer, -1.f, 1.f);
    const float Moving = FMath::SmoothStep(30.f, 650.f, Speed);
    HopAge += DeltaTime;
    const float Load = FMath::SmoothStep(175.f, 750.f, Speed);
    const float LeanTarget = Sliding ? (Bicycle ? 15.f + 5.f * Load : 19.f + 5.f * Load) * DriftSide :
        Mounted ? (Bicycle ? 11.f : 14.f) * Steering * Moving : 0.f;
    Lean = FMath::FInterpTo(Lean, -LeanTarget, DeltaTime, Sliding ? 6.f : 5.f);
    SlideYaw = FMath::FInterpTo(SlideYaw, Sliding ? (Bicycle ? 5.f : 7.f) * DriftSide : 0.f, DeltaTime, 6.f);
    const float SteerTarget = CanSteer ? (Sliding ? (-9.f * DriftSide + 3.f * Steering) :
        FMath::Lerp(Bicycle ? 31.f : 26.f, Bicycle ? 6.f : 5.f, Moving) * Steering) : 0.f;
    FrontSteer = FMath::FInterpTo(FrontSteer, SteerTarget, DeltaTime, 12.f);
    UpdateVehicleSteering(*Character, Mounted, Mounted && !Bicycle);
    PedalPhase = FMath::Fmod(PedalPhase + DeltaTime * Speed * .0105f, 2.f * PI);
    const float Sway = Bicycle && !Sliding && RiderAxis(*Character, TEXT("ForwardInput")) > .1f ?
        FMath::Sin(PedalPhase) * 1.5f * Moving : 0.f;
    PedalSway = FMath::FInterpTo(PedalSway, Sway, DeltaTime, 12.f);
    const float WeightTarget = Sliding ? 2.4f * Load : Bicycle && BoostRemaining > 0.f ? 1.8f :
        Bicycle && RiderAxis(*Character, TEXT("ForwardInput")) < -.1f ? -1.4f * Moving : 0.f;
    WeightShift = FMath::FInterpTo(WeightShift, WeightTarget, DeltaTime, 7.f);
    if (auto* Light = TireGlow.Get()) Light->SetVisibility(false);
    if (!Mounted) return;

    const FVector Pivot = Character->GetCharacterMovement()->GetActorFeetLocation();
    const FVector Forward = Character->GetActorForwardVector().GetSafeNormal2D();
    const FVector Right = FVector::CrossProduct(FVector::UpVector, Forward);
    const FQuat Rotation = FQuat(FVector::UpVector, FMath::DegreesToRadians(SlideYaw)) *
        FQuat(Forward, FMath::DegreesToRadians(Lean + PedalSway)) *
        FQuat(Right, FMath::DegreesToRadians(WeightShift));
    const float Hop = Sliding && HopAge < .21f ?
        (Bicycle ? 3.f : 5.f) * FMath::Sin(PI * HopAge / .21f) : 0.f;
    const auto* Base = OriginalBike.Get();
    const FVector Head = Bicycle ? FVector(38, 0, 77) : FVector(50, 0, 98);
    const FVector Axis = (Head - FVector(62, 0, 33)).GetSafeNormal();
    auto* FrontWheel = Base && SplitSteering.IsValid() ? MeshPart(*Character, TEXT("FrontWheel")) : nullptr;
    const FQuat WheelTurn(Base ? Base->GetComponentTransform().TransformVectorNoScale(Axis) : FVector::UpVector,
        FMath::DegreesToRadians(FrontSteer));
    const FVector SteeringPivot = Base ? Base->GetComponentTransform().TransformPosition(Head) : Pivot;
    FVector WheelLocation;
    FQuat WheelRotation;
    if (FrontWheel)
    {
        RestPose.Add(FrontWheel, FrontWheel->GetRelativeTransform());
        WheelLocation = SteeringPivot + WheelTurn.RotateVector(FrontWheel->GetComponentLocation() - SteeringPivot);
        WheelRotation = WheelTurn * FrontWheel->GetComponentQuat();
    }
    TInlineComponentArray<USceneComponent*> Parts(Character);
    for (auto* Part : Parts)
    {
        if (Part == FrontWheel) continue;
        auto* StaticPart = Cast<UStaticMeshComponent>(Part);
        if (Part != Character->GetMesh() && (!StaticPart || StaticPart->IsCollisionEnabled())) continue;
        if (Part->IsSimulatingPhysics()) continue;
        bool FollowsPose = false;
        for (auto* Parent = Part->GetAttachParent(); Parent; Parent = Parent->GetAttachParent())
            if (Parent == Character->GetMesh() || Parent->IsA<UStaticMeshComponent>()) FollowsPose = true;
        if (FollowsPose) continue;
        RestPose.Add(Part, Part->GetRelativeTransform());
        Part->SetWorldLocationAndRotation(Pivot + Rotation.RotateVector(Part->GetComponentLocation() - Pivot) +
            FVector(0, 0, Hop), Rotation * Part->GetComponentQuat(), false, nullptr,
            ETeleportType::TeleportPhysics);
    }
    if (FrontWheel)
        FrontWheel->SetWorldLocationAndRotation(Pivot + Rotation.RotateVector(WheelLocation - Pivot) +
            FVector(0, 0, Hop), Rotation * WheelRotation, false, nullptr, ETeleportType::TeleportPhysics);
    if (UseRiderPose) UpdateRiderPose(*Character, Right * DriftSide, DriftPoseAlpha, !Bicycle);

    const int32 Tier = GetDriftTier();
    if (!Tier) return;
    auto* Light = TireGlow.Get();
    if (!Light)
    {
        Light = NewObject<UPointLightComponent>(Character);
        Light->SetCastShadows(false);
        Light->SetAttenuationRadius(155.f);
        Light->RegisterComponent();
        TireGlow = Light;
    }
    const FColor Spark = Tier == 1 ? FColor(85, 185, 255) : Tier == 2 ? FColor(255, 132, 39) : FColor(255, 73, 187);
    const FVector Contact = Pivot + Rotation.RotateVector(-Forward * 72.) + FVector(0, 0, 6);
    Light->SetWorldLocation(Contact);
    Light->SetLightColor(Spark);
    Light->SetIntensity(320.f + 160.f * Tier);
    Light->SetVisibility(true);
    if (auto* Streaks = World->GetLineBatcher(UWorld::ELineBatcherType::WorldPersistent))
    {
        for (int32 Index = 0; Index < 2; ++Index)
        {
            const FVector End = Contact - Forward * FMath::FRandRange(8.f, 27.f) +
                FVector(FMath::FRandRange(-9.f, 9.f), FMath::FRandRange(-9.f, 9.f), FMath::FRandRange(3.f, 11.f));
            Streaks->DrawLine(Contact, End, FLinearColor(Spark), 0, 1.2f, .035f);
        }
    }
}

bool UBogotaTwoWheelHandling::IsDrifting() const
{
    const ACharacter* Character = Rider.Get();
    return bDrifting && Character && DriftHeld(Cast<APlayerController>(Character->GetController()));
}

void UBogotaTwoWheelHandling::UpdateFootStamina(ACharacter& Character,
    const UCharacterMovementComponent& Movement, float DeltaTime)
{
    const bool OnFoot = !IsSet(&Character, TEXT("Riding")) && !IsSet(&Character, TEXT("RoadActive"));
    const auto* Sprint = FindFProperty<FBoolProperty>(Character.GetClass(), TEXT("Sprint"));
    const bool Running = OnFoot && Sprint && Sprint->GetPropertyValue_InContainer(&Character);
    if (Running && !bExhausted && Movement.IsMovingOnGround() &&
        Movement.Velocity.SizeSquared2D() > FMath::Square(170.f))
    {
        FootStamina = FMath::Max(0.f, FootStamina - 21.f * DeltaTime);
        RecoveryDelay = .85f;
        if (FootStamina == 0.f)
        {
            bExhausted = true;
            UE_LOG(LogBogotaHandling, Display, TEXT("Foot sprint stamina depleted"));
        }
    }
    else
    {
        const float RecoveryTime = FMath::Max(0.f, DeltaTime - RecoveryDelay);
        RecoveryDelay = FMath::Max(0.f, RecoveryDelay - DeltaTime);
        FootStamina = FMath::Min(100.f, FootStamina + 17.f * RecoveryTime);
    }

    if (bExhausted && Running) Sprint->SetPropertyValue_InContainer(&Character, false);
    if (bExhausted && FootStamina >= 25.f)
    {
        bExhausted = false;
        UE_LOG(LogBogotaHandling, Display, TEXT("Foot sprint stamina recovered"));
    }
}

void UBogotaTwoWheelHandling::OnMovement(float DeltaTime, FVector, FVector OldVelocity)
{
    ACharacter* Character = Rider.Get();
    if (!Character) return;
    auto* Controller = Cast<APlayerController>(Character->GetController());
    auto* Movement = Character->GetCharacterMovement();
    if (Controller) UpdateFootStamina(*Character, *Movement, DeltaTime);
    if (!Controller || !Movement->IsMovingOnGround() || !IsSet(Character, TEXT("Riding")) ||
        IsSet(Character, TEXT("RoadActive")) || IsSet(DeliveryOf(*Character), TEXT("PhoneOpen")))
    {
        ClearDrift();
        BoostRemaining = 0.f;
        return;
    }

    const float Speed = Movement->Velocity.Size2D();
    const float KeyboardSteering = FMath::Clamp(RiderAxis(*Character, TEXT("SideInput")), -1.f, 1.f);
    const float Steering = FMath::Abs(KeyboardSteering) > .05f ? KeyboardSteering : MouseSteer;
    if (Speed > 95.f)
    {
        const float MouseTurn = FMath::Abs(KeyboardSteering) <= .05f ? 65.f * Steering : 0.f;
        const float DriftTurn = bDrifting && DriftHeld(Controller) ? 20.f * Steering : 0.f;
        const float Turn = (MouseTurn + DriftTurn) * FMath::SmoothStep(95.f, 550.f, Speed) * DeltaTime;
        Character->AddActorWorldRotation(FRotator(0.f, Turn, 0.f));
    }
    const FVector Forward = Character->GetActorForwardVector().GetSafeNormal2D();
    const float ForwardSpeed = FVector::DotProduct(Movement->Velocity, Forward);
    const float Throttle = RiderAxis(*Character, TEXT("ForwardInput"));
    if (BoostRemaining > 0.f)
    {
        BoostRemaining = Throttle < -.1f || ForwardSpeed < 150.f ? 0.f : FMath::Max(0.f, BoostRemaining - DeltaTime);
        if (BoostRemaining > 0.f)
        {
            // Blueprint driving resets both velocity limit and BikeSpeed each frame.
            // Restore the turbo into that same drive state, not a one-frame velocity spike.
            const float TurboSpeed = FMath::FInterpConstantTo(Speed, BoostSpeed, DeltaTime, 1250.f);
            if (auto* Drive = FindFProperty<FNumericProperty>(Character->GetClass(), TEXT("BikeSpeed")))
                Drive->SetFloatingPointPropertyValue(Drive->ContainerPtrToValuePtr<void>(Character), TurboSpeed);
            Movement->MaxWalkSpeed = FMath::Max(Movement->MaxWalkSpeed, TurboSpeed);
            Movement->Velocity = Forward * TurboSpeed + FVector(0, 0, Movement->Velocity.Z);
        }
    }
    if (!DriftHeld(Controller))
    {
        const int32 Tier = DriftTier(DriftCharge);
        if (bDrifting && Tier && ForwardSpeed > 220.f && Throttle >= -.1f)
        {
            const float Charge = FMath::Min(DriftCharge, 4.8f);
            const float Bonus = 125.f + 103.f * Charge;
            ++DriftBoostCount;
            BoostRemaining = .42f + .26f * Charge;
            BoostSpeed = FMath::Max(Speed, RiderAxis(*Character, TEXT("BikeSpeed"))) + Bonus;
            Movement->Velocity += Forward * (.72f * Bonus);
            UE_LOG(LogBogotaHandling, Display, TEXT("Two-wheel mini-turbo tier=%d charge=%.2f entry=%.0f target=%.0f"),
                Tier, Charge, Speed, BoostSpeed);
        }
        if (bDrifting) UE_LOG(LogBogotaHandling, Display, TEXT("Two-wheel drift released"));
        ClearDrift();
        bWaitForRelease = false;
        return;
    }

    if (!bDrifting && !bWaitForRelease && ForwardSpeed > 220.f)
    {
        bDrifting = true;
        DriftSide = Steering < -.1f ? -1.f : 1.f;
        HopAge = 0.f;
        DriftDirection = OldVelocity.GetSafeNormal2D();
        if (DriftDirection.IsNearlyZero()) DriftDirection = Forward;
        UE_LOG(LogBogotaHandling, Display, TEXT("Two-wheel drift started with Space, steering=%.2f"), Steering);
    }

    if (bDrifting)
    {
        if (ForwardSpeed < 130.f || Throttle < -.1f)
        {
            ClearDrift();
            bWaitForRelease = true;
            return;
        }
        if (DriftCharge < .18f && FMath::Abs(Steering) > .18f) DriftSide = FMath::Sign(Steering);
        const int32 PreviousTier = DriftTier(DriftCharge);
        DriftCharge += DeltaTime * (.80f + .58f * FMath::Max(0.f, Steering * DriftSide));
        if (const int32 Tier = DriftTier(DriftCharge); Tier > PreviousTier)
            UE_LOG(LogBogotaHandling, Display, TEXT("Two-wheel drift charge tier=%d"), Tier);
        const float SlipAngle = IsMotorcycle(*Character) ? 16.f + 7.f * Steering * DriftSide :
            13.f + 6.f * Steering * DriftSide;
        const FVector SlipHeading = Forward.RotateAngleAxis(-SlipAngle * DriftSide, FVector::UpVector);
        DriftDirection = FMath::VInterpTo(DriftDirection, SlipHeading, DeltaTime, 7.f).GetSafeNormal2D();
        Movement->Velocity = FVector(DriftDirection.X * Speed, DriftDirection.Y * Speed, Movement->Velocity.Z);
    }
}

TStatId UBogotaTwoWheelHandling::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UBogotaTwoWheelHandling, STATGROUP_Tickables);
}
