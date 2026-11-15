from pathlib import Path
r=Path('outputs/BogotaVoxel/Source/BogotaVoxel');p=r/'BogotaGame.h';s=p.read_text().replace(' void SimulateWalkers(float Dt);',' TOptional<FVector> PedestrianTestObstacle;\n void SimulateWalkers(float Dt);');p.write_text(s)
p=r/'BogotaTraffic.cpp';s=p.read_text().replace('FVector PP=Player?Player->GetActorLocation():FVector::ZeroVector;','FVector PP=PedestrianTestObstacle.IsSet()?PedestrianTestObstacle.GetValue():Player?Player->GetActorLocation():FVector::ZeroVector;');s=s.replace('if(Player&&FMath::Abs(PP.Z-W.Position.Z)<300','if((Player||PedestrianTestObstacle.IsSet())&&FMath::Abs(PP.Z-W.Position.Z)<300')
pos=s.index('USkeleton* ABogotaCity::CreateCrowdSkeleton')
s=s[:pos]+'''FString ABogotaCity::ValidateStreetFlow(){
 if(Walkers.IsEmpty())BuildTraffic();
 auto SavedWalkers=Walkers;auto SavedVehicles=Vehicles;auto SavedJunctions=PedestrianJunctions;auto SavedAdmission=PedestrianNextAdmission;float SavedElapsed=Elapsed;
 const FVector Start(-8000,-8000,27);int32 Failures=0,PassedPlayer=0,PassedSlow=0;float MinPlayerDistance=1e9;
 for(int32 Scenario=0;Scenario<2;Scenario++){
  Walkers.Empty();Vehicles.Empty();PedestrianJunctions.Empty();PedestrianNextAdmission.Empty();PedestrianTestObstacle.Reset();
  for(int32 I=0;I<6;I++){FWalker W;W.Route={Start+FVector(-2000,0,0),Start+FVector(6000,0,0),Start+FVector(6000,1500,0),Start+FVector(-2000,1500,0)};W.Position=Start+FVector(-I*120,0,0);W.Speed=112;W.ModelIndex=0;Walkers.Add(W);}
  if(Scenario==0)PedestrianTestObstacle=Start+FVector(700,0,0);
  else {FWalker Slow=Walkers[0];Slow.Speed=38;Slow.ModelIndex=6;Slow.Position=Start+FVector(240,0,0);Walkers.Add(Slow);}
  for(int32 Step=0;Step<600;Step++){Elapsed+=1.f/15;SimulateWalkers(1.f/15);if(Scenario==0)for(const auto& W:Walkers)MinPlayerDistance=FMath::Min(MinPlayerDistance,FVector::Dist2D(W.Position,PedestrianTestObstacle.GetValue()));}
  for(int32 I=0;I<6;I++)if(Scenario==0){if(Walkers[I].Position.X>Start.X+1500)PassedPlayer++;}else if(Walkers[I].Position.X>Walkers.Last().Position.X+150)PassedSlow++;
  for(auto& W:Walkers)if(W.Visual.IsValid())W.Visual->Destroy();
 }
 Walkers=MoveTemp(SavedWalkers);Vehicles=MoveTemp(SavedVehicles);PedestrianJunctions=MoveTemp(SavedJunctions);PedestrianNextAdmission=MoveTemp(SavedAdmission);PedestrianTestObstacle.Reset();Elapsed=SavedElapsed;
 int32 ShortRoutes=0,WrongKeys=0,CrossingRoutes=0;
 for(const auto& W:Walkers)if(!W.CrossSegments.IsEmpty()){
  CrossingRoutes++;TArray<int32> Cross;for(int32 I=0;I<W.CrossSegments.Num();I++)if(W.CrossSegments[I])Cross.Add(I);
  if(Cross.Num()!=2||!W.CrossJunctions.IsValidIndex(Cross.Last())){WrongKeys++;continue;}
  if(W.CrossJunctions[Cross[0]]==W.CrossJunctions[Cross[1]])WrongKeys++;
  for(int32 C=0;C<2;C++){float Distance=0;for(int32 I=(Cross[C]+1)%W.Route.Num();I!=Cross[1-C];I=(I+1)%W.Route.Num())Distance+=FVector::Dist2D(W.Route[I],W.Route[(I+1)%W.Route.Num()]);if(Distance<5000)ShortRoutes++;}
 }
 Failures=(PassedPlayer!=6)+(PassedSlow!=6)+(MinPlayerDistance<120)+ShortRoutes+WrongKeys;
 return FString::Printf(TEXT("{\\"passed_stationary_player\\":%d,\\"passed_slow_walker\\":%d,\\"minimum_player_clearance_cm\\":%.1f,\\"crossing_routes\\":%d,\\"short_return_routes\\":%d,\\"incorrect_crossing_keys\\":%d,\\"failures\\":%d}"),PassedPlayer,PassedSlow,MinPlayerDistance,CrossingRoutes,ShortRoutes,WrongKeys,Failures);
}
'''+s[pos:];p.write_text(s)
