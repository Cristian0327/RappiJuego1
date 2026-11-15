from pathlib import Path
root=Path(__file__).resolve().parents[1];p=root/'outputs/BogotaVoxel/Source/BogotaVoxel/BogotaTraffic.cpp';s=p.read_text();a=s.index('FString ABogotaCity::ValidateCrowd(');b=s.index('void ABogotaCity::UpdateTrafficNight()',a);part=s[a:b]
part=part.replace('TArray<float> Start;','int32 PedestrianVehicleOverlaps=0;TArray<float> Start;')
part=part.replace('SimulateWalkers(1.f/15);}', '''SimulateWalkers(1.f/15);for(const auto& W:Walkers)if(W.Crossing)for(const auto& A:Vehicles){FVector D=W.Position-A.Position,Forward=FRotator(0,A.Heading,0).Vector(),Right(-Forward.Y,Forward.X,0);if(FMath::Abs(FVector::DotProduct(D,Forward))<A.HalfLength+30&&FMath::Abs(FVector::DotProduct(D,Right))<A.HalfWidth+30)PedestrianVehicleOverlaps++;}}''')
part=part.replace('return FString::Printf(TEXT("{\\"pedestrians', 'FString Result=FString::Printf(TEXT("{\\"pedestrians')
part=part.replace('Walkers.Num(),Models.Num(),Missing,Invalid,Minimum);', '''Walkers.Num(),Models.Num(),Missing,Invalid,Minimum);
 return Result.LeftChop(1)+FString::Printf(TEXT(",\\"parked_cars\\":%d,\\"crossings_completed\\":%d,\\"illegal_crossings\\":%d,\\"pedestrian_vehicle_overlap_frames\\":%d,\\"car_boardings\\":%d,\\"bus_boardings\\":%d,\\"bus_alightings\\":%d}"),ParkedCars.Num(),PedestrianCrossings,IllegalCrossings,PedestrianVehicleOverlaps,ParkedCarBoardings,TransitBoardings,TransitAlightings);''')
s=s[:a]+part+s[b:];p.write_text(s)
p=root/'work/validate_street_crowd.py';s=p.read_text().replace("r['rigs']={}","assert r['crossings_completed']>0 and r['illegal_crossings']==0 and r['pedestrian_vehicle_overlap_frames']==0,r\n assert r['parked_cars']>0 and r['car_boardings']>0 and r['bus_boardings']>0 and r['bus_alightings']>0,r\n r['rigs']={}");p.write_text(s)
