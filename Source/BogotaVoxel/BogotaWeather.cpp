#include "BogotaGame.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Camera/PlayerCameraManager.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "Components/DirectionalLightComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Json.h"

void ABogotaCity::UpdateWeather(float Dt){
 float Target=AdvanceDynamicWeather(Dt);
 if(FParse::Param(FCommandLine::Get(),TEXT("ForceRain")))Target=1;
 RainIntensity=FMath::FInterpConstantTo(RainIntensity,Target,Dt,.045f);
 const bool Storm=Target>.95f&&RainIntensity>.85f;
 HailIntensity=FMath::FInterpConstantTo(HailIntensity,Storm?1.f:0.f,Dt,.5f);
 LightningFlash=FMath::Max(0.f,LightningFlash-Dt*8);
 if(Storm){StormClock+=Dt;if(StormClock>=NextLightning){StormClock=0;NextLightning=RainRandom.FRandRange(14,28);LightningFlash=1;ThunderDelay=RainRandom.FRandRange(.8f,2.5f);LightningEvents++;}}
 else{StormClock=0;NextLightning=8;ThunderDelay=-1;LightningFlash=0;}
 if(ThunderDelay>=0){ThunderDelay-=Dt;if(ThunderDelay<0){ThunderEvents++;auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/World/Audio/S_Thunder.S_Thunder"));if(Sound)UGameplayStatics::PlaySound2D(this,Sound,.7f,RainRandom.FRandRange(.88f,1.08f));}}
 if(!LightningLight&&LightningFlash>0){LightningLight=NewObject<UDirectionalLightComponent>(this,TEXT("StormLightning"));AddInstanceComponent(LightningLight);LightningLight->SetupAttachment(RootComponent);LightningLight->SetMobility(EComponentMobility::Movable);LightningLight->SetWorldRotation(FRotator(-65,35,0));LightningLight->SetLightColor(FLinearColor(.72f,.82f,1));LightningLight->SetCastShadows(false);LightningLight->RegisterComponent();}
 if(LightningLight)LightningLight->SetIntensity(LightningFlash*7);
 if(!HailMesh&&HailIntensity>.001f){HailMesh=NewObject<UInstancedStaticMeshComponent>(this,TEXT("VoxelHail"));AddInstanceComponent(HailMesh);HailMesh->SetupAttachment(RootComponent);HailMesh->SetMobility(EComponentMobility::Movable);HailMesh->SetStaticMesh(Cube);HailMesh->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/World/M_Hail.M_Hail")));HailMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);HailMesh->SetCanEverAffectNavigation(false);HailMesh->CastShadow=false;HailMesh->RegisterComponent();for(int32 I=0;I<200;I++){HailDrops.Add(FVector::ZeroVector);HailFloors.Add(0);HailMesh->AddInstance(FTransform(FVector::ZeroVector));}}
 if(HailMesh)HailMesh->SetVisibility(HailIntensity>.005f);
 if(!RainMesh&&RainIntensity>.001f){
  RainMesh=NewObject<UInstancedStaticMeshComponent>(this,TEXT("VoxelRain"));AddInstanceComponent(RainMesh);RainMesh->SetupAttachment(RootComponent);RainMesh->SetMobility(EComponentMobility::Movable);RainMesh->SetStaticMesh(Cube);RainMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);RainMesh->SetCanEverAffectNavigation(false);RainMesh->CastShadow=false;
  auto* Mat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/World/M_Rain.M_Rain"));RainMesh->SetMaterial(0,Mat?Mat:Palette[5].Get());RainMesh->RegisterComponent();
  for(int32 I=0;I<1800;I++){RainDrops.Add(FVector::ZeroVector);RainFloors.Add(0);RainMesh->AddInstance(FTransform(FVector::ZeroVector));}
 }
 if(!RainMesh)return;RainMesh->SetVisibility(RainIntensity>.005f);if(RainIntensity<=.005f){if(HailMesh)HailMesh->SetVisibility(false);return;}
 FVector Eye=FVector::ZeroVector;auto* PC=GetWorld()->GetFirstPlayerController();if(PC&&PC->PlayerCameraManager)Eye=PC->PlayerCameraManager->GetCameraLocation();
 const bool Relocate=FVector::DistSquared(Eye,RainOrigin)>FMath::Square(800.f);if(Relocate)RainOrigin=Eye;
 const int32 Count=FMath::RoundToInt(600*RainIntensity+1200*FMath::Clamp((RainIntensity-.7f)/.3f,0.f,1.f));
 FCollisionQueryParams Query(SCENE_QUERY_STAT(RainRoof),false);if(PC&&PC->GetPawn())Query.AddIgnoredActor(PC->GetPawn());
 for(int32 I=0;I<RainDrops.Num();I++){
  auto& P=RainDrops[I];
  if(Relocate||P.Z<RainFloors[I]+25||FMath::Abs(P.X-Eye.X)>2200||FMath::Abs(P.Y-Eye.Y)>2200){
   P=Eye+FVector(RainRandom.FRandRange(-2100,2100),RainRandom.FRandRange(-2100,2100),RainRandom.FRandRange(300,2100));
   FHitResult Hit;RainFloors[I]=GetWorld()->LineTraceSingleByChannel(Hit,FVector(P.X,P.Y,Eye.Z+2300),FVector(P.X,P.Y,Eye.Z-3500),ECC_Visibility,Query)?Hit.ImpactPoint.Z:0;
   if(Relocate)P.Z=RainRandom.FRandRange(FMath::Min(RainFloors[I]+50,float(Eye.Z+2300)),Eye.Z+2300);
  }
  P+=FVector(-110,45,-1600)*FMath::Min(Dt,.1f);
  const bool Visible=I<Count&&P.Z>RainFloors[I]+25;
  RainMesh->UpdateInstanceTransform(I,FTransform(FRotator(0,0,-4),P,Visible?FVector(.025,.025,.45):FVector::ZeroVector),false,false,true);
 }
 RainMesh->MarkRenderStateDirty();
 if(HailMesh&&HailIntensity>.005f){
  for(int32 I=0;I<HailDrops.Num();I++){auto& P=HailDrops[I];if(Relocate||P.Z<HailFloors[I]+10||FMath::Abs(P.X-Eye.X)>2200||FMath::Abs(P.Y-Eye.Y)>2200){P=Eye+FVector(RainRandom.FRandRange(-2100,2100),RainRandom.FRandRange(-2100,2100),RainRandom.FRandRange(300,2300));FHitResult Hit;HailFloors[I]=GetWorld()->LineTraceSingleByChannel(Hit,FVector(P.X,P.Y,Eye.Z+2500),FVector(P.X,P.Y,Eye.Z-3500),ECC_Visibility,Query)?Hit.ImpactPoint.Z:0;}
   P+=FVector(-190,70,-2700)*FMath::Min(Dt,.1f);bool Visible=I<FMath::RoundToInt(200*HailIntensity)&&P.Z>HailFloors[I]+10;
   HailMesh->UpdateInstanceTransform(I,FTransform(FRotator::ZeroRotator,P,Visible?FVector(.055f):FVector::ZeroVector),false,false,true);
  }HailMesh->MarkRenderStateDirty();
 }
}


FString ABogotaCity::ValidateDynamicWeather(){
 auto Report=MakeShared<FJsonObject>();auto Checks=MakeShared<FJsonObject>();auto Check=[&](const TCHAR* Name,bool Passed){Checks->SetBoolField(Name,Passed);UE_LOG(LogTemp,Display,TEXT("DYNAMIC_WEATHER %s %s"),Name,Passed?TEXT("PASS"):TEXT("FAIL"));};
 int32 Starts=0;bool Adjacent=true;FRandomStream Samples(713);for(int32 State=0;State<4;State++)for(int32 I=0;I<20000;I++){int32 Next=NextWeatherState(State,Samples.FRand());if(State==0&&Next==1)Starts++;Adjacent&=Next>=0&&Next<=3&&FMath::Abs(Next-State)<=1;}
 Check(TEXT("probability_matches_35_percent"),FMath::Abs(Starts/20000.f-RainStartChance)<.02f);Check(TEXT("no_weather_level_skipped"),Adjacent);
 int32 SavedState=AutomaticWeatherState,SavedPrevious=PreviousWeatherOverride,SavedOverride=DeveloperRainOverride;float SavedRemaining=WeatherDecisionRemaining,SavedTarget=WeatherTargetIntensity,SavedRain=RainIntensity;bool SavedInitialized=WeatherInitialized;FRandomStream SavedRandom=WeatherRandom;
 auto Run=[&](int32 Seed,int32& Up,int32& Down,int32& States){WeatherInitialized=true;WeatherRandom.Initialize(Seed);AutomaticWeatherState=0;WeatherDecisionRemaining=1;DeveloperRainOverride=PreviousWeatherOverride=-1;TArray<uint8> History;States=1;int32 Last=0;for(int32 T=0;T<86400;T++){AdvanceDynamicWeather(1);States|=1<<AutomaticWeatherState;if(AutomaticWeatherState!=Last){if(AutomaticWeatherState>Last)Up++;else Down++;Last=AutomaticWeatherState;History.Add(uint8(AutomaticWeatherState));}}return History;};
 int32 Up=0,Down=0,States=0;auto First=Run(101,Up,Down,States);int32 Up2=0,Down2=0,States2=0;auto Same=Run(101,Up2,Down2,States2);Up2=Down2=States2=0;auto Different=Run(202,Up2,Down2,States2);
 Check(TEXT("all_weather_types_occur"),States==15);Check(TEXT("rain_intensifies_and_eases"),Up>0&&Down>0);Check(TEXT("seed_reproducible_for_testing"),First==Same);Check(TEXT("new_seed_changes_weather_sequence"),First!=Different);
 DeveloperRainOverride=3;float Hold=WeatherDecisionRemaining;AdvanceDynamicWeather(1000);Check(TEXT("developer_override_pauses_random_decisions"),WeatherDecisionRemaining==Hold);RainIntensity=1;DeveloperRainOverride=-1;AdvanceDynamicWeather(0);Check(TEXT("automatic_resumes_current_storm"),AutomaticWeatherState==3&&WeatherTargetIntensity==1&&WeatherDecisionRemaining>=45&&WeatherDecisionRemaining<=100);
 AutomaticWeatherState=SavedState;PreviousWeatherOverride=SavedPrevious;DeveloperRainOverride=SavedOverride;WeatherDecisionRemaining=SavedRemaining;WeatherTargetIntensity=SavedTarget;RainIntensity=SavedRain;WeatherInitialized=SavedInitialized;WeatherRandom=SavedRandom;
 Report->SetObjectField(TEXT("checks"),Checks);Report->SetNumberField(TEXT("sampled_rain_start_probability"),Starts/20000.f);Report->SetNumberField(TEXT("sampled_transitions"),80000);Report->SetNumberField(TEXT("simulated_seconds"),86400);Report->SetNumberField(TEXT("intensifications"),Up);Report->SetNumberField(TEXT("reductions"),Down);FString Result;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Result));return Result;
}
