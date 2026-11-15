from pathlib import Path
r=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1'); h=r/'Source/BogotaVoxel/BogotaGame.h'
s=h.read_text();s=s.replace(' UFUNCTION(CallInEditor,BlueprintCallable,Category="Crowd") FString ValidateStreetFlow();',' UFUNCTION(CallInEditor,BlueprintCallable,Category="Crowd") FString ValidateStreetFlow();\n UFUNCTION(CallInEditor,BlueprintCallable,Category="World|QA") FString ValidateMapRoutes(float Seconds=600);\n UFUNCTION(BlueprintPure,BlueprintImplementableEvent,Category="World|Weather") float RainAmountFor(float Seconds,int32 Day) const;\n UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="World|Weather",meta=(ClampMin="180")) float RainIntervalSeconds=480;\n UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="World|Weather",meta=(ClampMin="30")) float RainDurationSeconds=120;\n UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="World|Weather") float RainIntensity=0;')
s=s.replace(' void UpdateLighting();',' bool WalkerStepClear(FVector From,FVector To) const;\n float WalkerGroundHeight(FVector At) const;\n void UpdateWeather(float Dt);\n UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> RainMesh;\n TArray<FVector> RainDrops;\n TArray<float> RainFloors;\n FVector RainOrigin=FVector(1e9);\n FRandomStream RainRandom{271828};\n void UpdateLighting();');h.write_text(s)
p=r/'Source/BogotaVoxel/BogotaTraffic.cpp';s=p.read_text();s=s.replace('#include "Algo/Reverse.h"','#include "Algo/Reverse.h"\n#include "Json.h"\n#include "Engine/StaticMeshActor.h"\n#include "Components/StaticMeshComponent.h"')
start=s.index('  if(Nearest.Contains(I)&&(W.Activity==EPedActivity::Walking')
end=s.index('\n  int32 Rank=',start)
s=s[:start]+'''  // Anchor outdoor pedestrians to the street layer, never to their previous height.
  // Nearby roofs, other characters and cars cannot become a new walking floor.
  if(!W.TransitPassenger&&!PedHidden(W)&&W.Activity!=EPedActivity::EnteringCar&&W.Activity!=EPedActivity::LeavingCar)W.Position.Z=WalkerGroundHeight(W.Position);
'''+s[end:]
s=s.replace('    if(!Safe)Score-=100;','    if(Safe&&Score>BestScore&&!WalkerStepClear(W.Position,W.Position+Candidate*FMath::Max(Move,W.Speed*.8f)))Safe=false;\n    if(!Safe)Score-=100;')
s=s.replace('   float Distance=FVector::Dist2D(SteeringTarget,W.Position);Move=FMath::Min(Move,Distance);W.Position+=Dir*Move;W.Travelled+=Move;','   float Distance=FVector::Dist2D(SteeringTarget,W.Position);Move=FMath::Min(Move,Distance);\n   if(Move>0&&!WalkerStepClear(W.Position,W.Position+Dir*Move))Move=0;\n   W.Position+=Dir*Move;W.Travelled+=Move;')
# Only recover actual penetrations, including invalid spawns; use nearby free street space.
s=s.replace('  auto& W=Walkers[I];const FVector PreviousPosition=W.Position;float Move=0;','''  auto& W=Walkers[I];
  if(!W.TransitPassenger&&!PedHidden(W)&&W.Activity==EPedActivity::Walking){
   W.Position.Z=WalkerGroundHeight(W.Position);
   if(!WalkerStepClear(W.Position,W.Position)){
    bool Found=false;for(float Radius:{60.f,120.f,180.f,240.f,320.f,450.f,650.f}){for(int32 Direction=0;Direction<16;Direction++){
     FVector Candidate=W.Position+FVector(Radius,0,0).RotateAngleAxis(Direction*22.5f,FVector::UpVector);Candidate.Z=WalkerGroundHeight(Candidate);
     if(WalkerStepClear(Candidate,Candidate)){W.Position=Candidate;Found=true;break;}}
     if(Found)break;
    }
   }
  }
  const FVector PreviousPosition=W.Position;float Move=0;''')
