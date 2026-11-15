from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/BogotaTraffic.cpp');s=p.read_text();s=s.replace('FVector Target=W.Route[(W.Segment+1)%W.Route.Num()],Dir=(Target-W.Position).GetSafeNormal2D();float Facing=Dir.Rotation().Yaw;','''FVector Target=W.Route[(W.Segment+1)%W.Route.Num()];
   FVector SegmentDirection=(Target-W.Route[W.Segment]).GetSafeNormal2D();
   bool EndpointBlocked=(Player||PedestrianTestObstacle.IsSet())&&FMath::Abs(PP.Z-W.Position.Z)<300&&FVector::DistSquared2D(PP,Target)<FMath::Square(140.f);
   FVector SteeringTarget=EndpointBlocked?Target+SegmentDirection*220:Target,Dir=(SteeringTarget-W.Position).GetSafeNormal2D();''')
s=s.replace('float Distance=FVector::Dist2D(Target,W.Position);Move=FMath::Min(Move,Distance);W.Position+=Dir*Move;W.Travelled+=Move;','float Distance=FVector::Dist2D(SteeringTarget,W.Position);Move=FMath::Min(Move,Distance);W.Position+=Dir*Move;W.Travelled+=Move;')
s=s.replace('if(FVector::Dist2D(Target,W.Position)<18){W.Position=Target;if(W.Crossing)', 'if(FVector::Dist2D(Target,W.Position)<18||(EndpointBlocked&&FVector::DotProduct(W.Position-Target,SegmentDirection)>=0)){if(!EndpointBlocked)W.Position=Target;if(W.Crossing)')
s=s.replace('PassedPlayer=0,PassedSlow=0;','PassedPlayer=0,PassedSlow=0,PassedCorner=0;').replace('Scenario<2;Scenario++','Scenario<3;Scenario++')
s=s.replace('  if(Scenario==0)PedestrianTestObstacle=Start+FVector(700,0,0);\n  else {FWalker Slow=', '  if(Scenario==0)PedestrianTestObstacle=Start+FVector(700,0,0);\n  else if(Scenario==2){PedestrianTestObstacle=Start+FVector(1200,0,0);for(auto& W:Walkers){W.Route[1].X=Start.X+1200;W.Route[2].X=Start.X+1200;}}\n  else {FWalker Slow=')
s=s.replace('if(Scenario==0)for(const auto& W:Walkers)MinPlayerDistance','if(Scenario!=1)for(const auto& W:Walkers)MinPlayerDistance')
s=s.replace('}else if(Walkers[I].Position.X>Walkers.Last().Position.X+150)PassedSlow++;','}else if(Scenario==1){if(Walkers[I].Position.X>Walkers.Last().Position.X+150)PassedSlow++;}else if(Walkers[I].Position.Y>Start.Y+300)PassedCorner++;')
s=s.replace('Failures=(PassedPlayer!=6)+(PassedSlow!=6)+','Failures=(PassedPlayer!=6)+(PassedSlow!=6)+(PassedCorner!=6)+')
s=s.replace('\\"passed_slow_walker\\":%d,','\\"passed_slow_walker\\":%d,\\"passed_blocked_corner\\":%d,').replace('PassedPlayer,PassedSlow,MinPlayerDistance','PassedPlayer,PassedSlow,PassedCorner,MinPlayerDistance')
p.write_text(s)
