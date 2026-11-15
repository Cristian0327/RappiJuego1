#include "BogotaRobbery.h"
#include "BogotaAudio.h"
#include "Algo/RandomShuffle.h"
#include "BogotaLaneLibrary.h"
#include "BogotaTwoWheelHandling.h"

#include "Blueprint/UserWidget.h"
#include "Components/AudioComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/WorldSettings.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "PhysicalMaterials/PhysicalMaterial.h"
#include "Sound/SoundWave.h"
#include "TimerManager.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"

#if BOGOTA_WITH_FMOD
#include "FMODAudioComponent.h"
#include "FMODBlueprintStatics.h"
#include "FMODEvent.h"
#include "fmod_studio.hpp"
#endif

DEFINE_LOG_CATEGORY_STATIC(LogBogotaAudio, Log, All);

namespace
{
#if BOGOTA_WITH_FMOD
UFMODEvent* TrafficEvent(FName Name)
{
    return LoadObject<UFMODEvent>(nullptr, *FString::Printf(TEXT("/Game/FMOD/Events/%s.%s"),
        *Name.ToString(), *Name.ToString()));
}

bool UpdateFmodEngine(TWeakObjectPtr<UFMODAudioComponent>& Loop, AActor& Vehicle,
    FName Name, float Volume, float Pitch, UAudioComponent* ExistingLoop)
{
    UFMODAudioComponent* Component = Loop.Get();
    if (!Component)
    {
        UFMODEvent* Event = TrafficEvent(Name);
        Component = UFMODBlueprintStatics::PlayEventAttached(Event, Vehicle.GetRootComponent(),
            NAME_None, FVector::ZeroVector, EAttachLocation::KeepRelativeOffset, true, false, true);
        if (!Component) return false;
        Component->Play();
        if (!Component->IsPlaying())
        {
            Component->DestroyComponent();
            return false;
        }
        if (ExistingLoop) ExistingLoop->Stop();
        Loop = Component;
        UE_LOG(LogBogotaAudio, Display, TEXT("FMOD engine: %s %s"), *Vehicle.GetName(), *Name.ToString());
    }
    Component->SetVolume(Volume);
    Component->SetPitch(Pitch);
    return true;
}
#endif

USoundWave* LoadClip(const TCHAR* Group, const TCHAR* Name)
{
    return LoadObject<USoundWave>(nullptr, *FString::Printf(
        TEXT("/Game/Audio/SharedSounds/%s/%s.%s"), Group, Name, Name));
}

template <typename T>
const T* Field(const UObject* Object, FName Name)
{
    return Object ? FindFProperty<T>(Object->GetClass(), Name) : nullptr;
}

double Number(const UObject* Object, FName Name, double Default = 0.)
{
    if (const auto* Property = Field<FNumericProperty>(Object, Name))
    {
        const void* Value = Property->ContainerPtrToValuePtr<void>(Object);
        if (Property->IsFloatingPoint()) return Property->GetFloatingPointPropertyValue(Value);
        return static_cast<double>(Property->GetSignedIntPropertyValue(Value));
    }
    return Default;
}

bool Flag(const UObject* Object, FName Name)
{
    const auto* Property = Field<FBoolProperty>(Object, Name);
    return Property && Property->GetPropertyValue_InContainer(Object);
}

UObject* ObjectField(const UObject* Object, FName Name)
{
    const auto* Property = Field<FObjectPropertyBase>(Object, Name);
    return Property ? Property->GetObjectPropertyValue_InContainer(Object) : nullptr;
}

FText TextField(const UObject* Object, FName Name)
{
    const auto* Property = Field<FTextProperty>(Object, Name);
    return Property ? Property->GetPropertyValue_InContainer(Object) : FText::GetEmpty();
}

FString ShopTheme(const AActor* Shop)
{
    if (const auto* Theme = Field<FNameProperty>(Shop, TEXT("ThemeID")))
        return Theme->GetPropertyValue_InContainer(Shop).ToString();
    return FString();
}

void UpdateLoop(UWorld* World, TObjectPtr<UAudioComponent>& Component, USoundWave* Sound,
    float Volume, float Pitch, float Dt, bool MenuSound = false, float Response = 4.f)
{
    if (!IsValid(Component.Get())) Component = nullptr;
    if (Component && Component->Sound != Sound)
    {
        Component->FadeOut(.18f, 0.f);
        Component = nullptr;
    }
    if (!Component && Sound && Volume > .005f)
    {
        Component = UGameplayStatics::CreateSound2D(World, Sound, Response > 4.f ? Volume : .01f, Pitch);
        if (Component)
        {
            Component->bIsUISound = MenuSound;
            Component->Play();
            UE_LOG(LogBogotaAudio, Display, TEXT("Loop started: %s"), *Sound->GetName());
        }
    }
    if (!Component) return;
    const float Next = FMath::FInterpTo(Component->VolumeMultiplier, Volume, Dt, Response);
    if (Next < .005f && Volume <= 0.f)
    {
        Component->Stop();
        Component = nullptr;
        return;
    }
    Component->SetVolumeMultiplier(Next);
    Component->SetPitchMultiplier(FMath::FInterpTo(Component->PitchMultiplier, Pitch, Dt, FMath::Max(5.f, Response)));
}

UAudioComponent* SpatialSound(UWorld& World, USoundWave* Sound, FVector Position,
    float Volume, float Range, USceneComponent* Parent = nullptr, float StartTime = 0.f, float Pitch = 1.f,
    float Priority = 1.f)
{
    if (!Sound || !World.AllowAudioPlayback()) return nullptr;
    auto* Component = NewObject<UAudioComponent>(Parent ? Parent->GetOwner() : World.GetWorldSettings());
    Component->bAutoDestroy = true;
    Component->bAutoActivate = false;
    Component->bOverrideAttenuation = true;
    Component->bOverridePriority = true;
    Component->Priority = Priority;
    Component->AttenuationOverrides.SpatializationAlgorithm = Sound->NumChannels == 1
        ? SPATIALIZATION_HRTF : SPATIALIZATION_Default;
    Component->AttenuationOverrides.AttenuationShapeExtents = FVector(120.f, 0.f, 0.f);
    Component->AttenuationOverrides.FalloffDistance = Range;
    Component->AttenuationOverrides.bEnableOcclusion = true;
    Component->AttenuationOverrides.OcclusionLowPassFilterFrequency = 2400.f;
    Component->AttenuationOverrides.OcclusionVolumeAttenuation = .58f;
    Component->AttenuationOverrides.OcclusionInterpolationTime = .22f;
    Component->OcclusionCheckInterval = .35f;
    Component->SetSound(Sound);
    Component->SetVolumeMultiplier(Volume);
    Component->SetPitchMultiplier(Pitch);
    if (Parent) Component->SetupAttachment(Parent);
    else Component->SetWorldLocation(Position);
    Component->RegisterComponent();
    Component->Play(StartTime);
    return Component;
}

void PlayPriorityCue(UWorld& World, USoundWave* Sound, float Volume, float Pitch)
{
    if (auto* Component = UGameplayStatics::CreateSound2D(&World, Sound, Volume, Pitch))
    {
        Component->bOverridePriority = true;
        Component->Priority = 3.f;
        Component->Play();
    }
}

enum class EStepSurface { Pavement, Shop, Road, Trail, Grass, Wood, Metal, Stair, Puddle };

EStepSurface StepSurface(const FHitResult& Hit, bool Indoors)
{
    const auto* Floor = Cast<UStaticMeshComponent>(Hit.GetComponent());
    const UStaticMesh* Mesh = Floor ? Floor->GetStaticMesh() : nullptr;
    const FString Name = (Mesh ? Mesh->GetName() : FString()) +
        (Hit.PhysMaterial.IsValid() ? Hit.PhysMaterial->GetName() : FString());
    if (Name.Contains(TEXT("Stair")) || Name.Contains(TEXT("Escalera"))) return EStepSurface::Stair;
    if (Name.Contains(TEXT("Puddle")) || Name.Contains(TEXT("Charco"))) return EStepSurface::Puddle;
    if (Name.Contains(TEXT("Wood")) || Name.Contains(TEXT("Madera"))) return EStepSurface::Wood;
    if (Name.Contains(TEXT("Metal")) || Name.Contains(TEXT("Grate"))) return EStepSurface::Metal;
    if (Indoors) return EStepSurface::Shop;
    if (Name.Contains(TEXT("Asphalt"))) return EStepSurface::Road;
    if (Name.Contains(TEXT("ParkSoil")) || Name.Contains(TEXT("Grass"))) return EStepSurface::Grass;
    if (Name == TEXT("SM_Rec_MonserratePath") ||
        Name == TEXT("SM_Bogota_CaminoMonserrate"))
        return EStepSurface::Trail;
    return EStepSurface::Pavement;
}

void PlayFootstep(UWorld& World, const UCharacterMovementComponent& Movement, bool Indoors,
    float Speed, bool Pedestrian = false, bool Wet = false)
{
    FVector Foot = Movement.GetActorFeetLocation();
    FHitResult Contact = Movement.CurrentFloor.HitResult;
    const auto* Character = Cast<ACharacter>(Movement.GetOwner());
    if (Character && Character->GetMesh())
    {
        const auto* Mesh = Character->GetMesh();
        const FName Left = TEXT("foot_l");
        const FName Right = TEXT("foot_r");
        if (Mesh->DoesSocketExist(Left) && Mesh->DoesSocketExist(Right))
        {
            const FVector A = Mesh->GetSocketLocation(Left);
            const FVector B = Mesh->GetSocketLocation(Right);
            const FVector Planted = A.Z < B.Z ? A : B;
            if (FVector::DistSquared(Planted, Foot) < FMath::Square(120.)) Foot = Planted;
        }
        FHitResult SurfaceHit;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(BogotaFootContact), false, Character);
        Query.bReturnPhysicalMaterial = true;
        if (World.LineTraceSingleByChannel(SurfaceHit, Foot + FVector(0, 0, 30), Foot - FVector(0, 0, 45),
            ECC_Visibility, Query))
            Contact = SurfaceHit;
    }
    const EStepSurface Surface = StepSurface(Contact, Indoors);
    const bool Running = Speed > 300.f;
    const TCHAR* Name = Surface == EStepSurface::Stair ? TEXT("Stairs") :
        Surface == EStepSurface::Trail || Surface == EStepSurface::Grass ? TEXT("Gravel") :
        Running ? TEXT("Run") : TEXT("Walk");
    const FString ClipName = FString::Printf(TEXT("Foot_%s_%d"), Name, FMath::RandRange(1, 5));
    USoundWave* Step = LoadClip(TEXT("Recorded"), *ClipName);
    if (!Step) return;
    const float Pitch = FMath::FRandRange(.96f, 1.04f);
    const float Volume = Pedestrian ? FMath::Clamp(Speed / 1600.f, .15f, .26f)
        : Running ? .90f : .76f;
    if (Pedestrian)
        SpatialSound(World, Step, Foot, Volume, 700.f, nullptr, 0.f, Pitch);
    else
    {
        PlayPriorityCue(World, Step, Volume, Pitch);
        if (Surface == EStepSurface::Puddle || (Wet && Surface == EStepSurface::Road))
            PlayPriorityCue(World, LoadClip(TEXT("WorldFoley"), TEXT("Step_Puddle")), .11f, Pitch);
    }
    UE_LOG(LogBogotaAudio, Verbose, TEXT("Footstep %s: %s"), Pedestrian ? TEXT("pedestrian") : TEXT("player"), *ClipName);
}

