#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "BogotaGame.generated.h"

class UHierarchicalInstancedStaticMeshComponent;
class UInstancedStaticMeshComponent;
class UDirectionalLightComponent;
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
 bool PlayerControlled=false,DevParked=false;
 float DoorOpen=0,VisualDoorOpen=0,GroundOffset=0,GroundPitch=0,GroundRoll=0;
 TMap<FName,FTransform> DoorRest;
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
struct FParkedTrafficCar {bool CurbParked=false;float DoorOpen=0,VisualDoorOpen=0,DoorTarget=0;TMap<FName,FTransform> DoorRest;TArray<TWeakObjectPtr<USpotLightComponent>> Headlights;FVector Position=FVector::ZeroVector,Door=FVector::ZeroVector;float Heading=90;int32 Walker=INDEX_NONE;bool Occupied=false;TWeakObjectPtr<UPoseableMeshComponent> Visual;};
struct FWalker {
 TArray<FVector> Route;
 FVector Position=FVector::ZeroVector,Velocity=FVector::ZeroVector,PreviousPosition=FVector::ZeroVector;
 float PreviousHeading=0;bool YieldingToPlayer=false;
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
 friend class ABogotaPlayer;
 ABogotaCity();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(EditAnywhere,BlueprintReadWrite, Category="Bogota") float CycleMinutes=24;
 UPROPERTY(VisibleAnywhere,BlueprintReadWrite, Category="Bogota") float Hour=9;
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
 UFUNCTION(CallInEditor,BlueprintCallable,Category="World|QA") FString ValidateMapRoutes(float Seconds=600);
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|Weather") int32 NextWeatherState(int32 CurrentState,float Roll) const;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="World|Weather",meta=(ClampMin="0",ClampMax="1")) float RainStartChance=.35f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="World|Weather") FVector2D DryWeatherHold=FVector2D(90,180);
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="World|Weather") FVector2D WetWeatherHold=FVector2D(45,100);
 UPROPERTY(VisibleAnywhere,BlueprintReadWrite,Category="World|Weather") int32 AutomaticWeatherState=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadWrite,Category="World|Weather") float WeatherDecisionRemaining=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadWrite,Category="World|Weather") float WeatherTargetIntensity=0;
 UPROPERTY(Transient,BlueprintReadWrite,Category="World|Weather") FRandomStream WeatherRandom;
 UPROPERTY(Transient,BlueprintReadWrite,Category="World|Weather") bool WeatherInitialized=false;
 UPROPERTY(Transient,BlueprintReadWrite,Category="World|Weather") int32 PreviousWeatherOverride=-1;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="World|Weather") float AdvanceDynamicWeather(float Dt);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="World|Weather") float ChooseWeatherHold();
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|Weather") int32 WeatherStateForIntensity(float Intensity) const;
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|Weather") float WeatherIntensityForState(int32 State) const;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="World|Parking") void InitializeParkingPlan(int32 Seed);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="World|Parking") FVector ParkingPoseFor(int32 Slot,float Side);
 UPROPERTY(Transient,BlueprintReadWrite,Category="World|Parking") FRandomStream ParkingRandom;
 UPROPERTY(Transient,BlueprintReadWrite,Category="World|Parking") TArray<int32> CurbParkingSlots;
 FString ValidateDynamicWeather();
 UPROPERTY(VisibleAnywhere,BlueprintReadWrite,Category="World|Weather") float RainIntensity=0;
 UPROPERTY(Transient,BlueprintReadWrite,Category="World|Weather") int32 DeveloperRainOverride=-1;
 UFUNCTION(BlueprintCallable,Category="Crowd") class USkeleton* CreateCrowdSkeleton(class USkeletalMesh* Source);
 UFUNCTION(BlueprintCallable,Category="Crowd") void BindCrowdMesh(class USkeletalMesh* Mesh,class USkeleton* Skeleton);
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|Districts") FString DistrictAt(FVector P) const;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="World|Clock") void AdvanceTime();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="World|Clock") void AdvanceClock(float Dt);
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|Clock") float HourForCycle(float Seconds) const;
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|TrafficPaint") FLinearColor TrafficPaintFor(int32 VehicleIndex) const;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="World|TrafficPaint") TArray<FLinearColor> TrafficPaintPalette;
 UFUNCTION(BlueprintCallable,Category="World|Rendering") void RefreshWorldLighting();
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|Signals") bool TrafficNSGreen() const;
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|Signals") bool TrafficEWGreen() const;
 UFUNCTION(BlueprintCallable,Category="World|Rendering") void SetDetail(int32 Detail);
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
 UPROPERTY(BlueprintReadWrite,Category="World|Clock") float Elapsed=0;
 UPROPERTY(BlueprintReadWrite,Category="World|Clock") float CycleSeconds=180;
 float SimAccumulator=0, LightAccumulator=0, PedAccumulator=0;
 int32 DetailLevel=2;
 UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> TrafficMaterial;
 UPROPERTY() TArray<TObjectPtr<class USkeletalMesh>> CrowdMeshes;
 UPROPERTY() TArray<TObjectPtr<UAnimationAsset>> CrowdClips;
 UPROPERTY() TObjectPtr<UMaterialInterface> CrowdMaterial;
 UPROPERTY(BlueprintReadWrite,Category="World|Clock") int32 GameDay=0;
 int32 G66CheckedNight=-1,G66LastNight=-100;
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
 void ApplyVehicleDoors(UPoseableMeshComponent* Visual,bool Bus,float Left,float Right,TMap<FName,FTransform>& Rest);
 void UpdateParkedDoors(float Dt);
 bool ResolveVehicleGround(const FStreetAgent& Vehicle,FVector At,float Heading,FVector& Ground,FRotator& Rotation) const;
 void UpdateVehicleGroundVisual(FStreetAgent& Vehicle,FVector At,float Heading,float Dt);
 FString ValidateVehicleDynamics();
 void TickVehicleDynamicsVisualCheck();
 TOptional<FVector> PedestrianTestObstacle;
 void SimulateWalkers(float Dt);
 void UpdateWalkerVisuals(float Alpha);
 bool WalkerStreetStepClear(const FWalker& Walker,FVector From,FVector To) const;
 float StreetClearance(FVector At) const;
 void SimulateDeveloperCar(int32 Index,float Dt);
 FString ValidatePedestrianPresentation();
 void BuildStreetInteractions();
 bool UpdateWalkerInteraction(FWalker& Walker,float Dt);
 bool WalkerStepClear(FVector From,FVector To) const;
 float WalkerGroundHeight(FVector At) const;
 void UpdateWeather(float Dt);
 UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> RainMesh;
 UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> HailMesh;
 UPROPERTY() TObjectPtr<UDirectionalLightComponent> LightningLight;
 UPROPERTY(VisibleAnywhere,BlueprintReadWrite,Category="World|Weather") float HailIntensity=0;
 TArray<FVector> HailDrops;
 TArray<float> HailFloors;
 float StormClock=0,NextLightning=8,LightningFlash=0,ThunderDelay=-1;
 int32 LightningEvents=0,ThunderEvents=0;
 TArray<FVector> RainDrops;
 TArray<float> RainFloors;
 FVector RainOrigin=FVector(1e9);
 FRandomStream RainRandom{271828};
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
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Animation|Locomotion") float GetWalkPlayRate(float Speed) const;
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Camera") void UpdateCameraRig(float Dt);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Vehicle") float AdvanceDriveSpeed(float Dt,float TopSpeed);
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="Delivery|Vehicle") float SteeringAngle(float Dt) const;
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="Delivery|Movement") float WalkingSpeed() const;
 UFUNCTION(BlueprintCallable,Category="Delivery|Vehicle") void SetDeliveryDriveInput(float Throttle,bool Boost) {ForwardInput=FMath::Clamp(Throttle,-1.f,1.f);Sprint=Boost;}
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void StopForPhone();
 void RefreshVehicleArt();
 bool DeliveryVehiclePlaced=false;
 UFUNCTION(BlueprintCallable,Category="Delivery|Vehicle") bool PlaceDeliveryVehicle();
 void FinishDeliveryRide();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void ActionPressed();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void ActionReleased();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void PickupPressed();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void PickupReleased();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void KeyboardActionPressed();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void PhonePressed();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void VehiclePressed();
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Pause") bool Paused=false;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|Quality") int32 Quality=2;
 UPROPERTY(BlueprintReadWrite,Category="Delivery|World") ABogotaCity* City=nullptr;
 FString InteractionText() const;
 UFUNCTION(BlueprintCallable,Category="Delivery|Vehicle") void Interact();
 UFUNCTION(Exec,BlueprintCallable,Category="Developer") void BogDev(bool Enabled=true);
 UFUNCTION(Exec,BlueprintCallable,Category="Developer") void BogRain(int32 Mode=1);
 UFUNCTION(Exec,BlueprintCallable,Category="Developer") void BogCar(int32 Index=-1);
 UFUNCTION(BlueprintCallable,Category="Developer") void SpawnPurpleBus();
 int32 DeveloperPurpleBusIndex=INDEX_NONE;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Developer") int32 DeveloperCarIndex=-1;
 bool EnterDeveloperCar(int32 Index=-1);
 bool LeaveDeveloperCar();
 UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="Developer|Drive") FVector2D DeveloperDriveInput() const;
 FString ValidateDeveloperTools();
 void UpdateDeveloperCarView(float Dt);
 float DeveloperCameraLength=430,DeveloperLastHeading=0;
 FVector DeveloperCameraOffset=FVector::ZeroVector;
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
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void MoveForward(float V);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void MoveRight(float V);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void Turn(float V);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void Look(float V);
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void StartSprint();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void EndSprint();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void JumpOrBrake();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Input") void StopJump();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|World") void SkipTime();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Quality") void ToggleQuality();
 UFUNCTION(BlueprintCallable,BlueprintImplementableEvent,Category="Delivery|Pause") void TogglePause();
};

UCLASS()
class BOGOTAVOXEL_API ABogotaHUD : public AHUD {
 GENERATED_BODY()
public:
 virtual void DrawHUD() override;
private:
 void Text(const FString& S,float X,float Y,FLinearColor C,float Scale=1);
};

UCLASS()
class BOGOTAVOXEL_API ABogotaGameMode : public AGameModeBase {
 GENERATED_BODY()
public:
 ABogotaGameMode();
 virtual void BeginPlay() override;
};

