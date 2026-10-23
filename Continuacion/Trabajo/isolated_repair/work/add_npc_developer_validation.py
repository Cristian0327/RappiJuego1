from pathlib import Path
r=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1')
p=r/'Source/BogotaVoxel/BogotaTraffic.cpp';s=p.read_text();s+=r'''
FString ABogotaCity::ValidatePedestrianPresentation(){
 auto Saved=Walkers;auto SavedJunctions=PedestrianJunctions;auto SavedAdmission=PedestrianNextAdmission;auto SavedObstacle=PedestrianTestObstacle;float SavedElapsed=Elapsed;
 auto R=MakeShared<FJsonObject>();int32 URO=0;for(const auto& W:Walkers)if(W.Visual.IsValid())if(auto* S=Cast<USkeletalMeshComponent>(W.Visual->GetRootComponent()))if(S->bEnableUpdateRateOptimizations)URO++;
 R->SetNumberField(TEXT("visible_npcs_with_animation_throttling"),URO);
 Walkers.Empty();PedestrianJunctions.Empty();PedestrianNextAdmission.Empty();
 const FVector Start(-8000,-45000,26);FWalker P;P.Route={Start,Start+FVector(6000,0,0),Start+FVector(6000,1500,0),Start+FVector(0,1500,0)};P.Position=P.PreviousPosition=Start;P.Speed=112;
 auto* Probe=GetWorld()->SpawnActor<AStaticMeshActor>();Probe->SetMobility(EComponentMobility::Movable);Probe->GetStaticMeshComponent()->SetStaticMesh(Cube);Probe->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);Probe->SetActorLocation(Start);P.Visual=Probe;Walkers.Add(P);PedestrianTestObstacle=Start+FVector(0,2000,0);
 float Acc=0,MaxJump=0;int32 Moving=0;FVector Last=Start;
 for(int32 Frame=0;Frame<120;Frame++){Acc+=1.f/60;while(Acc>=1.f/15){Elapsed+=1.f/15;SimulateWalkers(1.f/15);Acc-=1.f/15;}UpdateWalkerVisuals(Acc*15);FVector At=Probe->GetActorLocation();float D=FVector::Dist2D(At,Last);if(D>.1f)Moving++;MaxJump=FMath::Max(MaxJump,D);Last=At;}
 float Before=Walkers[0].Travelled+Acc*P.Speed;Acc+=.2f;while(Acc>=1.f/15){SimulateWalkers(1.f/15);Acc-=1.f/15;}float Loss=FMath::Abs(Walkers[0].Travelled+Acc*P.Speed-Before-.2f*P.Speed);
 R->SetNumberField(TEXT("moving_render_frames"),Moving);R->SetNumberField(TEXT("render_frames"),120);R->SetNumberField(TEXT("maximum_render_step_cm"),MaxJump);R->SetNumberField(TEXT("hitch_time_loss_cm"),Loss);Probe->Destroy();Walkers.Empty();
 int32 Yielded=0,Resumed=0,RoadIntrusions=0;float MinPlayerDistance=1e9,MaxWaitingTurn=0;
 for(float Side:{-1.f,1.f}){
  auto* Wall=GetWorld()->SpawnActor<AStaticMeshActor>();Wall->SetMobility(EComponentMobility::Movable);Wall->GetStaticMeshComponent()->SetStaticMesh(Cube);Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Wall->SetActorLocation(FVector(Side*1160,-4000,150));Wall->SetActorScale3D(FVector(1,20,3));
  PedestrianTestObstacle=FVector(Side*950,-4100,116);Walkers.Empty();
  for(int32 I=0;I<6;I++){FWalker W;W.Route={FVector(Side*950,-6000,26),FVector(Side*950,-2000,26),FVector(Side*1020,-2000,26),FVector(Side*1020,-6000,26)};W.Position=W.PreviousPosition=FVector(Side*950,-4300-I*125,26);W.Heading=90;W.Speed=112;W.ModelIndex=0;Walkers.Add(W);}
  bool DidYield=false;
  for(int32 Step=0;Step<225;Step++){Elapsed+=1.f/15;float Previous=Walkers[0].Heading;SimulateWalkers(1.f/15);DidYield|=Walkers[0].YieldingToPlayer;
   for(const auto& W:Walkers){if(StreetClearance(W.Position)<39)RoadIntrusions++;MinPlayerDistance=FMath::Min(MinPlayerDistance,FVector::Dist2D(W.Position,PedestrianTestObstacle.GetValue()));}
   if(Step>150)MaxWaitingTurn=FMath::Max(MaxWaitingTurn,FMath::Abs(FMath::FindDeltaAngleDegrees(Previous,Walkers[0].Heading)));
  }
  if(DidYield)Yielded++;TArray<float> Travel;for(auto& W:Walkers)Travel.Add(W.Travelled);PedestrianTestObstacle=FVector(1e8);
  for(int32 Step=0;Step<300;Step++){Elapsed+=1.f/15;SimulateWalkers(1.f/15);}
  bool All=true;for(int32 I=0;I<Walkers.Num();I++)if(Walkers[I].Travelled-Travel[I]<500)All=false;if(All)Resumed++;
  for(auto& W:Walkers)if(W.Visual.IsValid())W.Visual->Destroy();Walkers.Empty();Wall->Destroy();
 }
 R->SetNumberField(TEXT("confined_sidewalk_scenarios"),2);R->SetNumberField(TEXT("yielded_without_entering_road"),Yielded);R->SetNumberField(TEXT("resumed_after_player_leaves"),Resumed);R->SetNumberField(TEXT("road_intrusion_frames"),RoadIntrusions);R->SetNumberField(TEXT("minimum_player_clearance_cm"),MinPlayerDistance);R->SetNumberField(TEXT("maximum_waiting_turn_degrees"),MaxWaitingTurn);
 Walkers=MoveTemp(Saved);PedestrianJunctions=MoveTemp(SavedJunctions);PedestrianNextAdmission=MoveTemp(SavedAdmission);PedestrianTestObstacle=SavedObstacle;Elapsed=SavedElapsed;
 FString Result;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Result));return Result;
}
''';p.write_text(s)
p=r/'Source/BogotaVoxel/BogotaDeveloper.cpp';s=p.read_text();s+=r'''
FString ABogotaPlayer::ValidateDeveloperTools(){
 auto R=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Checks;auto Check=[&](const TCHAR* Name,bool OK){auto V=MakeShared<FJsonObject>();V->SetStringField(TEXT("id"),Name);V->SetBoolField(TEXT("passed"),OK);Checks.Add(MakeShared<FJsonValueObject>(V));UE_LOG(LogTemp,Display,TEXT("DEV_NPC_CHECK %s %s"),Name,OK?TEXT("PASS"):TEXT("FAIL"));};
 auto* PC=Cast<APlayerController>(Controller);int32 Balance=Delivery->Balance;PC->ConsoleCommand(TEXT("BogRain 1"));Check(TEXT("rain_requires_developer_mode"),City->DeveloperRainOverride==-1);
 PC->ConsoleCommand(TEXT("BogDev 1"));Check(TEXT("developer_console_command"),Delivery->DeveloperMode);
 PC->ConsoleCommand(TEXT("BogRain 1"));Check(TEXT("rain_on_immediately"),City->DeveloperRainOverride==1&&City->RainIntensity>.99f);
 PC->ConsoleCommand(TEXT("BogRain 0"));Check(TEXT("rain_off_immediately"),City->DeveloperRainOverride==0&&City->RainIntensity<.01f);
 PC->ConsoleCommand(TEXT("BogRain -1"));Check(TEXT("rain_automatic"),City->DeveloperRainOverride==-1);
 PC->ConsoleCommand(TEXT("BogCar 0"));Check(TEXT("enter_traffic_car"),DeveloperCarIndex==0&&IsHidden()&&GetCapsuleComponent()->GetCollisionEnabled()==ECollisionEnabled::NoCollision);
 FVector Before=City->Vehicles[0].Position;MoveForward(.8f);MoveRight(0);Check(TEXT("blueprint_inputs_reach_developer_car"),DeveloperDriveInput().X>.7f);
 for(int32 I=0;I<60;I++){City->SimulateTraffic(1.f/30);City->UpdateTrafficVisuals(1);UpdateDeveloperCarView(1.f/30);}Check(TEXT("car_drives_from_input"),FVector::Dist2D(Before,City->Vehicles[0].Position)>200);
 ForwardInput=SideInput=0;Check(TEXT("safe_exit_restores_walking"),LeaveDeveloperCar()&&!IsHidden()&&GetCharacterMovement()->MovementMode==MOVE_Walking);
 int32 Entered=0,Exited=0;for(int32 Index:{1,4,5,16,32,60,96,97,98,99}){BogCar(Index);if(DeveloperCarIndex==Index)Entered++;if(LeaveDeveloperCar())Exited++;}
 Check(TEXT("varied_cars_taxis_and_buses_enter"),Entered==10);Check(TEXT("varied_cars_taxis_and_buses_exit"),Exited==10);
 int32 Expected=City->Vehicles.Num();if(!City->ParkedCars.IsEmpty()){SetActorLocation(City->ParkedCars[0].Door+FVector(0,0,92));Interact();Check(TEXT("F_enters_parked_car"),DeveloperCarIndex==Expected);Check(TEXT("F_exits_parked_car"),LeaveDeveloperCar());}
 BogDev(false);Check(TEXT("developer_exit_restores_balance"),!Delivery->DeveloperMode&&Delivery->Balance==Balance&&City->DeveloperRainOverride==-1);
 R->SetArrayField(TEXT("checks"),Checks);TSharedPtr<FJsonObject> Ped;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(City->ValidatePedestrianPresentation()),Ped);R->SetObjectField(TEXT("pedestrians"),Ped);
 FString Result;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Result));return Result;
}
''';p.write_text(s)
p=r/'Source/BogotaVoxel/BogotaCity.cpp';s=p.read_text();needle=' if(FParse::Param(FCommandLine::Get(),TEXT("RainVisualCheck")))';s=s.replace(needle,''' if(FParse::Param(FCommandLine::Get(),TEXT("NpcDeveloperTest"))&&Elapsed>3){
  if(auto* P=Cast<ABogotaPlayer>(UGameplayStatics::GetPlayerPawn(this,0))){FString Report=P->ValidateDeveloperTools();FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/TEXT("npc_developer_validation.json")));UE_LOG(LogTemp,Display,TEXT("NPC_DEVELOPER_REPORT %s"),*Report);FGenericPlatformMisc::RequestExit(false);return;}
 }
'''+needle);p.write_text(s)
