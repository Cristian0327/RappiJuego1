#include "GameFramework/InputDeviceSubsystem.h"
#include "GameFramework/InputSettings.h"
#include "Engine/LocalPlayer.h"
#include "Engine/Texture2D.h"
#include "ImageUtils.h"
#include "Misc/Paths.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SBoxPanel.h"
#include "BogotaRobbery.h"
#include "BogotaAudio.h"

#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "AnimationRuntime.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/AudioComponent.h"
#include "Components/InputComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "ConvexVolume.h"
#include "Engine/LocalPlayer.h"
#include "Engine/StaticMesh.h"
#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/NativeWidgetHost.h"
#include "Engine/Console.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Styling/CoreStyle.h"
#include "Components/ActorComponent.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/SBoxPanel.h"
#include "Animation/SkeletalMeshActor.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PawnMovementComponent.h"

#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "SceneView.h"
#include "Sound/SoundBase.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"

namespace
{
TAutoConsoleVariable<float> PromptSeconds(TEXT("BogRob.PromptSeconds"), 2.5f, TEXT("Seconds for the first robbery prompt. Later prompts use 80% and 60%."));
const FKey Keyboard[] = {EKeys::Q, EKeys::E, EKeys::R, EKeys::F};
const FKey Gamepad[] = {EKeys::Gamepad_FaceButton_Bottom, EKeys::Gamepad_FaceButton_Right,
    EKeys::Gamepad_FaceButton_Left, EKeys::Gamepad_FaceButton_Top};
const TCHAR* PadLabels[] = {TEXT("A / ×"), TEXT("B / ○"),
    TEXT("X / □"), TEXT("Y / △")};
constexpr float BikeProtectionSeconds = 5.f * 60.f;
constexpr int32 BikeRescueCost = 50000;
constexpr int32 MotoRescueCost = 80000;
constexpr float ApproachSeconds = 6.f;
constexpr float ForcedDismountSeconds = 3.f;
constexpr double MinimumChaseSpeed = 650.0;
constexpr double ChaseSpeedAdvantage = 325.0;
constexpr double GrabDistance = 60.0;
constexpr double OpenEscapeDistance = 1200.0;
constexpr float ThiefMountSeconds = .60f; // The player mount takes .68 seconds.
constexpr float MinimumRetreatSeconds = .75f;
constexpr float OffscreenGraceSeconds = .30f;
constexpr float BuildingCoverSeconds = .12f;
constexpr float RetreatSeconds = 2.4f;
constexpr double RetreatSpeed = 2250.0;
constexpr double VehicleEscapeSpeed = 2500.0;

FRotator FaceTravelDirection(const USkeletalMesh& Mesh, const FVector& Direction)
{
    const FReferenceSkeleton& Skeleton = Mesh.GetRefSkeleton();
    const int32 Left = Skeleton.FindBoneIndex(TEXT("thigh_l"));
    const int32 Right = Skeleton.FindBoneIndex(TEXT("thigh_r"));
    FRotator Heading = Direction.GetSafeNormal2D().Rotation();
    if (Left != INDEX_NONE && Right != INDEX_NONE)
    {
        const FVector LeftHip = FAnimationRuntime::GetComponentSpaceTransformRefPose(Skeleton, Left).GetLocation();
        const FVector RightHip = FAnimationRuntime::GetComponentSpaceTransformRefPose(Skeleton, Right).GetLocation();
        const FVector Forward = FVector::CrossProduct(FVector::UpVector, LeftHip - RightHip).GetSafeNormal2D();
        Heading.Yaw -= Forward.Rotation().Yaw;
    }
    return Heading;
}

bool PlayThiefAnimation(USkeletalMeshComponent& Mesh, UAnimSequence* Clip, bool bLoop, float Rate = 1.f)
{
    const USkeletalMesh* Asset = Mesh.GetSkeletalMeshAsset();
    if (!IsValid(Clip) || !IsValid(Asset) || Clip->GetSkeleton() != Asset->GetSkeleton())
    {
        return false;
    }

    // SetAnimationAsset changes the asset used by the single-node instance.
    // Finish its previous evaluation before changing that asset.
    Mesh.HandleExistingParallelEvaluationTask(true, true);
    Mesh.SetAnimationMode(EAnimationMode::AnimationSingleNode, false);
    if (UAnimSingleNodeInstance* Instance = Mesh.GetSingleNodeInstance())
    {
        Instance->SetAnimationAsset(Clip, bLoop, Rate);
        Instance->SetPosition(0.f, false);
        Instance->SetPlaying(true);
        return true;
    }
    return false;
}

bool FindRetreatStep(UWorld* World, const FVector& From, FVector& To, const FCollisionQueryParams& Params)
{
    FHitResult Ground;
    if (!World->LineTraceSingleByChannel(Ground, To + FVector(0, 0, 45),
        To - FVector(0, 0, 75), ECC_Visibility, Params) || Ground.ImpactNormal.Z < 0.65)
    {
        return false;
    }
    To.Z = Ground.ImpactPoint.Z + 2.0;
    return !World->SweepTestByChannel(From + FVector(0, 0, 85), To + FVector(0, 0, 85),
        FQuat::Identity, ECC_Visibility, FCollisionShape::MakeCapsule(29.0, 65.0), Params);
}

FVector PickRetreatDestination(APlayerController& Controller, const FVector& Start,
    const FCollisionQueryParams& Params)
{
    FVector CameraLocation;
    FRotator View;
    Controller.GetPlayerViewPoint(CameraLocation, View);
    const APawn* Pawn = Controller.GetPawn();
    const FVector Origin = Pawn ? Pawn->GetActorLocation() : CameraLocation;
    const FVector Away = (Start - Origin).GetSafeNormal2D();
    const double EscapeYaw = Away.IsNearlyZero() ? View.Yaw + 180.0 : Away.Rotation().Yaw;
    const FVector CameraForward = FRotator(0, View.Yaw, 0).Vector();
    const bool bFarFromPlayer = FVector::DistSquared2D(Start, Origin) >= FMath::Square(OpenEscapeDistance);
    FVector Destination = Start;
    double BestScore = -TNumericLimits<double>::Max();
    for (const double Angle : {0.0, 30.0, -30.0, 60.0, -60.0, 90.0, -90.0,
        120.0, -120.0, 150.0, -150.0, 180.0})
    {
        const FVector Direction = FRotator(0, EscapeYaw + Angle, 0).Vector();
        FVector Reach = Start;
        for (int32 Step = 0; Step < 13; ++Step)
        {
            FVector Next = Reach + Direction * (Step == 0 ? 55.0 : 170.0);
            if (!FindRetreatStep(Controller.GetWorld(), Reach, Next, Params))
            {
                break;
            }
            Reach = Next;
        }
        const double Travel = FVector::Dist2D(Start, Reach);
        const double Gain = FVector::Dist2D(Origin, Reach) - FVector::Dist2D(Origin, Start);
        const double ViewDepthGain = FVector::DotProduct(Reach - Start, CameraForward);
        const double Score = Travel + .75 * Gain - (bFarFromPlayer ? ViewDepthGain : 0.0);
        if (Travel > 0.0 && Score > BestScore)
        {
            BestScore = Score;
            Destination = Reach;
        }
    }
    return Destination;
}

bool IsBehindBuilding(APlayerController& Controller, const UPrimitiveComponent& Building,
    int32 Instance, const FVector& Point, const FCollisionQueryParams& Params)
{
    FVector Camera;
    FRotator View;
    Controller.GetPlayerViewPoint(Camera, View);
    FHitResult Hit;
    return Controller.GetWorld()->LineTraceSingleByChannel(Hit, Camera, Point, ECC_Visibility, Params) &&
        Hit.GetComponent() == &Building && (Instance == INDEX_NONE || Hit.Item == Instance);
}

bool IsEscapeActorOccluded(APlayerController& Controller, AActor& Actor, const FCollisionQueryParams& Params,
    const UPrimitiveComponent* Building, int32 Instance)
{
    const FBox Bounds = Actor.GetComponentsBoundingBox(true);
    if (!Bounds.IsValid)
    {
        return false;
    }
    FVector Camera;
    FRotator View;
    Controller.GetPlayerViewPoint(Camera, View);
    const FVector Center = Bounds.GetCenter();
    const FVector Extent = Bounds.GetExtent() * .85;
    for (const FVector& Offset : {FVector::ZeroVector, FVector(Extent.X, 0, 0), FVector(-Extent.X, 0, 0),
        FVector(0, Extent.Y, 0), FVector(0, -Extent.Y, 0), FVector(0, 0, Extent.Z), FVector(0, 0, -Extent.Z)})
    {
        FHitResult Hit;
        if (!Controller.GetWorld()->LineTraceSingleByChannel(Hit, Camera, Center + Offset, ECC_Visibility, Params) ||
            !Hit.GetComponent() || Hit.GetComponent()->Mobility != EComponentMobility::Static ||
            (Building && (Hit.GetComponent() != Building || (Instance != INDEX_NONE && Hit.Item != Instance))))
        {
            return false;
        }
    }
    return true;
}

bool IsOutsideEscapeView(APlayerController& Controller, AActor& Actor)
{
    const ULocalPlayer* LocalPlayer = Controller.GetLocalPlayer();
    FSceneViewProjectionData Projection;
    if (!LocalPlayer || !LocalPlayer->ViewportClient || !LocalPlayer->ViewportClient->Viewport ||
        !LocalPlayer->GetProjectionData(LocalPlayer->ViewportClient->Viewport, Projection))
    {
        return false;
    }
    const FBox Bounds = Actor.GetComponentsBoundingBox(true);
    FConvexVolume ViewFrustum;
    GetViewFrustumBounds(ViewFrustum, Projection.ComputeViewProjectionMatrix(), false);
    return Bounds.IsValid && !ViewFrustum.IntersectBox(Bounds.GetCenter(), Bounds.GetExtent() + FVector(35.0));
}

bool CheckEscapeSegment(UWorld* World, const FVector& From, FVector& To, const FCollisionQueryParams& Params)
{
    const int32 Steps = FMath::Max(1, FMath::CeilToInt(FVector::Dist2D(From, To) / 105.0));
    FVector Ground = From;
    for (int32 Step = 1; Step <= Steps; ++Step)
    {
        FVector Next = FMath::Lerp(From, To, double(Step) / Steps);
        Next.Z = Ground.Z;
        if (!FindRetreatStep(World, Ground, Next, Params))
        {
            return false;
        }
        Ground = Next;
    }
    To = Ground;
    return true;
}

bool ReadFlag(const UObject* Object, const TCHAR* Name)
{
    const FBoolProperty* Property = Object ? FindFProperty<FBoolProperty>(Object->GetClass(), Name) : nullptr;
    return Property && Property->GetPropertyValue_InContainer(Object);
}

UObject* FindDeliveryCore(APawn* Pawn)
{
    const FObjectPropertyBase* Field = Pawn ? FindFProperty<FObjectPropertyBase>(Pawn->GetClass(), TEXT("Delivery")) : nullptr;
    return Field ? Field->GetObjectPropertyValue_InContainer(Pawn) : nullptr;
}

AActor* PlayerTwoWheeler(APawn* Pawn)
{
    const FObjectPropertyBase* Field = Pawn ? FindFProperty<FObjectPropertyBase>(Pawn->GetClass(), TEXT("ParkedVehicle")) : nullptr;
    return Field ? Cast<AActor>(Field->GetObjectPropertyValue_InContainer(Pawn)) : nullptr;
}

AActor* ParkedTwoWheeler(APawn* Pawn)
{
    const FIntProperty* Transition = Pawn ? FindFProperty<FIntProperty>(Pawn->GetClass(), TEXT("TransitionState")) : nullptr;
    if (ReadFlag(Pawn, TEXT("Riding")) || (Transition && Transition->GetPropertyValue_InContainer(Pawn) != 0))
    {
        return nullptr;
    }
    return PlayerTwoWheeler(Pawn);
}

FVector PickVehiclePickup(UWorld* World, const FVector& Start, const FRotator& Facing,
    const FCollisionQueryParams& Query, FRotator& Heading)
{
    constexpr double StepSize = 170.0;
    const bool bLongTrip = FMath::RandBool();
    const double Desired = bLongTrip ? FMath::FRandRange(11000.f, 18000.f)
                                   : FMath::FRandRange(4500.f, 7500.f);
    TArray<int32, TInlineAllocator<12>> Bearings;
    for (int32 I = 0; I < 12; ++I)
    {
        Bearings.Add(I * 30);
    }
    for (int32 I = Bearings.Num() - 1; I > 0; --I)
    {
        Bearings.Swap(I, FMath::RandRange(0, I));
    }

    FVector Best = Start;
    double BestDistance = 0.0;
    for (int32 Bearing : Bearings)
    {
        const FRotator Direction(0, Facing.Yaw + Bearing, 0);
        FVector Reach = Start;
        for (double Travel = StepSize; Travel <= Desired + StepSize; Travel += StepSize)
        {
            FVector Next = Reach + Direction.Vector() * StepSize;
            if (!FindRetreatStep(World, Reach, Next, Query))
            {
                break;
            }
            Reach = Next;
        }
        const double Distance = FVector::Dist2D(Start, Reach);
        if (Distance > BestDistance)
        {
            Best = Reach;
            BestDistance = Distance;
            Heading = Direction;
        }
        if (Distance >= Desired)
        {
            break;
        }
    }
    UE_LOG(LogTemp, Display, TEXT("Vehicle pickup: selected %.0f m (requested %.0f m)"),
        BestDistance / 100.0, Desired / 100.0);
    return Best;
}

bool SaveRescueBalance(UObject& Delivery)
{
    UFunction* Save = Delivery.FindFunction(TEXT("SaveProfile"));
    const FBoolProperty* Saved = Save ? CastField<FBoolProperty>(Save->GetReturnProperty()) : nullptr;
    if (!Saved || Save->NumParms != 1)
    {
        return false;
    }
    FStructOnScope Params(Save);
    Delivery.ProcessEvent(Save, Params.GetStructMemory());
    return Saved->GetPropertyValue_InContainer(Params.GetStructMemory());
}

bool IsConsoleOpen(UWorld* World)
{
    const UGameViewportClient* Viewport = World->GetGameViewport();
    return Viewport && Viewport->ViewportConsole && Viewport->ViewportConsole->ConsoleActive();
}

#if !UE_BUILD_SHIPPING
bool IsDeveloperMode(UWorld* World)
{
    const APlayerController* Controller = World ? World->GetFirstPlayerController() : nullptr;
    const APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
    if (!Pawn)
    {
        return false;
    }

    for (const UActorComponent* Component : Pawn->GetComponents())
    {
        if (const FBoolProperty* Mode = FindFProperty<FBoolProperty>(Component->GetClass(), TEXT("DeveloperMode")))
        {
            return Mode->GetPropertyValue_InContainer(Component);
        }
    }
    return false;
}

FAutoConsoleCommandWithWorldAndArgs PreviewCommand(
    TEXT("BogRobPreview"), TEXT("Preview robbery. Args: Rayas, Hornets, or Cancel. Requires ESOYAM."),
    FConsoleCommandWithWorldAndArgsDelegate::CreateLambda(
        [](const TArray<FString>& Args, UWorld* World)
        {
            if (!IsDeveloperMode(World))
            {
                return;
            }
            if (UBogotaRobbery* Robbery = World->GetSubsystem<UBogotaRobbery>())
            {
                if (Args.Num() == 1 && Args[0].Equals(TEXT("Cancel"), ESearchCase::IgnoreCase))
                {
                    Robbery->CancelPreview();
                }
                else if (Args.Num() == 1)
                {
                    Robbery->StartPreview(Args[0]);
                }
                else
                {
                    UE_LOG(LogTemp, Display, TEXT("BogRobPreview Rayas | Hornets | Cancel"));
                }
            }
        }));
FAutoConsoleCommandWithWorld AbelardoCommand(
    TEXT("Abelardo"), TEXT("Preview Abelardo after ESOYAM."),
    FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
    {
        if (IsDeveloperMode(World))
        {
            if (UBogotaRobbery* Robbery = World->GetSubsystem<UBogotaRobbery>())
            {
                Robbery->StartPreview(TEXT("Rayas"));
            }
        }
    }));

