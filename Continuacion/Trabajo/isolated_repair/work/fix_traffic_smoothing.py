from pathlib import Path
root=Path(__file__).resolve().parents[1];src=root/'outputs/BogotaVoxel/Source/BogotaVoxel'
p=src/'BogotaGame.h';s=p.read_text()
s=s.replace('FVector Position=FVector::ZeroVector;\n float Speed=0','FVector Position=FVector::ZeroVector,PreviousPosition=FVector::ZeroVector;\n float PreviousHeading=0,PreviousWheelAngle=0,SteeringRate=0;\n float Speed=0')
s=s.replace(' void SimulateTraffic(float Dt);',' void SimulateTraffic(float Dt);\n void UpdateTrafficVisuals(float Alpha);')
s=s.replace(' UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> TrafficMaterial;',' UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> TrafficMaterial;\n UPROPERTY() TArray<TObjectPtr<class USkeletalMesh>> CrowdMeshes;\n UPROPERTY() TArray<TObjectPtr<UAnimationAsset>> CrowdClips;\n UPROPERTY() TObjectPtr<UMaterialInterface> CrowdMaterial;')
p.write_text(s)
p=src/'BogotaTraffic.cpp';s=p.read_text()
needle=' G66Random.Initialize(int32(FDateTime::Now().GetTicks()));'
s=s.replace(needle,''' // Load shared crowd resources once, before gameplay; entering another block
 // must not synchronously import a character or animation on a moving frame.
 CrowdMeshes.Empty();for(const auto& Spec:CrowdModels){FString N=Spec.Name;CrowdMeshes.Add(LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Crowd/People/SK_%s.SK_%s"),*N,*N)));}
 CrowdMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Crowd/MI_Crowd.MI_Crowd"));
 CrowdClips.Empty();for(const TCHAR* Path:{TEXT("/Game/Crowd/AN_CrowdWalk_Mixamo.AN_CrowdWalk_Mixamo"),TEXT("/Game/Crowd/AN_CrowdIdle.AN_CrowdIdle"),TEXT("/Game/Crowd/AN_CrowdEnterCar.AN_CrowdEnterCar"),TEXT("/Game/Crowd/AN_CrowdEnterCar.AN_CrowdEnterCar"),TEXT("/Game/Crowd/AN_CrowdBoard.AN_CrowdBoard"),TEXT("/Game/Crowd/AN_CrowdBoard.AN_CrowdBoard"),TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane"),TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane")})CrowdClips.Add(LoadObject<UAnimationAsset>(nullptr,Path));
'''+needle)
s=s.replace('A.PathDistance=SpawnDistance;A.LoopLength=LoopLength;','A.PathDistance=SpawnDistance;A.LoopLength=LoopLength;A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;')
s=s.replace('  auto& A=Vehicles[Index];FVector Target=', '  auto& A=Vehicles[Index];A.PreviousPosition=A.Position;A.PreviousHeading=A.Heading;A.PreviousWheelAngle=A.WheelAngle;FVector Target=')
begin=s.index('  if(A.Visual.IsValid()){\n   auto* V=A.Visual.Get();V->GetOwner()->SetActorLocationAndRotation(A.Position')
end=s.index('  auto* C=VehicleCollision[Index]',begin)
visual=s[begin:end]
s=s[:begin]+'  A.SteeringRate=Turn/FMath::Max(Dt,.001f);\n'+s[end:]
visual=visual.replace('  if(A.Visual.IsValid()){','  if(A.Visual.IsValid()){\n   FVector Position=FMath::Lerp(A.PreviousPosition,A.Position,Alpha);float Heading=A.PreviousHeading+FMath::FindDeltaAngleDegrees(A.PreviousHeading,A.Heading)*Alpha;\n   float WheelAngle=A.PreviousWheelAngle+FMath::FindDeltaAngleDegrees(A.PreviousWheelAngle,A.WheelAngle)*Alpha;\n   bool Near=FVector::DistSquared2D(CameraPosition,Position)<FMath::Square(24000.f);A.Visual->GetOwner()->SetActorHiddenInGame(!Near);A.Visual->SetComponentTickEnabled(Near);if(!Near)continue;')
visual=visual.replace('SetActorLocationAndRotation(A.Position,FRotator(0,A.Heading,0))','SetActorLocationAndRotation(Position,FRotator(0,Heading,0))')
visual=visual.replace('-Turn/Dt*.32f','-A.SteeringRate*.32f').replace('Turn/Dt*.25f','A.SteeringRate*.25f').replace('DegreesToRadians(A.WheelAngle)','DegreesToRadians(WheelAngle)')
idx=s.index('FString ABogotaCity::ValidateTraffic')
s=s[:idx]+'''void ABogotaCity::UpdateTrafficVisuals(float Alpha){
 FVector CameraPosition=FVector::ZeroVector;if(auto* PC=GetWorld()->GetFirstPlayerController())if(PC->PlayerCameraManager)CameraPosition=PC->PlayerCameraManager->GetCameraLocation();
 for(auto& A:Vehicles){
'''+visual+''' }
}
'''+s[idx:]
s=s.replace('auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Crowd/People/SK_%s.SK_%s"),*Name,*Name));\n    if(!Mesh)', 'auto* Mesh=CrowdMeshes.IsValidIndex(W.ModelIndex)?CrowdMeshes[W.ModelIndex].Get():nullptr;\n    if(!Mesh)')
s=s.replace('S->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Crowd/MI_Crowd.MI_Crowd")))','S->SetMaterial(0,CrowdMaterial)')
s=s.replace('S->PlayAnimation(LoadObject<UAnimationAsset>(nullptr,CrowdModels[W.ModelIndex].Cane?TEXT("/Game/Crowd/AN_CrowdCane.AN_CrowdCane"):TEXT("/Game/Crowd/AN_CrowdWalk_Mixamo.AN_CrowdWalk_Mixamo")),true)','S->PlayAnimation(CrowdClips[CrowdModels[W.ModelIndex].Cane?6:0],true)')
start=s.index('    const TCHAR* Paths[]={TEXT("/Game/Crowd/AN_CrowdWalk_Mixamo')
end=s.index('\n',start)
s=s[:start]+s[end+1:]
s=s.replace('auto* A=LoadObject<UAnimationAsset>(nullptr,Paths[Clip]);','auto* A=CrowdClips[Clip].Get();')
p.write_text(s)
p=src/'BogotaCity.cpp';s=p.read_text()
s=s.replace(' if(SimAccumulator>=.0333f){SimulateTraffic(FMath::Min(SimAccumulator,.1f));SimAccumulator=0;}',''' // Preserve elapsed time and render between fixed simulation states.
 constexpr float TrafficStep=1.f/30;int32 TrafficSteps=0;
 while(SimAccumulator>=TrafficStep&&TrafficSteps++<15){SimulateTraffic(TrafficStep);SimAccumulator-=TrafficStep;}
 UpdateTrafficVisuals(FMath::Clamp(SimAccumulator/TrafficStep,0.f,1.f));''')
p.write_text(s)
