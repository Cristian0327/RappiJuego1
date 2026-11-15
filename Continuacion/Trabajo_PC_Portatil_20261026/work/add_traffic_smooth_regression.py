from pathlib import Path
p=Path(__file__).resolve().parents[1]/'outputs/BogotaVoxel/Source/BogotaVoxel/BogotaTraffic.cpp';s=p.read_text(encoding='utf-8-sig')
needle=' FString Result=FString::Printf(TEXT("{\\"seconds\\":%.1f,\\"vehicles'
idx=s.index(needle)
code=''' // Reproduce the original visual cadence separately from junction waiting:
 // a free car must change position on render frames between simulation steps.
 TArray<FStreetAgent> SavedVehicles=Vehicles;TArray<FWalker> SavedWalkers=Walkers;auto SavedReservations=TrafficReservations;
 FStreetAgent Probe=Vehicles[0];Probe.Route={FVector(-9000,-9000,9),FVector(-4000,-9000,9),FVector(-4000,-4000,9),FVector(-9000,-4000,9)};Probe.Segment=0;Probe.Position=Probe.PreviousPosition=Probe.Route[0];Probe.Heading=Probe.PreviousHeading=0;Probe.Speed=Probe.Velocity=900;Probe.PathDistance=0;Probe.LoopLength=PathLength(Probe.Route);Probe.Wait=Probe.StopCooldown=Probe.Travelled=0;
 Vehicles.Empty();Vehicles.Add(Probe);Walkers.Empty();TrafficReservations.Empty();UpdateTrafficVisuals(1);
 float Accumulator=0;int32 MovingRenderFrames=0;FVector PreviousVisual=Probe.Visual.IsValid()?Probe.Visual->GetOwner()->GetActorLocation():FVector::ZeroVector;
 for(int32 Frame=0;Frame<120;Frame++){Accumulator+=1.f/60;while(Accumulator>=1.f/30){SimulateTraffic(1.f/30);Accumulator-=1.f/30;}UpdateTrafficVisuals(Accumulator*30);
  if(Vehicles[0].Visual.IsValid()){FVector Current=Vehicles[0].Visual->GetOwner()->GetActorLocation();if(Frame>0&&FVector::Dist2D(Current,PreviousVisual)>1)MovingRenderFrames++;PreviousVisual=Current;}}
 float BeforeHitch=Vehicles[0].Travelled;Accumulator+=.2f;while(Accumulator>=1.f/30){SimulateTraffic(1.f/30);Accumulator-=1.f/30;}float HitchLoss=FMath::Abs((Vehicles[0].Travelled-BeforeHitch)-180);
 Vehicles=MoveTemp(SavedVehicles);Walkers=MoveTemp(SavedWalkers);TrafficReservations=MoveTemp(SavedReservations);UpdateTrafficVisuals(1);
'''
s=s[:idx]+code+s[idx:]
old='UE_LOG(LogTemp,Display,TEXT("TRAFFIC_VALIDATION %s"),*Result);return Result;'
new='Result=Result.LeftChop(1)+FString::Printf(TEXT(",\\"moving_render_frames\\":%d,\\"render_frames\\":120,\\"hitch_time_loss_cm\\":%.2f}"),MovingRenderFrames,HitchLoss);UE_LOG(LogTemp,Display,TEXT("TRAFFIC_VALIDATION %s"),*Result);return Result;'
assert old in s;s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