const FConsoleCommandWithWorldDelegate NeroPreview =
    FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
    {
        if (IsDeveloperMode(World))
        {
            if (UBogotaRobbery* Robbery = World->GetSubsystem<UBogotaRobbery>())
            {
                Robbery->StartPreview(TEXT("Hornets"));
            }
        }
    });
FAutoConsoleCommandWithWorld NeroCommand(TEXT("Nero"), TEXT("Preview Hornets after ESOYAM."), NeroPreview);
#endif
}

bool UBogotaRobbery::DoesSupportWorldType(EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::PIE || WorldType == EWorldType::Game;
}

TStatId UBogotaRobbery::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UBogotaRobbery, STATGROUP_Tickables);
}

void UBogotaRobbery::PlayRobberySound(ASkeletalMeshActor& Actor)
{
    if (UAudioComponent* Previous = RobberyVoice.Get())
    {
        Previous->Stop();
    }
    const FString Name = FString::Printf(TEXT("S_Robbery_%s"), GetCharacterName());
    const FString Path = FString::Printf(TEXT("/Game/Robbery/Audio/%s.%s"), *Name, *Name);
    const FSoftObjectPath SoundPath(Path);
    if (USoundBase* Sound = Cast<USoundBase>(SoundPath.TryLoad()))
    {
        RobberyVoice = UGameplayStatics::SpawnSoundAttached(Sound, Actor.GetRootComponent());
    }
}

void UBogotaRobbery::StartPreview(const FString& Variant)
{
    const bool bRayas = Variant.Equals(TEXT("Rayas"), ESearchCase::IgnoreCase);
    if (!bRayas && !Variant.Equals(TEXT("Hornets"), ESearchCase::IgnoreCase))
    {
        UE_LOG(LogTemp, Display, TEXT("BogRobPreview Rayas | Hornets | Cancel"));
        return;
    }

    if (Thief.IsValid())
    {
        return;
    }

    CancelPreview();
    SpawnEncounter(bRayas);
}

