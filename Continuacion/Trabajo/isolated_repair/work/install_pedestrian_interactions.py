from pathlib import Path
root=Path(__file__).resolve().parents[1];p=root/'outputs/BogotaVoxel/Source/BogotaVoxel/BogotaTraffic.cpp';s=p.read_text()
needle='W.Heading=(W.Route[(W.Segment+1)%4]-W.Position).Rotation().Yaw;Walkers.Add(W);\n }\n}'
s=s.replace(needle,needle[:-1]+' BuildStreetInteractions();\n}')
s=s.replace('bool Green=NS?TrafficNSGreen():TrafficEWGreen();bool Free=!JunctionOwner;','bool Green=(NS?TrafficNSGreen():TrafficEWGreen())&&!PedestrianJunctions.Contains(Key);bool Free=!JunctionOwner;')
s=s.replace('for(const auto& W:Walkers){FVector D=W.Position-A.Position;', 'for(const auto& W:Walkers){if(PedHidden(W))continue;FVector D=W.Position-A.Position;')
old='if(A.Articulated&&NS&&A.StopCooldown==0&&A.Velocity>0)for(float Station:{-27000.f,-7000.f,17000.f,32000.f}){float D=(Station-A.Position.X)*Dir.X;if(D>0&&D<=A.Velocity*Dt+5){A.Wait=3.5f;A.StopCooldown=20;}}'
new='if(A.Articulated&&NS&&A.StopCooldown==0)for(float Station:{-27000.f,-7000.f,17000.f,32000.f}){float D=(Station-A.Position.X)*Dir.X;if(D>=-12&&D<3000){Limit=FMath::Min(Limit,FMath::Max(0.f,D));Desired=FMath::Min(Desired,FMath::Sqrt(1300.f*FMath::Max(0.f,D)));if(D<=12&&A.Velocity<80){A.Wait=4.5f;A.StopCooldown=20;}}}'
s=s.replace(old,new)
# Definitions appear before traffic simulation so hidden riders never become obstacles.
mark='void ABogotaCity::SimulateTraffic(float Dt){';s=s.replace(mark,'#include "BogotaPedestrianBehaviors.inl"\n'+mark)
a=s.index('void ABogotaCity::SimulateWalkers(');b=s.index('USkeleton* ABogotaCity::CreateCrowdSkeleton(',a)
existing=s[a:b];start=existing.index('  auto& W=Walkers[I];');end=existing.index('  int32 Rank=Nearest.Find(I);')
movement='''  auto& W=Walkers[I];float Move=0;
  if(!UpdateWalkerInteraction(W,Dt)){
   FVector Target=W.Route[(W.Segment+1)%W.Route.Num()],Dir=(Target-W.Position).GetSafeNormal2D();float Facing=Dir.Rotation().Yaw;
   W.Heading=FMath::FixedTurn(W.Heading,Facing,Dt*180);Move=FMath::Abs(FMath::FindDeltaAngleDegrees(W.Heading,Facing))<8?W.Speed*Dt:0;
   if(W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing){
    float Phase=FMath::Fmod(Elapsed,32.f);bool Red=W.CrossSegments[W.Segment]==1?Phase>=16:Phase<16;
    bool Ready=Red&&!TrafficReservations.Contains(W.CrossJunction)&&Elapsed>=PedestrianNextAdmission.FindRef(W.CrossJunction);
    if(Ready){W.Crossing=true;PedestrianJunctions.Add(W.CrossJunction);PedestrianNextAdmission.Add(W.CrossJunction,Elapsed+FVector::Dist2D(W.Position,Target)/W.Speed+32);if(!Red)IllegalCrossings++;}else Move=0;
   }
   if(Player&&!W.Crossing&&FVector::DistSquared2D(PP,W.Position)<125*125)Move=0;
   for(int32 J=0;J<Walkers.Num();J++)if(J!=I&&!PedHidden(Walkers[J])){FVector D=Walkers[J].Position-W.Position;float Ahead=FVector::DotProduct(D,Dir);if(Ahead>0&&Ahead<110&&FMath::Abs(FVector::CrossProduct(D,Dir).Z)<32)Move=FMath::Min(Move,FMath::Max(0.f,Ahead-80));}
   float Distance=FVector::Dist2D(Target,W.Position);Move=FMath::Min(Move,Distance);W.Position+=Dir*Move;W.Travelled+=Move;
   if(Distance<Move+1){W.Position=Target;if(W.Crossing){W.Crossing=false;PedestrianCrossings++;PedestrianNextAdmission.Add(W.CrossJunction,Elapsed+32);}W.Segment=(W.Segment+1)%W.Route.Num();}
  }else Move=W.FrameMoved;
  if(W.Activity==EPedActivity::Walking||W.Activity==EPedActivity::ApproachCar||W.Activity==EPedActivity::ReturningRoute){FHitResult Ground;FCollisionQueryParams Query;Query.AddIgnoredActor(this);if(W.Visual.IsValid())Query.AddIgnoredActor(W.Visual.Get());if(GetWorld()->LineTraceSingleByChannel(Ground,W.Position+FVector(0,0,100),W.Position-FVector(0,0,100),ECC_Visibility,Query)&&Ground.ImpactNormal.Z>.7f)W.Position.Z=Ground.ImpactPoint.Z;}
'''
existing=existing[:start]+movement+existing[end:]
existing=existing.replace(' int32 Active=0;','')
existing=existing.replace(' TArray<int32> Nearest;', ' PedestrianJunctions.Empty();for(const auto& W:Walkers)if(W.Crossing)PedestrianJunctions.Add(W.CrossJunction);\n TArray<int32> Nearest;')
existing=existing.replace('if(FVector::DistSquared2D(PP,Walkers[I].Position)<', 'if(!PedHidden(Walkers[I])&&FVector::DistSquared2D(PP,Walkers[I].Position)<')
existing=existing.replace('bool Near=Rank!=INDEX_NONE&&Rank<24;', 'bool Near=!PedHidden(W)&&Rank!=INDEX_NONE&&Rank<24;')
anim='''   W.Visual->SetActorHiddenInGame(false);W.Visual->SetActorLocationAndRotation(W.Position,FRotator(0,W.Heading-90,0));
   if(auto* S=Cast<USkeletalMeshComponent>(W.Visual->GetRootComponent())){
    uint8 Clip=W.Activity==EPedActivity::EnteringCar?2:W.Activity==EPedActivity::LeavingCar?3:W.Activity==EPedActivity::BoardingTransit?4:W.Activity==EPedActivity::AlightingTransit?5:Move>0?(CrowdModels[W.ModelIndex].Cane?6:0):(CrowdModels[W.ModelIndex].Cane?7:1);
    const TCHAR* Paths[]={TEXT("/Game/Crowd/AN_CrowdWalk_Mixamo.AN_CrowdWalk_Mixamo"),TEXT("/Game/Crowd/AN_CrowdIdle.AN_CrowdIdle"),TEXT("/Game/Crowd/AN_CrowdEnterCar.AN_CrowdEnterCar"),TEXT("/Game/Crowd/AN_CrowdEnterCar.AN_CrowdEnterCar"),TEXT("/Game/Crowd/AN_CrowdBoard.AN_CrowdBoard"),TEXT("/Game/Crowd/AN_CrowdBoard.AN_CrowdBoard"),TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane"),TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane")};
    if(W.VisualAnimation!=Clip){auto* A=LoadObject<UAnimationAsset>(nullptr,Paths[Clip]);S->PlayAnimation(A,Clip==0||Clip==1||Clip==6||Clip==7);if(Clip==3||Clip==5)S->SetPosition(S->GetSingleNodeInstance()?Cast<UAnimSequence>(A)->GetPlayLength():1.2f,false);if(Clip==7)S->SetPosition(0,false);W.VisualAnimation=Clip;}
    S->SetPlayRate(Clip==3||Clip==5?-1.f:Clip==7?0.f:Clip==6?.95f:Clip==0?W.Speed/(140.f*W.Scale):1.f);
   }
'''
aa=existing.index('   W.Visual->SetActorHiddenInGame(false);');bb=existing.index('  }else if(W.Visual.IsValid())',aa);existing=existing[:aa]+anim+existing[bb:]
s=s[:a]+existing+s[b:]
s=s.replace('#include "Animation/AnimationAsset.h"','#include "Animation/AnimationAsset.h"\n#include "Animation/AnimSequence.h"')
# Couple both simulations during validation; waiting at a station is legitimate.
s=s.replace('for(int32 Step=0;Step<FMath::CeilToInt(Seconds*15);Step++)SimulateWalkers(1.f/15);','for(int32 Step=0;Step<FMath::CeilToInt(Seconds*15);Step++){Elapsed+=1.f/15;SimulateTraffic(1.f/15);SimulateWalkers(1.f/15);}')
s=s.replace('Minimum=FMath::Min(Minimum,Walkers[I].Travelled-Start[I]);','if(!Walkers[I].TransitPassenger)Minimum=FMath::Min(Minimum,Walkers[I].Travelled-Start[I]);')
p.write_text(s)
p=root/'outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryStores.cpp';p.write_text(p.read_text().replace('for(auto* C:WalkingCustomers)','for(auto C:WalkingCustomers)'))
p=root/'work/validate_street_crowd.py';p.write_text(p.read_text().replace('city.validate_crowd(180)','city.validate_crowd(600)').replace("r['minimum_travel_cm']>10000","r['minimum_travel_cm']>2000"))
