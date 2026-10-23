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

