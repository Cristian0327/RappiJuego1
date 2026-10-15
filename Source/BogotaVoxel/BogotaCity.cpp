#include "DeliverySystem.h"
#include "EngineUtils.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Animation/AnimationAsset.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Camera/CameraComponent.h"
#include "Camera/CameraActor.h"
#include "GameFramework/PlayerController.h"
#include "BogotaGame.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Animation/AnimationAsset.h"

// X is north and Y is east. Coordinates are centimetres. This is a deliberately
// compressed, authored interpretation, not a GIS survey or navigational map.
enum EP { Asphalt,Concrete,Brick,Ochre,Cream,White,Charcoal,Glass,Green,Leaf,Trunk,Red,Yellow,Teal,Orange,Glow,Blue,Stone,Earth,Grass, Roof,Steel,Count };
static const TCHAR* ColorNames[]={TEXT("Asphalt"),TEXT("Concrete"),TEXT("Brick"),TEXT("Ochre"),TEXT("Cream"),TEXT("White"),TEXT("Charcoal"),TEXT("Glass"),TEXT("Green"),TEXT("Leaf"),TEXT("Trunk"),TEXT("Red"),TEXT("Yellow"),TEXT("Teal"),TEXT("Orange"),TEXT("Glow"),TEXT("Blue"),TEXT("Stone"),TEXT("Earth"),TEXT("Grass"),TEXT("Roof"),TEXT("Steel")};

