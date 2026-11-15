#include "BogotaShopVisitors.h"

#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogBogotaShopVisitors, Log, All);

namespace
{
bool ClearWalk(UWorld& World, const FVector& From, const FVector& To)
{
    const FVector Torso(0, 0, 92);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(BogotaShopVisitor), false);
    Params.bFindInitialOverlaps = true;
    return !World.SweepTestByObjectType(From + Torso, To + Torso, FQuat::Identity,
        FCollisionObjectQueryParams(ECC_WorldStatic), FCollisionShape::MakeCapsule(24.f, 58.f), Params);
}

bool FloorAt(UWorld& World, FVector& Position)
{
    FHitResult Hit;
    if (!World.LineTraceSingleByObjectType(Hit, Position + FVector(0, 0, 50), Position - FVector(0, 0, 55),
        FCollisionObjectQueryParams(ECC_WorldStatic), FCollisionQueryParams(SCENE_QUERY_STAT(BogotaShopFloor), false)) ||
        Hit.ImpactNormal.Z < .65f) return false;
    Position.Z = Hit.ImpactPoint.Z + 2.;
    return true;
}

FScriptArrayHelper ReadArray(AActor& Shop, const FArrayProperty& Property)
{
    return FScriptArrayHelper(&Property, Property.ContainerPtrToValuePtr<void>(&Shop));
}
}

bool UBogotaShopVisitors::DoesSupportWorldType(EWorldType::Type WorldType) const
{
    return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

TStatId UBogotaShopVisitors::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UBogotaShopVisitors, STATGROUP_Tickables);
}