void UBogotaRobbery::ObservePickup(UObject* Delivery, bool bCheckedOut, bool bOutside, double Hour)
{
    const double Now = GetWorld()->GetTimeSeconds();
    const double ObservedSeconds = LastStreetObservation < 0.
        ? 0. : FMath::Clamp(Now - LastStreetObservation, 0., .5);
    LastStreetObservation = Now;
    if (bCheckedOut)
    {
        PickupCandidate = Delivery;
        PickupExpires = Now + 12.;
    }
    if (!Delivery || !bOutside || Thief.IsValid() || GetWorld()->IsPaused() || IsConsoleOpen(GetWorld()))
    {
        return;
    }
    const bool bPickup = PickupCandidate.Get() == Delivery && Now <= PickupExpires;
    if (bPickup)
    {
        PickupCandidate.Reset();
    }

    const FIntProperty* Balance = FindFProperty<FIntProperty>(Delivery->GetClass(), TEXT("Balance"));
    const bool bCashEligible = Balance && CalculateBalanceLoss(Balance->GetPropertyValue_InContainer(Delivery)) > 0;
    APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
    if (!Pawn)
    {
        return;
    }
    const bool bRiding = ReadFlag(Pawn, TEXT("Riding"));
    const AActor* Vehicle = bRiding ? PlayerTwoWheeler(Pawn) : ParkedTwoWheeler(Pawn);
    const bool bVehicleEligible = Vehicle && CanStealVehicle(Delivery) && !RetainedVehicle.IsValid() && (bRiding ||
        FVector::DistSquared2D(Vehicle->GetActorLocation(), Pawn->GetActorLocation()) <= FMath::Square(420.0));
    if ((bRiding || !bCashEligible) && !bVehicleEligible)
    {
        return;
    }
    if (bPickup && ProtectedPickups > 0)
    {
        --ProtectedPickups;
        return;
    }
    const double PickupChance = Hour < 6. ? .16 : Hour < 12. ? .045 : Hour < 19. ? .07 : .12;
    const double StreetChancePerMinute = Hour < 6. ? .36 : Hour < 12. ? .16 : Hour < 19. ? .22 : .29;
    // Convert the per-minute risk to the elapsed eligible gameplay time.
    const double Chance = bPickup ? PickupChance
        : 1. - FMath::Pow(1. - StreetChancePerMinute, ObservedSeconds / 60.);
    if (FMath::FRand() >= Chance)
    {
        return;
    }
    const bool bRayas = !bRiding && bCashEligible && (!bVehicleEligible || FMath::FRand() < .60f);
    if (StartEncounter(bRayas))
    {
        EncounterDelivery = Delivery;
        ProtectedPickups = 2;
    }
}

bool UBogotaRobbery::StartEncounter(bool bRayas)
{
    APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    if (Thief.IsValid() || (!bRayas && !CanStealVehicle(FindDeliveryCore(Controller ? Controller->GetPawn() : nullptr))) ||
        !SpawnEncounter(bRayas))
    {
        return false;
    }
    bGameplayEncounter = true;
    return true;
}

int32 UBogotaRobbery::CalculateBalanceLoss(int32 Balance)
{
    return Balance < 3000 ? 0 : static_cast<int32>(FMath::Min<int64>(12000, int64(Balance) * 15 / 100));
}

bool UBogotaRobbery::SpawnEncounter(bool bRayas)
{
    UWorld* World = GetWorld();
    APlayerController* Controller = World->GetFirstPlayerController();
    APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
    const FIntProperty* Transition = Pawn
        ? FindFProperty<FIntProperty>(Pawn->GetClass(), TEXT("TransitionState")) : nullptr;
    if (!Pawn || (Transition && Transition->GetPropertyValue_InContainer(Pawn) != 0))
    {
        return false;
    }

    if (bRayas && ReadFlag(Pawn, TEXT("Riding")))
    {
        return false;
    }
    const TCHAR* CharacterName = bRayas ? TEXT("Rayas") : TEXT("Hornets");
    const TCHAR* MeshPath = bRayas
        ? TEXT("/Game/Robbery/Rayas/SK_Rayas.SK_Rayas")
        : TEXT("/Game/Robbery/Hornets/SK_Hornets.SK_Hornets");
    USkeletalMesh* Mesh = LoadObject<USkeletalMesh>(nullptr, MeshPath);
    if (!Mesh)
    {
        UE_LOG(LogTemp, Warning, TEXT("Missing robbery mesh: %s"), CharacterName);
        return false;
    }

    const FRotator PawnYaw(0, Pawn->GetActorRotation().Yaw, 0);
    const FVector Center = Pawn->GetActorLocation();
    const FBox MeshBounds = Mesh->GetBounds().GetBox();
    const double ImportedHeight = MeshBounds.GetSize().Z;
    // The current FBXs can import their meter dimensions as Unreal centimeters.
    const double MeshScale = (ImportedHeight >= 1.0 && ImportedHeight <= 3.0 ? 100.0 : 1.0) * 1.13;
    const double Height = ImportedHeight * MeshScale;
    const FVector FeetOffset(0, 0, 2.0 - MeshBounds.Min.Z * MeshScale);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(BogotaRobberyPreview), false, Pawn);
    Params.AddIgnoredActor(PlayerTwoWheeler(Pawn));
    FVector Target;
    bool bFoundApproach = false;
    for (const double Angle : {24.0, -24.0, 42.0, -42.0, 0.0})
    {
        const FVector Direction = FRotator(0, PawnYaw.Yaw + 180.0 + Angle, 0).Vector();
        FVector Start;
        FHitResult Floor;
        const FVector StartGuess = Center + Direction * 235.0;
        if (!World->LineTraceSingleByChannel(Floor, StartGuess + FVector(0, 0, 65),
            StartGuess - FVector(0, 0, 230), ECC_Visibility, Params) || Floor.ImpactNormal.Z < .65)
        {
            continue;
        }
        Start = Floor.ImpactPoint + FVector(0, 0, 2);
        FVector Middle = Start + Direction * -100.0;
        FVector End = Start + Direction * -192.0;
        if (FindRetreatStep(World, Start, Middle, Params) &&
            FindRetreatStep(World, Middle, End, Params))
        {
            Origin = Start + FeetOffset - FVector(0, 0, 2);
            Target = End + FeetOffset - FVector(0, 0, 2);
            bFoundApproach = true;
            break;
        }
    }
    if (!bFoundApproach)
    {
        UE_LOG(LogTemp, Warning, TEXT("Robbery %s: no clear ground behind player"), CharacterName);
        return false;
    }

    const FRotator Rotation = FaceTravelDirection(*Mesh, Target - Origin);
    ASkeletalMeshActor* Actor = World->SpawnActor<ASkeletalMeshActor>(Origin, Rotation);
    if (!Actor)
    {
        return false;
    }
    Actor->GetSkeletalMeshComponent()->SetSkeletalMesh(Mesh);
    Actor->SetActorScale3D(FVector(MeshScale));
    Actor->SetActorEnableCollision(false);
    UE_LOG(LogTemp, Display, TEXT("Robbery %s: spawned at %s, mesh height %.1f cm"),
        CharacterName, *Origin.ToCompactString(), Height);
    bRayasEncounter = bRayas;
    Thief = Actor;
    Player = Pawn;
    Phase = EPhase::Approach;
    TimeLeft = ApproachSeconds;
    RetreatElapsed = 0.f;
    FootstepTime = 0.10f;
    OutOfSightTime = 0.f;
    PlayClip(TEXT("Run"), true);
    if (UGameViewportClient* Viewport = World->GetGameViewport())
    {
        OverlayViewport = Viewport;
        const FString ArtDirectory = FPaths::Combine(FPaths::ProjectPluginsDir(), TEXT("BogotaPhonePreview/Resources"));
        if (!EncounterPanel.GetResourceObject())
        {
            if (auto* Texture = FImageUtils::ImportFileAsTexture2D(FPaths::Combine(ArtDirectory, TEXT("RoboAviso.png"))))
            {
                Texture->Filter = TF_Bilinear;
                Texture->UpdateResource();
                Texture->AddToRoot();
                EncounterPanel.SetResourceObject(Texture);
                EncounterPanel.SetImageSize(FVector2D::ZeroVector);
            }
        }
        const FString FontFile = FPaths::Combine(ArtDirectory, TEXT("f1-secuencia-quad-ffp.ttf"));
        const FSlateFontInfo Font = FPaths::FileExists(FontFile) ? FSlateFontInfo(FontFile, 22)
            : FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), 22);
        Overlay = SNew(SBox)
            .HAlign(HAlign_Center).VAlign(VAlign_Center)
            .Visibility(EVisibility::HitTestInvisible)
            [
                SNew(SBox).WidthOverride(370).MinDesiredHeight(54)
                [
                    SNew(SOverlay)
                    + SOverlay::Slot()[SNew(SImage).Image(&EncounterPanel).ColorAndOpacity(FLinearColor(1, 1, 1, .72f))]
                    + SOverlay::Slot().Padding(12,5).VAlign(VAlign_Center).HAlign(HAlign_Center)
                    [
                        SNew(SHorizontalBox)
                        + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,10,0)
                        [SAssignNew(PromptIcon, SImage).DesiredSizeOverride(FVector2D(39,33)).Visibility(EVisibility::Collapsed)]
                        + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
                        [
                            SAssignNew(PromptText, STextBlock)
                            .Font(Font).Justification(ETextJustify::Center)
                            .ColorAndOpacity(FLinearColor(.87f,.95f,.97f))
                        ]
                    ]
                ]
            ];
        Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 100);
    }
    Show(TEXT("Un ladrón se acerca"));
    PlayRobberySound(*Actor);
    return true;
}

UAnimSequence* UBogotaRobbery::FindClip(const TCHAR* Clip) const
{
    const FString Name = FString::Printf(TEXT("AN_%s_%s"), GetCharacterName(), Clip);
    const FString Path = FString::Printf(TEXT("/Game/Robbery/%s/%s.%s"), GetCharacterName(), *Name, *Name);
    return LoadObject<UAnimSequence>(nullptr, *Path);
}