ABogotaCity::ABogotaCity() {
 PrimaryActorTick.bCanEverTick=true;
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("CityRoot"));
 RootComponent->SetMobility(EComponentMobility::Static);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> C(TEXT("/Engine/BasicShapes/Cube.Cube")); Cube=C.Object;
 for(int32 I=0;I<Count;I++){
  ConstructorHelpers::FObjectFinder<UMaterialInterface> M(*FString::Printf(TEXT("/Game/World/M_%s.M_%s"),ColorNames[I],ColorNames[I])); Palette.Add(M.Object);
  auto S=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(*FString::Printf(TEXT("Solid_%d"),I));
  S->SetupAttachment(RootComponent);S->SetStaticMesh(Cube);S->SetMaterial(0,M.Object);S->SetMobility(EComponentMobility::Movable);S->SetCollisionProfileName(TEXT("BlockAll"));S->SetCanEverAffectNavigation(false);S->SetCullDistances(80000,100000);S->bAutoRebuildTreeOnInstanceChanges=false;Solid.Add(S);
  auto D=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(*FString::Printf(TEXT("Decor_%d"),I));
  D->SetupAttachment(RootComponent);D->SetStaticMesh(Cube);D->SetMaterial(0,M.Object);D->SetMobility(EComponentMobility::Movable);D->SetCollisionEnabled(ECollisionEnabled::NoCollision);D->SetCanEverAffectNavigation(false);D->SetCullDistances(24000,34000);D->CastShadow=I!=Glow && I!=Glass && I!=White;D->bAutoRebuildTreeOnInstanceChanges=false;Detail.Add(D);
  auto V=CreateDefaultSubobject<UInstancedStaticMeshComponent>(*FString::Printf(TEXT("Traffic_%d"),I));
  V->SetupAttachment(RootComponent);V->SetStaticMesh(Cube);V->SetMaterial(0,M.Object);V->SetMobility(EComponentMobility::Movable);V->SetCollisionEnabled(ECollisionEnabled::NoCollision);V->SetCanEverAffectNavigation(false);V->SetCullDistances(26000,35000);Moving.Add(V);
 }
 NorthRoads={-36000,-24000,-12000,0,12000,24000,36000};EastRoads={-22000,-11000,0,11000,22000};
}
void ABogotaCity::Block(FVector C,FVector S,int32 P,bool Collision){
 auto* Mesh=Collision?Solid[P].Get():Detail[P].Get();Mesh->AddInstance(FTransform(FRotator::ZeroRotator,C,S/100));StaticVoxelCount++;
}
void ABogotaCity::Label(FString T,FVector P,float Size,FRotator R){
 auto* L=NewObject<UTextRenderComponent>(this);AddInstanceComponent(L);L->SetupAttachment(RootComponent);L->SetWorldLocation(P);L->SetWorldRotation(R);L->SetText(FText::FromString(T));L->SetWorldSize(Size);L->SetHorizontalAlignment(EHTA_Center);L->SetTextRenderColor(FColor(238,236,207));L->SetCollisionEnabled(ECollisionEnabled::NoCollision);L->RegisterComponent();Signs.Add(L);
}
void ABogotaCity::Tree(FVector P,FRandomStream& R){
 float H=R.RandRange(700,1100);Block(P+FVector(0,0,H*.4),FVector(100,100,H*.8),Trunk);Block(P+FVector(0,0,H),FVector(650,650,400),Green,false);Block(P+FVector(0,0,H+300),FVector(450,450,250),Leaf,false);Block(P+FVector(0,0,H+470),FVector(250,250,150),Green,false);
}
void ABogotaCity::Building(float X,float Y,float SX,float SY,int32 Floors,int32 Style,FRandomStream& R){
 FMapFootprint Footprint;Footprint.Center=FVector(X,Y,0);Footprint.Extent=FVector2D(SX*.5f,SY*.5f);MapFootprints.Add(Footprint);
 float Z=20,H=Floors*300;int32 Wall=Style==0?(R.RandRange(0,1)?Ochre:Cream):(Style==1?Brick:(R.RandRange(0,1)?Cream:Concrete));
 Block(FVector(X,Y,Z+H*.5),FVector(SX,SY,H),Wall);Block(FVector(X,Y,H+45),FVector(SX+80,SY+80,70),Style==0?Roof:Charcoal);
 for(int32 F=0;F<Floors;F++){
  float WZ=170+300*F;
  if(F%3==0)Block(FVector(X,Y,320+F*300),FVector(SX+25,SY+25,25),Stone,false);
  int32 NX=FMath::Clamp(int32(SX/350),2,8),NY=FMath::Clamp(int32(SY/350),2,8);
  for(int32 J=0;J<NX;J++)for(int32 Sign:{-1,1}){
   float WX=X-SX*.5+(J+.5f)*SX/NX;int32 Mat=R.FRand()<.26?Glow:Glass;
   Block(FVector(WX,Y+Sign*(SY*.5+4),WZ),FVector(Style==2?210:120,12,155),Mat,false);
   if(Style==0)Block(FVector(WX,Y+Sign*(SY*.5+22),WZ-87),FVector(160,60,20),Teal,false);
  }
  for(int32 J=0;J<NY;J++)for(int32 Sign:{-1,1})Block(FVector(X+Sign*(SX*.5+4),Y-SY*.5+(J+.5f)*SY/NY,WZ),FVector(12,Style==2?210:120,155),R.FRand()<.22?Glow:Glass,false);
 }
 Block(FVector(X,Y-SY*.5-10,140),FVector(170,25,260),Charcoal,false);
 if(Style==0){for(int32 L=0;L<4;L++)Block(FVector(X,Y,H+90+L*65),FVector(SX+120,SY+120-L*SY/5,80),Roof,false);}
 else if(Floors>5)Block(FVector(X,Y,H+220),FVector(SX*.55,SY*.55,300),Wall);
 if(Floors<5){int32 Shop=R.RandRange(0,2)==0?Teal:Red;Block(FVector(X,Y-SY*.5-50,295),FVector(SX*.7,180,75),Shop,false);}
}
void ABogotaCity::BuildCity(){
 FRandomStream R(26092026);
 Block(FVector(0,0,-120),FVector(96000,76000,240),Grass);
 for(float Y:EastRoads){
  float Width=Y==0?2300:1500;
  Block(FVector(0,Y,1),FVector(84000,Width,12),Asphalt);
  for(int32 S:{-1,1}){
   Block(FVector(0,Y+S*(Width*.5+380),13),FVector(84000,760,26),Concrete);
   Block(FVector(0,Y+S*(Width*.5+150),29),FVector(83000,230,8),Teal,false);
  }
  for(int32 X=-40800;X<42000;X+=600){Block(FVector(X,Y,9),FVector(300,16,4),Yellow,false);if(Y==0)for(int32 S:{-1,1})Block(FVector(X,S*530,12),FVector(340,45,12),Red,false);}
 }
 for(float X:NorthRoads){
  Block(FVector(X,0,3),FVector(1500,53000,12),Asphalt);
  for(int32 S:{-1,1}){Block(FVector(X+S*1150,0,13),FVector(800,53000,26),Concrete);Block(FVector(X+S*900,0,29),FVector(220,53000,8),Teal,false);}
  for(int32 Y=-25000;Y<26000;Y+=600)Block(FVector(X,Y,11),FVector(16,300,4),Yellow,false);
 }
 // Clear intersections with flush road plates; ramps keep every cycle route continuous.
 for(float X:NorthRoads)for(float Y:EastRoads){
  Block(FVector(X,Y,23),FVector(3100,Y==0?3850:3100,8),Asphalt);
  for(int32 S:{-1,1})for(int32 K=-4;K<=4;K++){
   Block(FVector(X+S*1250,Y+K*145,29),FVector(300,70,4),White,false);
   Block(FVector(X+K*145,Y+S*(Y==0?1550:1250),29),FVector(70,300,4),White,false);
  }
  Block(FVector(X+1600,Y+1900,270),FVector(35,35,540),Steel);
  Block(FVector(X+1600,Y+1900,570),FVector(140,85,260),Charcoal,false);
  SignalTransforms.Add(FTransform(FRotator::ZeroRotator,FVector(X+1600,Y+1848,570),FVector(.6,.2,.6)));SignalNorthSouth.Add(false);
  Block(FVector(X-1850,Y+1500,270),FVector(35,35,540),Steel);Block(FVector(X-1850,Y+1500,570),FVector(85,140,260),Charcoal,false);
  SignalTransforms.Add(FTransform(FRotator(0,90,0),FVector(X-1798,Y+1500,570),FVector(.6,.2,.6)));SignalNorthSouth.Add(true);
 }
 for(int32 IX=0;IX<NorthRoads.Num()-1;IX++)for(int32 IY=0;IY<EastRoads.Num()-1;IY++){
  float X=(NorthRoads[IX]+NorthRoads[IX+1])*.5,Y=(EastRoads[IY]+EastRoads[IY+1])*.5;
  // Reserved landmark squares: Bolivar, Parque 93, Usaquen, and central park.
  if((IX==2&&IY==3)||(IX==4&&IY==3)||(IX==5&&IY==3)||(IX==3&&IY==1))continue;
  int32 Style=X<0?(Y>11000?0:1):2;
  for(int32 A:{-1,1})for(int32 B:{-1,1}){
   int32 Floors=Style==0?R.RandRange(1,3):Style==1?R.RandRange(2,5):R.RandRange(5,12);
   if(A==-1&&B==-1)continue; // This frontage belongs to the walk-in delivery shop.
   Building(X+A*2600,Y+B*2200,R.RandRange(2000,3000),R.RandRange(1800,2700),Floors,Style,R);
  }
  for(int32 K=0;K<3;K++)Tree(FVector(X-3200+K*2800,Y,30),R);
 }
 // Street furniture is instanced rather than one ticking actor per object.
 for(float Y:EastRoads)for(int32 X=-39000;X<=39000;X+=3000)for(int32 S:{-1,1}){
  float Off=(Y==0?1900:1500)*S;
  if(FMath::Fmod(float(X+36000),12000)<1900)continue;
  Block(FVector(X,Y+Off,400),FVector(45,45,800),Steel);
  Block(FVector(X,Y+Off-S*120,790),FVector(70,280,50),Charcoal,false);
  Block(FVector(X,Y+Off-S*220,758),FVector(60,100,15),Glow,false);
  if(X%6000==3000)Tree(FVector(X+650,Y+Off+S*180,30),R);
 }
 // Layered eastern cordillera: intentional voxel silhouettes, not smooth terrain.
 for(int32 X=-44000;X<=44000;X+=2200){
  int32 H=R.RandRange(2500,7000);
  for(int32 L=0;L<7;L++)Block(FVector(X,28500+L*1700,(H+L*700)*.5),FVector(2300,2200,H+L*700),L%3==0?Green:Earth);
 }
 // Ciudad Bolivar's southwestern, inhabited hills.
 for(int32 I=0;I<7;I++)for(int32 J=0;J<4;J++){
  float X=-34000-I*1400,Y=-25000-J*1600,Z=(I+J)*180;
  Block(FVector(X,Y,Z*.5),FVector(1500,1700,Z+20),Earth);
  Block(FVector(X,Y,Z+230),FVector(800,900,450),I%2?Brick:Ochre);
  Block(FVector(X,Y,Z+470),FVector(860,940,35),Steel,false);
 }
 BuildLandmarks();
 for(int32 I=0;I<Solid.Num();I++){Solid[I]->BuildTreeIfOutdated(false,true);Detail[I]->BuildTreeIfOutdated(false,true);Solid[I]->MarkRenderStateDirty();Detail[I]->MarkRenderStateDirty();}
 UE_LOG(LogTemp,Display,TEXT("BOGOTA_CITY voxels=%d materials=%d city=840x530m"),StaticVoxelCount,Count);
}
void ABogotaCity::BuildLandmarks(){
 FRandomStream R(1820);
 // Plaza de Bolivar and Cathedral, east edge of the civic square.
 FVector Plaza(-6000,16500,35);Block(Plaza,FVector(8500,7800,40),Stone);
 for(int32 I=-3;I<=3;I++)for(int32 J=-3;J<=3;J++)Block(Plaza+FVector(I*1000,J*900,22),FVector(950,850,4),(I+J)%2?Concrete:Stone,false);
 Block(Plaza+FVector(0,0,180),FVector(450,450,300),Charcoal);Block(Plaza+FVector(0,0,420),FVector(110,160,220),Steel);Block(Plaza+FVector(0,0,570),FVector(110,110,90),Steel);
 FVector Church(-6000,20200,0);Block(Church+FVector(0,0,1000),FVector(3400,1300,2000),Cream);
 for(int32 S:{-1,1}){Block(Church+FVector(S*1250,0,1450),FVector(600,1300,2900),Ochre);for(int32 L=0;L<4;L++)Block(Church+FVector(S*1250,0,2950+L*100),FVector(650-L*140,650-L*140,120),Charcoal);Block(Church+FVector(S*1250,-670,2500),FVector(240,30,400),Charcoal,false);}
 for(int32 I=-2;I<=2;I++){Block(Church+FVector(I*520,-690,950),FVector(140,150,1900),White);Block(Church+FVector(I*520,-700,320),FVector(260,30,600),Trunk,false);}
 for(int32 L=0;L<5;L++)Block(Church+FVector(0,-710,2050+L*110),FVector(2100-L*400,160,120),Cream,false);
 Building(-10200,16500,1600,6000,3,0,R);Building(-1500,16500,1400,6000,3,0,R);
 Label(TEXT("PLAZA DE BOLIVAR"),FVector(-6000,15100,240),145);
 Label(TEXT("LA CANDELARIA"),FVector(-3500,19300,2400),190);
 // Colpatria's stepped crown is visible across the city.
 FVector Col(3700,7000,0);Block(Col+FVector(0,0,6100),FVector(1700,1700,12200),Concrete);
 for(int32 F=0;F<40;F++)for(int32 S:{-1,1}){Block(Col+FVector(S*860,0,F*300+120),FVector(16,1550,160),Glass,false);Block(Col+FVector(0,S*860,F*300+120),FVector(1550,16,160),Glass,false);}
 for(int32 L=0;L<4;L++)Block(Col+FVector(0,0,12280+L*160),FVector(1750-L*240,1750-L*240,160),White);
 Label(TEXT("COLPATRIA"),Col+FVector(0,-880,12500),170);
 // Parque 93, Usaquen colonial square and the Chapinero brick church.
 for(FVector Park:{FVector(18000,16500,20),FVector(30000,16500,20),FVector(6000,-5500,20)}){
  Block(Park,FVector(8500,7400,20),Grass);Block(Park+FVector(0,0,20),FVector(700,7400,10),Concrete);Block(Park+FVector(0,0,21),FVector(8500,700,10),Concrete);
  for(int32 I=0;I<24;I++){FVector P=Park+FVector(R.FRandRange(-3600,3600),R.FRandRange(-3000,3000),20);if(FMath::Abs(P.X-Park.X)>600&&FMath::Abs(P.Y-Park.Y)>600)Tree(P,R);}
  Block(Park+FVector(1200,1200,80),FVector(1100,1100,120),Stone);Block(Park+FVector(1200,1200,143),FVector(930,930,8),Teal,false);
 }
 Label(TEXT("PARQUE 93"),FVector(18000,14500,250),180);Label(TEXT("USAQUEN"),FVector(30000,14500,250),210);
 Building(30000,19700,2800,1500,3,0,R);Block(FVector(28600,19700,800),FVector(500,900,1600),Cream);Block(FVector(28600,19700,1700),FVector(80,80,350),Charcoal);
 FVector Lourdes(15000,5500,0);Block(Lourdes+FVector(0,0,1300),FVector(2100,2600,2600),Brick);
 for(int32 S:{-1,1}){Block(Lourdes+FVector(S*850,-900,1800),FVector(480,600,3600),Brick);for(int32 L=0;L<6;L++)Block(Lourdes+FVector(S*850,-900,3650+L*110),FVector(500-L*80,500-L*80,120),Charcoal);}
 Label(TEXT("CHAPINERO / LOURDES"),Lourdes+FVector(0,-1450,200),140);
 // Monserrate's sanctuary and switchback footpath on the eastern ridge.
 FVector Mon(0,31000,6900);Block(Mon-FVector(0,0,900),FVector(4200,4200,1800),Earth);Block(Mon,FVector(3600,3300,80),Stone);
 Block(Mon+FVector(0,0,650),FVector(1800,900,1300),White);Block(Mon+FVector(800,0,950),FVector(420,650,1900),White);for(int32 L=0;L<4;L++)Block(Mon+FVector(800,0,1950+L*100),FVector(500-L*110,500-L*110,110),Roof);
 Block(Mon+FVector(800,0,2390),FVector(40,40,230),Charcoal);Block(Mon+FVector(800,0,2430),FVector(160,40,35),Charcoal);
 Label(TEXT("MONSERRATE"),Mon+FVector(0,-1300,200),200);
 Label(TEXT("RESTREPO / SUR"),FVector(-29000,4500,300),220);
 Label(TEXT("CIUDAD BOLIVAR"),FVector(-39000,-25900,2200),200);
 // Caracas trunk line: platform, roof, translucent screen and red portal signs.
 for(float X:{-27000.f,-7000.f,17000.f,32000.f}){
  Block(FVector(X,0,55),FVector(3000,390,110),Concrete);
  for(int32 S:{-1,1})Block(FVector(X,S*160,210),FVector(2750,18,250),Glass,false);
  for(int32 I=-1;I<=1;I++)Block(FVector(X+I*1100,0,270),FVector(50,50,480),Steel);
  Block(FVector(X,0,515),FVector(3300,600,90),Charcoal);Block(FVector(X-1200,0,620),FVector(400,80,150),Red,false);
  Label(TEXT("TRANSMILENIO"),FVector(X,-315,525),85,FRotator(0,-90,0));
 }
 ParkedBikes={FVector(-6200,14100,60),FVector(18000,15000,30),FVector(-28000,1600,30),FVector(30200,15000,30)};
 for(FVector P:ParkedBikes){
  auto* A=GetWorld()->SpawnActor<AStaticMeshActor>();A->SetMobility(EComponentMobility::Movable);A->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/World/SM_Bicycle.SM_Bicycle")));A->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);A->SetActorLocation(P);BikeActors.Add(A);
 }
}

