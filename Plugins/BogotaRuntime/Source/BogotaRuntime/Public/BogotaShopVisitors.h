#pragma once

#include "Subsystems/WorldSubsystem.h"
#include "BogotaShopVisitors.generated.h"

class USkeletalMeshComponent;

UCLASS()
class UBogotaShopVisitors : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    struct FVisit
    {
        TWeakObjectPtr<USkeletalMeshComponent> Mesh;
        TArray<FVector, TInlineAllocator<7>> Stops;
        float Speed = 85.f;
        float Wait = 0.f;
        float BlockedTime = 0.f;
        int32 Target = 1;
        int32 Direction = 1;
        bool bWalking = false;
        bool bDoorRoute = false;
    };

    void SetWalking(AActor& Shop, FVisit& Visit, int32 Index, bool Walking);
    void MoveVisitor(AActor& Shop, FVisit& Visit, int32 Index, const FVector& Player, float Dt);
    void RegisterShop(AActor& Shop);

    TMap<TWeakObjectPtr<AActor>, TArray<FVisit>> Shops;
    float NextDiscovery = 0.f;
};
