from pathlib import Path
root=Path(__file__).resolve().parents[1];src=root/'outputs/BogotaVoxel/Source/BogotaVoxel'
p=src/'BogotaGame.h';s=p.read_text();s=s.replace('int32 Segment=0;\n float Heading=0;\n TWeakObjectPtr<AActor> Visual;','int32 Segment=0,ModelIndex=0;\n float Heading=0,Speed=112,Scale=1,Travelled=0;\n TWeakObjectPtr<AActor> Visual;');s=s.replace('FString ValidateG66();','FString ValidateG66();\n UFUNCTION(CallInEditor,BlueprintCallable,Category="Crowd") FString ValidateCrowd(float Seconds=180);');p.write_text(s)
p=src/'BogotaTraffic.cpp';s=p.read_text().replace('#include "TrafficModelCatalog.inl"','#include "TrafficModelCatalog.inl"\n#include "CrowdCatalog.inl"');s=s.replace('Vehicles.Empty();Walkers.Empty();','Vehicles.Empty();for(auto& W:Walkers)if(W.Visual.IsValid())W.Visual->Destroy();Walkers.Empty();')
a=s.index(' for(int32 I=0;I<42;I++){');b=s.index('\n}\nvoid ABogotaCity::SimulateTraffic',a)
s=s[:a]+''' for(int32 Block=0;Block<24;Block++)for(int32 Lane=0;Lane<6;Lane++){
  FWalker W;int32 IX=Block%6,IY=Block/6;float Offset=Lane%2?36:-36;
  float X0=NorthRoads[IX]+1100+Offset,X1=NorthRoads[IX+1]-1100-Offset;
  float Y0=EastRoads[IY]+(IY==2?1530:1130)+Offset,Y1=EastRoads[IY+1]-(IY==1?1530:1130)-Offset;
  W.Route={FVector(X0,Y0,26),FVector(X1,Y0,26),FVector(X1,Y1,26),FVector(X0,Y1,26)};
  if(Lane%2)Algo::Reverse(W.Route);W.ModelIndex=(Block+Lane*5)%24;const auto& Spec=CrowdModels[W.ModelIndex];W.Scale=Spec.Scale;W.Speed=Spec.Speed;
  float Distance=PathLength(W.Route)*(Lane+.35f)/6;
  for(int32 Segment=0;Segment<4;Segment++){float Length=FVector::Dist2D(W.Route[Segment],W.Route[(Segment+1)%4]);if(Distance<Length){W.Segment=Segment;W.Position=FMath::Lerp(W.Route[Segment],W.Route[(Segment+1)%4],Distance/Length);break;}Distance-=Length;}
  W.Heading=(W.Route[(W.Segment+1)%4]-W.Position).Rotation().Yaw;Walkers.Add(W);
 }'''+s[b:]