void UBogotaRobbery::PlayClip(const TCHAR* Clip, bool bLoop)
{
    if (!PlayThiefAnimation(*Thief->GetSkeletalMeshComponent(), FindClip(Clip), bLoop))
    {
        UE_LOG(LogTemp, Warning, TEXT("Missing robbery animation: %s %s"), GetCharacterName(), Clip);
    }
}

bool UBogotaRobbery::ShowPromptIcon(APlayerController* Controller)
{
    if (!PromptIcon || Prompt < 0 || Prompt >= 4) return false;
    int32 Family = 0;
    if (const auto* LocalUser = Controller ? Controller->GetLocalPlayer() : nullptr)
    {
        if (const auto* Devices = UInputDeviceSubsystem::Get())
        {
            const auto Hardware = Devices->GetMostRecentlyUsedHardwareDevice(LocalUser->GetPlatformUserId());
            if (Hardware.PrimaryDeviceType == EHardwareDevicePrimaryType::Gamepad)
            {
                const FString Id = Hardware.HardwareDeviceIdentifier.ToString();
                Family = Id.Contains(TEXT("DualSense")) || Id.Contains(TEXT("DualShock")) ||
                    Id.Contains(TEXT("PlayStation")) || Id.Contains(TEXT("Sony")) ? 2 : 1;
            }
        }
    }
    const int32 Index = Family * 4 + Prompt;
    if (PromptArt != Index || !PromptBrush)
    {
        const FString Path = FPaths::Combine(FPaths::ProjectPluginsDir(),
            FString::Printf(TEXT("BogotaPhonePreview/Resources/Robo%d%d.png"), Family, Prompt));
        UTexture2D* Texture = FImageUtils::ImportFileAsTexture2D(Path);
        if (!Texture) return false;
        Texture->Filter = TF_Bilinear;
        Texture->UpdateResource();
        if (PromptBrush)
            if (auto* Previous = PromptBrush->GetResourceObject()) Previous->RemoveFromRoot();
        Texture->AddToRoot();
        PromptBrush = MakeShared<FSlateBrush>();
        PromptBrush->SetResourceObject(Texture);
        PromptIcon->SetImage(PromptBrush.Get());
        PromptArt = Index;
    }
    PromptIcon->SetVisibility(EVisibility::HitTestInvisible);
    return true;
}

void UBogotaRobbery::Show(const FString& Message)
{
    if (PromptIcon && !Message.StartsWith(TEXT("ZÁFATE"))) PromptIcon->SetVisibility(EVisibility::Collapsed);
    if (PromptText.IsValid())
    {
        PromptText->SetText(FText::FromString(Message));
    }
}

void UBogotaRobbery::AdvancePrompt()
{
    const int32 Offset = FMath::RandRange(1, 3);
    Prompt = Prompt == INDEX_NONE ? FMath::RandRange(0, 3) : (Prompt + Offset) % 4;
    TimeLeft = FMath::Clamp(PromptSeconds.GetValueOnGameThread(), 1.25f, 5.f) * (1.f - .20f * FMath::Clamp(Step, 0, 2));
}

void UBogotaRobbery::FinishPrompt(bool bEscaped)
{
    ASkeletalMeshActor* Actor = Thief.Get();
    if (!bEscaped && !bRayasEncounter)
    {
        if (ReadFlag(Player.Get(), TEXT("Riding")))
        {
            Phase = EPhase::ForcedDismount;
            TimeLeft = ForcedDismountSeconds;
            bDismountRequested = false;
            Show(TEXT("El ladrón te baja del vehículo."));
            return;
        }
        if (BeginVehicleEscape())
        {
            bGameplayEncounter = false;
            EncounterDelivery.Reset();
            PlayRobberySound(*Actor);
            OnEncounterResolved.Broadcast(false, false);
            return;
        }
    }
    ReleaseMovement();
    StartRetreat();
    Show(bEscaped ? TEXT("Lograste zafarte.") : TEXT("QTE fallido."));
    if (bGameplayEncounter)
    {
        bGameplayEncounter = false;
        if (UObject* Delivery = EncounterDelivery.Get(); Delivery && !bEscaped && bRayasEncounter)
        {
            const FIntProperty* Balance = FindFProperty<FIntProperty>(Delivery->GetClass(), TEXT("Balance"));
            UFunction* Save = Delivery->FindFunction(TEXT("SaveProfile"));
            const FBoolProperty* Saved = Save ? CastField<FBoolProperty>(Save->GetReturnProperty()) : nullptr;
            if (Balance && Saved && Save->NumParms == 1)
            {
                const int32 Before = Balance->GetPropertyValue_InContainer(Delivery);
                const int32 Loss = CalculateBalanceLoss(Before);
                if (Loss > 0)
                {
                    Balance->SetPropertyValue_InContainer(Delivery, Before - Loss);
                    FStructOnScope Params(Save);
                    Delivery->ProcessEvent(Save, Params.GetStructMemory());
                    if (Saved->GetPropertyValue_InContainer(Params.GetStructMemory()))
                    {
                        if (FTextProperty* Status = FindFProperty<FTextProperty>(Delivery->GetClass(), TEXT("StatusMessage")))
                        {
                            Status->SetPropertyValue_InContainer(Delivery, FText::FromString(
                                FString::Printf(TEXT("Perdiste %d COP."), Loss)));
                        }
                        Show(FString::Printf(TEXT("Perdiste %d COP."), Loss));
                        PlayRobberySound(*Actor);
                    }
                    else
                    {
                        Balance->SetPropertyValue_InContainer(Delivery, Before);
                    }
                }
            }
        }
        EncounterDelivery.Reset();
        OnEncounterResolved.Broadcast(bRayasEncounter, bEscaped);
    }
}

#if !UE_BUILD_SHIPPING
void UBogotaRobbery::ReadDeveloperCode()
{
    UWorld* World = GetWorld();
    APlayerController* Controller = World->GetFirstPlayerController();
    APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
    const auto* DeliveryField = Pawn
        ? FindFProperty<FObjectPropertyBase>(Pawn->GetClass(), TEXT("Delivery")) : nullptr;
    const UObject* Delivery = DeliveryField ? DeliveryField->GetObjectPropertyValue_InContainer(Pawn) : nullptr;
    const auto* PhoneOpen = Delivery ? FindFProperty<FBoolProperty>(Delivery->GetClass(), TEXT("PhoneOpen")) : nullptr;
    if (!IsDeveloperMode(World) || (PhoneOpen && PhoneOpen->GetPropertyValue_InContainer(Delivery)) ||
        World->IsPaused())
    {
        DeveloperCode.Reset();
        return;
    }

    const double Now = World->GetRealTimeSeconds();
    if (Now - LastDeveloperKey > 3.)
    {
        DeveloperCode.Reset();
    }

    TCHAR Letter = 0;
    for (TCHAR Key = TEXT('A'); Key <= TEXT('Z'); ++Key)
    {
        if (Controller->WasInputKeyJustPressed(FKey(FName(*FString::Chr(Key)))))
        {
            Letter = Key;
            break;
        }
    }
    if (Letter == 0)
    {
        return;
    }

    LastDeveloperKey = Now;
    DeveloperCode.AppendChar(Letter);
    DeveloperCode = DeveloperCode.Right(8);
    const bool bAbelardo = DeveloperCode.EndsWith(TEXT("ABELARDO"));
    if (bAbelardo || DeveloperCode.EndsWith(TEXT("NERO")) || DeveloperCode.EndsWith(TEXT("LADRON")))
    {
        DeveloperCode.Reset();
        StartPreview(bAbelardo ? TEXT("Rayas") : TEXT("Hornets"));
    }
}
#endif

bool UBogotaRobbery::CanStealVehicle(const UObject* Delivery) const
{
    const FByteProperty* Type = Delivery ? FindFProperty<FByteProperty>(Delivery->GetClass(), TEXT("Vehicle")) : nullptr;
    if (!Type)
    {
        return false;
    }
    if (Type->GetPropertyValue_InContainer(Delivery) == 1)
    {
        return true;
    }
    const FIntProperty* Balance = FindFProperty<FIntProperty>(Delivery->GetClass(), TEXT("Balance"));
    return ActivePlaySeconds >= BikeProtectionSeconds && Balance &&
        Balance->GetPropertyValue_InContainer(Delivery) >= BikeRescueCost;
}

