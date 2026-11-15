from pathlib import Path
p=Path('work/render_main_motion.py');s=p.read_text().replace("if o.type in {'MESH','ARMATURE'}:o.scale*=.01", "if o.type=='ARMATURE':o.scale*=.01");p.write_text(s)
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/BogotaGame.h');s=p.read_text(encoding='utf-8');s=s.replace('UPROPERTY() TObjectPtr<UAnimationAsset> MotoRide;', 'UPROPERTY() TObjectPtr<UAnimationAsset> MotoRide;\n UPROPERTY() TObjectPtr<UAnimationAsset> JumpClip;\n float LandingTime=0;\n bool WasAirborne=false;');s=s.replace('UPROPERTY() TObjectPtr<UStaticMeshComponent> PhoneModel;', 'UPROPERTY() TObjectPtr<UStaticMeshComponent> PhoneModel;\n UPROPERTY() TObjectPtr<USkeletalMeshComponent> CargoBackpack;\n UPROPERTY() TObjectPtr<USkeletalMeshComponent> CargoWaist;\n UPROPERTY() TObjectPtr<UStaticMeshComponent> CargoPanniers;');p.write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/BogotaPlayer.cpp');s=p.read_text(encoding='utf-8');s=s.replace('#include "Animation/AnimationAsset.h"','#include "Animation/AnimationAsset.h"\n#include "Animation/AnimSequence.h"');s=s.replace('Super::BeginPlay();GetMesh()', 'Super::BeginPlay();if(auto* A=LoadObject<UAnimationAsset>(nullptr,TEXT("/Game/VoxelExplorer/AN_MixamoWalk.AN_MixamoWalk")))Walk=A;JumpClip=LoadObject<UAnimationAsset>(nullptr,TEXT("/Game/VoxelExplorer/AN_MixamoJump.AN_MixamoJump"));GetMesh()',1)
a=s.index('  float Speed=GetVelocity().Size2D();UAnimationAsset* Clip=');b=s.index('\n CameraBoom->',a);s=s[:a]+'''  float Speed=GetVelocity().Size2D();bool Airborne=!Riding&&GetCharacterMovement()->IsFalling();if(WasAirborne&&!Airborne)LandingTime=.18f;WasAirborne=Airborne;LandingTime=FMath::Max(0.f,LandingTime-Dt);
 UAnimationAsset* Clip=Riding?(Moto&&MotoRide?MotoRide.Get():Pedal.Get()):((Airborne||LandingTime>0)&&JumpClip?JumpClip.Get():(Speed>10?Walk.Get():Idle.Get()));
 if(Clip&&Clip!=CurrentClip){GetMesh()->PlayAnimation(Clip,Clip!=JumpClip);CurrentClip=Clip;}
 GetMesh()->SetPlayRate(Riding?1.f:(Clip==Walk?FMath::Clamp(Speed/180,.4f,3.7f):1.f));
 if(Riding&&!Moto)if(auto* A=Cast<UAnimSequence>(Pedal))GetMesh()->SetPosition(FMath::Fmod(CrankAngle/(2*PI),1.f)*A->GetPlayLength(),false);
 if(Clip==JumpClip&&JumpClip){float Phase=Airborne?FMath::GetMappedRangeValueClamped(FVector2D(430,-430),FVector2D(.65,1.40),GetVelocity().Z):1.4f+(.18f-LandingTime)*2.f;GetMesh()->SetPosition(Phase,false);GetMesh()->SetPlayRate(0);}
'''+s[b:];p.write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryVehicleArt.cpp');s=p.read_text(encoding='utf-8');a=s.index(' if(!PhoneModel)');s=s[:a]+''' auto Wear=[&](TObjectPtr<USkeletalMeshComponent>& C,const TCHAR* Name,const TCHAR* Upgrade){
  if(!C){C=NewObject<USkeletalMeshComponent>(this,Name);C->SetupAttachment(GetMesh());C->RegisterComponent();C->SetSkeletalMesh(LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Delivery/Art/SK_%s.SK_%s"),Name,Name)));C->SetLeaderPoseComponent(GetMesh());C->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
  C->SetHiddenInGame(!Delivery->Owns(Upgrade));C->SetOwnerNoSee(Delivery->InsideStore!=nullptr);
 };
 Wear(CargoBackpack,TEXT("CargoBackpack"),TEXT("CargoBackpack"));Wear(CargoWaist,TEXT("CargoWaist"),TEXT("CargoWaist"));
 if(!CargoPanniers){CargoPanniers=NewObject<UStaticMeshComponent>(this,TEXT("CargoPanniers"));CargoPanniers->SetupAttachment(RootComponent);CargoPanniers->RegisterComponent();CargoPanniers->SetStaticMesh(ArtMesh(TEXT("SM_CargoPanniers")));CargoPanniers->SetRelativeLocation(FVector(0,0,-90));CargoPanniers->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
 CargoPanniers->SetHiddenInGame(!Moto||!Riding||!Delivery->Owns(TEXT("CargoPanniers")));
 if(City&&City->BikeActors.Num()>0)if(auto* Parked=Cast<AStaticMeshActor>(City->BikeActors[0].Get())){
  auto* C=FindObject<UStaticMeshComponent>(Parked,TEXT("ParkedPanniers"));if(!C){C=NewObject<UStaticMeshComponent>(Parked,TEXT("ParkedPanniers"));C->SetupAttachment(Parked->GetRootComponent());C->RegisterComponent();C->SetStaticMesh(ArtMesh(TEXT("SM_CargoPanniers")));C->SetCollisionEnabled(ECollisionEnabled::NoCollision);}C->SetVisibility(Moto&&Delivery->Owns(TEXT("CargoPanniers")));
 }
'''+s[a:];p.write_text(s,encoding='utf-8')
