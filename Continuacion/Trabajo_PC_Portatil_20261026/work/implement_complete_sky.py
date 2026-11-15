from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/BogotaCity.cpp');s=p.read_text()
a=s.index(' float Angle=Phase<960?');z=s.index('\n}',a)
s=s[:a]+''' // The sun completes a full orbit, including below the horizon at night.
 float SolarAngle=(Hour-6.f)/24.f*360.f;float Elev=FMath::Sin(FMath::DegreesToRadians(SolarAngle));
 float DayMix=FMath::SmoothStep(-.08f,.2f,Elev),Twilight=1-FMath::SmoothStep(.02f,.4f,FMath::Abs(Elev));
 FVector SunDirection(FMath::Cos(FMath::DegreesToRadians(SolarAngle))*.8f,FMath::Cos(FMath::DegreesToRadians(SolarAngle))*.6f,Elev);
 FVector LightDirection=Elev>=0?-SunDirection:SunDirection;
 Sun->SetActorRotation(LightDirection.Rotation());Sun->GetLightComponent()->SetIntensity(Elev>0?6.f*(.3f+.7f*Elev):.22f);
 FLinearColor Warm(1,.44f,.19f),Noon(1,.95f,.85f),Night(.32f,.45f,.75f);
 Sun->GetLightComponent()->SetLightColor(Elev>=0?FMath::Lerp(Warm,Noon,FMath::Clamp(Elev*2,0.f,1.f)):Night);
 Ambient->GetLightComponent()->SetIntensity(.55f+DayMix*2.45f);
 Ambient->GetLightComponent()->SetLightColor(FMath::Lerp(FLinearColor(.38f,.48f,.72f),FLinearColor(.86f,.92f,1),DayMix));
 FLinearColor Horizon=FMath::Lerp(FLinearColor(.012f,.02f,.055f),FLinearColor(.28f,.56f,.92f),DayMix);
 Horizon=FMath::Lerp(Horizon,FLinearColor(.9f,.24f,.075f),Twilight*.72f);
 if(SkyMaterial){SkyMaterial->SetVectorParameterValue(TEXT("Horizon"),Horizon);SkyMaterial->SetVectorParameterValue(TEXT("Zenith"),FMath::Lerp(FLinearColor(.002f,.004f,.018f),FLinearColor(.025f,.16f,.5f),DayMix));
  SkyMaterial->SetVectorParameterValue(TEXT("SunDir"),FLinearColor(SunDirection));SkyMaterial->SetVectorParameterValue(TEXT("MoonDir"),FLinearColor(-SunDirection));
  SkyMaterial->SetScalarParameterValue(TEXT("Daylight"),DayMix);SkyMaterial->SetScalarParameterValue(TEXT("Twilight"),Twilight);SkyMaterial->SetScalarParameterValue(TEXT("Night"),1-DayMix);SkyMaterial->SetScalarParameterValue(TEXT("CloudTime"),Elapsed);
 }
 if(GlowMaterial)GlowMaterial->SetScalarParameterValue(TEXT("GlowStrength"),FMath::Lerp(3.f,.15f,DayMix));
 Fog->GetComponent()->SetFogInscatteringColor(FMath::Lerp(FLinearColor(.025f,.035f,.07f),FLinearColor(.37f,.53f,.7f),DayMix));
'''+s[z:]
# Add deterministic sky visual cycle capture for validation, not game controls.
pos=s.index(' if(FParse::Param(FCommandLine::Get(),TEXT("NightVisualCheck")))')
s=s[:pos]+''' if(FParse::Param(FCommandLine::Get(),TEXT("SkyCycleVisualCheck"))){
  static ACameraActor* SkyCamera=nullptr;static int32 Captured=0;int32 Shot=FMath::Clamp(int32((Elapsed-2)/5),0,3);const float Phases[]={0,480,950,1200};CycleSeconds=Phases[Shot];
  if(auto* PC=GetWorld()->GetFirstPlayerController()){if(!SkyCamera)SkyCamera=GetWorld()->SpawnActor<ACameraActor>();SkyCamera->SetActorLocationAndRotation(FVector(-5500,14500,650),FRotator(22,Shot==3?130:-35,0));SkyCamera->GetCameraComponent()->SetFieldOfView(90);PC->SetViewTarget(SkyCamera);
   if(Elapsed>4+Captured*5&&Captured<4){PC->ConsoleCommand(TEXT("HighResShot 1280x720"));Captured++;}}
 }
'''+s[pos:];p.write_text(s)
