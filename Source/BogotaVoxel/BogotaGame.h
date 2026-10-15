#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "BogotaGame.generated.h"

class UHierarchicalInstancedStaticMeshComponent;
class UInstancedStaticMeshComponent;
class USpringArmComponent;
class UCameraComponent;
class UAnimationAsset;
class UStaticMesh;
class UMaterialInterface;
class ADirectionalLight;
class ASkyLight;
class AExponentialHeightFog;
class UMaterialInstanceDynamic;
class UTextRenderComponent;
class UBoxComponent;
class UPoseableMeshComponent;
class UDeliveryComponent;
class USpotLightComponent;

struct FStreetAgent {
 TArray<FVector> Route;
 int32 Segment=0;
 FVector Position=FVector::ZeroVector,PreviousPosition=FVector::ZeroVector;
 float PreviousHeading=0,PreviousWheelAngle=0,SteeringRate=0;
 float Speed=0, Heading=0, Wait=0;
 bool Bus=false;
 bool Articulated=false;
 int32 LaneGroup=0;
 float Velocity=0, WheelAngle=0, StopCooldown=0, Travelled=0;
 float HalfLength=210, WheelRadius=33,ModelScale=1;
 TArray<TWeakObjectPtr<USpotLightComponent>> Headlights;
 float HalfWidth=90,PathDistance=0,LoopLength=0;
 TWeakObjectPtr<UPoseableMeshComponent> Visual;
 TArray<FTransform> WheelRest;
 FTransform ArticulationRest;
 TArray<int32> PartIndices;
 TArray<int32> PartColors;
 TArray<FTransform> Parts;
};
enum class EPedActivity:uint8 {Walking,ApproachCar,EnteringCar,InsideCar,LeavingCar,WaitingTransit,BoardingTransit,InsideTransit,AlightingTransit,ReturningRoute};
struct FParkedTrafficCar {TArray<TWeakObjectPtr<USpotLightComponent>> Headlights;FVector Position=FVector::ZeroVector,Door=FVector::ZeroVector;float Heading=90;int32 Walker=INDEX_NONE;bool Occupied=false;TWeakObjectPtr<UPoseableMeshComponent> Visual;};
struct FWalker {
 TArray<FVector> Route;
 FVector Position=FVector::ZeroVector,Velocity=FVector::ZeroVector;
 int32 Segment=0,ModelIndex=0;
 float Heading=0,Speed=112,Scale=1,Travelled=0,BlockedTime=0;
 TWeakObjectPtr<AActor> Visual;
 TArray<uint8> CrossSegments;
 TArray<int32> CrossJunctions;
 int32 CrossJunction=INDEX_NONE,ParkedCar=INDEX_NONE,BusIndex=INDEX_NONE,StationIndex=INDEX_NONE,BoardedStation=INDEX_NONE;
 bool Crossing=false,TransitPassenger=false;
 EPedActivity Activity=EPedActivity::Walking;
 FVector ResumePosition=FVector::ZeroVector,ActionStart=FVector::ZeroVector,ActionEnd=FVector::ZeroVector;
 float ActionTime=0,NextInteraction=0,FrameMoved=0;
 uint8 VisualAnimation=255;
};

