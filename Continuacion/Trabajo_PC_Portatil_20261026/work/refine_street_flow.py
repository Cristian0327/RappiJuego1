from pathlib import Path
r=Path('outputs/BogotaVoxel/Source/BogotaVoxel');p=r/'BogotaGame.h';s=p.read_text().replace('FVector Position=FVector::ZeroVector;\n int32 Segment=0,ModelIndex=0;','FVector Position=FVector::ZeroVector,Velocity=FVector::ZeroVector;\n int32 Segment=0,ModelIndex=0;');p.write_text(s)
p=r/'BogotaTraffic.cpp';s=p.read_text();needle='   if(!InsideJunction)break;SpawnDistance='
s=s.replace(needle,'''   for(const auto& B:Vehicles){FVector D=B.Position-A.Position,Forward=FRotator(0,A.Heading,0).Vector();if(FMath::Abs(FVector::DotProduct(D,Forward))<A.HalfLength+B.HalfLength+300&&FMath::Abs(FVector::CrossProduct(D,Forward).Z)<A.HalfWidth+B.HalfWidth+80)InsideJunction=true;}
   if(!InsideJunction)break;SpawnDistance=''',1)
s=s.replace('auto& W=Walkers[I];float Move=0;','auto& W=Walkers[I];const FVector PreviousPosition=W.Position;float Move=0;')
s=s.replace('if(FVector::DotProduct(D,Relative)>0)Safe=false;else Score-=.5f;','if(FVector::DotProduct(D,Relative)>1.e-3f)Safe=false;else Score-=.5f;')
s=s.replace('else if(Closest<Radius&&Time>0)Safe=false;','''else if(Closest<Radius&&Time>0){Score-=10.f*(Radius-Closest)/Radius;
      float StepTime=FMath::Clamp(FVector::DotProduct(D,Relative)/FMath::Max(1.f,Relative.SizeSquared2D()),0.f,Dt);
      if((D-Relative*StepTime).Size2D()<Radius)Safe=false;
     }''')
s=s.replace('FVector OV=O.Activity==EPedActivity::Walking?FRotator(0,O.Heading,0).Vector()*O.Speed:FVector::ZeroVector;Obstacle','FVector OV=O.Velocity;Obstacle')
s=s.replace('  }else Move=W.FrameMoved;\n  if(Nearest.Contains','  }else Move=W.FrameMoved;\n  W.Velocity=(W.Position-PreviousPosition)/FMath::Max(.001f,Dt);\n  if(Nearest.Contains')
p.write_text(s)
