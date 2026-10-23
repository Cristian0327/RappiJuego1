from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
src=root/'outputs/BogotaVoxel/Source/BogotaVoxel'
backup=root/'work/Backups/CityVisuals_20261014'
backup.mkdir(parents=True,exist_ok=True)
for name in ['BogotaTraffic.cpp','BogotaPedestrianBehaviors.inl','BogotaGame.h','BogotaCity.cpp','BogotaPlayer.cpp']:
 if not (backup/name).exists():shutil.copy2(src/name,backup/name)
p=src/'BogotaGame.h';s=p.read_text()
s=s.replace('struct FParkedTrafficCar {','struct FParkedTrafficCar {TArray<TWeakObjectPtr<USpotLightComponent>> Headlights;')
p.write_text(s)
p=src/'BogotaTraffic.cpp';s=p.read_text()
start=s.index(' for(float Side:{-1.f,1.f}){auto* Light=')
end=s.index('\n',start)
s=s[:start]+'  A.Headlights=CreateTrafficHeadlights(Actor,Visual,A.HalfLength/A.ModelScale,A.HalfWidth/A.ModelScale,A.Bus?115.f:65.f);}\n'+s[end+1:]
idx=s.index('TArray<FVector> RoundedLoop')
s=s[:idx]+'''constexpr int32 PedestriansPerBlock=36;
// A shared scale keeps parked/driving cars, wheels, doors and collisions aligned.
float TrafficModelScale(const FTrafficModelSpec& Spec){return Spec.HalfLength<210?1.18f:1.12f;}
TArray<TWeakObjectPtr<USpotLightComponent>> CreateTrafficHeadlights(AActor* Actor,USceneComponent* Root,float HalfLength,float HalfWidth,float Height){
 TArray<TWeakObjectPtr<USpotLightComponent>> Lights;
 for(float Side:{-1.f,1.f}){
  auto* Light=NewObject<USpotLightComponent>(Actor);Actor->AddInstanceComponent(Light);Light->SetupAttachment(Root);Light->SetMobility(EComponentMobility::Movable);
  Light->SetIntensityUnits(ELightUnits::Lumens);Light->SetRelativeLocation(FVector(HalfLength-15,Side*HalfWidth*.65f,Height));Light->SetRelativeRotation(FRotator(-10,0,0));
  Light->SetIntensity(2800);Light->SetLightColor(FLinearColor(1,.92f,.8f));Light->SetAttenuationRadius(2400);Light->SetInnerConeAngle(16);Light->SetOuterConeAngle(32);Light->SetCastShadows(false);Light->SetVisibility(false);Light->RegisterComponent();Lights.Add(Light);
 }
 return Lights;
}
'''+s[idx:]
s=s.replace('A.ModelScale=1.f;','A.ModelScale=A.Bus?1.f:TrafficModelScale(ModelSpec);')
s=s.replace('Lane<6;Lane++','Lane<PedestriansPerBlock;Lane++')
s=s.replace('float Offset=Lane%2?36:-36;','float Offset=(Lane%2?48.f:-48.f)+((Lane/2)%3)*80.f;')
s=s.replace('(Block*6+Lane)%UE_ARRAY_COUNT','(Block*PedestriansPerBlock+Lane)%UE_ARRAY_COUNT')
s=s.replace('(Lane+.35f)/6;','(Lane+.35f)/PedestriansPerBlock;')
s=s.replace('Rank<24','Rank<(DetailLevel==0?48:120)')
# Spatial lookup avoids checking every walker against every other walker.
needle=' for(int32 I=0;I<Walkers.Num();I++){\n  auto& W=Walkers[I];float Move=0;'
replacement=''' TMap<FIntPoint,TArray<int32>> PedGrid;
 auto Cell=[](FVector P){return FIntPoint(FMath::FloorToInt(P.X/250),FMath::FloorToInt(P.Y/250));};
 for(int32 I=0;I<Walkers.Num();I++)if(!PedHidden(Walkers[I]))PedGrid.FindOrAdd(Cell(Walkers[I].Position)).Add(I);
 for(int32 I=0;I<Walkers.Num();I++){
  auto& W=Walkers[I];float Move=0;'''