USTRUCT(BlueprintType) struct FMapFootprint {
 GENERATED_BODY()
 UPROPERTY(BlueprintReadWrite) FVector Center=FVector::ZeroVector;
 UPROPERTY(BlueprintReadWrite) FVector2D Extent=FVector2D::ZeroVector;
};
UCLASS()
class BOGOTAVOXEL_API ABogotaCity : public AActor {
 GENERATED_BODY()
public:
 ABogotaCity();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(EditAnywhere, Category="Bogota") float CycleMinutes=24;
 UPROPERTY(VisibleAnywhere, Category="Bogota") float Hour=9;
 UPROPERTY(VisibleAnywhere, Category="Bogota") int32 StaticVoxelCount=0;
 UPROPERTY(BlueprintReadWrite,Category="Map") TArray<FMapFootprint> MapFootprints;
 UPROPERTY(BlueprintReadWrite,Category="Map") TArray<float> NorthRoads;
 UPROPERTY(BlueprintReadWrite,Category="Map") TArray<float> EastRoads;
 TArray<FStreetAgent> Vehicles;
 TArray<FWalker> Walkers;
 TArray<FParkedTrafficCar> ParkedCars;
 TSet<int32> PedestrianJunctions;
 TMap<int32,float> PedestrianNextAdmission;
 int32 PedestrianCrossings=0,IllegalCrossings=0,ParkedCarBoardings=0,TransitBoardings=0,TransitAlightings=0;
 UPROPERTY() TArray<FVector> ParkedBikes;
 UPROPERTY() TArray<TWeakObjectPtr<AActor>> BikeActors;
 UFUNCTION(CallInEditor,Category="Bogota") void BakeCity();
 UFUNCTION(BlueprintCallable,CallInEditor,Category="Map") void BuildMapMetadata();
 UFUNCTION(CallInEditor,BlueprintCallable,Category="Traffic") FString ValidateTraffic(float Seconds=180);
 UFUNCTION(CallInEditor,BlueprintCallable,Category="Traffic") FString ValidateG66();
 UFUNCTION(CallInEditor,BlueprintCallable,Category="Crowd") FString ValidateCrowd(float Seconds=180);
 UFUNCTION(CallInEditor,BlueprintCallable,Category="Crowd") FString ValidateStreetFlow();
 UFUNCTION(BlueprintCallable,Category="Crowd") class USkeleton* CreateCrowdSkeleton(class USkeletalMesh* Source);
 UFUNCTION(BlueprintCallable,Category="Crowd") void BindCrowdMesh(class USkeletalMesh* Mesh,class USkeleton* Skeleton);
 FString DistrictAt(FVector P) const;
 void AdvanceTime();
 bool TrafficNSGreen() const;
 bool TrafficEWGreen() const;
 void SetDetail(int32 Detail);
protected:
 UPROPERTY() TObjectPtr<UStaticMesh> Cube;
 UPROPERTY() TArray<TObjectPtr<UMaterialInterface>> Palette;
 UPROPERTY() TArray<TObjectPtr<UHierarchicalInstancedStaticMeshComponent>> Solid;
 UPROPERTY() TArray<TObjectPtr<UHierarchicalInstancedStaticMeshComponent>> Detail;
 UPROPERTY() TArray<TObjectPtr<UInstancedStaticMeshComponent>> Moving;
 UPROPERTY() TObjectPtr<ADirectionalLight> Sun;
 UPROPERTY() TObjectPtr<ASkyLight> Ambient;
 UPROPERTY() TObjectPtr<AExponentialHeightFog> Fog;
 UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> SkyMaterial;
 UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> GlowMaterial;
 UPROPERTY() TArray<TObjectPtr<UTextRenderComponent>> Signs;
 UPROPERTY() TArray<TObjectPtr<UBoxComponent>> VehicleCollision;
 UPROPERTY() TArray<TObjectPtr<UInstancedStaticMeshComponent>> SignalLights;
 UPROPERTY() TArray<FTransform> SignalTransforms;
 UPROPERTY() TArray<bool> SignalNorthSouth;
 float Elapsed=0, SimAccumulator=0, LightAccumulator=0, CycleSeconds=180, PedAccumulator=0;
 int32 DetailLevel=2;
 UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> TrafficMaterial;
 UPROPERTY() TArray<TObjectPtr<class USkeletalMesh>> CrowdMeshes;
 UPROPERTY() TArray<TObjectPtr<UAnimationAsset>> CrowdClips;
 UPROPERTY() TObjectPtr<UMaterialInterface> CrowdMaterial;
 int32 GameDay=0,G66CheckedNight=-1,G66LastNight=-100;
 bool G66Scheduled=false,G66Active=false;
 float G66StartHour=2.5f;
 FRandomStream G66Random;
 void UpdateTrafficNight();
 TMultiMap<int32,int32> TrafficReservations;
 void Block(FVector Center,FVector Size,int32 Color,bool Collision=true);
 void Label(FString Text,FVector Position,float Size=150,FRotator Rotation=FRotator(0,-90,0));
 void BuildCity();
 void Building(float X,float Y,float SX,float SY,int32 Floors,int32 Style,FRandomStream& R);
 void Tree(FVector P,FRandomStream& R);
 void BuildLandmarks();
 void BuildTraffic();
 void SimulateTraffic(float Dt);
 void UpdateTrafficVisuals(float Alpha);
 TOptional<FVector> PedestrianTestObstacle;
 void SimulateWalkers(float Dt);
 void BuildStreetInteractions();
 bool UpdateWalkerInteraction(FWalker& Walker,float Dt);
 void UpdateLighting();
 void UpdateSignals();
};

