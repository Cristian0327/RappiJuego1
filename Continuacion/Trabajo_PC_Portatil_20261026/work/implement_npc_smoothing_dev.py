from pathlib import Path
r=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1')
p=r/'Source/BogotaVoxel/BogotaGame.h';s=p.read_text().replace(' bool Bus=false;',' bool PlayerControlled=false,DevParked=false;\n bool Bus=false;')
s=s.replace(' FVector Position=FVector::ZeroVector,Velocity=FVector::ZeroVector;',' FVector Position=FVector::ZeroVector,Velocity=FVector::ZeroVector,PreviousPosition=FVector::ZeroVector;\n float PreviousHeading=0;bool YieldingToPlayer=false;')
s=s.replace(' ABogotaCity();',' friend class ABogotaPlayer;\n ABogotaCity();')
s=s.replace(' UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="World|Weather") float RainIntensity=0;',' UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="World|Weather") float RainIntensity=0;\n UPROPERTY(Transient,BlueprintReadWrite,Category="World|Weather") int32 DeveloperRainOverride=-1;')
s=s.replace(' void SimulateWalkers(float Dt);',' void SimulateWalkers(float Dt);\n void UpdateWalkerVisuals(float Alpha);\n bool WalkerStreetStepClear(const FWalker& Walker,FVector From,FVector To) const;\n float StreetClearance(FVector At) const;\n void SimulateDeveloperCar(int32 Index,float Dt);\n FString ValidatePedestrianPresentation();')
s=s.replace(' UFUNCTION(BlueprintCallable,Category="Delivery|Vehicle") void Interact();',''' UFUNCTION(BlueprintCallable,Category="Delivery|Vehicle") void Interact();
 UFUNCTION(Exec) void BogDev(bool Enabled=true);
 UFUNCTION(Exec) void BogRain(int32 Mode=1);
 UFUNCTION(Exec) void BogCar(int32 Index=-1);
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Developer") int32 DeveloperCarIndex=-1;
 bool EnterDeveloperCar(int32 Index=-1);
 bool LeaveDeveloperCar();
 FVector2D DeveloperDriveInput() const;
 FString ValidateDeveloperTools();
 void UpdateDeveloperCarView(float Dt);
 float DeveloperCameraLength=430,DeveloperLastHeading=0;
 FVector DeveloperCameraOffset=FVector::ZeroVector;''');p.write_text(s)
