#include "DeliveryAnimInstance.h"
#include "BogotaGame.h"
#include "DeliverySystem.h"
#include "Animation/AnimSequence.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
void UDeliveryAnimInstance::NativeUpdateAnimation(float Dt){
 Super::NativeUpdateAnimation(Dt);FDeliveryMotionInput Input;
 if(auto* P=Cast<ABogotaPlayer>(TryGetPawnOwner())){
  Input.HasRider=true;Input.Speed=P->GetVelocity().Size2D();Input.Riding=P->Riding;
  Input.Moto=P->Delivery&&P->Delivery->Vehicle==EDeliveryVehicle::Motorcycle;
  Input.Falling=P->GetCharacterMovement()->IsFalling();Input.LandingTime=P->LandingTime;
  Input.VerticalSpeed=P->GetVelocity().Z;Input.JumpVelocity=P->GetCharacterMovement()->JumpZVelocity;
  Input.CrankAngle=P->CrankAngle;Input.TargetWalkRate=P->GetWalkPlayRate(Input.Speed);Input.WalkResponse=P->WalkRateResponse;
  if(auto* Clip=Cast<UAnimSequence>(P->Pedal))Input.PedalLength=Clip->GetPlayLength();
  if(auto* Clip=Cast<UAnimSequence>(P->JumpClip))Input.JumpLength=Clip->GetPlayLength();
 }else{
  auto* Mesh=GetSkelMeshComponent();if(!Mesh)return;
  const FVector At=Mesh->GetComponentLocation();const float Distance=FVector::Dist2D(At,PreviousPosition);
  Input.Speed=MotionInitialized&&Dt>.0001f&&Distance<200?Distance/Dt:0;PreviousPosition=At;MotionInitialized=true;
 }
 UpdateMotion(Input,Dt);
}
void UDeliveryAnimInstance::UpdateMotion_Implementation(FDeliveryMotionInput Motion,float Dt){
 Walking=Motion.Speed>(Motion.HasRider?(Walking?8.f:25.f):(Walking?3.f:8.f));Mounted=Motion.Riding;Motorcycle=Motion.Moto;
 Jumping=!Mounted&&(Motion.Falling||Motion.LandingTime>0);
 const float Rate=Motion.HasRider?Motion.TargetWalkRate:FMath::Clamp(Motion.Speed/50.f,.3f,1.6f);
 WalkRate=FMath::FInterpTo(WalkRate,Rate,Dt,Motion.WalkResponse);
 PedalTime=FMath::Fmod(Motion.CrankAngle/(2*PI),1.f)*Motion.PedalLength;
 const float Phase=Motion.Falling?FMath::GetMappedRangeValueClamped(FVector2D(Motion.JumpVelocity,-Motion.JumpVelocity),FVector2D(.30f,.70f),Motion.VerticalSpeed):FMath::Lerp(.70f,1.f,FMath::Clamp(1.f-Motion.LandingTime/.18f,0.f,1.f));
 JumpTime=FMath::Clamp(Phase,0.f,1.f)*Motion.JumpLength;
}