UCLASS()
class BOGOTAVOXEL_API ABogotaPlayer : public ACharacter {
 GENERATED_BODY()
public:
 friend class UDeliveryComponent;
class USpotLightComponent;
 friend class UDeliveryAnimInstance;
 ABogotaPlayer();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<USpringArmComponent> CameraBoom;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UCameraComponent> Camera;
 UPROPERTY(VisibleAnywhere,BlueprintReadWrite) bool Riding=false;
 UFUNCTION(BlueprintPure,Category="Delivery|Input") bool IsRiding() const {return Riding;}
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Delivery") TObjectPtr<UDeliveryComponent> Delivery;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Delivery|Art") TArray<TObjectPtr<UStaticMeshComponent>> MotorcycleParts;
 UFUNCTION(BlueprintPure,Category="Delivery|Input") bool WantsBoost() const {return Sprint;}
 UFUNCTION(BlueprintPure,Category="Delivery|Input") bool HasThrottle() const {return FMath::Abs(ForwardInput)>.1f;}
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Animation|Locomotion",meta=(ClampMin="1")) float WalkReferenceSpeed=390.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Animation|Locomotion",meta=(ClampMin="0.1")) float MinimumWalkRate=.35f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Animation|Locomotion",meta=(ClampMin="0.1")) float MaximumWalkRate=1.65f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Animation|Locomotion",meta=(ClampMin="0.1")) float WalkRateResponse=8.f;
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Animation|Locomotion") float GetWalkPlayRate(float Speed) const;
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Camera") void UpdateCameraRig(float Dt);
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Vehicle") float AdvanceDriveSpeed(float Dt,float TopSpeed);
 UFUNCTION(BlueprintPure,BlueprintNativeEvent,Category="Delivery|Vehicle") float SteeringAngle(float Dt) const;
 UFUNCTION(BlueprintPure,BlueprintNativeEvent,Category="Delivery|Movement") float WalkingSpeed() const;
 UFUNCTION(BlueprintCallable,Category="Delivery|Vehicle") void SetDeliveryDriveInput(float Throttle,bool Boost) {ForwardInput=FMath::Clamp(Throttle,-1.f,1.f);Sprint=Boost;}
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void StopForPhone();
 void RefreshVehicleArt();
 bool DeliveryVehiclePlaced=false;
 UFUNCTION(BlueprintCallable,Category="Delivery|Vehicle") bool PlaceDeliveryVehicle();
 void FinishDeliveryRide();
 void ActionPressed();
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void ActionReleased();
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void PickupPressed();
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void PickupReleased();
 void KeyboardActionPressed();
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void PhonePressed();
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void VehiclePressed();
 bool FullMap=false, Paused=false;
 int32 Quality=2;
 ABogotaCity* City=nullptr;
 FString InteractionText() const;
 void Interact();
protected:
 UPROPERTY() TObjectPtr<UAnimationAsset> Idle;
 UPROPERTY() TObjectPtr<UAnimationAsset> Walk;
 UPROPERTY() TObjectPtr<UAnimationAsset> Pedal;
 UPROPERTY() TObjectPtr<UAnimationAsset> MotoRide;
 UPROPERTY() TObjectPtr<UAnimationAsset> JumpClip;
 float LandingTime=0;
 float LocomotionRate=1;
 bool WasAirborne=false;
 UPROPERTY() TObjectPtr<UAnimationAsset> CurrentClip;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> Bicycle;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> FrontWheel;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> RearWheel;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> LeftPedal;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> RightPedal;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> UpgradeMesh;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> PhoneModel;
 UPROPERTY() TObjectPtr<USkeletalMeshComponent> CargoBackpack;
 UPROPERTY() TObjectPtr<USkeletalMeshComponent> CargoWaist;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> CargoPanniers;
 FString VehicleArtKey;
  float CrankAngle=0;
  UPROPERTY(BlueprintReadWrite,Category="Delivery|Input") float ForwardInput=0;
  UPROPERTY(BlueprintReadWrite,Category="Delivery|Input") float SideInput=0;
  UPROPERTY(BlueprintReadWrite,Category="Delivery|Vehicle") float BikeSpeed=0;
  float WheelAngle=0;
  int32 BikeIndex=INDEX_NONE;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Input") bool Sprint=false;
 bool TestHarness=false,TestWalk=false,TestMount=false,TestRide=false,TestDismount=false;
 float TestTime=0;
 int32 TestStage=0;
 FVector TestStart=FVector::ZeroVector;
 void TickValidation(float Dt);
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void MoveForward(float V);
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void MoveRight(float V);
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void Turn(float V);
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void Look(float V);
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void StartSprint();
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void EndSprint();
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void JumpOrBrake();
 UFUNCTION(BlueprintCallable,BlueprintNativeEvent,Category="Delivery|Input") void StopJump();
 void ToggleMap(); void SkipTime(); void ToggleQuality(); void TogglePause();
};

UCLASS()
class BOGOTAVOXEL_API ABogotaHUD : public AHUD {
 GENERATED_BODY()
public:
 virtual void DrawHUD() override;
private:
 void Text(const FString& S,float X,float Y,FLinearColor C,float Scale=1);
 void Map(ABogotaPlayer* P,float X,float Y,float W,float H,bool Full);
};

UCLASS()
class BOGOTAVOXEL_API ABogotaGameMode : public AGameModeBase {
 GENERATED_BODY()
public:
 ABogotaGameMode();
 virtual void BeginPlay() override;
};