a=s.index('void ABogotaCity::SimulateWalkers(');b=s.index('void ABogotaCity::UpdateTrafficNight()',a)
s=s[:a]+'''void ABogotaCity::SimulateWalkers(float Dt){
 auto* Player=UGameplayStatics::GetPlayerPawn(this,0);FVector PP=Player?Player->GetActorLocation():FVector::ZeroVector;
 TArray<int32> Nearest;for(int32 I=0;I<Walkers.Num();I++)if(FVector::DistSquared2D(PP,Walkers[I].Position)<FMath::Square(DetailLevel==0?6500.f:10000.f))Nearest.Add(I);
 Nearest.Sort([&](int32 A,int32 B){return FVector::DistSquared2D(PP,Walkers[A].Position)<FVector::DistSquared2D(PP,Walkers[B].Position);});
 for(int32 I=0;I<Walkers.Num();I++){
  auto& W=Walkers[I];FVector Target=W.Route[(W.Segment+1)%4],Dir=(Target-W.Position).GetSafeNormal2D();float Facing=Dir.Rotation().Yaw;
  W.Heading=FMath::FixedTurn(W.Heading,Facing,Dt*180);float Move=FMath::Abs(FMath::FindDeltaAngleDegrees(W.Heading,Facing))<8?W.Speed*Dt:0;
  if(Player&&FVector::DistSquared2D(PP,W.Position)<125*125)Move=0;
  for(int32 J=0;J<Walkers.Num();J++)if(J!=I){FVector D=Walkers[J].Position-W.Position;float Ahead=FVector::DotProduct(D,Dir);if(Ahead>0&&Ahead<110&&FMath::Abs(FVector::CrossProduct(D,Dir).Z)<32)Move=FMath::Min(Move,FMath::Max(0.f,Ahead-80));}
  float Distance=FVector::Dist2D(Target,W.Position);Move=FMath::Min(Move,Distance);W.Position+=Dir*Move;W.Travelled+=Move;
  if(Distance<Move+1){W.Position=Target;W.Segment=(W.Segment+1)%4;}
  FHitResult Ground;FCollisionQueryParams Query;Query.AddIgnoredActor(this);if(W.Visual.IsValid())Query.AddIgnoredActor(W.Visual.Get());
  if(GetWorld()->LineTraceSingleByChannel(Ground,W.Position+FVector(0,0,100),W.Position-FVector(0,0,100),ECC_Visibility,Query)&&Ground.ImpactNormal.Z>.7f)W.Position.Z=Ground.ImpactPoint.Z;
  int32 Rank=Nearest.Find(I);bool Near=Rank!=INDEX_NONE&&Rank<24;
  if(Near){
   if(!W.Visual.IsValid()){
    const FString Name=CrowdModels[W.ModelIndex].Name;auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Crowd/SK_%s.SK_%s"),*Name,*Name));
    if(!Mesh)continue;auto* A=GetWorld()->SpawnActor<AActor>();auto* S=NewObject<USkeletalMeshComponent>(A);A->SetRootComponent(S);A->AddInstanceComponent(S);S->SetSkeletalMeshAsset(Mesh);S->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Crowd/M_CrowdPixel.M_CrowdPixel")));S->SetCollisionEnabled(ECollisionEnabled::NoCollision);S->bEnableUpdateRateOptimizations=true;S->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;S->RegisterComponent();S->PlayAnimation(LoadObject<UAnimationAsset>(nullptr,TEXT("/Game/VoxelExplorer/AN_MixamoWalk.AN_MixamoWalk")),true);S->SetPosition((I%17)*.07f,false);A->SetActorScale3D(FVector(W.Scale));W.Visual=A;
   }
   W.Visual->SetActorHiddenInGame(false);W.Visual->SetActorLocationAndRotation(W.Position,FRotator(0,W.Heading+180,0));if(auto* S=Cast<USkeletalMeshComponent>(W.Visual->GetRootComponent()))S->SetPlayRate(Move>0?W.Speed/(140.f*W.Scale):0);
  }else if(W.Visual.IsValid())W.Visual->SetActorHiddenInGame(true);
 }
}
FString ABogotaCity::ValidateCrowd(float Seconds){
 if(Walkers.IsEmpty())BuildTraffic();int32 Missing=0;TSet<int32> Models;
 for(const auto& W:Walkers)Models.Add(W.ModelIndex);
 for(int32 I=0;I<24;I++){FString Name=CrowdModels[I].Name;auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Crowd/SK_%s.SK_%s"),*Name,*Name));if(!Mesh||!Mesh->GetSkeleton()||!Mesh->GetMaterial(0))Missing++;}
 TArray<float> Start;for(const auto& W:Walkers)Start.Add(W.Travelled);
 for(int32 Step=0;Step<FMath::CeilToInt(Seconds*15);Step++)SimulateWalkers(1.f/15);
 float Minimum=1e9;int32 Invalid=0;for(int32 I=0;I<Walkers.Num();I++){Minimum=FMath::Min(Minimum,Walkers[I].Travelled-Start[I]);if(Walkers[I].Position.ContainsNaN())Invalid++;}
 return FString::Printf(TEXT("{\\"pedestrians\\":%d,\\"variants\\":%d,\\"missing_assets\\":%d,\\"invalid_positions\\":%d,\\"minimum_travel_cm\\":%.1f}"),Walkers.Num(),Models.Num(),Missing,Invalid,Minimum);
}

'''+s[b:];p.write_text(s)
p=src/'BogotaPlayer.cpp';p.write_text(p.read_text().replace('City->Walkers.Num()==42','City->Walkers.Num()==144'))
p=root/'outputs/BogotaVoxel/Config/DefaultGame.ini';s=p.read_text();s+='\n+DirectoriesToAlwaysCook=(Path="/Game/Crowd")\n';p.write_text(s)