# Sweep helper ignores moving actors via object type; city solids and authored storefronts are WorldStatic.
s+='''
bool ABogotaCity::WalkerStepClear(FVector From,FVector To) const{
 FHitResult Hit;FCollisionQueryParams Query(SCENE_QUERY_STAT(PedestrianWalls),false);
 From.Z=WalkerGroundHeight(From);To.Z=WalkerGroundHeight(To);
 return !GetWorld()->SweepSingleByObjectType(Hit,From+FVector(0,0,100),To+FVector(0,0,100),FQuat::Identity,FCollisionObjectQueryParams(ECC_WorldStatic),FCollisionShape::MakeCapsule(34,75),Query);
}
float ABogotaCity::WalkerGroundHeight(FVector At) const{
 // All outdoor street routes are on the ground layer. Query a fixed 80 cm band;
 // never trace from the previous foot height (which used to climb walls/roofs).
 FHitResult Hit;FCollisionQueryParams Query(SCENE_QUERY_STAT(PedestrianFloor),false);
 if(GetWorld()->LineTraceSingleByObjectType(Hit,FVector(At.X,At.Y,80),FVector(At.X,At.Y,-20),FCollisionObjectQueryParams(ECC_WorldStatic),Query)&&Hit.ImpactNormal.Z>.7f&&Hit.ImpactPoint.Z<=60)return Hit.ImpactPoint.Z;
 return 26.f;
}
FString ABogotaCity::ValidateMapRoutes(float Seconds){
 if(Vehicles.IsEmpty())BuildTraffic();
 auto Report=MakeShared<FJsonObject>();Report->SetNumberField(TEXT("seconds"),Seconds);
 int32 InsideWalls=0,Airborne=0,Invalid=0,StaticCarHits=0;float MaxHeight=0;
 TArray<float> PreviousTravel,Still,Longest;for(const auto& W:Walkers){PreviousTravel.Add(W.Travelled);Still.Add(0);Longest.Add(0);}
 int32 HeightRecoveries=0;for(int32 I=0;I<Walkers.Num();I+=37)if(!Walkers[I].TransitPassenger){Walkers[I].Position.Z=5000;HeightRecoveries++;}
 const int32 Steps=FMath::CeilToInt(Seconds*15);
 for(int32 Step=0;Step<Steps;Step++){
  Elapsed+=1.f/15;SimulateTraffic(1.f/30);SimulateTraffic(1.f/30);SimulateWalkers(1.f/15);
  for(int32 I=0;I<Walkers.Num();I++){const auto& W=Walkers[I];bool SignalWait=W.CrossSegments.IsValidIndex(W.Segment)&&W.CrossSegments[W.Segment]&&!W.Crossing;
   Still[I]=W.Activity==EPedActivity::Walking&&!SignalWait&&W.Travelled-PreviousTravel[I]<.01f?Still[I]+1.f/15:0;Longest[I]=FMath::Max(Longest[I],Still[I]);PreviousTravel[I]=W.Travelled;
   if(Step%15==0&&!W.TransitPassenger&&!PedHidden(W)&&W.Activity==EPedActivity::Walking){if(!WalkerStepClear(W.Position,W.Position)){InsideWalls++;if(InsideWalls<6)UE_LOG(LogTemp,Warning,TEXT("MAP_WALL id=%d pos=%s"),I,*W.Position.ToString());}if(W.Position.Z>65)Airborne++;if(W.Position.ContainsNaN())Invalid++;MaxHeight=FMath::Max(MaxHeight,float(W.Position.Z));}
  }
  if(Step%15==0)for(const auto& A:Vehicles){FHitResult Hit;FVector P=A.Position+FVector(0,0,100);if(GetWorld()->OverlapBlockingTestByChannel(P,FRotator(0,A.Heading,0).Quaternion(),ECC_WorldStatic,FCollisionShape::MakeBox(FVector(A.HalfLength*.9f,A.HalfWidth*.9f,60)),FCollisionQueryParams()))StaticCarHits++;}
 }
 int32 Stalled=0;float MaxStop=0;for(int32 I=0;I<Longest.Num();I++){MaxStop=FMath::Max(MaxStop,Longest[I]);if(Longest[I]>25){Stalled++;if(Stalled<=12)UE_LOG(LogTemp,Warning,TEXT("MAP_STALL id=%d seconds=%.1f pos=%s segment=%d"),I,Longest[I],*Walkers[I].Position.ToString(),Walkers[I].Segment);}}
 Report->SetNumberField(TEXT("pedestrians"),Walkers.Num());Report->SetNumberField(TEXT("vehicles"),Vehicles.Num());Report->SetNumberField(TEXT("wall_penetration_samples"),InsideWalls);Report->SetNumberField(TEXT("airborne_samples"),Airborne);Report->SetNumberField(TEXT("invalid_positions"),Invalid);Report->SetNumberField(TEXT("maximum_street_foot_height_cm"),MaxHeight);Report->SetNumberField(TEXT("injected_invalid_heights"),HeightRecoveries);Report->SetNumberField(TEXT("unplanned_stalls"),Stalled);Report->SetNumberField(TEXT("longest_unplanned_stop_seconds"),MaxStop);Report->SetNumberField(TEXT("static_vehicle_overlap_samples"),StaticCarHits);Report->SetNumberField(TEXT("crossings_completed"),PedestrianCrossings);Report->SetNumberField(TEXT("illegal_crossings"),IllegalCrossings);
 FString Result;FJsonSerializer::Serialize(Report.ToSharedRef(),TJsonWriterFactory<>::Create(&Result));return Result;
}
''';p.write_text(s)
p=r/'Source/BogotaVoxelEditor/DeliveryEditorLibrary.h';s=p.read_text().replace(' static FString ValidateTrafficPaint(UClass* CityClass);',' static FString ValidateTrafficPaint(UClass* CityClass);\n UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static FString ValidateMapRoutes(float Seconds);');p.write_text(s)
p=r/'Source/BogotaVoxelEditor/DeliveryEditorLibrary.cpp';s=p.read_text();s+='''
FString UDeliveryEditorLibrary::ValidateMapRoutes(float Seconds){
 FEditorScriptExecutionGuard Guard;UWorld* World=GEditor->GetEditorWorldContext().World();
 for(TActorIterator<ABogotaCity> It(World);It;++It)return It->ValidateMapRoutes(Seconds);
 return TEXT("{}");
}
''';p.write_text(s)