p=r/'Source/BogotaVoxel/BogotaTraffic.cpp';s=p.read_text();s=s.replace('  auto& W=Walkers[I];\n  if(!W.TransitPassenger','  auto& W=Walkers[I];W.PreviousPosition=W.Position;W.PreviousHeading=W.Heading;\n  if(!W.TransitPassenger',1)
s=s.replace('if(WalkerStepClear(Candidate,Candidate)){W.Position=Candidate;Found=true;break;}','if(WalkerStepClear(Candidate,Candidate)&&StreetClearance(Candidate)>=40){W.Position=Candidate;Found=true;break;}')
s=s.replace('  const FVector PreviousPosition=W.Position;float Move=0;','  if(FVector::DistSquared(W.PreviousPosition,W.Position)>FMath::Square(250.f))W.PreviousPosition=W.Position;\n  const FVector PreviousPosition=W.Position;float Move=0;')
s=s.replace('   const float Corridor=W.Crossing?150.f:230.f;','''   const float Corridor=W.Crossing?150.f:230.f;
   bool Yield=false,Retreat=false;
   if(!W.Crossing&&(Player||PedestrianTestObstacle.IsSet())&&FMath::Abs(PP.Z-W.Position.Z)<300){
    FVector D=PP-W.Position,Right(-Dir.Y,Dir.X,0);float Ahead=FVector::DotProduct(D,Dir);
    bool Left=WalkerStreetStepClear(W,W.Position,W.Position+Right*170)&&FVector::Dist2D(PP,W.Position+Right*170)>=145;
    bool RightFree=WalkerStreetStepClear(W,W.Position,W.Position-Right*170)&&FVector::Dist2D(PP,W.Position-Right*170)>=145;
    if(W.YieldingToPlayer&&((D.Size2D()>350)||Left||RightFree))W.YieldingToPlayer=false;
    if(Ahead> -35&&Ahead<240&&FMath::Abs(FVector::CrossProduct(D,Dir).Z)<145&&!Left&&!RightFree)W.YieldingToPlayer=true;
    Yield=W.YieldingToPlayer;
    Retreat=Yield&&D.Size2D()<140&&WalkerStreetStepClear(W,W.Position,W.Position-Dir*W.Speed*Dt);
   }else W.YieldingToPlayer=false;
''')
s=s.replace('!WalkerStepClear(W.Position,W.Position+Candidate*FMath::Max(Move,W.Speed*.8f))','!WalkerStreetStepClear(W,W.Position,W.Position+Candidate*FMath::Max(Move,W.Speed*.8f))')
s=s.replace('   if(BestScore< -50)Move=0;\n   Dir=BestDir;','   if(BestScore< -50||Yield)Move=0;\n   if(Retreat){BestDir=-Dir;Move=W.Speed*Dt;}\n   Dir=BestDir;')
s=s.replace('!WalkerStepClear(W.Position,W.Position+Dir*Move)','!WalkerStreetStepClear(W,W.Position,W.Position+Dir*Move)')
s=s.replace('S->bEnableUpdateRateOptimizations=true;','S->bEnableUpdateRateOptimizations=false;')
s=s.replace('W.Visual=A;','W.Visual=A;W.PreviousPosition=W.Position;W.PreviousHeading=W.Heading;')
s=s.replace('return WalkerStepClear(From,To);};','return WalkerStreetStepClear(A,From,To)&&WalkerStreetStepClear(B,From,To);};')
s=s.replace('W.Activity==EPedActivity::Walking&&!SignalWait&&W.Travelled','W.Activity==EPedActivity::Walking&&!SignalWait&&!W.YieldingToPlayer&&W.Travelled')
# Controlled cars no longer follow an old route slot or hold an intersection reservation.
s=s.replace('  auto& A=Vehicles[Index];A.PreviousPosition=', '  auto& A=Vehicles[Index];if(A.PlayerControlled||A.DevParked){SimulateDeveloperCar(Index,Dt);continue;}A.PreviousPosition=')
s=s.replace('if(B.LaneGroup!=A.LaneGroup)continue;','if(B.LaneGroup!=A.LaneGroup||B.PlayerControlled||B.DevParked)continue;')
s=s.replace('J!=Index&&Vehicles[J].LaneGroup!=A.LaneGroup','J!=Index&&(Vehicles[J].LaneGroup!=A.LaneGroup||Vehicles[J].PlayerControlled||Vehicles[J].DevParked)')
s+='''
float ABogotaCity::StreetClearance(FVector At)const{
 float Clearance=1e9;for(float X:NorthRoads)Clearance=FMath::Min(Clearance,float(FMath::Abs(At.X-X)-750));for(float Y:EastRoads)Clearance=FMath::Min(Clearance,float(FMath::Abs(At.Y-Y)-(Y==0?1150:750)));return Clearance;
}
bool ABogotaCity::WalkerStreetStepClear(const FWalker& W,FVector From,FVector To)const{
 if(!WalkerStepClear(From,To))return false;
 if(W.Crossing||W.TransitPassenger||W.Activity!=EPedActivity::Walking)return true;
 const float Before=StreetClearance(From),After=StreetClearance(To);return After>=40||(Before<40&&After>Before+.01f);
}
void ABogotaCity::UpdateWalkerVisuals(float Alpha){
 for(auto& W:Walkers)if(W.Visual.IsValid()&&!W.Visual->IsHidden()){
  FVector P=FMath::Lerp(W.PreviousPosition,W.Position,Alpha);float H=W.PreviousHeading+FMath::FindDeltaAngleDegrees(W.PreviousHeading,W.Heading)*Alpha;
  W.Visual->SetActorLocationAndRotation(P,FRotator(0,H-90,0));
 }
}
''';p.write_text(s)
p=r/'Source/BogotaVoxel/BogotaCity.cpp';s=p.read_text().replace('while(PedAccumulator>=PedStep&&PedSteps++<4){SimulateWalkers(PedStep);PedAccumulator-=PedStep;}','while(PedAccumulator>=PedStep&&PedSteps++<4){SimulateWalkers(PedStep);PedAccumulator-=PedStep;}\n UpdateWalkerVisuals(FMath::Clamp(PedAccumulator/PedStep,0.f,1.f));');p.write_text(s)
p=r/'Source/BogotaVoxel/BogotaWeather.cpp';s=p.read_text().replace(' if(FParse::Param(FCommandLine::Get(),TEXT("ForceRain")))Target=1;',' if(DeveloperRainOverride>=0)Target=DeveloperRainOverride==1?1.f:0.f;\n if(FParse::Param(FCommandLine::Get(),TEXT("ForceRain")))Target=1;');p.write_text(s)
p=r/'Source/BogotaVoxel/DeliveryStores.cpp';s=p.read_text().replace('bEnableUpdateRateOptimizations=true','bEnableUpdateRateOptimizations=false');p.write_text(s)
p=r/'Source/BogotaVoxel/BogotaPlayer.cpp';s=p.read_text().replace('  if(Delivery&&Delivery->PhoneOpen)return;','  if(Delivery&&Delivery->PhoneOpen)return;\n  if(DeveloperCarIndex!=INDEX_NONE){LeaveDeveloperCar();return;}\n  if(Delivery&&Delivery->DeveloperMode&&EnterDeveloperCar())return;',1)
s=s.replace('  if(!Riding&&BikeSpeed<0){','  if(DeveloperCarIndex!=INDEX_NONE){UpdateDeveloperCarView(Dt);return;}\n  if(!Riding&&BikeSpeed<0){',1);p.write_text(s)
p=r/'Source/BogotaVoxel/DeliverySystem.cpp';s=p.read_text().replace('void UDeliveryComponent::ToggleDeveloperMode(){','void UDeliveryComponent::ToggleDeveloperMode(){\n if(DeveloperMode)if(auto* Rider=Cast<ABogotaPlayer>(GetOwner()))if(Rider->DeveloperCarIndex!=INDEX_NONE&&!Rider->LeaveDeveloperCar())return;');p.write_text(s)
p=r/'Config/DefaultInput.ini';s=p.read_text();
if '+ConsoleKeys=F10' not in s:s+='\n+ConsoleKeys=F10\n'
p.write_text(s)