void ABogotaCity::BeginPlay(){
 Super::BeginPlay();if(StaticVoxelCount==0)BuildCity();if(MapFootprints.IsEmpty())BuildMapMetadata();StaticVoxelCount=0;for(int32 I=0;I<Solid.Num();I++)StaticVoxelCount+=Solid[I]->GetInstanceCount()+Detail[I]->GetInstanceCount();for(int32 I=0;I<Solid.Num();I++)Solid[I]->SetVisibility(true);for(int32 I=0;I<Detail.Num();I++)Detail[I]->SetVisibility(true);UE_LOG(LogTemp,Display,TEXT("BOGOTA_RENDER city=%s solid0=%d solid0vis=%d solid0mesh=%s mat=%s loc=%s"),*GetActorLocation().ToString(),Solid.Num()?Solid[0]->GetInstanceCount():0,Solid.Num()&&Solid[0]->IsVisible()?1:0,Solid.Num()?*GetNameSafe(Solid[0]->GetStaticMesh()):TEXT("None"),Solid.Num()?*GetNameSafe(Solid[0]->GetMaterial(0)):TEXT("None"),*GetActorLocation().ToString());BuildTraffic();
 for(int32 I=0;I<3;I++){
  auto* S=NewObject<UInstancedStaticMeshComponent>(this);S->SetupAttachment(RootComponent);S->SetMobility(EComponentMobility::Movable);S->SetStaticMesh(Cube);S->SetCollisionEnabled(ECollisionEnabled::NoCollision);S->CastShadow=false;
  auto* M=UMaterialInstanceDynamic::Create(Palette[I==0?Red:I==1?Yellow:Green],this);M->SetScalarParameterValue(TEXT("GlowStrength"),3);S->SetMaterial(0,M);S->RegisterComponent();
  for(auto T:SignalTransforms){T.AddToTranslation(FVector(0,0,(1-I)*80));S->AddInstance(T);}SignalLights.Add(S);
 }
 UpdateSignals();
 Sun=GetWorld()->SpawnActor<ADirectionalLight>();Sun->SetMobility(EComponentMobility::Movable);auto* SunLight=Cast<UDirectionalLightComponent>(Sun->GetLightComponent());SunLight->DynamicShadowDistanceMovableLight=16000;SunLight->DynamicShadowCascades=4;SunLight->ShadowBias=.3f;SunLight->ShadowSharpen=.25f;SunLight->LightSourceAngle=2.f;
 Ambient=GetWorld()->SpawnActor<ASkyLight>();Ambient->GetLightComponent()->SetMobility(EComponentMobility::Movable);Ambient->GetLightComponent()->SkyDistanceThreshold=50000.f;Ambient->GetLightComponent()->bLowerHemisphereIsBlack=false;Ambient->GetLightComponent()->SetIntensity(2.5f);Ambient->GetLightComponent()->SetLightColor(FLinearColor(.72f,.8f,1.f));
 Fog=GetWorld()->SpawnActor<AExponentialHeightFog>();Fog->SetActorLocation(FVector(0,0,-200));Fog->GetComponent()->SetFogDensity(.00012f);Fog->GetComponent()->SetFogHeightFalloff(.25f);Fog->GetComponent()->SetVolumetricFog(false);
 auto* Sky=GetWorld()->SpawnActor<AStaticMeshActor>();Sky->SetActorEnableCollision(false);Sky->SetMobility(EComponentMobility::Movable);Sky->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere.Sphere")));Sky->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("NoCollision"));Sky->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);Sky->GetStaticMeshComponent()->CastShadow=false;Sky->SetActorScale3D(FVector(2200));
 SkyMaterial=UMaterialInstanceDynamic::Create(LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/World/M_Sky.M_Sky")),this);Sky->GetStaticMeshComponent()->SetMaterial(0,SkyMaterial);
 GlowMaterial=UMaterialInstanceDynamic::Create(Palette[Glow],this);Detail[Glow]->SetMaterial(0,GlowMaterial);Moving[Glow]->SetMaterial(0,GlowMaterial);
 UpdateLighting();Ambient->GetLightComponent()->RecaptureSky();
}
void ABogotaCity::BakeCity(){if(StaticVoxelCount==0)BuildCity();if(MapFootprints.IsEmpty())BuildMapMetadata();}
void ABogotaCity::BuildMapMetadata(){
 MapFootprints.Empty();
 // Read the walls actually stored in the baked map, preserving all authored geometry.
 for(int32 PaletteIndex:{Concrete,Brick,Ochre,Cream})if(Solid.IsValidIndex(PaletteIndex))for(int32 I=0;I<Solid[PaletteIndex]->GetInstanceCount();I++){FTransform T;if(!Solid[PaletteIndex]->GetInstanceTransform(I,T,true))continue;FVector Size=T.GetScale3D().GetAbs()*100,At=T.GetLocation();if(Size.X<1000||Size.Y<1000||Size.Z<250||At.Z<100)continue;FMapFootprint F;F.Center=FVector(At.X,At.Y,0);F.Extent=FVector2D(Size.X*.5,Size.Y*.5);MapFootprints.Add(F);}
}

FString ABogotaCity::DistrictAt(FVector P) const {if(P.Y>27000)return TEXT("Cerros orientales");if(P.X<-22000)return P.Y<-21000?TEXT("Ciudad Bolivar"):TEXT("Sur / Restrepo");if(P.X<1000)return P.Y>11000?TEXT("Centro / La Candelaria"):TEXT("Centro");if(P.X<24000)return TEXT("Chapinero / Parque 93");return TEXT("Norte / Usaquen");}
void ABogotaCity::AdvanceTime(){float Old=CycleSeconds;CycleSeconds=FMath::Fmod(CycleSeconds+360,1440);if(CycleSeconds<Old)GameDay++;UpdateLighting();UpdateTrafficNight();}
void ABogotaCity::UpdateLighting(){
 // 16 real minutes from 06:00 to 18:00, 8 minutes from 18:00 back to 06:00.
 float Phase=FMath::Fmod(CycleSeconds,1440.f);Hour=Phase<960?6+Phase/80:FMath::Fmod(18+(Phase-960)/40,24.f);
 // The sun completes a full orbit, including below the horizon at night.
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

}
void ABogotaCity::SetDetail(int32 L){DetailLevel=L;for(auto& D:Detail)D->SetCullDistances(L==0?15000:26000,L==0?22000:36000);Cast<UDirectionalLightComponent>(Sun->GetLightComponent())->DynamicShadowDistanceMovableLight=L==0?7000:16000;}
void ABogotaCity::UpdateSignals(){
 float T=FMath::Fmod(Elapsed,32.f);
 for(int32 J=0;J<SignalTransforms.Num();J++){
  bool NS=SignalNorthSouth[J],GreenOn=NS?TrafficNSGreen():TrafficEWGreen(),Amber=NS?(T>=13&&T<16):(T>=29);
  int32 X=0,Y=0;FVector At=SignalTransforms[J].GetLocation();for(int32 I=1;I<NorthRoads.Num();I++)if(FMath::Abs(At.X-NorthRoads[I])<FMath::Abs(At.X-NorthRoads[X]))X=I;for(int32 I=1;I<EastRoads.Num();I++)if(FMath::Abs(At.Y-EastRoads[I])<FMath::Abs(At.Y-EastRoads[Y]))Y=I;if(PedestrianJunctions.Contains(X*100+Y)){GreenOn=false;Amber=false;}
  for(int32 I=0;I<SignalLights.Num();I++){FTransform Tr=SignalTransforms[J];Tr.AddToTranslation(FVector(0,0,(1-I)*80));bool On=I==2?GreenOn:I==1?Amber:(!GreenOn&&!Amber);if(!On)Tr.SetScale3D(FVector::ZeroVector);SignalLights[I]->UpdateInstanceTransform(J,Tr,false,false,true);}
 }
 for(auto& S:SignalLights)S->MarkRenderStateDirty();
}
void ABogotaCity::Tick(float Dt){
 Super::Tick(Dt);Elapsed+=Dt;
 if(FParse::Param(FCommandLine::Get(),TEXT("StoreCrowdVisualCheck"))&&Elapsed>2){
  static ACameraActor* StoreCamera=nullptr;static int32 Captured=0;int32 Shot=Elapsed<9?0:Elapsed<15?1:2;
  ADeliveryPoint* Shop=nullptr;for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)if(It->WalkingCustomers.Num()>0&&(Shot!=0||It->StoreKind==2)&&(Shot!=1||It->StoreKind==1)){Shop=*It;break;}
  if(Shop&&Shop->WalkingCustomers[0])if(auto* PC=GetWorld()->GetFirstPlayerController()){
   auto C=Shop->WalkingCustomers[0];FVector Target=C->GetComponentLocation()+FVector(0,0,95);
   if(APawn* Pawn=PC->GetPawn())Pawn->SetActorLocation(C->GetComponentLocation()+FVector(0,230,90));
   if(!StoreCamera)StoreCamera=GetWorld()->SpawnActor<ACameraActor>();FVector Eye=Target+FVector(380,-350,130);StoreCamera->SetActorLocationAndRotation(Eye,(Target-Eye).Rotation());StoreCamera->GetCameraComponent()->SetFieldOfView(65);PC->SetViewTarget(StoreCamera);
   if((Shot==0&&Elapsed>6&&Captured==0)||(Shot==1&&Elapsed>12&&Captured==1)||(Shot==2&&Elapsed>18&&Captured==2)){PC->ConsoleCommand(TEXT("HighResShot 1"));Captured++;}
  }
 }
 if(FParse::Param(FCommandLine::Get(),TEXT("CrowdVisualCheck"))&&!Walkers.IsEmpty()){
  static ACameraActor* Camera=nullptr;static int32 Captured=0;int32 Shot=Elapsed<9?0:Elapsed<15?1:2;const int32 Wanted=Shot==0?46:Shot==1?40:6;int32 Chosen=0;for(int32 I=0;I<Walkers.Num();I++)if(Walkers[I].ModelIndex==Wanted){Chosen=I;break;}auto& W=Walkers[Chosen];
  if(auto* PC=GetWorld()->GetFirstPlayerController()){
   if(!Camera)Camera=GetWorld()->SpawnActor<ACameraActor>();
   if(APawn* Pawn=PC->GetPawn())Pawn->SetActorLocation(W.Position+FVector(0,450,90));
   FVector Eye=W.Position+FRotator(0,W.Heading,0).RotateVector(FParse::Param(FCommandLine::Get(),TEXT("HeadVolumeVisualCheck"))?FVector(320,-300,330):FVector(400,-350,170));Camera->SetActorLocationAndRotation(Eye,(W.Position+FVector(0,0,85)-Eye).Rotation());Camera->GetCameraComponent()->SetFieldOfView(55);PC->SetViewTarget(Camera);
   if((Shot==0&&Elapsed>6&&Captured==0)||(Shot==1&&Elapsed>12&&Captured==1)||(Shot==2&&Elapsed>18&&Captured==2)){PC->ConsoleCommand(TEXT("HighResShot 1"));Captured++;}
  }
 }

 if(FParse::Param(FCommandLine::Get(),TEXT("CityRepairVisualCheck"))&&!Walkers.IsEmpty()){
  static ACameraActor* Camera=nullptr;static int32 Captured=0;
  static TArray<float> FrameTimes;static bool Reported=false;
  if(Elapsed>2)FrameTimes.Add(Dt);
  int32 Shot=FMath::Clamp(int32((Elapsed-3)/5),0,6);
  if(auto* PC=GetWorld()->GetFirstPlayerController()){
   if(!Camera)Camera=GetWorld()->SpawnActor<ACameraActor>();
   if(Shot<4){
    int32 Wanted=Shot<2?27:46,Chosen=0;for(int32 I=0;I<Walkers.Num();I++)if(Walkers[I].ModelIndex==Wanted&&Walkers[I].CrossSegments.IsEmpty()){Chosen=I;break;}auto& W=Walkers[Chosen];
    if(APawn* Pawn=PC->GetPawn())Pawn->SetActorLocation(W.Position+FVector(0,450,90));
    FVector Eye=W.Position+FRotator(0,W.Heading,0).RotateVector(FVector(190,Shot%2?35.f:-35.f,Shot%2?75.f:145.f));
    Camera->SetActorLocationAndRotation(Eye,(W.Position+FVector(0,0,135)-Eye).Rotation());Camera->GetCameraComponent()->SetFieldOfView(42);
   }else if(Shot==4){
    auto& W=Walkers[Walkers.Num()/2];if(APawn* Pawn=PC->GetPawn())Pawn->SetActorLocation(W.Position+FVector(0,350,90));
    FVector Eye=W.Position+FVector(1400,-1700,650);Camera->SetActorLocationAndRotation(Eye,(W.Position+FVector(0,0,70)-Eye).Rotation());Camera->GetCameraComponent()->SetFieldOfView(65);
   }else if(!ParkedCars.IsEmpty()){
    CycleSeconds=1300;const auto& P=ParkedCars[0];FVector Forward=FRotator(0,P.Heading,0).Vector();
    if(APawn* Pawn=PC->GetPawn())Pawn->SetActorLocation(P.Position+FVector(220,0,95));
    FVector Eye=P.Position+FVector(850,800,430);Camera->SetActorLocationAndRotation(Eye,(P.Position+Forward*430+FVector(0,0,50)-Eye).Rotation());Camera->GetCameraComponent()->SetFieldOfView(65);
   }
   PC->SetViewTarget(Camera);
   if(Elapsed>6+Captured*5&&Captured<7){PC->ConsoleCommand(TEXT("HighResShot 1"));Captured++;}
   if(Elapsed>40&&!Reported){Reported=true;float Sum=0;for(float T:FrameTimes)Sum+=T;FrameTimes.Sort();float P95=FrameTimes.IsEmpty()?0:FrameTimes[FMath::Min(FrameTimes.Num()-1,int32(FrameTimes.Num()*.95f))];UE_LOG(LogTemp,Display,TEXT("CITY_RENDER_PERFORMANCE {\"frames\":%d,\"average_fps\":%.2f,\"p95_frame_ms\":%.2f}"),FrameTimes.Num(),FrameTimes.Num()/FMath::Max(.001f,Sum),P95*1000);PC->ConsoleCommand(TEXT("quit"));}
  }
 }
 if(FParse::Param(FCommandLine::Get(),TEXT("SkyCycleVisualCheck"))){
  static ACameraActor* SkyCamera=nullptr;static int32 Captured=0;int32 Shot=FMath::Clamp(int32((Elapsed-2)/5),0,3);const float Phases[]={0,480,950,1200};CycleSeconds=Phases[Shot];
  if(auto* PC=GetWorld()->GetFirstPlayerController()){if(!SkyCamera)SkyCamera=GetWorld()->SpawnActor<ACameraActor>();SkyCamera->SetActorLocationAndRotation(FVector(-5500,14500,650),FRotator(22,Shot==3?130:-35,0));SkyCamera->GetCameraComponent()->SetFieldOfView(90);PC->SetViewTarget(SkyCamera);
   if(Elapsed>4+Captured*5&&Captured<4){PC->ConsoleCommand(TEXT("HighResShot 1280x720"));Captured++;}}
 }
 if(FParse::Param(FCommandLine::Get(),TEXT("NightVisualCheck")))CycleSeconds=1300;
 if(FParse::Param(FCommandLine::Get(),TEXT("TrafficVisualCheck"))&&!Vehicles.IsEmpty()){
  static ACameraActor* CheckCamera=nullptr;static int32 Captured=0;
  if(!CheckCamera)CheckCamera=GetWorld()->SpawnActor<ACameraActor>();
  const int32 Shot=Elapsed<8?0:Elapsed<11?1:Elapsed<16?2:3;const auto& A=Vehicles[Shot==0?0:Shot==1?4:Shot==2?34:37];FVector Eye=A.Position+FRotator(0,A.Heading,0).RotateVector(A.Articulated?FVector(1900,-700,500):FVector(620,-610,245));
  if(FParse::Param(FCommandLine::Get(),TEXT("ScaleVisualCheck")))if(APawn* Player=GetWorld()->GetFirstPlayerController()->GetPawn()){Player->SetActorLocationAndRotation(A.Position+FRotator(0,A.Heading,0).RotateVector(FVector(0,-250,90)),FRotator(0,A.Heading,0));Eye=A.Position+FRotator(0,A.Heading,0).RotateVector(A.Articulated?FVector(1900,-700,500):FVector(700,-900,280));}
  if(FParse::Param(FCommandLine::Get(),TEXT("ScaleVisualCheck"))){CheckCamera->GetCameraComponent()->SetProjectionMode(ECameraProjectionMode::Orthographic);CheckCamera->GetCameraComponent()->SetOrthoWidth(A.Articulated?2200.f:850.f);Eye=A.Position+FRotator(0,A.Heading,0).RotateVector(FVector(0,-700,A.Articulated?185:120));}
  if(FParse::Param(FCommandLine::Get(),TEXT("TrafficScaleStudio"))){
   const FVector Stage(0,-45000,0);static AActor* ModelActor=nullptr;static UPoseableMeshComponent* Model=nullptr;static USkeletalMesh* LastModel=nullptr;static AActor* PersonActor=nullptr;
   if(!ModelActor){ModelActor=GetWorld()->SpawnActor<AActor>();Model=NewObject<UPoseableMeshComponent>(ModelActor);ModelActor->SetRootComponent(Model);ModelActor->AddInstanceComponent(Model);Model->SetCollisionEnabled(ECollisionEnabled::NoCollision);Model->RegisterComponent();
    auto* Floor=GetWorld()->SpawnActor<AStaticMeshActor>();Floor->SetMobility(EComponentMobility::Movable);Floor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Floor->GetStaticMeshComponent()->SetStaticMesh(Cube);Floor->GetStaticMeshComponent()->SetMaterial(0,Palette[Concrete]);Floor->SetActorLocation(Stage-FVector(0,0,10));Floor->SetActorScale3D(FVector(36,24,.2));
    PersonActor=GetWorld()->SpawnActor<AActor>();auto* Person=NewObject<USkeletalMeshComponent>(PersonActor);PersonActor->SetRootComponent(Person);PersonActor->AddInstanceComponent(Person);Person->SetSkeletalMeshAsset(LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/VoxelExplorer/SK_VoxelExplorer.SK_VoxelExplorer")));Person->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB.M_VoxelExplorerRuntimeRGB")));Person->SetCollisionEnabled(ECollisionEnabled::NoCollision);Person->SetRelativeRotation(FRotator(0,-90,0));Person->RegisterComponent();Person->PlayAnimation(LoadObject<UAnimationAsset>(nullptr,TEXT("/Game/VoxelExplorer/AN_Idle.AN_Idle")),true);
    auto* Back=GetWorld()->SpawnActor<AStaticMeshActor>();Back->SetMobility(EComponentMobility::Movable);Back->GetStaticMeshComponent()->SetStaticMesh(Cube);Back->GetStaticMeshComponent()->SetMaterial(0,Palette[Cream]);Back->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);Back->GetStaticMeshComponent()->CastShadow=false;Back->SetActorLocation(Stage+FVector(0,500,350));Back->SetActorScale3D(FVector(36,.1,7));
    auto* LampActor=GetWorld()->SpawnActor<AActor>();auto* Lamp=NewObject<UPointLightComponent>(LampActor);LampActor->SetRootComponent(Lamp);LampActor->AddInstanceComponent(Lamp);Lamp->SetMobility(EComponentMobility::Movable);Lamp->SetIntensityUnits(ELightUnits::Lumens);Lamp->SetIntensity(50000);Lamp->SetAttenuationRadius(3000);Lamp->SetCastShadows(false);Lamp->RegisterComponent();LampActor->SetActorLocation(Stage+FVector(0,-900,700));}

   auto* Mesh=Cast<USkeletalMesh>(A.Visual->GetSkinnedAsset());if(Mesh!=LastModel){Model->SetSkinnedAssetAndUpdate(Mesh);Model->SetMaterial(0,TrafficMaterial);LastModel=Mesh;}
   ModelActor->SetActorLocationAndRotation(Stage,FRotator::ZeroRotator);ModelActor->SetActorScale3D(FVector::OneVector);
   PersonActor->SetActorLocationAndRotation(Stage+FVector(A.Articulated?1050:350,0,0),FRotator::ZeroRotator);
   Eye=Stage+FVector(0,-1000,180);CheckCamera->SetActorLocationAndRotation(Eye,(Stage+FVector(0,0,100)-Eye).Rotation());CheckCamera->GetCameraComponent()->SetProjectionMode(ECameraProjectionMode::Orthographic);CheckCamera->GetCameraComponent()->SetOrthoWidth(A.Articulated?2400.f:1000.f);
  }else CheckCamera->SetActorLocationAndRotation(Eye,(A.Position+FVector(0,0,75)-Eye).Rotation());
  if(auto* PC=GetWorld()->GetFirstPlayerController()){PC->SetViewTarget(CheckCamera);if((Captured==0&&Elapsed>6)||(Captured==1&&Elapsed>10)||(Captured==2&&Elapsed>14)||(Captured==3&&Elapsed>19)){PC->ConsoleCommand(TEXT("HighResShot 1280x720"));Captured++;}}
 }
float OldCycle=CycleSeconds;CycleSeconds=FMath::Fmod(CycleSeconds+Dt*24/FMath::Max(1.f,CycleMinutes),1440.f);if(CycleSeconds<OldCycle)GameDay++;LightAccumulator+=Dt;SimAccumulator+=Dt;PedAccumulator+=Dt;
 if(LightAccumulator>.25f){UpdateLighting();UpdateSignals();UpdateTrafficNight();LightAccumulator=0;}
 // Preserve elapsed time and render between fixed simulation states.
 constexpr float TrafficStep=1.f/30;int32 TrafficSteps=0;
 while(SimAccumulator>=TrafficStep&&TrafficSteps++<15){SimulateTraffic(TrafficStep);SimAccumulator-=TrafficStep;}
 UpdateTrafficVisuals(FMath::Clamp(SimAccumulator/TrafficStep,0.f,1.f));
 if(PedAccumulator>=.066f){SimulateWalkers(FMath::Min(PedAccumulator,.2f));PedAccumulator=0;}
}