void UBogotaRobbery::PlanEscape(APlayerController& Controller, const FVector& Start, const FCollisionQueryParams& Params)
{
    UWorld* World = GetWorld();
    EscapeRoute.Reset();
    EscapeBuilding.Reset();
    EscapeInstance = INDEX_NONE;
    EscapeWaypoint = 0;
    EscapeReplanTime = 1.f;
    OutOfSightTime = 0.f;
    double BestLength = 14000.0;
    TArray<FHitResult, TInlineAllocator<36>> NearbyWalls;
    for (int32 Ray = 0; Ray < 36; ++Ray)
    {
        const FVector Eye = Start + FVector(0, 0, 140);
        const FVector Direction = FRotator(0, Ray * 10.0, 0).Vector();
        FHitResult Wall;
        if (!World->LineTraceSingleByChannel(Wall, Eye, Eye + Direction * 6500.0, ECC_Visibility, Params) ||
            FMath::Abs(Wall.ImpactNormal.Z) > .25)
        {
            continue;
        }
        NearbyWalls.Add(Wall);
    }
    NearbyWalls.StableSort([](const FHitResult& A, const FHitResult& B) { return A.Distance < B.Distance; });
    TSet<TPair<UPrimitiveComponent*, int32>> Examined;
    for (const FHitResult& Wall : NearbyWalls)
    {
        UPrimitiveComponent* Building = Wall.GetComponent();
        if (!Building || Building->Mobility != EComponentMobility::Static)
        {
            continue;
        }
        const auto Key = TPair<UPrimitiveComponent*, int32>(Building, Wall.Item);
        if (Examined.Contains(Key))
        {
            continue;
        }
        Examined.Add(Key);
        FBox Box = Building->Bounds.GetBox();
        if (const UInstancedStaticMeshComponent* Instances = Cast<UInstancedStaticMeshComponent>(Building))
        {
            FTransform Transform;
            if (!Instances->GetStaticMesh() || !Instances->GetInstanceTransform(Wall.Item, Transform, true))
            {
                continue;
            }
            Box = Instances->GetStaticMesh()->GetBoundingBox().TransformBy(Transform);
        }
        const FVector Size = Box.GetSize();
        if (Size.X < 250.0 || Size.Y < 250.0 || Size.Z < 230.0 ||
            Size.X > 9000.0 || Size.Y > 9000.0)
        {
            continue;
        }
        for (const double Clearance : {135.0, 265.0})
        {
            const FBox Perimeter = Box.ExpandBy(Clearance);
            const FVector Corners[] = {
                {Perimeter.Min.X, Perimeter.Min.Y, Start.Z}, {Perimeter.Max.X, Perimeter.Min.Y, Start.Z},
                {Perimeter.Max.X, Perimeter.Max.Y, Start.Z}, {Perimeter.Min.X, Perimeter.Max.Y, Start.Z}
            };
            for (int32 Entry = 0; Entry < 4; ++Entry)
            {
                FVector First = Corners[Entry];
                if (FVector::Dist2D(Start, First) >= BestLength ||
                    !CheckEscapeSegment(World, Start, First, Params))
                {
                    continue;
                }
                for (const int32 Turn : {-1, 1})
                {
                    TArray<FVector> Route{First};
                    double Length = FVector::Dist2D(Start, First);
                    for (int32 Side = 1; Side <= 3; ++Side)
                    {
                        const FVector From = Route.Last();
                        FVector To = Corners[(Entry + Turn * Side + 4) % 4];
                        Length += FVector::Dist2D(From, To);
                        if (Length >= BestLength || !CheckEscapeSegment(World, From, To, Params))
                        {
                            break;
                        }
                        Route.Add(To);
                        if (IsBehindBuilding(Controller, *Building, Wall.Item, To + FVector(0, 0, 45), Params) &&
                            IsBehindBuilding(Controller, *Building, Wall.Item, To + FVector(0, 0, 175), Params))
                        {
                            EscapeRoute = Route;
                            EscapeBuilding = Building;
                            EscapeInstance = Wall.Item;
                            BestLength = Length;
                            break;
                        }
                    }
                }
            }
        }
        if (EscapeBuilding.IsValid())
        {
            break;
        }
    }
    if (EscapeRoute.IsEmpty())
    {
        EscapeRoute.Add(PickRetreatDestination(Controller, Start, Params));
    }
    else
    {
        UE_LOG(LogTemp, Display, TEXT("Robbery escape: %s route around %s, %d waypoints, %.0f cm"),
            GetCharacterName(), *GetNameSafe(EscapeBuilding.Get()), EscapeRoute.Num(), BestLength);
    }
}

FVector UBogotaRobbery::AdvanceEscape(APlayerController& Controller, const FVector& Current, double Speed,
    float DeltaTime, const FCollisionQueryParams& Params)
{
    EscapeReplanTime -= DeltaTime;
    if (EscapeWaypoint < EscapeRoute.Num())
    {
        const FVector Target = EscapeRoute[EscapeWaypoint];
        const FVector Direction = (Target - Current).GetSafeNormal2D();
        const double Distance = FVector::Dist2D(Current, Target);
        const double Travel = FMath::Min(Speed * FMath::Min(DeltaTime, .05f), Distance);
        FVector Next = Current + Direction * Travel;
        if (CheckEscapeSegment(GetWorld(), Current, Next, Params))
        {
            if (Distance - Travel < 1.0)
            {
                ++EscapeWaypoint;
                if (EscapeWaypoint >= EscapeRoute.Num())
                {
                    EscapeReplanTime = 0.f;
                }
            }
            return Next;
        }
    }
    if (EscapeReplanTime <= 0.f && OutOfSightTime <= 0.f)
    {
        // A clear stretch in an open area can lead to a reachable house.
        // Recheck at the end of each stretch or when the current path is blocked.
        PlanEscape(Controller, Current, Params);
    }
    return Current;
}

bool UBogotaRobbery::CanFinishEscape(APlayerController& Controller, AActor& Actor, AActor* Vehicle,
    float DeltaTime, const FCollisionQueryParams& Params)
{
    const APawn* Pawn = Controller.GetPawn();
    const UPrimitiveComponent* Building = EscapeBuilding.Get();
    const bool bFarInOpen = !Building && Pawn &&
        FVector::DistSquared2D(Pawn->GetActorLocation(), Actor.GetActorLocation()) >= FMath::Square(OpenEscapeDistance);
    const auto IsHidden = [&](AActor& Candidate)
    {
        return IsEscapeActorOccluded(Controller, Candidate, Params, Building, EscapeInstance) ||
            (bFarInOpen && IsOutsideEscapeView(Controller, Candidate));
    };
    const bool bHidden = (Building || bFarInOpen) && IsHidden(Actor) && (!Vehicle || IsHidden(*Vehicle));
    OutOfSightTime = bHidden ? OutOfSightTime + DeltaTime : 0.f;
    return OutOfSightTime >= (Building ? BuildingCoverSeconds : OffscreenGraceSeconds) &&
        RetreatElapsed >= MinimumRetreatSeconds;
}

void UBogotaRobbery::StartRetreat()
{
    Phase = EPhase::Retreat;
    TimeLeft = RetreatSeconds;
    RetreatElapsed = OutOfSightTime = 0.f;
    ASkeletalMeshActor* Actor = Thief.Get();
    APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    FCollisionQueryParams Query(SCENE_QUERY_STAT(BogotaRobberyRetreat), false, Actor);
    Query.AddIgnoredActor(Player.Get());
    Query.AddIgnoredActor(ParkedTwoWheeler(Player.Get()));
    PlanEscape(*Controller, Actor->GetActorLocation(), Query);
    PlayClip(TEXT("Run"), true);
}

bool UBogotaRobbery::TrackGrabPosition(float DeltaTime)
{
    ASkeletalMeshActor* Actor = Thief.Get();
    APawn* Pawn = Player.Get();
    const FVector Current = Actor->GetActorLocation();
    const FRotator PawnYaw(0, Pawn->GetActorRotation().Yaw, 0);
    const FVector Behind = -PawnYaw.Vector();
    const FVector Goal = Pawn->GetActorLocation() + Behind * GrabDistance;
    const bool bChasing = Phase == EPhase::Approach;
    const double Speed = bChasing
        ? FMath::Max(MinimumChaseSpeed, Pawn->GetVelocity().Size2D() + ChaseSpeedAdvantage)
        : 650.0;
    const FVector Target(Goal.X, Goal.Y, Current.Z);
    const FVector DirectStep = FMath::VInterpConstantTo(Current, Target, DeltaTime, Speed);
    FCollisionQueryParams Route(SCENE_QUERY_STAT(BogotaRobberyApproach), false, Actor);
    Route.AddIgnoredActor(Pawn);
    Route.AddIgnoredActor(PlayerTwoWheeler(Pawn));
    FVector Next = DirectStep;
    if (!CheckEscapeSegment(GetWorld(), Current, Next, Route))
    {
        if (!bChasing)
        {
            return false;
        }
        // Take a clear step to either side when a corner blocks the direct line.
        const FVector ChaseStep = DirectStep - Current;
        Next = Current;
        for (const double Angle : {45.0, -45.0, 80.0, -80.0})
        {
            FVector Candidate = Current + ChaseStep.RotateAngleAxis(Angle, FVector::UpVector);
            if (CheckEscapeSegment(GetWorld(), Current, Candidate, Route))
            {
                Next = Candidate;
                break;
            }
        }
    }
    const bool bAtPlayer = FVector::DistSquared2D(Next, Goal) <= FMath::Square(6.0) &&
        FMath::Abs(Next.Z - Pawn->GetActorLocation().Z) <= 160.0;
    const FVector Travel = (Next - Current).GetSafeNormal2D();
    const USkeletalMesh* Mesh = Actor->GetSkeletalMeshComponent()->GetSkeletalMeshAsset();
    const FVector Facing = bChasing && !bAtPlayer && !Travel.IsNearlyZero() ? Travel : -Behind;
    Actor->SetActorLocationAndRotation(Next, FaceTravelDirection(*Mesh, Facing));
    if (bChasing)
    {
        Actor->GetSkeletalMeshComponent()->SetPlayRate(Travel.IsNearlyZero() ? 0.f :
            static_cast<float>(FMath::Clamp(Speed / MinimumChaseSpeed, 1.0, 2.0)));
    }
    return bAtPlayer;
}

