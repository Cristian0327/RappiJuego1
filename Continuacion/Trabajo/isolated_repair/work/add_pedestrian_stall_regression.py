from pathlib import Path
p=Path(__file__).resolve().parents[1]/'outputs/BogotaVoxel/Source/BogotaVoxel/BogotaTraffic.cpp'
s=p.read_text()
s=s.replace('int32 PedestrianVehicleOverlaps=0;TArray<float> Start;for(const auto& W:Walkers)Start.Add(W.Travelled);','int32 PedestrianVehicleOverlaps=0;TArray<float> Start,LastTravel,Still,Longest;for(const auto& W:Walkers){Start.Add(W.Travelled);LastTravel.Add(W.Travelled);Still.Add(0);Longest.Add(0);}')
needle='SimulateWalkers(1.f/15);for(const auto& W:Walkers)if(W.Crossing)'
replace='''SimulateWalkers(1.f/15);
 for(int32 I=0;I<Walkers.Num();I++){const auto& W=Walkers[I];bool SignalWait=W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing;
  Still[I]=W.Activity==EPedActivity::Walking&&!SignalWait&&W.Travelled-LastTravel[I]<.01f?Still[I]+1.f/15:0;Longest[I]=FMath::Max(Longest[I],Still[I]);LastTravel[I]=W.Travelled;}
 for(const auto& W:Walkers)if(W.Crossing)'''
assert needle in s;s=s.replace(needle,replace)
needle=' FString Result=FString::Printf(TEXT("{\\"pedestrians'
idx=s.index(needle)
s=s[:idx]+''' float LongestUnplannedStop=0;int32 StalledWalkers=0;for(int32 I=0;I<Longest.Num();I++){LongestUnplannedStop=FMath::Max(LongestUnplannedStop,Longest[I]);if(Longest[I]>20){StalledWalkers++;if(StalledWalkers<=8)UE_LOG(LogTemp,Warning,TEXT("PEDESTRIAN_STALL id=%d duration=%.1f segment=%d position=%s"),I,Longest[I],Walkers[I].Segment,*Walkers[I].Position.ToString());}}
'''+s[idx:]
s=s.replace('return Result.LeftChop(1)+FString::Printf(TEXT(",\\"parked_cars', 'Result=Result.LeftChop(1)+FString::Printf(TEXT(",\\"stalled_walkers\\":%d,\\"longest_unplanned_stop_seconds\\":%.2f}"),StalledWalkers,LongestUnplannedStop);\n return Result.LeftChop(1)+FString::Printf(TEXT(",\\"parked_cars')
p.write_text(s)