void UBogotaShopVisitors::RegisterShop(AActor& Shop)
{
    const UClass* Class = Shop.GetClass();
    const auto* MeshArray = FindFProperty<FArrayProperty>(Class, TEXT("WalkingCustomers"));
    const auto* StartArray = FindFProperty<FArrayProperty>(Class, TEXT("CustomerPathStart"));
    const auto* EndArray = FindFProperty<FArrayProperty>(Class, TEXT("CustomerPathEnd"));
    const auto* SpeedArray = FindFProperty<FArrayProperty>(Class, TEXT("CustomerSpeeds"));
    const auto* MeshField = MeshArray ? CastField<FObjectPropertyBase>(MeshArray->Inner) : nullptr;
    const auto* SpeedField = SpeedArray ? CastField<FNumericProperty>(SpeedArray->Inner) : nullptr;
    const auto* StartField = StartArray ? CastField<FStructProperty>(StartArray->Inner) : nullptr;
    const auto* EndField = EndArray ? CastField<FStructProperty>(EndArray->Inner) : nullptr;
    if (!MeshField || !SpeedField || !SpeedField->IsFloatingPoint() || !StartArray || !EndArray ||
        !StartField || !EndField || StartField->Struct != TBaseStructure<FVector>::Get() ||
        EndField->Struct != TBaseStructure<FVector>::Get() ||
        !Shop.FindFunction(TEXT("SetCustomerPose"))) return;

    auto Meshes = ReadArray(Shop, *MeshArray);
    auto Starts = ReadArray(Shop, *StartArray);
    auto Ends = ReadArray(Shop, *EndArray);
    auto Speeds = ReadArray(Shop, *SpeedArray);
    if (!Meshes.Num() || Starts.Num() != Meshes.Num() || Ends.Num() != Meshes.Num() || Speeds.Num() != Meshes.Num()) return;
    TArray<FVisit>& Visitors = Shops.Add(&Shop);
    Visitors.SetNum(Meshes.Num());
    const FTransform& Frame = Shop.GetActorTransform();
    for (int32 Index = 0; Index < Meshes.Num(); ++Index)
    {
        auto& Visit = Visitors[Index];
        Visit.Mesh = Cast<USkeletalMeshComponent>(MeshField->GetObjectPropertyValue(Meshes.GetRawPtr(Index)));
        if (!Visit.Mesh.IsValid()) continue;
        const FVector Start = *reinterpret_cast<const FVector*>(Starts.GetRawPtr(Index));
        const FVector End = *reinterpret_cast<const FVector*>(Ends.GetRawPtr(Index));
        Visit.Speed = FMath::Clamp(static_cast<float>(SpeedField->GetFloatingPointPropertyValue(Speeds.GetRawPtr(Index))), 42.f, 115.f);
        Visit.Wait = 2.f + 2.f * Index;
        Visit.bWalking = true;
        SetWalking(Shop, Visit, Index, false);
        Visit.Stops = {Frame.TransformPosition(Start), Frame.TransformPosition(End)};
        if (Index != 0) continue;

        UWorld& World = *Shop.GetWorld();
        FVector Outside = Frame.TransformPosition(FVector(0, -220, Start.Z));
        FVector Threshold = Frame.TransformPosition(FVector(0, 45, Start.Z));
        FVector Vestibule = Frame.TransformPosition(FVector(0, FMath::Clamp(Start.Y * .52, 180., 390.), Start.Z));
        if (!FloorAt(World, Outside) || !FloorAt(World, Threshold) || !FloorAt(World, Vestibule) ||
            !ClearWalk(World, Outside, Threshold) || !ClearWalk(World, Threshold, Vestibule))
            continue;

        TArray<FVector, TInlineAllocator<7>> DoorPath = {Outside, Threshold, Vestibule};
        if (!ClearWalk(World, Vestibule, Visit.Stops[0]))
        {
            bool FoundAisle = false;
            // Approach parallel to the shelves and turn only in a clear aisle.
            for (const double TurnY : {Start.Y, Start.Y + 180., Start.Y - 180., Start.Y + 360., Start.Y - 320.})
            {
                FVector Center = Frame.TransformPosition(FVector(0, TurnY, Start.Z));
                FVector Aisle = Frame.TransformPosition(FVector(Start.X, TurnY, Start.Z));
                if (!FloorAt(World, Center) || !FloorAt(World, Aisle) ||
                    !ClearWalk(World, Vestibule, Center) || !ClearWalk(World, Center, Aisle) ||
                    !ClearWalk(World, Aisle, Visit.Stops[0])) continue;
                DoorPath.Add(Center);
                if (FMath::Abs(TurnY - Start.Y) > 5.) DoorPath.Add(Aisle);
                FoundAisle = true;
                break;
            }
            if (!FoundAisle) continue;
        }
        DoorPath.Append(Visit.Stops);
        Visit.Stops = MoveTemp(DoorPath);
        Visit.Target = Visit.Stops.Num() - 1;
        Visit.bDoorRoute = true;
        UE_LOG(LogBogotaShopVisitors, Verbose, TEXT("Shop entrance route verified: %s"), *Shop.GetName());
    }
    // The authored store tick only drove its former two-point customer movement.
    Shop.SetActorTickEnabled(false);
}

void UBogotaShopVisitors::SetWalking(AActor& Shop, FVisit& Visit, int32 Index, bool Walking)
{
    if (Visit.bWalking == Walking) return;
    Visit.bWalking = Walking;
    UFunction* Function = Shop.FindFunction(TEXT("SetCustomerPose"));
    FStructOnScope Parameters(Function);
    auto* IndexField = FindFProperty<FIntProperty>(Function, TEXT("Index"));
    auto* WalkField = FindFProperty<FBoolProperty>(Function, TEXT("Walking"));
    if (!IndexField || !WalkField) return;
    IndexField->SetPropertyValue_InContainer(Parameters.GetStructMemory(), Index);
    WalkField->SetPropertyValue_InContainer(Parameters.GetStructMemory(), Walking);
    Shop.ProcessEvent(Function, Parameters.GetStructMemory());
}

