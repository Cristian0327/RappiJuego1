from pathlib import Path
p=Path(__file__).resolve().parents[1]/'outputs/BogotaVoxel/Source/BogotaVoxel/BogotaTraffic.cpp';s=p.read_text()
s=s.replace('FMath::Abs(A.Position.X-X)<1400+A.HalfLength+100&&FMath::Abs(A.Position.Y-Y)<1400+A.HalfLength+100','FMath::Abs(A.Position.X-X)<1550+A.HalfLength+100&&FMath::Abs(A.Position.Y-Y)<(Y==0?1925:1550)+A.HalfLength+100')
s=s.replace('FMath::Abs(A.Position.X-NorthRoads[X])>1400+A.HalfLength||FMath::Abs(A.Position.Y-EastRoads[Y])>1400+A.HalfLength','FMath::Abs(A.Position.X-NorthRoads[X])>1550+A.HalfLength||FMath::Abs(A.Position.Y-EastRoads[Y])>(EastRoads[Y]==0?1925:1550)+A.HalfLength')
s=s.replace('float StopDistance=Ahead-1400-A.HalfLength;','const float StopBand=NS?1550.f:EastRoads[Y]==0?1925.f:1550.f;float StopDistance=Ahead-StopBand-A.HalfLength;')
s=s.replace('Forward<1400+2*A.HalfLength+300','Forward<StopBand+2*A.HalfLength+300')
needle='bool Ready=Red&&!TrafficReservations.Contains(W.CrossJunction)&&Elapsed>=PedestrianNextAdmission.FindRef(W.CrossJunction);'
s=s.replace(needle,needle+'''
    if(Ready){FVector Center=(W.Position+Target)*.5f,Across=(Target-W.Position).GetSafeNormal2D(),Side(-Across.Y,Across.X,0);float Half=FVector::Dist2D(W.Position,Target)*.5f;
     for(const auto& Car:Vehicles){FVector Forward=FRotator(0,Car.Heading,0).Vector(),Right(-Forward.Y,Forward.X,0),Delta=Car.Position-Center;bool Intersects=true;
      for(FVector Axis:{Forward,Right,Across,Side}){float Extent=Car.HalfLength*FMath::Abs(FVector::DotProduct(Forward,Axis))+Car.HalfWidth*FMath::Abs(FVector::DotProduct(Right,Axis))+Half*FMath::Abs(FVector::DotProduct(Across,Axis))+45*FMath::Abs(FVector::DotProduct(Side,Axis));if(FMath::Abs(FVector::DotProduct(Delta,Axis))>Extent){Intersects=false;break;}}
      if(Intersects){Ready=false;break;}
     }
    }
''');p.write_text(s)
