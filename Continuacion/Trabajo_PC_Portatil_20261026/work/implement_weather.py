from pathlib import Path
r=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1')
p=r/'Source/BogotaVoxel/BogotaTraffic.cpp';s=p.read_text().replace(' From.Z=WalkerGroundHeight(From);To.Z=WalkerGroundHeight(To);',' From.Z=26;To.Z=26;').replace('FCollisionShape::MakeCapsule(34,75),Query);','FCollisionShape::MakeCapsule(34,65),Query);');p.write_text(s)
p=r/'Source/BogotaVoxel/BogotaCity.cpp';s=p.read_text().replace('Super::Tick(Dt);Elapsed+=Dt;','Super::Tick(Dt);Elapsed+=Dt;UpdateWeather(Dt);')
s=s.replace('Sun->GetLightComponent()->SetIntensity(Elev>0?6.f*(.3f+.7f*Elev):.22f);','Sun->GetLightComponent()->SetIntensity((Elev>0?6.f*(.3f+.7f*Elev):.22f)*(1.f-.55f*RainIntensity));')
s=s.replace('Horizon=FMath::Lerp(Horizon,FLinearColor(.9f,.24f,.075f),Twilight*.72f);','Horizon=FMath::Lerp(Horizon,FLinearColor(.9f,.24f,.075f),Twilight*.72f);\n Horizon=FMath::Lerp(Horizon,FMath::Lerp(FLinearColor(.016,.025,.045),FLinearColor(.24,.31,.39),DayMix),RainIntensity*.8f);')
s=s.replace('FLinearColor(.025f,.16f,.5f),DayMix));','FLinearColor(.025f,.16f,.5f),DayMix)*(1.f-.5f*RainIntensity));')
s=s.replace('Fog->GetComponent()->SetFogInscatteringColor','Fog->GetComponent()->SetFogDensity(.00012f+RainIntensity*.0006f);\n Fog->GetComponent()->SetFogInscatteringColor');p.write_text(s)
p=r/'Source/BogotaVoxel/BogotaWeather.cpp';p.write_text('''#include "BogotaGame.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Camera/PlayerCameraManager.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"

void ABogotaCity::UpdateWeather(float Dt){
 float Target=FMath::Clamp(RainAmountFor(CycleSeconds,GameDay),0.f,1.f);
 if(FParse::Param(FCommandLine::Get(),TEXT("ForceRain")))Target=1;
 RainIntensity=FMath::FInterpConstantTo(RainIntensity,Target,Dt,.045f);
 if(!RainMesh&&RainIntensity>.001f){
  RainMesh=NewObject<UInstancedStaticMeshComponent>(this,TEXT("VoxelRain"));AddInstanceComponent(RainMesh);RainMesh->SetupAttachment(RootComponent);RainMesh->SetMobility(EComponentMobility::Movable);RainMesh->SetStaticMesh(Cube);RainMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);RainMesh->SetCanEverAffectNavigation(false);RainMesh->CastShadow=false;
  auto* Mat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/World/M_Rain.M_Rain"));RainMesh->SetMaterial(0,Mat?Mat:Palette[5]);RainMesh->RegisterComponent();
  for(int32 I=0;I<600;I++){RainDrops.Add(FVector::ZeroVector);RainFloors.Add(0);RainMesh->AddInstance(FTransform(FVector::ZeroVector));}
 }
 if(!RainMesh)return;RainMesh->SetVisibility(RainIntensity>.005f);if(RainIntensity<=.005f)return;
 FVector Eye=FVector::ZeroVector;auto* PC=GetWorld()->GetFirstPlayerController();if(PC&&PC->PlayerCameraManager)Eye=PC->PlayerCameraManager->GetCameraLocation();
 const bool Relocate=FVector::DistSquared(Eye,RainOrigin)>FMath::Square(800.f);if(Relocate)RainOrigin=Eye;
 const int32 Count=FMath::RoundToInt(600*RainIntensity);
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
  RainMesh->UpdateInstanceTransform(I,FTransform(FRotator(0,0,-4),P,Visible?FVector(.035,.035,.65):FVector::ZeroVector),false,false,true);
 }
 RainMesh->MarkRenderStateDirty();
}
''')
