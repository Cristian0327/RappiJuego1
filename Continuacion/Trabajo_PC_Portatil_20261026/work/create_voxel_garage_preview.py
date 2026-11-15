from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryVehicleArt.cpp');s=p.read_text(encoding='utf-8')
s=s.replace('FVector(180,-280,155)','FVector(260,-430,250)').replace('Capture->OrthoWidth=220','Capture->OrthoWidth=400')
s=s.replace('Capture->PostProcessSettings.AutoExposureBias=8','Capture->PostProcessSettings.AutoExposureBias=7')
needle=' auto* Light=CreateDefaultSubobject<UPointLightComponent>(TEXT("WorkshopLight"));'
garage=r''' // The preview is an actual voxel workshop, visible only to its dedicated camera.
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
 static ConstructorHelpers::FObjectFinder<UMaterialInterface> Concrete(TEXT("/Game/World/M_Concrete.M_Concrete")),Steel(TEXT("/Game/World/M_Steel.M_Steel")),Teal(TEXT("/Game/World/M_Teal.M_Teal")),Dark(TEXT("/Game/World/M_Charcoal.M_Charcoal")),Orange(TEXT("/Game/World/M_Orange.M_Orange")),White(TEXT("/Game/World/M_White.M_White")),Glow(TEXT("/Game/World/M_Glow.M_Glow"));
 int32 BlockIndex=0;
 auto Block=[&](FVector P,FVector Size,UMaterialInterface* Material){auto* C=CreateDefaultSubobject<UStaticMeshComponent>(FName(*FString::Printf(TEXT("GarageBlock%03d"),BlockIndex++)));C->SetupAttachment(RootComponent);C->SetStaticMesh(Cube.Object);C->SetRelativeLocation(P);C->SetRelativeScale3D(Size/100);C->SetMaterial(0,Material);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetVisibleInSceneCaptureOnly(true);C->SetCastShadow(false);};
 Block(FVector(0,0,-14),FVector(560,480,20),Dark.Object);
 for(int32 X=0;X<8;X++)for(int32 Y=0;Y<6;Y++)Block(FVector(-245+X*70,-195+Y*70,-2),FVector(68,68,6),(X+Y)%2?Concrete.Object:Steel.Object);
 for(int32 X=0;X<8;X++)for(int32 Z=0;Z<4;Z++)Block(FVector(-245+X*70,205,22+Z*44),FVector(68,16,42),Z==1?Teal.Object:Concrete.Object);
 Block(FVector(-285,0,84),FVector(16,420,180),Concrete.Object);
 Block(FVector(-276,0,66),FVector(4,420,42),Teal.Object);
 // Raised service pad and square safety markings leave breathing room around the model.
 Block(FVector(0,0,0),FVector(240,120,4),Dark.Object);
 for(int32 X=0;X<6;X++)Block(FVector(-110+X*44,-70,1),FVector(22,12,4),Orange.Object);
 Block(FVector(-185,115,64),FVector(116,60,12),Steel.Object);
 for(int32 X=0;X<2;X++)for(int32 Y=0;Y<2;Y++)Block(FVector(-232+X*94,92+Y*46,30),FVector(10,10,60),Dark.Object);
 Block(FVector(-185,191,111),FVector(116,10,68),Dark.Object);
 for(int32 X=0;X<4;X++){Block(FVector(-224+X*26,182,113),FVector(6,6,34),White.Object);Block(FVector(-224+X*26,182,131),FVector(16,6,8),Steel.Object);}
 Block(FVector(178,125,25),FVector(52,52,48),Orange.Object);Block(FVector(178,125,52),FVector(56,56,6),Dark.Object);Block(FVector(183,125,75),FVector(44,44,40),Teal.Object);
 Block(FVector(10,194,165),FVector(126,20,12),Dark.Object);Block(FVector(10,181,162),FVector(112,8,6),Glow.Object);
 Block(FVector(10,193,112),FVector(102,8,52),Teal.Object);
 for(int32 I=0;I<3;I++)Block(FVector(-20+I*30,186,112),FVector(12,6,28),White.Object);
'''
assert needle in s;s=s.replace(needle,garage+needle)
s=s.replace('Target->InitAutoFormat(640,360)','Target->InitAutoFormat(640,448)')
p.write_text(s,encoding='utf-8')
