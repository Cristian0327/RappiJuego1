from pathlib import Path
r=Path('outputs/BogotaVoxel/Source/BogotaVoxel')
p=r/'BogotaGame.h';s=p.read_text();s=s.replace('TArray<uint8> CrossSegments;','TArray<uint8> CrossSegments;\n TArray<int32> CrossJunctions;');s=s.replace('FString ValidateCrowd(float Seconds=180);','FString ValidateCrowd(float Seconds=180);\n UFUNCTION(CallInEditor,BlueprintCallable,Category="Crowd") FString ValidateStreetFlow();');p.write_text(s)
p=r/'BogotaPedestrianBehaviors.inl';s=p.read_text();a=s.index('   if(Lane==4){');z=s.index('   W.Segment=0;',a)
s=s[:a]+'''   // Cross at two different intersections, with a full block between them.
   // Each crossing owns its own signal key rather than immediately returning.
   if(Lane==4){int32 Left=FMath::Min(IX,4),Road=Left+1;float X=NorthRoads[Road],Y0=EastRoads[IY]+(IY==2?1530:1130),Y1=EastRoads[IY+1]-(IY==1?1530:1130);
    float L=NorthRoads[Left]+1130,R=NorthRoads[Road+1]-1130;
    W.Route={FVector(X-1100,Y0,27),FVector(X-900,Y0,27),FVector(X+900,Y0,27),FVector(X+1100,Y0,27),FVector(R,Y0,27),FVector(R,Y1,27),FVector(X+1100,Y1,27),FVector(X+900,Y1,27),FVector(X-900,Y1,27),FVector(X-1100,Y1,27),FVector(L,Y1,27),FVector(L,Y0,27)};
    W.CrossSegments.Init(0,12);W.CrossSegments[1]=W.CrossSegments[7]=2;W.CrossJunctions.Init(INDEX_NONE,12);W.CrossJunctions[1]=Road*100+IY;W.CrossJunctions[7]=Road*100+IY+1;
   }else {int32 Below=FMath::Min(IY,2),Road=Below+1;float Y=EastRoads[Road],Curb=Road==2?1530:1130,X0=NorthRoads[IX]+1130,X1=NorthRoads[IX+1]-1130;
    float B=EastRoads[Below]+(Below==2?1530:1130),T=EastRoads[Road+1]-(Road==1?1530:1130);
    W.Route={FVector(X0,Y-Curb,27),FVector(X0,Y-Curb+180,27),FVector(X0,Y+Curb-180,27),FVector(X0,Y+Curb,27),FVector(X0,T,27),FVector(X1,T,27),FVector(X1,Y+Curb,27),FVector(X1,Y+Curb-180,27),FVector(X1,Y-Curb+180,27),FVector(X1,Y-Curb,27),FVector(X1,B,27),FVector(X0,B,27)};
    W.CrossSegments.Init(0,12);W.CrossSegments[1]=W.CrossSegments[7]=1;W.CrossJunctions.Init(INDEX_NONE,12);W.CrossJunctions[1]=IX*100+Road;W.CrossJunctions[7]=(IX+1)*100+Road;
   }
   W.CrossJunction=W.CrossJunctions[1];
'''+s[z:];s=s.replace('for(int32 I=34;I<Vehicles.Num();I++){auto& Bus=Vehicles[I];if((G66Active&&I==37)||','for(int32 I=0;I<Vehicles.Num();I++){auto& Bus=Vehicles[I];if(!Bus.Articulated||(G66Active&&I==Vehicles.Num()-1)||');p.write_text(s)
p=r/'BogotaTraffic.cpp';s=p.read_text();s=s.replace('for(int32 I=0;I<38;I++){','constexpr int32 PrivateCount=96,BusCount=4;\n for(int32 I=0;I<PrivateCount+BusCount;I++){');s=s.replace('TrafficCarModels[I<30?I%20:20+I%2]','TrafficCarModels[I%12<10?I%20:20+I%2]');s=s.replace('A.Articulated=I>=34','A.Articulated=I>=PrivateCount').replace('A.LaneGroup=A.Articulated?2:I%2','A.LaneGroup=A.Articulated?6:I%6');a=s.index('  else if(A.LaneGroup==0)A.Route=');z=s.index('  const float LoopLength=',a)
s=s[:a]+'''  else {const int32 Circuit=A.LaneGroup/2;const bool Reverse=A.LaneGroup%2;
   const float X0[]={-36000,-24000,-12000},X1[]={36000,24000,12000},Y0[]={-22000,-11000,-22000},Y1[]={22000,11000,22000};
   const float Lane=Reverse?420.f:-420.f;
   A.Route=RoundedLoop(X0[Circuit]+Lane,X1[Circuit]-Lane,Y0[Circuit]+Lane,Y1[Circuit]-Lane,420,Reverse);
  }
  int32 Ordinal=A.Articulated?I-PrivateCount:I/6,Count=A.Articulated?BusCount:PrivateCount/6;
'''+s[z:]
s=s.replace('if(Along<A.HalfLength+B.HalfLength+300)InsideJunction=true;','if(Along<A.HalfLength+B.HalfLength+300)InsideJunction=true;')
# Include cars from another circuit when they share the physical lane.
needle='  for(int32 X=0;X<NorthRoads.Num();X++)for(int32 Y=0;Y<EastRoads.Num();Y++){'
pos=s.index(needle,s.index('void ABogotaCity::SimulateTraffic'))
s=s[:pos]+'''  for(int32 J=0;J<Vehicles.Num();J++)if(J!=Index&&Vehicles[J].LaneGroup!=A.LaneGroup){const auto& B=Vehicles[J];FVector D=Old[J]-A.Position;float Ahead=FVector::DotProduct(D,Dir),Side=FMath::Abs(FVector::CrossProduct(D,Dir).Z);
   if(Ahead>0&&Ahead<5000&&Side<A.HalfWidth+B.HalfWidth+40&&FVector::DotProduct(Dir,FRotator(0,B.Heading,0).Vector())>.9f){float Gap=FMath::Max(0.f,Ahead-A.HalfLength-B.HalfLength-190);Limit=FMath::Min(Limit,Gap);Desired=FMath::Min(Desired,Gap/1.25f);}
  }
'''+s[pos:]
s=s.replace('W.Heading=FMath::FixedTurn(W.Heading,Facing,Dt*180);Move=FMath::Abs(FMath::FindDeltaAngleDegrees(W.Heading,Facing))<8?W.Speed*Dt:0;','Move=W.Speed*Dt;')
s=s.replace('float Phase=FMath::Fmod(Elapsed,32.f);bool Red=', 'if(W.CrossJunctions.IsValidIndex(W.Segment))W.CrossJunction=W.CrossJunctions[W.Segment];\n    float Phase=FMath::Fmod(Elapsed,32.f);bool Red=')
a=s.index('   if(Player&&!W.Crossing');z=s.index('  }else Move=W.FrameMoved;',a)
s=s[:a]+'''   // Choose a collision-free local velocity. Slow walkers remain slow, while
   // followers may pass immediately instead of waiting for a zero-speed timer.
   const FIntPoint GridCell=Cell(W.Position);TArray<int32> NearbyAgents;
   for(int32 X=-2;X<=2;X++)for(int32 Y=-2;Y<=2;Y++)if(const auto* Nearby=PedGrid.Find(GridCell+FIntPoint(X,Y)))NearbyAgents.Append(*Nearby);
   FVector BestDir=Dir;float BestScore=-1e9;const FVector RouteStart=W.Route[W.Segment],RouteDir=(Target-RouteStart).GetSafeNormal2D();
   const float Corridor=W.Crossing?150.f:230.f;
   for(float Angle:{0.f,-25.f,25.f,-45.f,45.f,-70.f,70.f,-90.f,90.f,-115.f,115.f,-150.f,150.f,180.f}){
    FVector Candidate=Dir.RotateAngleAxis(Angle,FVector::UpVector),Velocity=Candidate*W.Speed;
    float Score=FVector::DotProduct(Candidate,Dir)*3.f+(Angle<0?.04f:0.f);bool Safe=true;
    auto Obstacle=[&](FVector At,FVector OtherVelocity,float Radius){FVector D=At-W.Position,Relative=Velocity-OtherVelocity;float Time=FMath::Clamp(FVector::DotProduct(D,Relative)/FMath::Max(1.f,Relative.SizeSquared2D()),0.f,1.8f);
     float Now=D.Size2D(),Closest=(D-Relative*Time).Size2D();
     if(Now<Radius){if(FVector::DotProduct(D,Relative)>0)Safe=false;else Score-=.5f;}
     else if(Closest<Radius&&Time>0)Safe=false;
    };
    if(Player&&FMath::Abs(PP.Z-W.Position.Z)<300&&FVector::DistSquared2D(PP,W.Position)<FMath::Square(500.f))Obstacle(PP,FVector::ZeroVector,135);
    for(int32 J:NearbyAgents)if(J!=I){const auto& O=Walkers[J];if(FMath::Abs(O.Position.Z-W.Position.Z)>150)continue;
     FVector OV=O.Activity==EPedActivity::Walking?FRotator(0,O.Heading,0).Vector()*O.Speed:FVector::ZeroVector;Obstacle(O.Position,OV,76);
    }
    FVector Next=W.Position+Candidate*W.Speed*.8f;float CurrentSide=FMath::Abs(FVector::CrossProduct(W.Position-RouteStart,RouteDir).Z),NextSide=FMath::Abs(FVector::CrossProduct(Next-RouteStart,RouteDir).Z);
    if(NextSide>Corridor&&NextSide>CurrentSide)Safe=false;
    if(!Safe)Score-=100;
    if(Score>BestScore){BestScore=Score;BestDir=Candidate;}
   }
   if(BestScore< -50)Move=0;
   Dir=BestDir;if(Move>0)W.Heading=FMath::FixedTurn(W.Heading,Dir.Rotation().Yaw,Dt*300);
   bool WaitingSignal=W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing;
   W.BlockedTime=Move<.01f&&!WaitingSignal?W.BlockedTime+Dt:0;
   float Distance=FVector::Dist2D(Target,W.Position);Move=FMath::Min(Move,Distance);W.Position+=Dir*Move;W.Travelled+=Move;
   // Advance only after actually reaching the endpoint, never after a sideways step.
   if(FVector::Dist2D(Target,W.Position)<18){W.Position=Target;if(W.Crossing){W.Crossing=false;PedestrianCrossings++;PedestrianNextAdmission.Add(W.CrossJunction,Elapsed+2);}W.Segment=(W.Segment+1)%W.Route.Num();}
'''+s[z:]
p.write_text(s)
print('Updated pedestrian steering, crossings and 100-vehicle distribution')