bool FemaleVoice(const USkeletalMeshComponent* Mesh)
{
    const USkeletalMesh* Model = Mesh ? Mesh->GetSkeletalMeshAsset() : nullptr;
    if (!Model) return false;
    const FName Name = Model->GetFName();
    if (Name == TEXT("SK_CustomerOffice") || Name == TEXT("SK_Cashier") ||
        Name == TEXT("SK_Pharmacist") || Name == TEXT("SK_Florist"))
        return true;
    const FString ModelName = Name.ToString();
    if (ModelName.StartsWith(TEXT("SK_Citizen")))
    {
        // Match the authored street crowd catalog, also reused by store customers.
        static const TSet<int32> Women = {1,3,4,7,9,11,14,15,17,18,19,22,25,27,30,31,
            32,33,34,35,36,38,41,43,45,47,49,51,53,55,58};
        return Women.Contains(FCString::Atoi(*ModelName.Mid(10)));
    }
    return false;
}

float Voice(UWorld& World, const USkeletalMeshComponent* Mesh, FVector Position, int32 Reaction,
    float Volume = .69f, float Range = 1150.f, float Pitch = 1.f)
{
    static const TCHAR* Clips[2][3] = {
        {TEXT("Male_bad_Mono"), TEXT("Male_neutral_Mono"), TEXT("Male_good_Mono")},
        {TEXT("Fem_bad_Mono"), TEXT("Fem_neutral_Mono"), TEXT("Fem_good_Mono")}
    };
    if (Reaction < 0 || Reaction > 2) return 0.f;
    USoundWave* Sound = LoadClip(TEXT("NPC"), Clips[FemaleVoice(Mesh)][Reaction]);
    if (SpatialSound(World, Sound, Position + FVector(0., 0., 115.), Volume, Range, nullptr, 0.f, Pitch,
        Volume >= .65f ? 3.f : 1.f))
    {
        UE_LOG(LogBogotaAudio, Display, TEXT("Voice: %s"), *Sound->GetName());
        return Sound->Duration;
    }
    return 0.f;
}

USkeletalMeshComponent* ShopSpeaker(AActor& Shop, FVector Listener, bool StaffPreferred)
{
    TInlineComponentArray<USkeletalMeshComponent*> Meshes(&Shop);
    USkeletalMeshComponent* Result = nullptr;
    double Best = FMath::Square(1200.);
    for (USkeletalMeshComponent* Mesh : Meshes)
    {
        if (!Mesh->IsVisible() || !Mesh->GetSkeletalMeshAsset()) continue;
        const FString Name = Mesh->GetSkeletalMeshAsset()->GetName();
        const bool Customer = Name.Contains(TEXT("Customer")) || Name.StartsWith(TEXT("SK_Citizen"));
        const double Distance = FVector::DistSquared(Mesh->GetComponentLocation(), Listener);
        const double Score = Distance * (StaffPreferred && !Customer ? .20 : 1.);
        if (Score < Best)
        {
            Best = Score;
            Result = Mesh;
        }
    }
    return Result;
}
}

void UBogotaAudioLibrary::PlayReaction(AActor* Speaker, int32 Reaction)
{
    if (!IsValid(Speaker) || Speaker->GetNetMode() == NM_DedicatedServer) return;
    if (UWorld* World = Speaker->GetWorld())
        Voice(*World, Cast<USkeletalMeshComponent>(ObjectField(Speaker, TEXT("VoxelMesh"))),
            Speaker->GetActorLocation(), Reaction);
}

void UBogotaAudioLibrary::PlayRobberyFootstep(AActor& Walker)
{
    if (UWorld* World = Walker.GetWorld())
    {
        const FString Name = FString::Printf(TEXT("Foot_Walk_%d"), FMath::RandRange(1, 5));
        SpatialSound(*World, LoadClip(TEXT("Recorded"), *Name), Walker.GetActorLocation(),
            .60f, 700.f, nullptr, 0.f, FMath::FRandRange(.96f, 1.04f));
    }
}

void UBogotaAudioLibrary::PlayMissionFinish(const UObject* WorldContext)
{
    UWorld* World = GEngine->GetWorldFromContextObject(WorldContext, EGetWorldErrorMode::ReturnNull);
    if (!World || !World->AllowAudioPlayback()) return;
    PlayPriorityCue(*World, LoadClip(TEXT("Delivery"), TEXT("Accomplish_mission")), .95f, 1.f);
}

