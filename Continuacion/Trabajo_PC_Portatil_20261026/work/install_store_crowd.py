from pathlib import Path
root=Path(__file__).resolve().parents[1];p=root/'outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryStores.cpp';s=p.read_text();s=s.replace('#include "Animation/AnimSequence.h"','#include "Animation/AnimSequence.h"\n#include "Materials/MaterialInterface.h"\nnamespace {\n#include "CrowdCatalog.inl"\n}')
s=s.replace('UpdateCustomer(I,Dt);','UpdateCrowdCustomer(I,Dt);')
a=s.index('void ADeliveryPoint::UpdateCustomer_Implementation(');b=s.index('FVector ADeliveryPoint::InteriorPosition_',a)
s=s[:a]+'''void ADeliveryPoint::UpdateCustomer_Implementation(int32 Index,float Dt){UpdateCrowdCustomer(Index,Dt);}
void ADeliveryPoint::UpdateCrowdCustomer(int32 I,float Dt){
 auto* Player=UGameplayStatics::GetPlayerPawn(this,0);
 if(!WalkingCustomers.IsValidIndex(I)||!CustomerPathStart.IsValidIndex(I))return;auto* C=WalkingCustomers[I].Get();if(!C)return;
 auto Rest=[&](){if(C->AnimationData.AnimToPlay!=CustomerIdleClips[I])C->PlayAnimation(CustomerIdleClips[I],true);if(CustomerUsesCane[I]){C->SetPosition(0,false);C->SetPlayRate(0);}else C->SetPlayRate(1);};
 FHitResult Ground;FCollisionQueryParams GroundQuery;if(Player)GroundQuery.AddIgnoredActor(Player);FVector Foot=C->GetComponentLocation();
 if(GetWorld()->LineTraceSingleByChannel(Ground,Foot+FVector(0,0,100),Foot-FVector(0,0,100),ECC_Visibility,GroundQuery)&&Ground.ImpactNormal.Z>.7f){auto At=C->GetRelativeLocation();At.Z=Ground.ImpactPoint.Z-GetActorLocation().Z;C->SetRelativeLocation(At);}
 if(CustomerWaits[I]>0){CustomerWaits[I]=FMath::Max(0.f,CustomerWaits[I]-Dt);Rest();return;}
 FVector From=C->GetRelativeLocation(),To=CustomerStops[I]?CustomerPathEnd[I]:CustomerPathStart[I];To.Z=From.Z;FVector Delta=To-From;float Dist=Delta.Size2D();
 if(Dist<4){CustomerStops[I]=1-CustomerStops[I];CustomerWaits[I]=4.f+I*2;Rest();return;}
 FVector Next=From+Delta.GetSafeNormal2D()*FMath::Min(Dist,Dt*CustomerSpeeds[I]);
 if(Player&&FVector::Dist2D(GetActorLocation()+Next,Player->GetActorLocation())<100){Rest();return;}
 FHitResult Block;FCollisionQueryParams Query;if(Player)Query.AddIgnoredActor(Player);
 if(GetWorld()->SweepSingleByChannel(Block,GetActorLocation()+From+FVector(0,0,95),GetActorLocation()+Next+FVector(0,0,95),FQuat::Identity,ECC_WorldStatic,FCollisionShape::MakeCapsule(35,80),Query)){CustomerStops[I]=1-CustomerStops[I];CustomerWaits[I]=2;Rest();return;}
 if(C->AnimationData.AnimToPlay!=CustomerWalkClips[I])C->PlayAnimation(CustomerWalkClips[I],true);
 C->SetPlayRate(CustomerUsesCane[I]?.95f:CustomerSpeeds[I]/(140.f*C->GetRelativeScale3D().X));
 C->SetRelativeRotation(FMath::RInterpTo(C->GetRelativeRotation(),FRotator(0,Delta.Rotation().Yaw-90,0),Dt,5));C->SetRelativeLocation(Next);
}

'''+s[b:]
s=s.replace('void ADeliveryPoint::BuildStore(){','void ADeliveryPoint::BuildStore(){\n for(auto* C:WalkingCustomers)if(C)C->DestroyComponent();WalkingCustomers.Empty();CustomerWalkClips.Empty();CustomerIdleClips.Empty();CustomerStops.Empty();CustomerWaits.Empty();CustomerPathStart.Empty();CustomerPathEnd.Empty();CustomerSpeeds.Empty();CustomerUsesCane.Empty();')
a=s.index(' const TCHAR* Customers[]=');b=s.index(' const TCHAR* Goods[5][3]',a)
s=s[:a]+''' // Replace the former two repeated customers with a quiet, varied population.
 const uint32 CustomerSeed=FCrc::StrCrc32(*PointID.ToString());const int32 CustomerCount=4*HalfWidth*HalfDepth/10000.f<120?1:2;
 for(int32 I=0;I<CustomerCount;I++){
  const auto& Spec=CrowdModels[(CustomerSeed+I*13)%UE_ARRAY_COUNT(CrowdModels)];FString Name=Spec.Name;
  auto* C=NewObject<USkeletalMeshComponent>(this);AddInstanceComponent(C);C->SetupAttachment(RootComponent);
  const float X=(I==0?-1.f:1.f)*FMath::Min(430.f,HalfWidth*.4f);float StartY=FMath::Min(850.f,HalfDepth*2-450),EndY=StoreKind==1?FMath::Max(200.f,CounterDistanceMeters*100-175):HalfDepth*2-500;
  if(FMath::Abs(EndY-StartY)<180)StartY=FMath::Max(180.f,EndY-300);
  FVector From(X,StartY,10),To(X,EndY,10);C->SetRelativeLocation(FVector(X,StartY-HalfDepth,10-15000));C->SetRelativeRotation(FRotator(0,-90,0));C->SetRelativeScale3D(FVector(Spec.Scale));
  C->SetSkeletalMeshAsset(LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Crowd/People/SK_%s.SK_%s"),*Name,*Name)));C->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Crowd/MI_Crowd.MI_Crowd")));C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;C->bEnableUpdateRateOptimizations=true;C->RegisterComponent();
  auto* Walk=LoadObject<UAnimSequence>(nullptr,Spec.Cane?TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane"):TEXT("/Game/Crowd/AN_CrowdWalk_Mixamo.AN_CrowdWalk_Mixamo"));auto* Idle=LoadObject<UAnimSequence>(nullptr,Spec.Cane?TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane"):TEXT("/Game/Crowd/AN_CrowdIdle.AN_CrowdIdle"));
  WalkingCustomers.Add(C);CustomerWalkClips.Add(Walk);CustomerIdleClips.Add(Idle);CustomerStops.Add(1);CustomerWaits.Add(2.f+I*3);CustomerPathStart.Add(From);CustomerPathEnd.Add(To);CustomerSpeeds.Add(Spec.Cane?Spec.Speed:65.f);CustomerUsesCane.Add(Spec.Cane);C->PlayAnimation(Idle,true);if(Spec.Cane){C->SetPlayRate(0);C->SetPosition(0,false);}
 }
'''+s[b:];p.write_text(s)
for name in ['harmonize_crowd_material.py','validate_street_crowd.py','cleanup_crowd_import.py']:
 p=root/'work'/name;s=p.read_text().replace('range(30)','range(40)').replace("r['variants']==30","r['variants']==40");p.write_text(s)
p=root/'work/import_street_crowd.py';p.write_text(p.read_text().replace('assert len(report)==30','assert len(report)==40'))
p=root/'work/render_crowd_review.py';p.write_text(p.read_text().replace('target=Vector((1035,270,80))','target=Vector((1035,400,80))'))