assert needle in s;s=s.replace(needle,replacement)
old='   for(int32 J=0;J<Walkers.Num();J++)if(J!=I&&!PedHidden(Walkers[J])){FVector D=Walkers[J].Position-W.Position;float Ahead=FVector::DotProduct(D,Dir);if(Ahead>0&&Ahead<110&&FMath::Abs(FVector::CrossProduct(D,Dir).Z)<32)Move=FMath::Min(Move,FMath::Max(0.f,Ahead-80));}'
new='''   // Opposing pedestrians pass on their right instead of stopping each other forever.
   const FIntPoint GridCell=Cell(W.Position);FVector Avoid=FVector::ZeroVector;float Limit=Move;
   for(int32 X=-1;X<=1;X++)for(int32 Y=-1;Y<=1;Y++)if(const auto* Nearby=PedGrid.Find(GridCell+FIntPoint(X,Y)))for(int32 J:*Nearby)if(J!=I){
    const auto& Other=Walkers[J];FVector D=Other.Position-W.Position;float Ahead=FVector::DotProduct(D,Dir),Side=FMath::Abs(FVector::CrossProduct(D,Dir).Z);
    if(Ahead>0&&Ahead<155&&Side<55){
     FVector OtherDir=FRotator(0,Other.Heading,0).Vector();
     const bool Following=FVector::DotProduct(Dir,OtherDir)>.7f&&Other.Activity==EPedActivity::Walking;
     if(Following)Limit=FMath::Min(Limit,FMath::Max(0.f,Ahead-75));
     else if(!W.Crossing)Avoid+=FVector(Dir.Y,-Dir.X,0)*(1-Side/65.f);
    }
   }
   if(!Avoid.IsNearlyZero()&&Move>0){Dir=(Dir+Avoid.GetClampedToMaxSize(1.2f)).GetSafeNormal2D();W.Heading=FMath::FixedTurn(W.Heading,Dir.Rotation().Yaw,Dt*180);}
   Move=FMath::Min(Move,Limit);'''
assert old in s;s=s.replace(old,new)
# Do not create/trace distant meshes that are not visible.
s=s.replace('if(W.Activity==EPedActivity::Walking||W.Activity==EPedActivity::ApproachCar||W.Activity==EPedActivity::ReturningRoute){FHitResult','if(Nearest.Contains(I)&&(W.Activity==EPedActivity::Walking||W.Activity==EPedActivity::ApproachCar||W.Activity==EPedActivity::ReturningRoute)){FHitResult')
# Allow a small group to cross together in a green pedestrian phase, but leave a
# full vehicle phase between groups. Admission remains gated by the vehicle check.
# Keep original signal admissions for now; regression will measure exit stalls.
needle=' for(int32 I=0;I<Vehicles.Num();I++){bool On=Night&&Nearby.Find(I)!=INDEX_NONE&&Nearby.Find(I)<6;for(auto& L:Vehicles[I].Headlights)if(L.IsValid())L->SetVisibility(On);}'
replacement=needle+'''
 TArray<int32> ParkedNearby;for(int32 I=0;I<ParkedCars.Num();I++)if(FVector::DistSquared2D(P,ParkedCars[I].Position)<FMath::Square(6000.f))ParkedNearby.Add(I);
 ParkedNearby.Sort([&](int32 A,int32 B){return FVector::DistSquared2D(P,ParkedCars[A].Position)<FVector::DistSquared2D(P,ParkedCars[B].Position);});
 for(int32 I=0;I<ParkedCars.Num();I++){bool On=Night&&ParkedNearby.Find(I)!=INDEX_NONE&&ParkedNearby.Find(I)<6;for(auto& L:ParkedCars[I].Headlights)if(L.IsValid())L->SetVisibility(On);}
'''
assert needle in s;s=s.replace(needle,replacement)
p.write_text(s)
p=src/'BogotaPedestrianBehaviors.inl';s=p.read_text()
s=s.replace('Block=I/6,IX=Block%6,IY=Block/6,Lane=I%6','Block=I/PedestriansPerBlock,IX=Block%6,IY=Block/6,Lane=I%PedestriansPerBlock')
s=s.replace('&&Lane>=4','&&(Lane==4||Lane==5)')
s=s.replace('V->SetCullDistance(18000);V->RegisterComponent();','V->SetCullDistance(18000);V->SetWorldScale3D(FVector(TrafficModelScale(Spec)));V->RegisterComponent();')
s=s.replace('FParkedTrafficCar P;P.Position','FParkedTrafficCar P;P.Headlights=CreateTrafficHeadlights(Actor,V,Spec.HalfLength,Spec.HalfWidth,65);P.Position')
s=s.replace('Side*(Spec.HalfWidth+85)','Side*(Spec.HalfWidth*TrafficModelScale(Spec)+85)')
p.write_text(s)
p=src/'BogotaPlayer.cpp';s=p.read_text().replace('City->Walkers.Num()==144','City->Walkers.Num()==864');p.write_text(s)
p=root/'work/validate_street_crowd.py';s=p.read_text().replace("r['pedestrians']==144","r['pedestrians']==864");p.write_text(s)