bool UBogotaAudioSubsystem::DoesSupportWorldType(EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

void UBogotaAudioSubsystem::OnWorldBeginPlay(UWorld& World)
{
    Super::OnWorldBeginPlay(World);
    if (World.GetNetMode() == NM_DedicatedServer || !World.AllowAudioPlayback()) return;

    for (const TCHAR* Name : {TEXT("Street_Bird_1"), TEXT("Street_Bird_2"), TEXT("Street_Bird_3")})
        Sounds.Add(Name, LoadClip(TEXT("Recorded"), Name));
    Sounds.Add(TEXT("Bike_Bell"), LoadClip(TEXT("Rider"), TEXT("Bike_Bell")));
    Sounds.Add(TEXT("Rain_soft"), LoadClip(TEXT("Ambience"), TEXT("Rain_soft")));
    for (const TCHAR* Name : {TEXT("Bike_Loop"), TEXT("Boost_ready"), TEXT("Pickup_Bag"), TEXT("Menu_Music")})
        Sounds.Add(Name, LoadClip(TEXT("Gameplay"), Name));
    for (const TCHAR* Name : {TEXT("Bike_Player"), TEXT("Bike_Freewheel"), TEXT("Bike_Chain"), TEXT("Bike_Skid"),
        TEXT("Moto_Skid"), TEXT("Bike_Brake"), TEXT("Ride_Mount"), TEXT("Ride_Dismount")})
        Sounds.Add(Name, LoadClip(TEXT("Rider"), Name));
    for (const TCHAR* Name : {TEXT("Moto_Recorded"), TEXT("Police_Moto_Recorded"), TEXT("Car_Recorded"), TEXT("Bus_Recorded"),
        TEXT("Horn_Recorded"), TEXT("Moto_Horn"), TEXT("TransMi_Horn"), TEXT("TransMi_Air"), TEXT("TransMi_Door")})
        Sounds.Add(Name, LoadClip(TEXT("Traffic"), Name));
    for (const TCHAR* Name : {
        TEXT("Park_Leaves"), TEXT("Park_Drop"), TEXT("Drain_Water"),
        TEXT("Canopy_Rain"), TEXT("Station_Air"), TEXT("Cabin_Roll"), TEXT("Shop_Fridge"), TEXT("Shop_Vent"),
        TEXT("Shop_Door"), TEXT("Shop_Scan"), TEXT("Shop_Payment"), TEXT("Bag_Zip"), TEXT("Goods_Paper"),
        TEXT("Goods_Carton"), TEXT("Goods_Leaves"), TEXT("Goods_Packaging"), TEXT("Delivery_Knock"),
        TEXT("Phone_Open"), TEXT("Phone_Close"), TEXT("Phone_Select"), TEXT("Phone_Cancel"),
        TEXT("Traffic_Tires"), TEXT("Traffic_TiresWet"), TEXT("Traffic_Brake"), TEXT("Taxi_Door"),
        TEXT("Traffic_Indicator"), TEXT("Bus_Warning"), TEXT("Bus_Stop"), TEXT("Bus_Board"),
        TEXT("Wheel_Joint"), TEXT("Wheel_Splash"), TEXT("Rider_Breath"), TEXT("Rider_Cloth"), TEXT("Soft_Landing"),
        TEXT("Crossing_Signal"), TEXT("Local_Bell"), TEXT("Metal_Shutter"), TEXT("Step_Metal")})
        Sounds.Add(Name, LoadClip(TEXT("WorldFoley"), Name));
    for (int32 Index = 1; Index <= 11; ++Index)
    {
        const FString Name = FString::Printf(TEXT("Station_Announcement_%02d"), Index);
        Sounds.Add(FName(*Name), LoadClip(TEXT("Station"), *Name));
    }
    for (TActorIterator<AActor> Actor(&World); Actor; ++Actor)
    {
        if (Actor->GetClass()->GetFName() == TEXT("BP_WorldState_C")) Weather = *Actor;
        if (Actor->GetClass()->GetFName() == TEXT("BP_GraphicsSettings_C")) Graphics = *Actor;
        if (Actor->ActorHasTag(TEXT("BogotaAudioPark"))) ParkPoints.Add(Actor->GetActorLocation());
        const FString ClassName = Actor->GetClass()->GetName();
        if (ClassName.Contains(TEXT("TransmiStation")))
        {
            StationPoints.Add(Actor->GetActorLocation());
            StationActors.Add(*Actor);
        }
        if (ClassName == TEXT("BP_BogotaSignal_C")) CrossingSignals.Add(*Actor);
        if (const auto* Mesh = Actor->FindComponentByClass<UStaticMeshComponent>())
            if (Mesh->GetStaticMesh() && Mesh->GetStaticMesh()->GetFName() == TEXT("SM_Monserrate_Referencia"))
                LandmarkBells.Add(*Actor);
        if (Actor->ActorHasTag(TEXT("AudioDrain")) || Actor->ActorHasTag(TEXT("AudioLocalBell")) ||
            Actor->ActorHasTag(TEXT("AudioShutter")) || Actor->ActorHasTag(TEXT("AudioAccessibleCrossing")))
            LocalEmitters.Add(*Actor);
    }
    LastRealTime = FPlatformTime::Seconds();
    Ready = true;
}

USoundWave* UBogotaAudioSubsystem::Clip(FName Name) const
{
    return Sounds.FindRef(Name).Get();
}

void UBogotaAudioSubsystem::Deinitialize()
{
    Ready = false;
#if BOGOTA_WITH_FMOD
    if (UFMODAudioComponent* Component = FmodRide.Get()) Component->Stop();
    for (const auto& Pair : Atmosphere)
        if (UFMODAudioComponent* Component = Pair.Value.Loop.Get()) Component->Stop();
    for (const auto& Pair : TrafficSources)
        if (UFMODAudioComponent* Component = Pair.Value.FmodLoop.Get()) Component->Stop();
#endif
    for (UAudioComponent* Component : {Ride.Get(), Freewheel.Get(), Chain.Get(), Skid.Get(),
        Rain.Get(), Menu.Get(), Interior.Get(),
        Station.Get(), CanopyRain.Get(), WetWheels.Get(), Drain.Get()})
        if (IsValid(Component)) Component->Stop();
    for (const auto& Pair : TrafficSources)
    {
        if (UAudioComponent* Component = Pair.Value.Loop.Get()) Component->Stop();
        if (UAudioComponent* Component = Pair.Value.Tires.Get()) Component->Stop();
    }
    TrafficSources.Empty();
    Super::Deinitialize();
}

void UBogotaAudioSubsystem::Tick(float DeltaTime)
{
    if (!Ready) return;
    UWorld* World = GetWorld();
    const bool Paused = UGameplayStatics::IsGamePaused(World);
    const double RealTime = FPlatformTime::Seconds();
    UpdateRemaining += Paused ? FMath::Min(.10, RealTime - LastRealTime) : DeltaTime;
    LastRealTime = RealTime;
    APlayerController* Controller = UGameplayStatics::GetPlayerController(World, 0);
    if (Controller && Controller->WasInputKeyJustPressed(EKeys::MiddleMouseButton)) PendingHorn = true;
    const bool BellDown = Controller && Controller->IsInputKeyDown(EKeys::E);
    const bool BellPressed = BellDown && !bBellWasDown;
    bBellWasDown = BellDown;
    if (!Paused)
    {
        if (BellPressed)
        {
            const APawn* Rider = Controller->GetPawn();
            const UObject* Core = ObjectField(Rider, TEXT("Delivery"));
            if (Flag(Rider, TEXT("Riding")) && !Flag(Rider, TEXT("RoadActive")) &&
                !Flag(Core, TEXT("PhoneOpen")) && Number(Core, TEXT("Vehicle")) == 0.)
            {
                PlayPriorityCue(*World, Clip(TEXT("Bike_Bell")), .60f, 1.f);
                UE_LOG(LogBogotaAudio, Display, TEXT("Bicycle bell"));
            }
        }
        const auto* Handling = World->GetSubsystem<UBogotaTwoWheelHandling>();
        if (Handling && Handling->GetDriftBoostCount() != LastDriftBoostCount)
        {
            LastDriftBoostCount = Handling->GetDriftBoostCount();
            PlayPriorityCue(*World, Clip(TEXT("Boost_ready")), .90f, 1.f);
            UE_LOG(LogBogotaAudio, Display, TEXT("Boost ready: drift turbo engaged"));
        }
    }
    if (UpdateRemaining < .033f) return;
    const float Dt = UpdateRemaining;
    UpdateRemaining = 0.f;

    const auto* Settings = Cast<UUserWidget>(ObjectField(Graphics.Get(), TEXT("Menu")));
    const bool SettingsVisible = Settings && Settings->IsInViewport() && Settings->IsVisible();
    const APawn* MenuPawn = Controller ? Controller->GetPawn() : nullptr;
    auto* Phone = Cast<UUserWidget>(ObjectField(ObjectField(MenuPawn, TEXT("Delivery")), TEXT("PhoneWidget")));
    if ((Paused || SettingsVisible) && Phone)
    {
        if (HiddenPhone.Get() != Phone)
        {
            HiddenPhone = Phone;
            PreviousPhoneVisibility = Phone->GetVisibility();
        }
        Phone->SetVisibility(ESlateVisibility::Hidden);
    }
    else if (auto* Previous = HiddenPhone.Get())
    {
        if (Previous->GetVisibility() == ESlateVisibility::Hidden)
            Previous->SetVisibility(PreviousPhoneVisibility);
        HiddenPhone.Reset();
    }
    UpdateLoop(World, Menu, Clip(TEXT("Menu_Music")), Paused || SettingsVisible ? .23f : 0.f, 1.f, Dt, true);
#if BOGOTA_WITH_FMOD
    if (UFMODAudioComponent* Component = FmodRide.Get()) Component->SetPaused(Paused);
    for (const auto& Pair : Atmosphere)
        if (UFMODAudioComponent* Component = Pair.Value.Loop.Get()) Component->SetPaused(Paused);
    for (const auto& Pair : TrafficSources)
        if (UFMODAudioComponent* Component = Pair.Value.FmodLoop.Get()) Component->SetPaused(Paused);
#endif
    if (Paused) return;

    APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
    const FVector Location = Pawn ? Pawn->GetActorLocation() : FVector::ZeroVector;
    const float Travel = Pawn && PreviousPawn.Get() == Pawn ? FVector::Dist2D(Location, PreviousLocation) : 0.f;
    const float Speed = Travel / Dt;
    RideSpeed = FMath::FInterpTo(RideSpeed, FMath::Min(Speed, 2800.f), Dt, 6.f);
    PreviousPawn = Pawn;
    PreviousLocation = Location;

    const bool Mounted = Flag(Pawn, TEXT("Riding")) && !Flag(Pawn, TEXT("RoadActive"));
    const float RainAmount = FMath::Clamp(static_cast<float>(Number(Weather.Get(), TEXT("RainIntensity"))), 0.f, 1.f);
    UObject* Delivery = ObjectField(Pawn, TEXT("Delivery"));
    if (Pawn) UpdateDelivery(*World, Delivery, Location);
    const ACharacter* Walker = Cast<ACharacter>(Pawn);
    if (Walker && Walker->GetCharacterMovement()->IsMovingOnGround() && !Mounted &&
        !Flag(Pawn, TEXT("RoadActive")) && Travel < 150.f && Speed > 45.f)
    {
        StepDistance += Travel;
        const float Stride = FMath::GetMappedRangeValueClamped(FVector2f(140.f, 650.f), FVector2f(64.f, 185.f), Speed);
        if (StepDistance >= Stride)
        {
            StepDistance = FMath::Fmod(StepDistance, Stride);
            PlayFootstep(*World, *Walker->GetCharacterMovement(), LastShop.IsValid(), Speed, false, RainAmount > .35f);
        }
    }
    else StepDistance = 0.f;
    const bool Motorcycle = Mounted && Number(Delivery, TEXT("Vehicle")) == 1.;
    const bool Bicycle = Mounted && !Motorcycle;
    const bool PedalBoost = Mounted && !Motorcycle && Flag(Delivery, TEXT("BoostActive"));
    const float VehicleSpeed = Walker ? Walker->GetCharacterMovement()->Velocity.Size2D() : RideSpeed;
    const float Motion = FMath::Clamp(FMath::Max(VehicleSpeed, RideSpeed) / 1500.f, 0.f, 1.f);
    const float ForwardInput = static_cast<float>(Number(Pawn, TEXT("ForwardInput")));
    const float Throttle = FMath::Clamp(ForwardInput, 0.f, 1.f);
    const float RideVolume = Motorcycle ? .21f + .13f * Motion + .10f * Throttle
        : Bicycle && (Motion > .012f || Throttle > .1f)
        ? .095f + .23f * FMath::Sqrt(Motion) + (PedalBoost ? .04f : 0.f) : 0.f;
    const FName RideName = Motorcycle ? TEXT("Moto_Recorded") : Clip(TEXT("Bike_Player")) ? TEXT("Bike_Player") : TEXT("Bike_Loop");
    const float MotoPitch = .86f + .49f * FMath::Sqrt(Motion) + .20f * Throttle;
    bool FmodRidePlaying = false;
#if BOGOTA_WITH_FMOD
    if (UFMODAudioComponent* Component = FmodRide.Get())
    {
        if (!Motorcycle || Component->GetOwner() != Pawn)
        {
            Component->Stop();
            FmodRide.Reset();
        }
    }
    if (Motorcycle)
    {
        FmodRidePlaying = UpdateFmodEngine(FmodRide, *Pawn, RideName, RideVolume, MotoPitch, Ride.Get());
        if (FmodRidePlaying) Ride = nullptr;
    }
#endif
    if (!FmodRidePlaying)
        UpdateLoop(World, Ride, Mounted ? Clip(RideName) : Ride ? Cast<USoundWave>(Ride->Sound) : nullptr,
            RideVolume, Motorcycle ? MotoPitch : .80f + .40f * Motion + (PedalBoost ? .13f : 0.f), Dt, false, 16.f);

    const auto* Handling = World->GetSubsystem<UBogotaTwoWheelHandling>();
    const bool Drifting = Mounted && Handling && Handling->IsDrifting();
    const bool Grounded = Walker && Walker->GetCharacterMovement()->IsMovingOnGround();
    const bool Braking = Mounted && Grounded && VehicleSpeed > 150.f &&
        ForwardInput < -.1f;
    UpdateLoop(World, Freewheel, Clip(TEXT("Bike_Freewheel")),
        Bicycle && Grounded && !Braking && Throttle < .1f ? .12f * Motion : 0.f, .84f + .56f * Motion, Dt, false, 16.f);
    UpdateLoop(World, Chain, Clip(TEXT("Bike_Chain")),
        Bicycle && Throttle > .1f ? (PedalBoost ? .15f : .08f) * FMath::Max(Motion, .25f) : 0.f,
        .90f + .40f * Motion, Dt, false, 16.f);
    if (Drifting)
        UpdateLoop(World, Skid, Clip(Motorcycle ? TEXT("Moto_Skid") : TEXT("Bike_Skid")),
            (Motorcycle ? .28f : .23f) + .19f * Motion, .93f + .22f * Motion, Dt, false, 22.f);
    else if (IsValid(Skid.Get()))
    {
        Skid->FadeOut(.055f, 0.f);
        Skid = nullptr;
        UE_LOG(LogBogotaAudio, Display, TEXT("Skid loop released"));
    }
    if (Pawn && Mounted != WasMounted)
    {
        if (auto* Sound = UGameplayStatics::CreateSound2D(World,
            Clip(Mounted ? TEXT("Ride_Mount") : TEXT("Ride_Dismount"))))
            Sound->FadeIn(.045f, .48f);
    }
    if (Braking && !WasBraking)
    {
        if (auto* Sound = UGameplayStatics::CreateSound2D(World, Clip(TEXT("Bike_Brake"))))
            Sound->FadeIn(.035f, .54f);
    }
    if (!Mounted || !Flag(Pawn, TEXT("Sprint"))) PlayedBoostCue = false;
    if (PedalBoost && !PlayedBoostCue)
    {
        PlayPriorityCue(*World, Clip(TEXT("Boost_ready")), .90f, 1.f);
        PlayedBoostCue = true;
        UE_LOG(LogBogotaAudio, Display, TEXT("Boost ready: pedal boost engaged"));
    }
    WasMounted = Mounted;
    WasBraking = Braking;
    if (Pawn)
    {
        if (PendingHorn && Motorcycle)
        {
            if (World->GetTimeSeconds() >= NextHorn)
            {
                UGameplayStatics::PlaySound2D(World, Clip(TEXT("Moto_Horn")), .78f);
                NextHorn = World->GetTimeSeconds() + .6f;
            }
            PendingHorn = false;
        }
        TrafficUpdateAge += Dt;
        if (TrafficUpdateAge >= .12f)
        {
            UpdateTraffic(*World, Location, TrafficUpdateAge, PendingHorn);
            UpdatePedestrianSteps(*World, Location, TrafficUpdateAge);
            UpdateConversation(*World, Location);
            TrafficUpdateAge = 0.f;
            PendingHorn = false;
        }
    }

    const double Hour = Number(Weather.Get(), TEXT("Hour"), 12.);
    const float NightWeight = FMath::Max(1.f - FMath::SmoothStep(5.f, 7.f, static_cast<float>(Hour)),
        FMath::SmoothStep(18.f, 20.f, static_cast<float>(Hour)));
    const float Outdoors = LastShop.IsValid() ? .27f : 1.f;
    float NearestPark = 4200.f;
    const FVector* NearestParkPoint = nullptr;
    if (Pawn)
        for (const FVector& ParkPoint : ParkPoints)
        {
            const float Distance = static_cast<float>(FVector::Dist2D(Location, ParkPoint));
            if (Distance >= NearestPark) continue;
            NearestPark = Distance;
            NearestParkPoint = &ParkPoint;
        }
    const float ParkWeight = (1.f - FMath::SmoothStep(1150.f, 4200.f, NearestPark)) * (1.f - .75f * NightWeight);
    if (Pawn) UpdateAtmosphere(*Pawn, Dt, RainAmount, NightWeight, ParkWeight);
    UpdateLoop(World, Rain, Clip(TEXT("Rain_soft")), .43f * RainAmount * Outdoors, .94f + .12f * RainAmount, Dt);
    const float Now = World->GetTimeSeconds();
    if (Pawn && NearestParkPoint && NearestPark < 1650.f && !LastShop.IsValid() &&
        NightWeight < .40f && RainAmount < .40f && Now >= NextParkBird)
    {
        const float Angle = FMath::FRandRange(0.f, 2.f * PI);
        const FVector BirdAt = *NearestParkPoint +
            FVector(400.f * FMath::Cos(Angle), 400.f * FMath::Sin(Angle), 390.f);
        const FString Name = FString::Printf(TEXT("Street_Bird_%d"), FMath::RandRange(1, 3));
        SpatialSound(*World, Clip(FName(*Name)), BirdAt, .17f * ParkWeight, 1650.f,
            nullptr, 0.f, FMath::FRandRange(.94f, 1.04f));
        NextParkBird = Now + FMath::FRandRange(20.f, 42.f);
    }
    if (Pawn) UpdateWorldFoley(*Pawn, Delivery, Dt, RainAmount, NightWeight, NearestParkPoint,
        NearestPark, VehicleSpeed, Mounted);
}

void UBogotaAudioSubsystem::UpdateAtmosphere(AActor& Listener, float Dt, float RainAmount, float NightWeight, float ParkWeight)
{
#if BOGOTA_WITH_FMOD
    const float Shelter = LastShop.IsValid() ? .23f : 1.f;
    const float Speech = Listener.GetWorld()->GetTimeSeconds() < SpeechUntil ? .56f : 1.f;
    const float Urban = Shelter * Speech * (1.f - .58f * RainAmount);
    const float TrafficDensity = FMath::SmoothStep(3.f, 16.f, static_cast<float>(TrafficSources.Num()));
    const float Steady = FMath::SmoothStep(.26f, .60f, RainAmount);
    const float Downpour = FMath::SmoothStep(.58f, .92f, RainAmount);
    const TPair<FName, float> Targets[] = {
        {TEXT("City_DistantTraffic"), (.07f + .04f * TrafficDensity) * Urban * (1.f - .65f * ParkWeight) * (1.f - NightWeight)},
        {TEXT("City_Neighborhood"), FMath::Lerp(.39f, .29f, NightWeight) * Urban * (1.f - .65f * ParkWeight)},
        {TEXT("Rain_Steady"), .11f * Steady * (1.f - Downpour) * Shelter},
        {TEXT("Rain_Downpour"), .14f * Downpour * Shelter},
    };
    for (const auto& Target : Targets)
    {
        auto& Layer = Atmosphere.FindOrAdd(Target.Key);
        UFMODAudioComponent* Component = Layer.Loop.Get();
        if (Component && Component->GetOwner() != &Listener)
        {
            Component->Stop();
            Layer.Loop.Reset();
            Component = nullptr;
        }
        Layer.Volume = FMath::FInterpTo(Layer.Volume, Target.Value, Dt, 1.5f);
        if (Layer.Volume < .005f)
        {
            if (Component) Component->Stop();
            Layer.Loop.Reset();
            continue;
        }
        if (!Component)
        {
            Component = UFMODBlueprintStatics::PlayEventAttached(TrafficEvent(Target.Key), Listener.GetRootComponent(),
                NAME_None, FVector::ZeroVector, EAttachLocation::KeepRelativeOffset, true, true, true);
            if (!Component) continue;
            Layer.Loop = Component;
            UE_LOG(LogBogotaAudio, Display, TEXT("FMOD atmosphere: %s"), *Target.Key.ToString());
        }
        Component->SetVolume(Layer.Volume);
    }
#endif
}

void UBogotaAudioSubsystem::UpdateConversation(UWorld& World, const FVector& Listener)
{
    const float Now = World.GetTimeSeconds();
    if (Now < SpeechUntil)
    {
        ConversationReply.Reset();
        return;
    }
    const AActor* Recipient = GreetedRecipient.Get();
    if (Recipient && FVector::DistSquared(Listener, Recipient->GetActorLocation()) < FMath::Square(420.))
    {
        ConversationReply.Reset();
        return;
    }
    if (auto* Reply = ConversationReply.Get())
    {
        if (Now < ReplyTime) return;
        if (Reply->IsVisible() && Reply->GetOwner() && !Reply->GetOwner()->IsHidden() &&
            FVector::DistSquared(Listener, Reply->GetComponentLocation()) < FMath::Square(1550.))
        {
            const float Mood = FMath::FRand();
            const int32 Reaction = Mood < .20f ? 0 : Mood < .52f ? 1 : 2;
            const float Duration = Voice(World, Reply, Reply->GetComponentLocation(), Reaction, .56f, 1550.f,
                FMath::FRandRange(.96f, 1.04f));
            NextConversation = Now + Duration + FMath::FRandRange(2.f, 4.5f);
        }
        ConversationReply.Reset();
    }
    if (Now < NextConversation) return;
    NextConversation = Now + 1.f;
    TArray<USkeletalMeshComponent*> Speakers;
    if (auto* Shop = LastShop.Get())
    {
        if (Now < NextShopVoice - 8.f) return;
        TInlineComponentArray<USkeletalMeshComponent*> Meshes(Shop);
        for (auto* Mesh : Meshes)
        {
            const auto* Asset = Mesh->GetSkeletalMeshAsset();
            if (Mesh->IsVisible() && Asset && (Asset->GetName().StartsWith(TEXT("SK_Citizen")) ||
                Asset->GetName().StartsWith(TEXT("SK_Customer"))))
                Speakers.Add(Mesh);
        }
    }
    else
    {
        for (TActorIterator<ACharacter> It(&World); It; ++It)
        {
            if (It->IsHidden() || It->IsPlayerControlled() || It->GetVelocity().SizeSquared2D() > FMath::Square(210.))
                continue;
            auto* Mesh = Cast<USkeletalMeshComponent>(ObjectField(*It, TEXT("VoxelMesh")));
            if (!Mesh) Mesh = It->GetMesh();
            const auto* Asset = Mesh ? Mesh->GetSkeletalMeshAsset() : nullptr;
            if (Asset && Asset->GetName().StartsWith(TEXT("SK_Citizen")))
                Speakers.Add(Mesh);
        }
        // Platform passengers are actors with a skeletal mesh rather than street characters.
        auto* PassengerClass = FindObject<UClass>(nullptr,
            TEXT("/Game/Traffic/Transit/BP_StationPassenger.BP_StationPassenger_C"));
        if (PassengerClass)
        {
            for (TActorIterator<AActor> It(&World, PassengerClass); It; ++It)
            {
                if (It->IsHidden() || Number(*It, TEXT("State")) != 0. ||
                    FVector::DistSquared(Listener, It->GetActorLocation()) > FMath::Square(1550.)) continue;
                auto* Mesh = Cast<USkeletalMeshComponent>(ObjectField(*It, TEXT("PassengerMesh")));
                if (Mesh && Mesh->IsVisible() && Mesh->GetSkeletalMeshAsset()) Speakers.AddUnique(Mesh);
            }
        }
    }
    if (Speakers.Num() > 1) Algo::RandomShuffle(Speakers);
    for (auto* Speaker : Speakers)
    {
        const FVector Position = Speaker->GetComponentLocation();
        if (FVector::DistSquared(Listener, Position) > FMath::Square(1300.)) continue;
        for (auto* Other : Speakers)
        {
            if (Other == Speaker || FVector::DistSquared(Position, Other->GetComponentLocation()) > FMath::Square(850.))
                continue;
            const float Duration = Voice(World, Speaker, Position, 1, .58f, 1550.f,
                FMath::FRandRange(.96f, 1.04f));
            if (Duration <= 0.f) return;
            ConversationReply = Other;
            ReplyTime = Now + Duration + FMath::FRandRange(.35f, .75f);
            NextConversation = ReplyTime + 3.f;
            UE_LOG(LogBogotaAudio, Display, TEXT("NPC conversation started"));
            return;
        }
    }
}

void UBogotaAudioSubsystem::UpdateWorldFoley(APawn& Pawn, UObject* Delivery, float Dt, float RainAmount,
    float NightWeight, const FVector* ParkPoint, float ParkDistance, float VehicleSpeed, bool Mounted)
{
    UWorld& World = *Pawn.GetWorld();
    const FVector At = Pawn.GetActorLocation();
    const float Now = World.GetTimeSeconds();
    const bool InCabin = Flag(&Pawn, TEXT("RoadActive"));
    const AActor* CabinVehicle = nullptr;
    if (InCabin)
        for (const auto& Entry : TrafficSources)
        {
            const AActor* Vehicle = Entry.Key.Get();
            if (Flag(Vehicle, TEXT("PlayerControlled")) &&
                FVector::DistSquared(Vehicle->GetActorLocation(), At) < FMath::Square(850.))
            {
                CabinVehicle = Vehicle;
                break;
            }
        }
    const bool BusCabin = Flag(CabinVehicle, TEXT("Bus"));
    const bool PhoneOpen = Flag(Delivery, TEXT("PhoneOpen"));
    AActor* Shop = LastShop.Get();
    const bool UnderCover = Shop || InCabin;
    const bool Speaking = Now < SpeechUntil;
    const float VoiceRoom = Speaking ? .45f : 1.f;

    float StationDistance = 3600.f;
    AActor* NearestStation = nullptr;
    for (const auto& Candidate : StationActors)
    {
        AActor* Actor = Candidate.Get();
        if (!Actor) continue;
        const float Distance = static_cast<float>(FVector::Dist(At, Actor->GetActorLocation()));
        if (Distance >= StationDistance) continue;
        StationDistance = Distance;
        NearestStation = Actor;
    }
    const float Platform = 1.f - FMath::SmoothStep(700.f, 3600.f, StationDistance);
    if (NearestStation)
    {
        const double Alpha = Number(NearestStation, TEXT("OpenAlpha"));
        const bool DoorsOpen = Alpha > .35;
        if (bool* WasOpen = PlatformDoorsOpen.Find(NearestStation))
        {
            if ((!*WasOpen && DoorsOpen) || (*WasOpen && Alpha < .12))
            {
                const FVector Center = NearestStation->GetActorLocation();
                const FVector Along = NearestStation->GetActorForwardVector();
                const FVector Door = Center + Along * FMath::Clamp(FVector::DotProduct(At - Center, Along), -700., 700.) +
                    FVector(0, 0, 115);
                if (SpatialSound(World, Clip(TEXT("TransMi_Door")), Door, DoorsOpen ? .78f : .56f,
                    2900.f, nullptr, 0.f, DoorsOpen ? 1.07f : .87f, 2.f))
                    UE_LOG(LogBogotaAudio, Display, TEXT("Station platform door: %s %s"),
                        *NearestStation->GetName(), DoorsOpen ? TEXT("open") : TEXT("closed"));
                *WasOpen = DoorsOpen;
            }
        }
        else PlatformDoorsOpen.Add(NearestStation, DoorsOpen);
    }
    if (!NearestStation || Number(NearestStation, TEXT("OpenAlpha")) < .12)
        AnnouncedPlatform.Reset();
    else if (NearestStation != AnnouncedPlatform.Get() && Number(NearestStation, TEXT("OpenAlpha")) > .35 &&
        StationDistance < 2400.f && Now >= NextStationVoice)
    {
        const int32 Id = static_cast<int32>(Number(NearestStation, TEXT("StationId"), -1.)) + 1;
        USoundWave* Announcement = Clip(FName(*FString::Printf(TEXT("Station_Announcement_%02d"), Id)));
        if (SpatialSound(World, Announcement, NearestStation->GetActorLocation() + FVector(0, 0, 280), .68f, 2700.f,
            nullptr, 0.f, 1.f, 2.5f))
        {
            AnnouncedPlatform = NearestStation;
            NextStationVoice = Now + 6.f;
            SpeechUntil = FMath::Max(SpeechUntil, Now + Announcement->Duration);
            UE_LOG(LogBogotaAudio, Display, TEXT("World foley: announcement for station %d"), Id);
        }
    }
    UpdateLoop(&World, Station, Clip(TEXT("Station_Air")),
        UnderCover ? 0.f : .23f * Platform * VoiceRoom, 1.f, Dt);
    const FString Theme = ShopTheme(Shop);
    const bool Food = Shop && (Number(Shop, TEXT("StoreKind"), -1.) == 0. ||
        Theme.Contains(TEXT("Market")) || Theme.Contains(TEXT("Cafe")) ||
        Theme.Contains(TEXT("Restaurant")) || Theme.Contains(TEXT("Fresh")));
    const FName InteriorName = InCabin ? TEXT("Cabin_Roll") : Food ? TEXT("Shop_Fridge") : TEXT("Shop_Vent");
    const float CabinSpeed = FMath::Clamp(VehicleSpeed / 1250.f, 0.f, 1.f);
    UpdateLoop(&World, Interior, Clip(InteriorName),
        (InCabin ? (BusCabin ? .14f : .075f) + .27f * CabinSpeed : Shop ? .18f : 0.f) * VoiceRoom,
        InCabin ? (BusCabin ? .67f : .91f) + .38f * CabinSpeed : 1.f, Dt);
    if (Interior)
    {
        Interior->SetLowPassFilterEnabled(InCabin);
        Interior->SetLowPassFilterFrequency(BusCabin ? 850.f : 1550.f);
    }
    UpdateLoop(&World, CanopyRain, Clip(TEXT("Canopy_Rain")),
        RainAmount * VoiceRoom * (UnderCover ? .25f : .10f * Platform), .92f, Dt);
    if (CanopyRain)
    {
        CanopyRain->SetLowPassFilterEnabled(UnderCover);
        CanopyRain->SetLowPassFilterFrequency(1550.f);
    }
    UpdateLoop(&World, WetWheels, Clip(TEXT("Traffic_TiresWet")),
        Mounted ? .31f * RainAmount * CabinSpeed : 0.f, .76f + .55f * CabinSpeed, Dt);

    if (Shop != FoleyShop.Get())
    {
        AActor* Door = Shop ? Shop : FoleyShop.Get();
        if (Door && SpatialSound(World, Clip(TEXT("Shop_Door")), At + Pawn.GetActorForwardVector() * 130.f, .46f, 1100.f))
            UE_LOG(LogBogotaAudio, Display, TEXT("World foley: shop threshold"));
        if (Door && !Shop)
        {
            const FString LeavingTheme = ShopTheme(Door);
            if (LeavingTheme.Contains(TEXT("Hardware")) || LeavingTheme.Contains(TEXT("Tech")))
                SpatialSound(World, Clip(TEXT("Metal_Shutter")), At, .19f, 800.f, nullptr, 0.f, .92f);
        }
        FoleyShop = Shop;
    }
    if (PhoneOpen != WasPhoneOpen)
    {
        UGameplayStatics::PlaySound2D(&World, Clip(PhoneOpen ? TEXT("Phone_Open") : TEXT("Phone_Close")), .55f);
        UE_LOG(LogBogotaAudio, Display, TEXT("World foley: phone %s"), PhoneOpen ? TEXT("opened") : TEXT("closed"));
    }
    const auto* SelectionField = Field<FStructProperty>(Delivery, TEXT("SelectedOffer"));
    if (SelectionField && SelectionField->Struct == TBaseStructure<FGuid>::Get())
    {
        const FGuid& Selection = *SelectionField->ContainerPtrToValuePtr<FGuid>(Delivery);
        if (PhoneOpen && WasPhoneOpen && Selection != LastPhoneSelection)
            UGameplayStatics::PlaySound2D(&World, Clip(Selection.IsValid() ? TEXT("Phone_Select") : TEXT("Phone_Cancel")), .45f);
        LastPhoneSelection = Selection;
    }
    if (InCabin != WasInCabin)
    {
        UGameplayStatics::PlaySound2D(&World, Clip(TEXT("Bus_Board")), .49f);
        if (InCabin)
        {
            FTimerHandle Handle;
            World.GetTimerManager().SetTimer(Handle, [WeakPawn = TWeakObjectPtr<APawn>(&Pawn),
                Step = TWeakObjectPtr<USoundWave>(Clip(TEXT("Step_Metal")))]
            {
                if (const APawn* Rider = WeakPawn.Get(); Flag(Rider, TEXT("RoadActive")) && Step.IsValid())
                    UGameplayStatics::PlaySound2D(Rider, Step.Get(), .39f, .91f);
            }, .24f, false);
        }
    }
    WasInCabin = InCabin;
    WasPhoneOpen = PhoneOpen;

    if (!UnderCover && ParkPoint && ParkDistance < 2550.f && Now >= NextParkDetail)
    {
        const FName Detail = RainAmount > .30f ? TEXT("Park_Drop") : TEXT("Park_Leaves");
        if (SpatialSound(World, Clip(Detail), *ParkPoint + FVector(0, 0, 170), (RainAmount > .30f ? .11f : .045f) * VoiceRoom, 1700.f,
            nullptr, 0.f, FMath::FRandRange(.85f, 1.12f)))
            UE_LOG(LogBogotaAudio, Display, TEXT("Park detail: %s"), *Detail.ToString());
        NextParkDetail = Now + FMath::FRandRange(13.f, 27.f);
    }

    const ACharacter* Walker = Cast<ACharacter>(&Pawn);
    if (!Walker) return;
    const auto* Move = Walker->GetCharacterMovement();
    const bool Grounded = Move->IsMovingOnGround();
    const EStepSurface Surface = StepSurface(Move->CurrentFloor.HitResult, Shop != nullptr);
    if (Grounded && !WasOnGround && PreviousVerticalSpeed < -330.f && !InCabin)
        UGameplayStatics::PlaySound2D(&World, Clip(TEXT("Soft_Landing")),
            FMath::GetMappedRangeValueClamped(FVector2f(330.f, 820.f), FVector2f(.16f, .37f), -PreviousVerticalSpeed));
    WasOnGround = Grounded;
    PreviousVerticalSpeed = Move->Velocity.Z;
    if (Grounded && !InCabin && Now >= NextEffort && VehicleSpeed > 220.f)
    {
        const bool Effort = Flag(Delivery, TEXT("BoostActive")) ||
            (Surface == EStepSurface::Trail && Number(&Pawn, TEXT("ForwardInput")) > .3);
        if (Effort || !Mounted)
            UGameplayStatics::PlaySound2D(&World, Clip(Effort ? TEXT("Rider_Breath") : TEXT("Rider_Cloth")),
                (Effort ? .41f : .23f) * VoiceRoom, FMath::FRandRange(.88f, 1.08f));
        NextEffort = Now + FMath::FRandRange(2.1f, 4.2f);
    }
    UPrimitiveComponent* Contact = Grounded ? Move->CurrentFloor.HitResult.GetComponent() : nullptr;
    const bool ContactChanged = Contact && WheelContact.IsValid() && WheelContact.Get() != Contact;
    WheelContact = Mounted ? Contact : nullptr;
    if (Mounted && Grounded && VehicleSpeed > 300.f && Now >= NextWheelDetail)
    {
        if (Surface == EStepSurface::Puddle || RainAmount > .62f)
            UGameplayStatics::PlaySound2D(&World, Clip(TEXT("Wheel_Splash")), .27f * CabinSpeed);
        else if (ContactChanged || Surface == EStepSurface::Stair || Surface == EStepSurface::Metal)
            UGameplayStatics::PlaySound2D(&World, Clip(TEXT("Wheel_Joint")), .34f * CabinSpeed);
        if (ContactChanged || Surface == EStepSurface::Stair || Surface == EStepSurface::Metal ||
            Surface == EStepSurface::Puddle || RainAmount > .62f)
            NextWheelDetail = Now + FMath::FRandRange(.55f, 1.25f);
    }
    float DrainDistance = StationDistance < 1800.f ? StationDistance : 1800.f;
    for (const auto& Emitter : LocalEmitters)
        if (const AActor* Actor = Emitter.Get(); Actor && Actor->ActorHasTag(TEXT("AudioDrain")))
            DrainDistance = FMath::Min(DrainDistance, static_cast<float>(FVector::Dist(Actor->GetActorLocation(), At)));
    UpdateLoop(&World, Drain, Clip(TEXT("Drain_Water")),
        .25f * RainAmount * VoiceRoom * (1.f - FMath::SmoothStep(250.f, 1800.f, DrainDistance)), 1.f, Dt);
    if (Now < NextLocalDetail) return;
    NextLocalDetail = Now + .8f;
    if (!UnderCover && RainAmount > .40f && Platform > .55f)
        for (const FVector& Point : StationPoints)
            if (FVector::DistSquared(Point, At) < FMath::Square(1700.))
            {
                SpatialSound(World, Clip(TEXT("Park_Drop")), Point + FVector(0, 0, 215), .30f * VoiceRoom, 1400.f);
                NextLocalDetail = Now + 3.f;
                break;
            }
    if (!Mounted && !UnderCover && Now >= NextCrossingCue && UBogotaLaneLibrary::IsPedestrianCrossingWindow(Now))
    {
        const AActor* Nearest = nullptr;
        double Distance = FMath::Square(950.);
        for (const auto& Signal : CrossingSignals)
        {
            const AActor* Actor = Signal.Get();
            if (!Actor) continue;
            const double Here = FVector::DistSquared(Actor->GetActorLocation(), At);
            if (Here >= Distance) continue;
            Distance = Here;
            Nearest = Actor;
        }
        if (Nearest && SpatialSound(World, Clip(TEXT("Crossing_Signal")), Nearest->GetActorLocation() + FVector(0, 0, 180),
            .36f * VoiceRoom, 1100.f))
            UE_LOG(LogBogotaAudio, Verbose, TEXT("World foley: pedestrian signal"));
        NextCrossingCue = Now + 1.1f;
    }
    if (!UnderCover && Now >= NextLandmarkBell && NightWeight < .45f)
        for (const auto& Bell : LandmarkBells)
            if (const AActor* Actor = Bell.Get(); Actor && FVector::DistSquared(Actor->GetActorLocation(), At) < FMath::Square(6500.))
            {
                SpatialSound(World, Clip(TEXT("Local_Bell")), Actor->GetActorLocation() + FVector(0, 0, 780), .34f * VoiceRoom, 7200.f);
                NextLandmarkBell = Now + 78.f;
                break;
            }
    for (const auto& Emitter : LocalEmitters)
    {
        const AActor* Actor = Emitter.Get();
        if (!Actor || FVector::DistSquared(Actor->GetActorLocation(), At) > FMath::Square(1800.f)) continue;
        FName Cue;
        if (Actor->ActorHasTag(TEXT("AudioDrain")) && RainAmount > .35f) Cue = TEXT("Park_Drop");
        else if (Actor->ActorHasTag(TEXT("AudioLocalBell"))) Cue = TEXT("Local_Bell");
        else if (Actor->ActorHasTag(TEXT("AudioShutter")) && Flag(Actor, TEXT("AudioMoving"))) Cue = TEXT("Metal_Shutter");
        else if (Actor->ActorHasTag(TEXT("AudioAccessibleCrossing")) && Flag(Actor, TEXT("PedestrianGo")))
            Cue = TEXT("Crossing_Signal");
        if (!Cue.IsNone())
        {
            SpatialSound(World, Clip(Cue), Actor->GetActorLocation(), .39f * VoiceRoom, 1800.f);
            NextLocalDetail = Now + (Cue == TEXT("Crossing_Signal") ? 1.f : 11.f);
            break;
        }
    }
}

void UBogotaAudioSubsystem::UpdatePedestrianSteps(UWorld& World, const FVector& Listener, float Dt)
{
    const bool Wet = Number(Weather.Get(), TEXT("RainIntensity")) > .35;
    for (auto It = PedestrianStepDistances.CreateIterator(); It; ++It)
    {
        const ACharacter* Pedestrian = It.Key().Get();
        if (!Pedestrian || FVector::DistSquared(Pedestrian->GetActorLocation(), Listener) > FMath::Square(850.))
            It.RemoveCurrent();
    }
    for (TActorIterator<ACharacter> It(&World); It; ++It)
    {
        ACharacter* Pedestrian = *It;
        if (Pedestrian == PreviousPawn.Get() || Pedestrian->IsHidden() ||
            FVector::DistSquared(Pedestrian->GetActorLocation(), Listener) > FMath::Square(850.))
            continue;
        const UCharacterMovementComponent* Movement = Pedestrian->GetCharacterMovement();
        const float Speed = Movement->Velocity.Size2D();
        if (!Movement->IsMovingOnGround() || Speed < 45.f) continue;
        float& Distance = PedestrianStepDistances.FindOrAdd(Pedestrian);
        const float Stride = FMath::GetMappedRangeValueClamped(FVector2f(100.f, 650.f), FVector2f(62.f, 116.f), Speed);
        Distance += Speed * Dt;
        if (Distance < Stride) continue;
        Distance = FMath::Fmod(Distance, Stride);
        PlayFootstep(World, *Movement, false, Speed, true, Wet);
    }
}

void UBogotaAudioSubsystem::UpdateDelivery(UWorld& World, UObject* Delivery, const FVector& Listener)
{
    const bool SameDelivery = Delivery && LastDelivery.Get() == Delivery;
    LastDelivery = Delivery;

    AActor* Recipient = Cast<AActor>(ObjectField(Delivery, TEXT("Recipient")));
    if (IsValid(Recipient))
    {
        const auto* OrderField = Field<FStructProperty>(Recipient, TEXT("OrderID"));
        const FGuid* Order = OrderField && OrderField->Struct == TBaseStructure<FGuid>::Get()
            ? OrderField->ContainerPtrToValuePtr<FGuid>(Recipient) : nullptr;
        if (Order && Order->IsValid() && (StyledRecipient.Get() != Recipient || StyledOrder != *Order))
        {
            static const FName Roles[] = {TEXT("CustomerOffice"), TEXT("CustomerStudent"),
                TEXT("CustomerOffice"), TEXT("CustomerNeighbor")};
            FName* Existing = RecipientRoles.Find(*Order);
            const FName Role = Existing ? *Existing : Roles[NextRecipient++ % UE_ARRAY_COUNT(Roles)];
            if (!Existing) RecipientRoles.Add(*Order, Role);
            if (UFunction* Initialize = Recipient->FindFunction(TEXT("InitializeAppearance")))
            {
                if (const auto* RoleParam = FindFProperty<FNameProperty>(Initialize, TEXT("AppearanceRole")))
                {
                    FStructOnScope Params(Initialize);
                    RoleParam->SetPropertyValue_InContainer(Params.GetStructMemory(), Role);
                    Recipient->ProcessEvent(Initialize, Params.GetStructMemory());
                    StyledRecipient = Recipient;
                    StyledOrder = *Order;
                    GreetedRecipient.Reset();
                    UE_LOG(LogBogotaAudio, Display, TEXT("Recipient appearance: %s"), *Role.ToString());
                }
            }
        }
    }

    if (IsValid(Recipient) && GreetedRecipient.Get() != Recipient &&
        FVector::DistSquared(Listener, Recipient->GetActorLocation()) < FMath::Square(350.))
    {
        GreetedRecipient = Recipient;
        UBogotaAudioLibrary::PlayReaction(Recipient, 1);
        SpeechUntil = World.GetTimeSeconds() + 2.4f;
        SpatialSound(World, Clip(TEXT("Delivery_Knock")), Recipient->GetActorLocation(), .29f, 760.f);
    }

    AActor* Shop = Cast<AActor>(ObjectField(Delivery, TEXT("InsideStore")));
    const int32 Basket = static_cast<int32>(Number(Delivery, TEXT("BasketCount")));
    const int32 State = static_cast<int32>(Number(Delivery, TEXT("State")));
    const bool CheckedOut = SameDelivery && LastDeliveryState == 2 && State == 3;
    const bool SameShop = IsValid(Shop) && LastShop.Get() == Shop;
    if (SameDelivery && ((SameShop && State == 2 && Basket > LastBasket) || CheckedOut))
    {
        UGameplayStatics::PlaySound2D(&World, Clip(TEXT("Pickup_Bag")), CheckedOut ? .29f : .61f);
        const FString Theme = ShopTheme(Shop);
        const FName Material = Theme.Contains(TEXT("Bakery")) || Theme.Contains(TEXT("Cafe")) ? TEXT("Goods_Paper") :
            Theme.Contains(TEXT("Florist")) ? TEXT("Goods_Leaves") :
            Theme.Contains(TEXT("Pharmacy")) ? TEXT("Goods_Carton") : TEXT("Goods_Packaging");
        UGameplayStatics::PlaySound2D(&World, Clip(CheckedOut ? TEXT("Bag_Zip") : Material), .53f);
        if (CheckedOut) UGameplayStatics::PlaySound2D(&World, Clip(TEXT("Shop_Payment")), .48f);
        else if (Basket % 2 == 0) UGameplayStatics::PlaySound2D(&World, Clip(TEXT("Shop_Scan")), .36f);
        UE_LOG(LogBogotaAudio, Display, TEXT("Pickup sound: %s"), CheckedOut ? TEXT("order") : TEXT("product"));
    }

    const FText Status = TextField(Delivery, TEXT("StatusMessage"));
    const FString StatusString = Status.ToString();
    const bool NewDenial = SameShop && !Status.EqualTo(LastShopStatus) &&
        (StatusString.Contains(TEXT("saldo")) || StatusString.Contains(TEXT("faltan")) ||
            StatusString.Contains(TEXT("sin dinero")) || StatusString.Contains(TEXT("presupuesto")));
    AActor* SpeakingShop = Shop ? Shop : CheckedOut ? LastShop.Get() : nullptr;
    const float Now = World.GetTimeSeconds();
    if (IsValid(SpeakingShop) && (CheckedOut || NewDenial || !SameShop || Now >= NextShopVoice))
    {
        const int32 Reaction = CheckedOut ? 2 : NewDenial ? 0 : 1;
        if (const auto* Speaker = ShopSpeaker(*SpeakingShop, Listener, Reaction != 1 || !SameShop))
        {
            const float Duration = Voice(World, Speaker, Speaker->GetComponentLocation(), Reaction);
            if (Duration > 0.f) SpeechUntil = Now + Duration + .22f;
            NextShopVoice = Now + (Reaction == 1 ? 13.f : 8.f);
        }
        else NextShopVoice = Now + 1.f;
    }
    LastShopStatus = Status;
    LastShop = Shop;
    LastBasket = Basket;
    LastDeliveryState = State;
}

void UBogotaAudioSubsystem::UpdateTraffic(UWorld& World, const FVector& Listener, float Dt, bool ManualHorn)
{
    if (!TwoWheelerClass.IsValid())
        TwoWheelerClass = FindObject<UClass>(nullptr,
            TEXT("/Game/Traffic/Services/BP_TwoWheelerCitizen.BP_TwoWheelerCitizen_C"));
    if (!TrafficClass.IsValid())
        TrafficClass = FindObject<UClass>(nullptr,
            TEXT("/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C"));

    if (!ServiceClass.IsValid())
        ServiceClass = FindObject<UClass>(nullptr,
            TEXT("/Game/Traffic/Services/BP_VoxelRoadVehicle.BP_VoxelRoadVehicle_C"));

    const float Now = World.GetTimeSeconds();
    const bool WetRoad = Number(Weather.Get(), TEXT("RainIntensity")) > .32;
    const bool Sheltered = LastShop.IsValid();
    const bool Speaking = Now < SpeechUntil;
    const float TrafficRoom = (Sheltered ? .46f : 1.f) * (Speaking ? .63f : 1.f);
    const APawn* ListenerPawn = UGameplayStatics::GetPlayerPawn(&World, 0);
    TSet<TWeakObjectPtr<AActor>> Active;
    for (UClass* Class : {TwoWheelerClass.Get(), TrafficClass.Get(), ServiceClass.Get()})
    {
        if (!Class) continue;
        const bool TwoWheeler = Class == TwoWheelerClass.Get();
        for (TActorIterator<AActor> It(&World, Class); It; ++It)
        {
            AActor* Vehicle = *It;
            const FVector Position = Vehicle->GetActorLocation();
            const bool Bike = TwoWheeler && Flag(Vehicle, TEXT("Bicycle"));
            const bool Moto = !Bike && (TwoWheeler || Vehicle->GetClass()->GetName().Contains(TEXT("Motorcycle")));
            const bool PoliceMoto = Moto && Vehicle->GetClass()->GetName().Contains(TEXT("Police"));
            const bool Bus = !TwoWheeler && Flag(Vehicle, TEXT("Bus"));
            const bool Taxi = !TwoWheeler && Flag(Vehicle, TEXT("Taxi"));
            const bool PlayerCar = !TwoWheeler && Flag(Vehicle, TEXT("PlayerControlled"));
            const float Range = Bus ? 5500.f : Moto ? 4400.f : Bike ? 2300.f : 3600.f;
            const double Distance = FVector::DistSquared(Position, Listener);
            const TWeakObjectPtr<AActor> Key(Vehicle);
            if (Active.Contains(Key)) continue;
            auto* Source = TrafficSources.Find(Key);
            const float Boundary = Source ? Range + 650.f : Range - 150.f;
            if (Vehicle->IsHidden() || Distance > FMath::Square(Boundary) ||
                (TwoWheeler && Number(Vehicle, TEXT("State")) >= 2.) ||
                (!TwoWheeler && !PlayerCar && Flag(Vehicle, TEXT("Parked"))))
                continue;
            Active.Add(Key);
            if (!Source)
            {
                Source = &TrafficSources.Add(Key);
                Source->LastPosition = Position;
                Source->NextHorn = Now + 1.2f;
                Source->AtStop = Bus && Number(Vehicle, TEXT("TransitDwell")) > 0.;
                Source->Closing = Bus && Flag(Vehicle, TEXT("TransitClosing"));
                Source->DoorsOpen = (Bus || Taxi) && (Number(Vehicle, TEXT("DoorAlphaRight")) > .45 ||
                    Number(Vehicle, TEXT("DoorAlphaLeft")) > .45);
            }

            const float SignalSpeed = FMath::Abs(static_cast<float>(Number(Vehicle, TEXT("Speed"))));
            const float Measured = FMath::Min(static_cast<float>(FVector::Dist2D(Position, Source->LastPosition)) / Dt, 3200.f);
            Source->LastPosition = Position;
            const float InstantSpeed = TwoWheeler ? Measured : FMath::Max(SignalSpeed, Measured * .65f);
            Source->PreviousSpeed = Source->Speed;
            Source->Speed = FMath::FInterpTo(Source->Speed, InstantSpeed, Dt, 3.5f);
            const float Motion = FMath::Clamp(Source->Speed / (Bus ? 1000.f : 1450.f), 0.f, 1.f);
            const float PitchVariance = .93f + .14f * (GetTypeHash(Vehicle->GetFName()) % 23) / 22.f;
            const float Load = Moto ? FMath::Clamp((Source->Speed - Source->PreviousSpeed) / (Dt * 950.f), -.15f, .23f) : 0.f;
            const float IdlePitch = Taxi ? 1.04f : PoliceMoto ? .90f : .87f;
            const float Pitch = PitchVariance * (IdlePitch + (Moto ? .50f : .40f) * FMath::Sqrt(Motion) + Load);
            const float BaseVolume = Bus ? .51f : Moto ? .34f : .44f;
            if (!PlayerCar && Distance < FMath::Square(3100.) && Now >= Source->NextOcclusion)
            {
                FCollisionQueryParams Query(SCENE_QUERY_STAT(BogotaTrafficOcclusion), false, Vehicle);
                if (ListenerPawn) Query.AddIgnoredActor(ListenerPawn);
                const bool Blocked = World.LineTraceTestByChannel(Listener + FVector(0, 0, 55),
                    Position + FVector(0, 0, 105), ECC_Visibility, Query);
                Source->OcclusionGain = Blocked ? .62f : 1.f;
                Source->NextOcclusion = Now + .28f + (GetTypeHash(Vehicle->GetFName()) % 13) * .01f;
            }
            const float Target = (Bike ? .19f * Motion : BaseVolume + .19f * Motion + .24f * Load) *
                (PlayerCar ? 1.f : TrafficRoom * Source->OcclusionGain);
            Source->SmoothedGain = FMath::FInterpTo(Source->SmoothedGain, Target, Dt, 5.f);
            const FName Engine = Bike ? TEXT("Bike_Loop") : PoliceMoto ? TEXT("Police_Moto_Recorded")
                : Moto ? TEXT("Moto_Recorded") : Bus ? TEXT("Bus_Recorded") : TEXT("Car_Recorded");
            const FName Horn = Moto ? TEXT("Moto_Horn") : Bus ? TEXT("TransMi_Horn") : TEXT("Horn_Recorded");
            UAudioComponent* Loop = Source->Loop.Get();
            bool FmodPlaying = false;
#if BOGOTA_WITH_FMOD
            if (!Bike)
            {
                FmodPlaying = UpdateFmodEngine(Source->FmodLoop, *Vehicle, Engine, Source->SmoothedGain, Pitch, Loop);
                if (FmodPlaying)
                {
                    Source->Loop.Reset();
                    Loop = nullptr;
                }
            }
#endif
            if (!FmodPlaying && !Loop && (!Bike || Motion > .045f))
            {
                USoundWave* Sound = Clip(Engine);
                const float Start = Sound ? Sound->Duration * (GetTypeHash(Vehicle->GetFName()) % 41) / 50.f : 0.f;
                Loop = SpatialSound(World, Sound, Position, .018f, Range, Vehicle->GetRootComponent(), Start, Pitch);
                Source->Loop = Loop;
                if (Loop)
                    UE_LOG(LogBogotaAudio, Verbose, TEXT("Vehicle audio: %s %s"), *Vehicle->GetName(), *Engine.ToString());
            }
            if (Loop)
            {
                Loop->SetVolumeMultiplier(FMath::Max(.003f, FMath::FInterpTo(Loop->VolumeMultiplier, Target, Dt, 3.f)));
                Loop->SetPitchMultiplier(FMath::FInterpTo(Loop->PitchMultiplier, Pitch, Dt, 3.f));
            }

            const FVector ToPlayer = Listener - Position;
            const bool BlockedByPlayer = Distance < FMath::Square(760.) &&
                FVector::DotProduct(ToPlayer.GetSafeNormal2D(), Vehicle->GetActorForwardVector()) > .72;
            const bool BrakingForTraffic = Source->PreviousSpeed - Source->Speed > 95.f &&
                (BlockedByPlayer || IsValid(ObjectField(Vehicle, TEXT("Leader"))));
            bool Queued = false;
            if (!TwoWheeler && !PlayerCar && !Bus && InstantSpeed < 175.f && Distance < FMath::Square(3400.))
            {
                const FVector Forward = Vehicle->GetActorForwardVector().GetSafeNormal2D();
                const FVector Right(-Forward.Y, Forward.X, 0);
                const double HalfLength = Number(Vehicle, TEXT("HalfLength"), 220.);
                for (const auto& Pair : TrafficSources)
                {
                    const AActor* Ahead = Pair.Key.Get();
                    if (!Ahead || Ahead == Vehicle || Ahead->IsHidden() || Pair.Value.Speed > 220.f ||
                        Flag(Ahead, TEXT("Parked")) || Flag(Ahead, TEXT("Bicycle"))) continue;
                    const FVector Offset = Ahead->GetActorLocation() - Position;
                    const double ForwardDistance = FVector::DotProduct(Offset, Forward);
                    if (ForwardDistance > 110. && ForwardDistance < HalfLength + Number(Ahead, TEXT("HalfLength"), 220.) + 460. &&
                        FMath::Abs(Offset.Z) < 150. && FMath::Abs(FVector::DotProduct(Offset, Right)) < 105. &&
                        FVector::DotProduct(Forward, Ahead->GetActorForwardVector()) > .92)
                    {
                        Queued = true;
                        break;
                    }
                }
            }
            Source->QueuedTime = Queued ? FMath::Min(15.f, Source->QueuedTime + Dt) : 0.f;
            const float Patience = 1.6f + 1.8f * (GetTypeHash(Vehicle->GetFName()) % 17) / 16.f;
            const bool QueueHorn = Source->QueuedTime >= Patience;
            const bool NearTires = !TwoWheeler && Distance < FMath::Square(1350.) && Motion > .12f;
            UAudioComponent* Tires = Source->Tires.Get();
            USoundWave* TireSound = Clip(WetRoad ? TEXT("Traffic_TiresWet") : TEXT("Traffic_Tires"));
            if (Tires && (!NearTires || Tires->Sound != TireSound))
            {
                Tires->FadeOut(.18f, 0.f);
                Source->Tires.Reset();
                Tires = nullptr;
            }
            if (NearTires && !Tires)
            {
                Tires = SpatialSound(World, TireSound, Position, .03f, 1420.f, Vehicle->GetRootComponent());
                Source->Tires = Tires;
                if (Tires) UE_LOG(LogBogotaAudio, Verbose, TEXT("World foley: %s %s"), *TireSound->GetName(),
                    *Vehicle->GetName());
            }
            if (Tires)
            {
                Tires->SetVolumeMultiplier(.28f * Motion * TrafficRoom);
                Tires->SetPitchMultiplier(.77f + .57f * Motion);
            }
            if (!TwoWheeler && Now >= Source->NextDetail && Distance < FMath::Square(1650.))
            {
                const double Steering = FMath::Abs(Number(Vehicle, TEXT("SteerAngle")));
                const FName Detail = BrakingForTraffic ? TEXT("Traffic_Brake") :
                    PlayerCar && Steering > 13. && Motion < .25f ? TEXT("Traffic_Indicator") : TEXT("");
                if (!Detail.IsNone())
                {
                    SpatialSound(World, Clip(Detail), Position, .38f * TrafficRoom, 1500.f);
                    Source->NextDetail = Now + (Detail == TEXT("Traffic_Indicator") ? .56f : 2.6f);
                }
            }
            if (!Bike && Now >= NextHorn && ((PlayerCar && ManualHorn) ||
                (!PlayerCar && !Moto && Now >= Source->NextHorn &&
                    (QueueHorn || (BrakingForTraffic && Distance < FMath::Square(2400.))))))
            {
                bool FmodHorn = false;
#if BOGOTA_WITH_FMOD
                if (!Moto && !Bus)
                {
                    const auto Instance = UFMODBlueprintStatics::PlayEventAtLocation(&World, TrafficEvent(Horn),
                        FTransform(Position), false);
                    if (UFMODBlueprintStatics::EventInstanceIsValid(Instance))
                    {
                        UFMODBlueprintStatics::EventInstanceSetVolume(Instance, (QueueHorn ? 1.25f : 1.03f) *
                            TrafficRoom * Source->OcclusionGain);
                        UFMODBlueprintStatics::EventInstanceSetPitch(Instance, PitchVariance);
                        FmodHorn = Instance.Instance->start() == FMOD_OK;
                        UFMODBlueprintStatics::EventInstanceRelease(Instance);
                        if (FmodHorn) UE_LOG(LogBogotaAudio, Display, TEXT("FMOD horn: %s"), *Vehicle->GetName());
                    }
                }
#endif
                if (!FmodHorn && SpatialSound(World, Clip(Horn), Position, .96f * TrafficRoom, Range, nullptr, 0.f, PitchVariance))
                    UE_LOG(LogBogotaAudio, Verbose, TEXT("Traffic horn: %s"), *Horn.ToString());
                if (QueueHorn) UE_LOG(LogBogotaAudio, Display, TEXT("Queue horn: %s after %.1fs"), *Vehicle->GetName(), Source->QueuedTime);
                Source->NextHorn = Now + (QueueHorn ? FMath::FRandRange(5.5f, 9.5f) : FMath::FRandRange(15.f, 27.f));
                NextHorn = Now + (PlayerCar ? .8f : QueueHorn ? FMath::FRandRange(1.1f, 2.f) : FMath::FRandRange(2.8f, 5.f));
            }

            if (Bus || Taxi)
            {
                const bool AtStop = Bus && Number(Vehicle, TEXT("TransitDwell")) > 0.;
                const bool DoorsOpen = Number(Vehicle, TEXT("DoorAlphaRight")) > .45 ||
                    Number(Vehicle, TEXT("DoorAlphaLeft")) > .45;
                const bool Closing = Bus && Flag(Vehicle, TEXT("TransitClosing"));
                if (AtStop && !Source->AtStop &&
                    SpatialSound(World, Clip(TEXT("TransMi_Air")), Position, .45f, 3500.f))
                {
                    UE_LOG(LogBogotaAudio, Verbose, TEXT("TransMi air brake"));
                    SpatialSound(World, Clip(TEXT("Bus_Stop")), Position + FVector(0, 0, 155), .37f, 1600.f);
                }
                if (Closing && !Source->Closing)
                {
                    if (SpatialSound(World, Clip(TEXT("Bus_Warning")), Position, .60f, 2200.f))
                        UE_LOG(LogBogotaAudio, Display, TEXT("World foley: bus closing warning"));
                }
                if (DoorsOpen != Source->DoorsOpen &&
                    SpatialSound(World, Clip(Bus ? TEXT("TransMi_Door") : TEXT("Taxi_Door")), Position + FVector(0, 0, 85),
                        Bus ? .72f : .47f, Bus ? 3500.f : 2700.f, nullptr, 0.f, DoorsOpen ? 1.04f : .89f))
                    UE_LOG(LogBogotaAudio, Verbose, TEXT("%s door: %s"), Bus ? TEXT("TransMi") : TEXT("Taxi"),
                        DoorsOpen ? TEXT("open") : TEXT("closed"));
                Source->AtStop = AtStop;
                Source->DoorsOpen = DoorsOpen;
                Source->Closing = Closing;
            }
        }
    }

    for (auto It = TrafficSources.CreateIterator(); It; ++It)
    {
        if (Active.Contains(It.Key())) continue;
#if BOGOTA_WITH_FMOD
        if (UFMODAudioComponent* Component = It.Value().FmodLoop.Get()) Component->Stop();
#endif
        if (UAudioComponent* Component = It.Value().Loop.Get()) Component->FadeOut(.25f, 0.f);
        if (UAudioComponent* Component = It.Value().Tires.Get()) Component->FadeOut(.18f, 0.f);
        It.RemoveCurrent();
    }
}

TStatId UBogotaAudioSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UBogotaAudioSubsystem, STATGROUP_Tickables);
}