void UBogotaRobbery::Tick(float DeltaTime)
{
    UpdateRescuePanel();
    if (!GetWorld()->IsPaused() && !IsConsoleOpen(GetWorld()))
    {
        const APlayerController* Controller = GetWorld()->GetFirstPlayerController();
        if (Controller && Controller->GetPawn())
        {
            ActivePlaySeconds += DeltaTime;
        }
    }
#if !UE_BUILD_SHIPPING
    if (!Thief.IsValid())
    {
        ReadDeveloperCode();
    }
#endif
    if (!Thief.IsValid())
    {
        if (Overlay.IsValid())
        {
            CancelPreview();
        }
        return;
    }
    APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    if (!Player.IsValid() || !Controller || Controller->GetPawn() != Player.Get())
    {
        CancelPreview();
        return;
    }

    if (GetWorld()->IsPaused() || (!bGameplayEncounter && IsConsoleOpen(GetWorld())))
    {
        return;
    }

    TimeLeft -= DeltaTime;
    if (bMovementLocked && ReadFlag(Player.Get(), TEXT("Riding")))
    {
        if (const FNumericProperty* Speed = FindFProperty<FNumericProperty>(Player->GetClass(), TEXT("BikeSpeed"));
            Speed && Speed->IsFloatingPoint())
        {
            Speed->SetFloatingPointPropertyValue(Speed->ContainerPtrToValuePtr<void>(Player.Get()), 0.);
        }
        if (UPawnMovementComponent* Movement = Player->GetMovementComponent())
        {
            Movement->StopMovementImmediately();
        }
    }
    if (Phase == EPhase::ForcedDismount)
    {
        if (!bDismountRequested)
        {
            bDismountRequested = true;
            if (UFunction* Dismount = Player->FindFunction(TEXT("MountPressed"));
                Dismount && Dismount->NumParms == 0)
            {
                Player->ProcessEvent(Dismount, nullptr);
            }
        }
        const bool bDismounted = ParkedTwoWheeler(Player.Get()) != nullptr;
        if (bDismounted && BeginVehicleEscape())
        {
            bGameplayEncounter = false;
            EncounterDelivery.Reset();
            PlayRobberySound(*Thief.Get());
            OnEncounterResolved.Broadcast(false, false);
        }
        else if (bDismounted || TimeLeft <= 0.f)
        {
            UE_LOG(LogTemp, Warning, TEXT("Robbery: forced dismount did not yield a stealable vehicle"));
            ReleaseMovement();
            StartRetreat();
            bGameplayEncounter = false;
            EncounterDelivery.Reset();
            OnEncounterResolved.Broadcast(false, false);
            Show(TEXT("El ladrón se retira."));
        }
        return;
    }
    if (Phase == EPhase::Approach)
    {
        const bool bAtPlayer = TrackGrabPosition(DeltaTime);
        if (!bAtPlayer && TimeLeft <= 0.f)
        {
            FinishPrompt(true);
            return;
        }
        FootstepTime -= DeltaTime;
        if (FootstepTime <= 0.f)
        {
            FootstepTime = .25f;
            UBogotaAudioLibrary::PlayRobberyFootstep(*Thief.Get());
        }
        if (bAtPlayer)
        {
            LockMovement(*Controller);
            Phase = EPhase::Prompt;
            Step = Errors = 0;
            Prompt = INDEX_NONE;
            PlayClip(TEXT("Prompt"), true);
            Thief->GetSkeletalMeshComponent()->SetPlayRate(1.f);
            PlayRobberySound(*Thief.Get());
            AdvancePrompt();
        }
        return;
    }
    if (Phase == EPhase::VehicleApproach || Phase == EPhase::VehicleMount || Phase == EPhase::VehicleEscape)
    {
        TickVehicleEscape(DeltaTime);
        return;
    }
    if (Phase == EPhase::Retreat)
    {
        RetreatElapsed += DeltaTime;
        ASkeletalMeshActor* Actor = Thief.Get();
        const FVector Current = Actor->GetActorLocation();
        FCollisionQueryParams Params(SCENE_QUERY_STAT(BogotaRobberyRetreat), false, Actor);
        Params.AddIgnoredActor(Player.Get());
        Params.AddIgnoredActor(ParkedTwoWheeler(Player.Get()));
        const double Acceleration = FMath::Clamp(RetreatElapsed / .30, 0.0, 1.0);
        const double Speed = FMath::Lerp(900.0, RetreatSpeed, Acceleration);
        const FVector Next = AdvanceEscape(*Controller, Current, Speed, DeltaTime, Params);
        const FVector Direction = (Next - Current).GetSafeNormal2D();
        Actor->GetSkeletalMeshComponent()->SetPlayRate(Direction.IsNearlyZero() ? 0.f : 1.45f);
        if (!Direction.IsNearlyZero())
        {
            const USkeletalMesh* Mesh = Actor->GetSkeletalMeshComponent()->GetSkeletalMeshAsset();
            const FRotator Heading = FMath::RInterpConstantTo(
                Actor->GetActorRotation(), FaceTravelDirection(*Mesh, Direction), DeltaTime, 1080.f);
            Actor->SetActorLocationAndRotation(Next, Heading);
        }

        if (TimeLeft <= 0.f && Overlay.IsValid())
        {
            Overlay->SetVisibility(EVisibility::Collapsed);
        }
        if (CanFinishEscape(*Controller, *Actor, nullptr, DeltaTime, Params))
        {
            CancelPreview();
        }
        return;
    }

    if (!TrackGrabPosition(DeltaTime))
    {
        FinishPrompt(true);
        return;
    }
    if (TimeLeft <= 0.f)
    {
        FinishPrompt(false);
        return;
    }
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Keyboard); ++Index)
    {
        if (Controller->WasInputKeyJustPressed(Keyboard[Index]) ||
            Controller->WasInputKeyJustPressed(Gamepad[Index]))
        {
            if (Index == Prompt)
            {
                if (++Step == 3)
                {
                    FinishPrompt(true);
                    return;
                }
                AdvancePrompt();
            }
            else if (++Errors == 2)
            {
                FinishPrompt(false);
                return;
            }
            break;
        }
    }
    if (ShowPromptIcon(Controller))
    {
        Show(FString::Printf(TEXT("ZÁFATE   %d / 3    %.1f s"), Step + 1, TimeLeft));
        return;
    }
    Show(FString::Printf(TEXT("ZÁFATE   %d / 3\nPulsa %s\nMando: %s    %.1f s"),
        Step + 1, *Keyboard[Prompt].GetFName().ToString(), PadLabels[Prompt], TimeLeft));
}

void UBogotaRobbery::LockMovement(APlayerController& Controller)
{
    APawn* Pawn = Player.Get();
    Controller.SetIgnoreMoveInput(true);
    bMovementLocked = true;
    Pawn->ConsumeMovementInputVector();
    if (UPawnMovementComponent* Movement = Pawn->GetMovementComponent())
    {
        Movement->StopMovementImmediately();
        if (UCharacterMovementComponent* Walking = Cast<UCharacterMovementComponent>(Movement);
            Walking && Walking->IsMovingOnGround() && !ReadFlag(Pawn, TEXT("Riding")))
        {
            PreviousMovementMode = Walking->MovementMode;
            FrozenWalkingMovement = Walking;
            Walking->DisableMovement();
        }
    }

    // The mount action shares F and the left face button with the QTE.
    // Consume the action while keeping raw key presses available to the QTE.
    UInputComponent* Input = NewObject<UInputComponent>(&Controller);
    FInputActionBinding Mount(TEXT("AnimatedMount"), IE_Pressed);
    Mount.ActionDelegate.GetDelegateForManualSet().BindLambda([] {});
    Input->AddActionBinding(MoveTemp(Mount));
    Controller.AddInstanceComponent(Input);
    Controller.PushInputComponent(Input);
    MountInputGuard = Input;
}

void UBogotaRobbery::ReleaseMovement()
{
    if (UCharacterMovementComponent* Walking = FrozenWalkingMovement.Get())
    {
        if (Walking->MovementMode == MOVE_None)
        {
            Walking->SetMovementMode(static_cast<EMovementMode>(PreviousMovementMode));
        }
    }
    FrozenWalkingMovement.Reset();
    if (bMovementLocked)
    {
        if (APlayerController* Controller = GetWorld()->GetFirstPlayerController())
        {
            if (UInputComponent* Input = MountInputGuard.Get())
            {
                Controller->PopInputComponent(Input);
                Input->DestroyComponent();
            }
            Controller->SetIgnoreMoveInput(false);
        }
        MountInputGuard.Reset();
        bMovementLocked = false;
    }
}

void UBogotaRobbery::CancelPreview()
{
    ReleaseMovement();
    if (Phase == EPhase::VehicleApproach || Phase == EPhase::VehicleMount || Phase == EPhase::VehicleEscape)
    {
        if (AActor* Vehicle = RetainedVehicle.Get())
        {
            Vehicle->SetActorHiddenInGame(bVehicleWasHidden);
            Vehicle->SetActorEnableCollision(bVehicleHadCollision);
        }
        RetainedVehicle.Reset();
        RescueDelivery.Reset();
    }
    Phase = EPhase::Approach;
    EscapeRoute.Reset();
    EscapeBuilding.Reset();
    VehicleMountClip = nullptr;
    VehicleRideClip = nullptr;
    if (OverlayViewport.IsValid() && Overlay.IsValid())
    {
        OverlayViewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
    }
    Overlay.Reset();
    PromptText.Reset();
    PromptIcon.Reset();
    if (PromptBrush)
        if (auto* Texture = PromptBrush->GetResourceObject()) Texture->RemoveFromRoot();
    PromptBrush.Reset();
    if (auto* Texture = EncounterPanel.GetResourceObject()) Texture->RemoveFromRoot();
    EncounterPanel.SetResourceObject(nullptr);
    PromptArt = INDEX_NONE;
    OverlayViewport.Reset();
    if (ASkeletalMeshActor* Actor = Thief.Get())
    {
        Actor->Destroy();
    }
    bGameplayEncounter = false;
    EncounterDelivery.Reset();
    Thief.Reset();
    RobberyVoice.Reset();
    Player.Reset();
}