void UBogotaShopVisitors::MoveVisitor(AActor& Shop, FVisit& Visit, int32 Index, const FVector& Player, float Dt)
{
    auto* Mesh = Visit.Mesh.Get();
    if (!Mesh) return;
    Visit.Wait = FMath::Max(0.f, Visit.Wait - Dt);
    if (Visit.Wait > 0.f) return;
    const FVector From = Mesh->GetComponentLocation();
    const FVector Goal = Visit.Stops[Visit.Target];
    const FVector Offset = Goal - From;
    const float Distance = Offset.Size2D();
    if (Distance < 5.f)
    {
        if (Visit.Target == 0 || Visit.Target == Visit.Stops.Num() - 1)
        {
            if (Visit.bDoorRoute && Visit.Target == 0)
                UE_LOG(LogBogotaShopVisitors, Verbose, TEXT("Shop visitor reached sidewalk: %s"), *Shop.GetName());
            Visit.Direction = Visit.Target == 0 ? 1 : -1;
            Visit.Wait = Visit.Target == 0 ? FMath::FRandRange(3.f, 6.f) : FMath::FRandRange(5.f, 10.f);
            SetWalking(Shop, Visit, Index, false);
        }
        Visit.Target += Visit.Direction;
        return;
    }

    FVector Next = From + Offset.GetSafeNormal2D() * FMath::Min(Distance, Visit.Speed * Dt);
    const double PlayerDistance = FVector::DistSquared2D(Player, Next);
    const bool PlayerBlocks = FMath::Abs(Player.Z - Next.Z) < 205. && PlayerDistance < FMath::Square(86.) &&
        PlayerDistance < FVector::DistSquared2D(Player, From);
    const bool Obstructed = !FloorAt(*Shop.GetWorld(), Next) || !ClearWalk(*Shop.GetWorld(), From, Next);
    if (PlayerBlocks || Obstructed)
    {
        SetWalking(Shop, Visit, Index, false);
        Visit.BlockedTime += Dt;
        if (Obstructed && Visit.BlockedTime >= 1.8f)
        {
            const int32 Previous = Visit.Target - Visit.Direction;
            if (Visit.Stops.IsValidIndex(Previous))
            {
                Visit.Target = Previous;
                Visit.Direction *= -1;
            }
            Visit.Wait = 1.1f;
            Visit.BlockedTime = 0.f;
        }
        return;
    }
    Visit.BlockedTime = 0.f;
    const FRotator Facing(0, Offset.Rotation().Yaw - 90., 0);
    Mesh->SetWorldLocationAndRotation(Next, FMath::RInterpTo(Mesh->GetComponentRotation(), Facing, Dt, 7.f));
    SetWalking(Shop, Visit, Index, true);
}

void UBogotaShopVisitors::Tick(float DeltaTime)
{
    UWorld* World = GetWorld();
    const auto* Controller = World->GetFirstPlayerController();
    const APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
    if (!Pawn || DeltaTime <= 0.f) return;
    const float Now = World->GetTimeSeconds();
    if (Now >= NextDiscovery)
    {
        NextDiscovery = Now + 1.f;
        auto* Class = FindObject<UClass>(nullptr,
            TEXT("/Game/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore.BP_DeliveryStore_C"));
        if (Class)
            for (TActorIterator<AActor> It(World, Class); It; ++It)
            {
                AActor* Shop = *It;
                if (!Shops.Contains(Shop) && FVector::DistSquared2D(Shop->GetActorLocation(), Pawn->GetActorLocation()) < FMath::Square(3600.))
                    RegisterShop(*Shop);
            }
    }
    for (auto It = Shops.CreateIterator(); It; ++It)
    {
        AActor* Shop = It.Key().Get();
        if (!Shop)
        {
            It.RemoveCurrent();
            continue;
        }
        auto& Visitors = It.Value();
        const FVector Player = Pawn->GetActorLocation();
        const bool Nearby = !Shop->IsHidden() && FVector::DistSquared(Shop->GetActorLocation(), Player) < FMath::Square(3400.);
        for (int32 Index = 0; Index < Visitors.Num(); ++Index)
        {
            if (Nearby) MoveVisitor(*Shop, Visitors[Index], Index, Player, FMath::Min(DeltaTime, .10f));
            else SetWalking(*Shop, Visitors[Index], Index, false);
        }
    }
}
