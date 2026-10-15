namespace {
constexpr float TransitStations[]={-27000.f,-7000.f,17000.f,32000.f};
bool PedHidden(const FWalker& W){return W.Activity==EPedActivity::InsideCar||W.Activity==EPedActivity::InsideTransit;}
void PedMove(FWalker& W,FVector Target,float Dt,float Speed){FVector D=Target-W.Position;float Distance=D.Size2D();float Move=FMath::Min(Distance,Speed*Dt);W.Position+=D.GetSafeNormal2D()*Move;W.FrameMoved=Move;W.Travelled+=Move;if(Move>0)W.Heading=FMath::FixedTurn(W.Heading,D.Rotation().Yaw,180*Dt);}
int32 NearestRoad(const TArray<float>& Roads,float P){int32 Best=0;for(int32 I=1;I<Roads.Num();I++)if(FMath::Abs(Roads[I]-P)<FMath::Abs(Roads[Best]-P))Best=I;return Best;}
}
void ABogotaCity::BuildStreetInteractions(){
 for(auto& P:ParkedCars)if(P.Visual.IsValid())P.Visual->GetOwner()->Destroy();ParkedCars.Empty();PedestrianJunctions.Empty();PedestrianNextAdmission.Empty();PedestrianCrossings=IllegalCrossings=ParkedCarBoardings=TransitBoardings=TransitAlightings=0;
 // Open the boarding gaps in the existing station screens, including baked maps.
 if(Detail.IsValidIndex(7))for(float Station:TransitStations)for(float Side:{-1.f,1.f}){
  auto* Glass=Detail[7].Get();for(int32 I=Glass->GetInstanceCount()-1;I>=0;I--){FTransform T;Glass->GetInstanceTransform(I,T,false);if(FVector::Dist(T.GetLocation(),FVector(Station,Side*160,210))<1)Glass->RemoveInstance(I);}
  for(FVector2D Range:{FVector2D(-1375,-800),FVector2D(-500,500),FVector2D(800,1375)})Glass->AddInstance(FTransform(FRotator::ZeroRotator,FVector(Station+(Range.X+Range.Y)*.5f,Side*160,210),FVector((Range.Y-Range.X)/100,.18,2.5)));
 }
 for(int32 I=0;I<Walkers.Num();I++){
  auto& W=Walkers[I];int32 Block=I/PedestriansPerBlock,IX=Block%6,IY=Block/6,Lane=I%PedestriansPerBlock;
  if(!CrowdModels[W.ModelIndex].Cane&&(Lane==4||Lane==5)){
   // Cross at two different intersections, with a full block between them.
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
   W.Segment=0;W.Position=W.Route[0];
  }
 }
 // Park only on the quieter side streets, outside the moving traffic lanes.
 for(int32 I=0;I<Walkers.Num()&&ParkedCars.Num()<12;I++){
  auto& W=Walkers[I];if(CrowdModels[W.ModelIndex].Cane||!W.CrossSegments.IsEmpty())continue;
  int32 Road=NearestRoad(NorthRoads,W.Position.X);float Side=W.Position.X>NorthRoads[Road]?1:-1;
  if(Road<2||Road>4||FMath::Abs(FMath::Abs(W.Position.X-NorthRoads[Road])-1100)>100||FMath::Abs(W.Position.Y-EastRoads[NearestRoad(EastRoads,W.Position.Y)])<2400)continue;
  FVector Position(NorthRoads[Road]+Side*560,W.Position.Y,9);bool Clear=true;for(const auto& P:ParkedCars)if(FVector::Dist2D(P.Position,Position)<1000)Clear=false;if(!Clear)continue;
  const auto& Spec=TrafficCarModels[(ParkedCars.Num()*7+4)%20];FString Name=Spec.Name;auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Traffic/Detailed/SK_%s.SK_%s"),*Name,*Name));if(!Mesh)continue;
  auto* Actor=GetWorld()->SpawnActor<AActor>();auto* V=NewObject<UPoseableMeshComponent>(Actor);Actor->SetRootComponent(V);Actor->AddInstanceComponent(V);V->SetSkinnedAssetAndUpdate(Mesh);V->SetMaterial(0,TrafficMaterial);V->SetCollisionEnabled(ECollisionEnabled::NoCollision);V->SetCullDistance(18000);V->SetWorldScale3D(FVector(TrafficModelScale(Spec)));V->RegisterComponent();Actor->SetActorLocationAndRotation(Position,FRotator(0,90,0));V->RefreshBoneTransforms();
  auto* Box=NewObject<UBoxComponent>(Actor);Actor->AddInstanceComponent(Box);Box->SetupAttachment(V);Box->SetBoxExtent(FVector(Spec.HalfLength,Spec.HalfWidth,85));Box->SetRelativeLocation(FVector(0,0,85));Box->SetCollisionProfileName(TEXT("BlockAllDynamic"));Box->SetCanEverAffectNavigation(false);Box->RegisterComponent();
  FParkedTrafficCar P;P.Headlights=CreateTrafficHeadlights(Actor,V,Spec.HalfLength,Spec.HalfWidth,65);P.Position=Position;P.Door=Position+FVector(Side*(Spec.HalfWidth*TrafficModelScale(Spec)+85),0,17);P.Heading=90;P.Walker=I;P.Visual=V;W.ParkedCar=ParkedCars.Num();W.NextInteraction=30+ParkedCars.Num()*9;ParkedCars.Add(P);
 }
 // One passenger per station keeps the platforms quiet. They ride between stops.
 for(int32 S=0;S<4;S++){
  auto& W=Walkers[Walkers.Num()-4+S];W.TransitPassenger=true;W.Crossing=false;W.CrossSegments.Empty();W.StationIndex=S;W.Activity=EPedActivity::WaitingTransit;W.Position=FVector(TransitStations[S]+650,0,110);W.Heading=90;
  while(CrowdModels[W.ModelIndex].Cane)W.ModelIndex=(W.ModelIndex+1)%UE_ARRAY_COUNT(CrowdModels);W.Scale=CrowdModels[W.ModelIndex].Scale;W.Speed=CrowdModels[W.ModelIndex].Speed;
 }
}
bool ABogotaCity::UpdateWalkerInteraction(FWalker& W,float Dt){
 W.FrameMoved=0;
 if(W.Activity==EPedActivity::Walking){
  if(W.ParkedCar!=INDEX_NONE&&!W.Crossing&&Elapsed>=W.NextInteraction){auto& P=ParkedCars[W.ParkedCar];if(!P.Occupied&&FMath::Abs(W.Position.X-P.Door.X)<600&&FVector::Dist2D(W.Position,P.Door)<1500){W.ResumePosition=W.Position;W.Activity=EPedActivity::ApproachCar;}}
  if(W.Activity==EPedActivity::Walking)return false;
 }
 W.ActionTime+=Dt;
 if(W.Activity==EPedActivity::ApproachCar){auto& P=ParkedCars[W.ParkedCar];PedMove(W,P.Door,Dt,W.Speed);if(FVector::Dist2D(W.Position,P.Door)<8){P.Occupied=true;W.Activity=EPedActivity::EnteringCar;W.ActionTime=0;W.ActionStart=W.Position;W.ActionEnd=P.Position+FVector(0,0,17);W.Heading=(W.ActionEnd-W.ActionStart).Rotation().Yaw;}}
 else if(W.Activity==EPedActivity::EnteringCar){W.Position=FMath::Lerp(W.ActionStart,W.ActionEnd,FMath::Clamp(W.ActionTime/1.2f,0.f,1.f));if(W.ActionTime>=1.2f){W.Activity=EPedActivity::InsideCar;W.ActionTime=0;ParkedCarBoardings++;}}
 else if(W.Activity==EPedActivity::InsideCar){if(W.ActionTime>20+W.ModelIndex%15){W.Activity=EPedActivity::LeavingCar;W.ActionTime=0;W.ActionStart=W.Position;W.ActionEnd=ParkedCars[W.ParkedCar].Door;W.Heading=(W.ActionEnd-W.ActionStart).Rotation().Yaw;}}
 else if(W.Activity==EPedActivity::LeavingCar){W.Position=FMath::Lerp(W.ActionStart,W.ActionEnd,FMath::Clamp(W.ActionTime/1.2f,0.f,1.f));if(W.ActionTime>=1.2f){ParkedCars[W.ParkedCar].Occupied=false;W.Activity=EPedActivity::ReturningRoute;W.NextInteraction=Elapsed+180;}}
 else if(W.Activity==EPedActivity::ReturningRoute){PedMove(W,W.ResumePosition,Dt,W.Speed);if(FVector::Dist2D(W.Position,W.ResumePosition)<8){W.Position=W.ResumePosition;W.Activity=EPedActivity::Walking;}}
 else if(W.Activity==EPedActivity::WaitingTransit){
  if(Elapsed<W.NextInteraction)return true;
  for(int32 I=0;I<Vehicles.Num();I++){auto& Bus=Vehicles[I];if(!Bus.Articulated||(G66Active&&I==Vehicles.Num()-1)||Bus.Wait<=0||Bus.Velocity>1||FMath::Abs(Bus.Position.X-TransitStations[W.StationIndex])>80)continue;
   bool DoorBusy=false;for(const auto& Other:Walkers)if(Other.BusIndex==I&&(Other.Activity==EPedActivity::BoardingTransit||Other.Activity==EPedActivity::AlightingTransit||(Other.Activity==EPedActivity::InsideTransit&&Other.BoardedStation!=W.StationIndex)))DoorBusy=true;if(DoorBusy)continue;
   FVector Door=Bus.Position+FRotator(0,Bus.Heading,0).RotateVector(FVector(650,0,0));Door.Y=Bus.Position.Y-FMath::Sign(Bus.Position.Y)*145;Door.Z=110;
   if(FMath::Abs(Door.X-W.Position.X)>350)continue;W.BusIndex=I;W.BoardedStation=W.StationIndex;W.Activity=EPedActivity::BoardingTransit;W.ActionTime=0;W.ActionStart=W.Position;W.ActionEnd=Door;W.Heading=(Door-W.Position).Rotation().Yaw;Bus.Wait=FMath::Max(Bus.Wait,3.f);break;
  }
 }
 else if(W.Activity==EPedActivity::BoardingTransit){auto& Bus=Vehicles[W.BusIndex];Bus.Wait=FMath::Max(Bus.Wait,.2f);W.Position=FMath::Lerp(W.ActionStart,W.ActionEnd,FMath::Clamp(W.ActionTime/1.2f,0.f,1.f));if(W.ActionTime>=1.2f){W.Activity=EPedActivity::InsideTransit;W.ActionTime=0;TransitBoardings++;}}
 else if(W.Activity==EPedActivity::InsideTransit){auto& Bus=Vehicles[W.BusIndex];W.Position=Bus.Position;
  if(Bus.Wait>0&&Bus.Velocity<1)for(int32 S=0;S<4;S++)if(S!=W.BoardedStation&&FMath::Abs(Bus.Position.X-TransitStations[S])<80){W.StationIndex=S;W.Activity=EPedActivity::AlightingTransit;W.ActionTime=0;W.ActionStart=Bus.Position+FRotator(0,Bus.Heading,0).RotateVector(FVector(650,0,0));W.ActionStart.Y=Bus.Position.Y-FMath::Sign(Bus.Position.Y)*145;W.ActionStart.Z=110;W.ActionEnd=FVector(W.ActionStart.X,0,110);W.Position=W.ActionStart;W.Heading=(W.ActionEnd-W.ActionStart).Rotation().Yaw;Bus.Wait=FMath::Max(Bus.Wait,2.f);break;}
 }
 else if(W.Activity==EPedActivity::AlightingTransit){auto& Bus=Vehicles[W.BusIndex];Bus.Wait=FMath::Max(Bus.Wait,.2f);W.Position=FMath::Lerp(W.ActionStart,W.ActionEnd,FMath::Clamp(W.ActionTime/1.2f,0.f,1.f));if(W.ActionTime>=1.2f){W.Activity=EPedActivity::WaitingTransit;W.ActionTime=0;W.BusIndex=INDEX_NONE;W.NextInteraction=Elapsed+12;TransitAlightings++;}}
 return true;
}

