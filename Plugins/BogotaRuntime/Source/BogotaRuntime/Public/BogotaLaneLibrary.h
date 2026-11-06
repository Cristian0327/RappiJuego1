#pragma once
#include "CoreMinimal.h"
#include "Templates/SubclassOf.h"
#include "Blueprint/UserWidget.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "BogotaLaneLibrary.generated.h"
class USplineComponent;
class UInstancedStaticMeshComponent;
UCLASS()
class BOGOTARUNTIME_API UBogotaLaneLibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable,Category="Bogota|Traffic")
 static double ClampRouteStep(AActor* Visitor,double RequestedStep);
 UFUNCTION(BlueprintCallable,Category="Bogota|Traffic")
 static void SimulateVehicleStep(AActor* Visitor,double DeltaTime,double Clearance,double DesiredSpeed);
 UFUNCTION(BlueprintCallable,Category="Bogota|Navigation")
 static void SimulateCrosswalk(AActor* Citizen,double TimeSeconds);
 UFUNCTION(BlueprintCallable,Category="Bogota|Navigation")
 static FVector AdvanceFarRoute(const TArray<FVector>& Route,UPARAM(ref) int32& RouteIndex,FVector Position,double Speed,double Dt,double HalfHeight);
 UFUNCTION(BlueprintCallable,Category="Bogota|Navigation")
 static void CopyVectorRange(const TArray<FVector>& Source,int32 Start,int32 Count,UPARAM(ref) TArray<FVector>& Destination);
 UFUNCTION(BlueprintPure,Category="Bogota|Traffic")
 static double VehicleClearance(AActor* Visitor,AActor* Other);
 UFUNCTION(BlueprintPure,Category="Bogota|Traffic")
 static double EnvelopeClearance(AActor* Visitor,AActor* Other);
 UFUNCTION(BlueprintCallable,Category="Bogota|Traffic")
 static bool PedestrianCorridorClear(const TArray<AActor*>& Vehicles,FVector Start,FVector Finish);
 UFUNCTION(BlueprintPure,Category="Bogota|Traffic")
 static double RouteSignalLimit(const TArray<int32>& GateLanes,const TArray<double>& GateDistances,const TArray<int32>& GateCounts,const TArray<bool>& Green,int32 Group,double Distance,double Length,double HalfLength,double AvailableRoom,bool CheckExit);
 UFUNCTION(BlueprintCallable,Category="Bogota|Streaming",meta=(WorldContext="WorldContextObject"))
 static int32 MaintainSectorCache(const UObject* WorldContextObject,const TArray<FName>& SectorNames,int32 MaximumCached=4);
 UFUNCTION(BlueprintCallable,Category="Bogota|Weather")
 static int32 UpdatePrecipitationDrops(UInstancedStaticMeshComponent* Mesh,UPARAM(ref) TArray<FVector>& Points,UPARAM(ref) TArray<double>& Floors,double Dt,FVector Eye,bool Relocate,int32 VisibleCount,bool Hail);
 UFUNCTION(BlueprintPure, Category="Bogota|Traffic")
 static float ClosestDistance(USplineComponent* Route, FVector Position);
 UFUNCTION(BlueprintPure, Category="Bogota|Traffic")
 static float ClosestInputKey(USplineComponent* Route, FVector Position);
 UFUNCTION(BlueprintPure, Category="Bogota|Navigation")
 static int32 NearestPoint(const TArray<FVector>& Points, FVector Position);
 UFUNCTION(BlueprintPure, Category="Bogota|Navigation")
 static FVector2D ProjectMapPoint(FVector Position, FVector Center, bool FullMap, double FullSpanX, double FullSpanY, double MiniSpanX, double MiniSpanY);
 UFUNCTION(BlueprintCallable, Category="Bogota|Traffic", meta=(WorldContext="WorldContextObject", DeterminesOutputType="ActorClass", DynamicOutputParam="OutActors"))
 static void GetActorsOfClassCached(const UObject* WorldContextObject, TSubclassOf<AActor> ActorClass, TArray<AActor*>& OutActors);
 UFUNCTION(BlueprintCallable,Category="Bogota|Performance")
 static void StaggerActorTick(AActor* Actor,float Interval,int32 Index,int32 Count);
 UFUNCTION(BlueprintCallable,Category="Bogota|Navigation")
 static void DrawProjectedRoads(UPARAM(ref) FPaintContext& Context,const TArray<FVector>& Starts,const TArray<FVector>& Ends,FVector Center,bool FullMap,FVector2D Origin,FVector2D Size,double FullSpanX,double FullSpanY,double MiniSpanX,double MiniSpanY);
};





