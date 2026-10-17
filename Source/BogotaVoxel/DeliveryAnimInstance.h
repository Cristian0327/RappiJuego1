#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "DeliveryAnimInstance.generated.h"
USTRUCT(BlueprintType)
struct FDeliveryMotionInput {
 GENERATED_BODY()
 UPROPERTY(BlueprintReadWrite) float Speed=0;
 UPROPERTY(BlueprintReadWrite) bool HasRider=false;
 UPROPERTY(BlueprintReadWrite) bool Riding=false;
 UPROPERTY(BlueprintReadWrite) bool Moto=false;
 UPROPERTY(BlueprintReadWrite) bool Falling=false;
 UPROPERTY(BlueprintReadWrite) float LandingTime=0;
 UPROPERTY(BlueprintReadWrite) float VerticalSpeed=0;
 UPROPERTY(BlueprintReadWrite) float JumpVelocity=420;
 UPROPERTY(BlueprintReadWrite) float CrankAngle=0;
 UPROPERTY(BlueprintReadWrite) float PedalLength=0;
 UPROPERTY(BlueprintReadWrite) float JumpLength=0;
 UPROPERTY(BlueprintReadWrite) float TargetWalkRate=1;
 UPROPERTY(BlueprintReadWrite) float WalkResponse=8;
};
UCLASS(Blueprintable)
class BOGOTAVOXEL_API UDeliveryAnimInstance:public UAnimInstance {
 GENERATED_BODY()
public:
 virtual void NativeUpdateAnimation(float DeltaSeconds) override;
 UFUNCTION(BlueprintImplementableEvent,BlueprintCallable,Category="Motion") void UpdateMotion(FDeliveryMotionInput Motion,float Dt);
 UPROPERTY(BlueprintReadWrite,Category="Motion") bool Walking=false;
 UPROPERTY(BlueprintReadWrite,Category="Motion") bool Mounted=false;
 UPROPERTY(BlueprintReadWrite,Category="Motion") bool Motorcycle=false;
 UPROPERTY(BlueprintReadWrite,Category="Motion") bool Jumping=false;
 UPROPERTY(BlueprintReadWrite,Category="Motion") float WalkRate=1;
 UPROPERTY(BlueprintReadWrite,Category="Motion") float PedalTime=0;
 UPROPERTY(BlueprintReadWrite,Category="Motion") float JumpTime=0;
private:
 FVector PreviousPosition=FVector::ZeroVector;
 bool MotionInitialized=false;
};