void UBogotaRobbery::RemoveRescuePanel()
{
    if (UNativeWidgetHost* Tile = RescueTile.Get())
    {
        Tile->RemoveFromParent();
    }
    if (UNativeWidgetHost* Page = RescuePage.Get())
    {
        Page->RemoveFromParent();
    }
    RescueTile.Reset();
    RescuePage.Reset();
}

bool UBogotaRobbery::BeginVehicleEscape()
{
    APawn* Pawn = Player.Get();
    UObject* Delivery = FindDeliveryCore(Pawn);
    AActor* Vehicle = ParkedTwoWheeler(Pawn);
    const FByteProperty* Type = Delivery ? FindFProperty<FByteProperty>(Delivery->GetClass(), TEXT("Vehicle")) : nullptr;
    if (!Type || !Vehicle || RetainedVehicle.IsValid() || (bGameplayEncounter && !CanStealVehicle(Delivery)) ||
        FVector::DistSquared2D(Vehicle->GetActorLocation(), Pawn->GetActorLocation()) > FMath::Square(420.0))
    {
        UE_LOG(LogTemp, Warning, TEXT("Vehicle escape: unavailable parked vehicle or rescue already active"));
        return false;
    }

    FCollisionQueryParams Params(SCENE_QUERY_STAT(BogotaVehicleEscape), false, Vehicle);
    Params.AddIgnoredActor(Pawn);
    Params.AddIgnoredActor(Thief.Get());
    const FVector Start = Vehicle->GetActorLocation();

    const bool bMoto = Type->GetPropertyValue_InContainer(Delivery) == 1;
    UAnimSequence* Ride = FindClip(bMoto ? TEXT("MotoRide") : TEXT("BikePedal"));
    UAnimSequence* Mount = nullptr;
    if (!Ride)
    {
        UE_LOG(LogTemp, Warning, TEXT("Vehicle escape: missing ride animation"));
        return false;
    }

    const FVector Current = Thief->GetActorLocation();
    const FVector Right = Vehicle->GetActorRightVector().GetSafeNormal2D();
    const double NearSide = FVector::DotProduct(Current - Start, Right) >= 0 ? 1.0 : -1.0;
    for (const double Side : {NearSide, -NearSide})
    {
        FVector Candidate = FVector(Start.X, Start.Y, Current.Z) + Right * (Side * 65.0);
        if (CheckEscapeSegment(GetWorld(), Current, Candidate, Params))
        {
            const TCHAR* Clip = bMoto
                ? (Side < 0 ? TEXT("MountMotoLeft") : TEXT("MountMoto"))
                : (Side < 0 ? TEXT("MountBikeLeft") : TEXT("MountBike"));
            if ((Mount = FindClip(Clip)) != nullptr)
            {
                MountFrom = Candidate;
                break;
            }
        }
    }
    if (!Mount)
    {
        UE_LOG(LogTemp, Warning, TEXT("Vehicle escape: no accessible mount side with an animation"));
        return false;
    }

    RetainedVehicle = Vehicle;
    RescueDelivery = Delivery;
    bVehicleWasHidden = Vehicle->IsHidden();
    bVehicleHadCollision = Vehicle->GetActorEnableCollision();
    RescueCost = bMoto ? MotoRescueCost : BikeRescueCost;
    bRescuePaid = false;
    RescueStatus = FText::GetEmpty();
    MountTo = Start;
    VehicleMountClip = Mount;
    VehicleRideClip = Ride;
    Phase = EPhase::VehicleApproach;
    TimeLeft = 4.f;
    PlayClip(TEXT("Walk"), true);
    RescueHeading = Vehicle->GetActorRotation();
    Show(bMoto ? TEXT("El ladr\u00f3n se lleva tu moto.") : TEXT("El ladr\u00f3n se lleva tu cicla."));
    return true;
}

void UBogotaRobbery::TickVehicleEscape(float DeltaTime)
{
    AActor* Vehicle = RetainedVehicle.Get();
    ASkeletalMeshActor* Actor = Thief.Get();
    USkeletalMeshComponent* MeshComponent = Actor ? Actor->GetSkeletalMeshComponent() : nullptr;
    if (!Vehicle || !MeshComponent || !MeshComponent->GetSkeletalMeshAsset() ||
        !IsValid(VehicleMountClip.Get()) || !IsValid(VehicleRideClip.Get()))
    {
        CancelPreview();
        return;
    }
    if (Phase == EPhase::VehicleApproach)
    {
        const FVector Current = Actor->GetActorLocation();
        const FVector Direction = (MountFrom - Current).GetSafeNormal2D();
        FVector Next = FMath::VInterpConstantTo(Current, MountFrom, DeltaTime, 400.f);
        FCollisionQueryParams Query(SCENE_QUERY_STAT(BogotaVehicleApproach), false, Actor);
        Query.AddIgnoredActor(Player.Get());
        Query.AddIgnoredActor(Vehicle);
        if (TimeLeft <= 0.f || !Vehicle->GetActorLocation().Equals(MountTo, 8.0) ||
            !FindRetreatStep(GetWorld(), Current, Next, Query))
        {
            RetainedVehicle.Reset();
            RescueDelivery.Reset();
            VehicleMountClip = nullptr;
            VehicleRideClip = nullptr;
            ReleaseMovement();
            StartRetreat();
            Show(TEXT("El ladr\u00f3n se retira."));
            return;
        }

        const USkeletalMesh* Mesh = Actor->GetSkeletalMeshComponent()->GetSkeletalMeshAsset();
        const bool bAtVehicle = FVector::DistSquared2D(Next, MountFrom) <= FMath::Square(2.0);
        const FVector Facing = bAtVehicle ? Vehicle->GetActorForwardVector() : Direction;
        Actor->SetActorLocationAndRotation(Next, FaceTravelDirection(*Mesh, Facing));
        if (bAtVehicle)
        {
            MountFrom = Next;
            Phase = EPhase::VehicleMount;
            MountSeconds = ThiefMountSeconds;
            TimeLeft = MountSeconds;
            const float MountRate = VehicleMountClip->GetPlayLength() / MountSeconds;
            if (!PlayThiefAnimation(*MeshComponent, VehicleMountClip.Get(), false, MountRate))
            {
                CancelPreview();
                return;
            }
            Vehicle->SetActorEnableCollision(false);
        }
        return;
    }

    if (Phase == EPhase::VehicleMount)
    {
        const float Alpha = 1.f - FMath::Clamp(TimeLeft / MountSeconds, 0.f, 1.f);
        Actor->SetActorLocation(FMath::Lerp(MountFrom, MountTo, FMath::SmoothStep(0.f, 1.f, Alpha)));
        if (TimeLeft <= 0.f)
        {
            if (!PlayThiefAnimation(*MeshComponent, VehicleRideClip.Get(), true))
            {
                CancelPreview();
                return;
            }
            APlayerController* Controller = GetWorld()->GetFirstPlayerController();
            if (!Controller)
            {
                CancelPreview();
                return;
            }
            FCollisionQueryParams RouteQuery(SCENE_QUERY_STAT(BogotaVehicleEscape), false, Vehicle);
            RouteQuery.AddIgnoredActor(Player.Get());
            RouteQuery.AddIgnoredActor(Actor);
            PlanEscape(*Controller, Vehicle->GetActorLocation(), RouteQuery);
            ReleaseMovement();
            Phase = EPhase::VehicleEscape;
            TimeLeft = 4.f;
            RetreatElapsed = OutOfSightTime = 0.f;
        }
        return;
    }

    RetreatElapsed += DeltaTime;
    const FVector Current = Vehicle->GetActorLocation();
    APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    if (!Controller)
    {
        CancelPreview();
        return;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(BogotaVehicleEscape), false, Vehicle);
    Params.AddIgnoredActor(Player.Get());
    Params.AddIgnoredActor(Actor);
    const FVector Next = AdvanceEscape(*Controller, Current, VehicleEscapeSpeed, DeltaTime, Params);
    const FVector Direction = (Next - Current).GetSafeNormal2D();
    const FRotator Heading = Direction.IsNearlyZero() ? Vehicle->GetActorRotation() : FMath::RInterpConstantTo(
        Vehicle->GetActorRotation(), Direction.Rotation(), DeltaTime, 720.f);
    Vehicle->SetActorLocationAndRotation(Next, Heading);
    const USkeletalMesh* Mesh = Actor->GetSkeletalMeshComponent()->GetSkeletalMeshAsset();
    Actor->SetActorLocationAndRotation(Next, FaceTravelDirection(*Mesh, Heading.Vector()));
    if (TimeLeft < 2.f && Overlay.IsValid())
    {
        Overlay->SetVisibility(EVisibility::Collapsed);
    }
    if (CanFinishEscape(*Controller, *Actor, Vehicle, DeltaTime, Params))
    {
        RescuePoint = Vehicle->GetActorLocation();
        RescueHeading = Vehicle->GetActorRotation();
        RescuePoint = PickVehiclePickup(GetWorld(), RescuePoint, RescueHeading, Params, RescueHeading);
        Vehicle->SetActorHiddenInGame(true);
        // Keep the existing actor and its equipment out of mounting range until release.
        Vehicle->SetActorLocation(RescuePoint + FVector(100000, 100000, -10000));
        Phase = EPhase::Retreat;
        CancelPreview();
    }

}

