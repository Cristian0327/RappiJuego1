from pathlib import Path
p=Path(__file__).resolve().parents[1]/'outputs/BogotaVoxel/Source/BogotaVoxel/BogotaCity.cpp';s=p.read_text();needle='Super::Tick(Dt);Elapsed+=Dt;'
s=s.replace(needle,needle+'''
 if(FParse::Param(FCommandLine::Get(),TEXT("CrowdVisualCheck"))&&!Walkers.IsEmpty()){
  static ACameraActor* Camera=nullptr;static int32 Captured=0;int32 Shot=Elapsed<9?0:Elapsed<15?1:2;auto& W=Walkers[Shot==0?0:Shot==1?8:60];
  if(auto* PC=GetWorld()->GetFirstPlayerController()){
   if(!Camera)Camera=GetWorld()->SpawnActor<ACameraActor>();
   if(auto* Pawn=PC->GetPawn())Pawn->SetActorLocation(W.Position+FVector(0,450,90));
   FVector Eye=W.Position+FRotator(0,W.Heading,0).RotateVector(FVector(400,-350,170));Camera->SetActorLocationAndRotation(Eye,(W.Position+FVector(0,0,85)-Eye).Rotation());Camera->GetCameraComponent()->SetFieldOfView(55);PC->SetViewTarget(Camera);
   if((Shot==0&&Elapsed>6&&Captured==0)||(Shot==1&&Elapsed>12&&Captured==1)||(Shot==2&&Elapsed>18&&Captured==2)){PC->ConsoleCommand(TEXT("HighResShot 1"));Captured++;}
  }
 }
''');p.write_text(s)