bool UBogotaRobbery::IsRobberyPromptActive() const
{
    return Thief.IsValid() && Phase == EPhase::Prompt;
}

int32 UBogotaRobbery::ServiceRescueQuote() const
{
    if (!RetainedVehicle.IsValid() || !RescueDelivery.IsValid() || Thief.IsValid()) return INDEX_NONE;
    return bRescuePaid ? 0 : RescueCost;
}

void UBogotaRobbery::PayServiceRescue()
{
    PayRescue();
}

FReply UBogotaRobbery::PayRescue()
{
    AActor* Vehicle = RetainedVehicle.Get();
    UObject* Delivery = RescueDelivery.Get();
    if (!Vehicle || !Delivery || bRescuePaid || Thief.IsValid())
    {
        return FReply::Handled();
    }
    const FIntProperty* Balance = FindFProperty<FIntProperty>(Delivery->GetClass(), TEXT("Balance"));
    const FBoolProperty* HasWaypoint = FindFProperty<FBoolProperty>(Delivery->GetClass(), TEXT("HasWaypoint"));
    const FStructProperty* Waypoint = FindFProperty<FStructProperty>(Delivery->GetClass(), TEXT("Waypoint"));
    if (!Balance || !HasWaypoint || !Waypoint || Waypoint->Struct != TBaseStructure<FVector>::Get())
    {
        RescueStatus = FText::FromString(TEXT("El rescate no est\u00e1 disponible."));
        return FReply::Handled();
    }
    const int32 Price = RescueCost;
    const int32 Before = Balance->GetPropertyValue_InContainer(Delivery);
    if (Before < Price)
    {
        RescueStatus = FText::FromString(TEXT("Saldo insuficiente. Re\u00fane el valor del rescate para recuperar tu veh\u00edculo."));
        return FReply::Handled();
    }
    Balance->SetPropertyValue_InContainer(Delivery, Before - Price);
    if (!SaveRescueBalance(*Delivery))
    {
        Balance->SetPropertyValue_InContainer(Delivery, Before);
        RescueStatus = FText::FromString(TEXT("No se pudo guardar el pago. Intenta otra vez."));
        return FReply::Handled();
    }
    bRescuePaid = true;
    Vehicle->SetActorLocationAndRotation(RescuePoint, RescueHeading);
    Vehicle->SetActorHiddenInGame(bVehicleWasHidden);
    Vehicle->SetActorEnableCollision(bVehicleHadCollision);
    PreviousWaypoint = *Waypoint->ContainerPtrToValuePtr<FVector>(Delivery);
    bPreviousWaypoint = HasWaypoint->GetPropertyValue_InContainer(Delivery);
    *Waypoint->ContainerPtrToValuePtr<FVector>(Delivery) = RescuePoint;
    HasWaypoint->SetPropertyValue_InContainer(Delivery, true);
    RescueStatus = FText::FromString(TEXT("Ubicaci\u00f3n marcada. Ve a recoger tu veh\u00edculo."));
    if (UFunction* Changed = Delivery->FindFunction(TEXT("Changed")); Changed && Changed->NumParms == 0)
    {
        Delivery->ProcessEvent(Changed, nullptr);
    }
    return FReply::Handled();
}

void UBogotaRobbery::UpdateRescuePanel()
{
    UObject* Delivery = RescueDelivery.Get();
    AActor* Vehicle = RetainedVehicle.Get();
    APlayerController* Controller = GetWorld()->GetFirstPlayerController();
    APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
    if (bRescuePaid && Vehicle && ReadFlag(Pawn, TEXT("Riding")) && PlayerTwoWheeler(Pawn) == Vehicle)
    {
        if (Delivery)
        {
            const FBoolProperty* HasWaypoint = FindFProperty<FBoolProperty>(Delivery->GetClass(), TEXT("HasWaypoint"));
            const FStructProperty* Waypoint = FindFProperty<FStructProperty>(Delivery->GetClass(), TEXT("Waypoint"));
            if (HasWaypoint && Waypoint && Waypoint->Struct == TBaseStructure<FVector>::Get())
            {
                FVector& Point = *Waypoint->ContainerPtrToValuePtr<FVector>(Delivery);
                if (HasWaypoint->GetPropertyValue_InContainer(Delivery) && Point.Equals(RescuePoint, 1.0))
                {
                    Point = PreviousWaypoint;
                    HasWaypoint->SetPropertyValue_InContainer(Delivery, bPreviousWaypoint);
                    if (UFunction* Changed = Delivery->FindFunction(TEXT("Changed")); Changed && Changed->NumParms == 0)
                    {
                        Delivery->ProcessEvent(Changed, nullptr);
                    }
                }
            }
        }
        RetainedVehicle.Reset();
        RescueDelivery.Reset();
        bRescuePaid = false;
        Delivery = nullptr;
    }
    if (!Vehicle || !ReadFlag(Delivery, TEXT("PhoneOpen")))
    {
        RemoveRescuePanel();
        return;
    }
    if (RescueTile.IsValid() && RescuePage.IsValid())
    {
        return;
    }

    TArray<UUserWidget*> Widgets;
    UWidgetBlueprintLibrary::GetAllWidgetsOfClass(this, Widgets, UUserWidget::StaticClass(), true);
    UCanvasPanel* Home = nullptr;
    for (UUserWidget* Widget : Widgets)
    {
        if (Widget->GetOwningPlayer() == Controller &&
            Widget->GetClass()->GetFName() == TEXT("WBP_BlueprintPhone_C"))
        {
            Home = Cast<UCanvasPanel>(Widget->GetWidgetFromName(TEXT("DesignerHome")));
            if (Home)
            {
                break;
            }
        }
    }
    if (!Home)
    {
        return;
    }

    RemoveRescuePanel();
    UNativeWidgetHost* Tile = NewObject<UNativeWidgetHost>(Home);
    UNativeWidgetHost* Page = NewObject<UNativeWidgetHost>(Home);
    RescueTile = Tile;
    RescuePage = Page;
    if (UCanvasPanelSlot* Slot = Home->AddChildToCanvas(Tile))
    {
        Slot->SetPosition(FVector2D(301, 370));
        Slot->SetSize(FVector2D(66, 110));
        Slot->SetZOrder(20);
    }
    if (UCanvasPanelSlot* Slot = Home->AddChildToCanvas(Page))
    {
        Slot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
        Slot->SetOffsets(FMargin(0.f));
        Slot->SetZOrder(21);
    }
    Page->SetVisibility(ESlateVisibility::Collapsed);
    Tile->SetContent(
        SNew(SButton)
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        .ButtonColorAndOpacity(FLinearColor(.08f, .46f, .55f))
        .OnClicked_Lambda([this]
        {
            if (UNativeWidgetHost* Host = RescuePage.Get())
            {
                Host->SetVisibility(ESlateVisibility::Visible);
            }
            return FReply::Handled();
        })
        [
            SNew(STextBlock).Text(FText::FromString(TEXT("Rescate")))
        ]);
    Page->SetContent(
        SNew(SBorder)
        .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
        .BorderBackgroundColor(FLinearColor(.035f, .065f, .10f))
        .Padding(24)
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot().AutoHeight()
            [
                SNew(SButton)
                .OnClicked_Lambda([this]
                {
                    if (UNativeWidgetHost* Host = RescuePage.Get())
                    {
                        Host->SetVisibility(ESlateVisibility::Collapsed);
                    }
                    return FReply::Handled();
                })
                [
                    SNew(STextBlock).Text(FText::FromString(TEXT("Volver")))
                ]
            ]
            + SVerticalBox::Slot().AutoHeight().Padding(0, 24, 0, 14)
            [
                SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Bold", 24))
                .Text(FText::FromString(TEXT("Rescate")))
            ]
            + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 18)
            [
                SNew(STextBlock).WrapTextAt(290.f).Text_Lambda([this]
                {
                    if (!RescueStatus.IsEmpty())
                    {
                        return RescueStatus;
                    }
                    return FText::FromString(RescueCost == MotoRescueCost
                        ? TEXT("Tu moto est\u00e1 retenida.") : TEXT("Tu cicla est\u00e1 retenida."));
                })
            ]
            + SVerticalBox::Slot().AutoHeight()
            [
                SNew(SButton).OnClicked_UObject(this, &UBogotaRobbery::PayRescue)
                .IsEnabled_Lambda([this] { return !bRescuePaid && !Thief.IsValid(); })
                [
                    SNew(STextBlock).Text_Lambda([this]
                    {
                        return bRescuePaid ? FText::FromString(TEXT("Consulta el mapa"))
                            : FText::FromString(FString::Printf(TEXT("Pagar %d COP"), RescueCost));
                    })
                ]
            ]
        ]);
}

void UBogotaRobbery::Deinitialize()
{
    CancelPreview();
    RemoveRescuePanel();
    Super::Deinitialize();
}


