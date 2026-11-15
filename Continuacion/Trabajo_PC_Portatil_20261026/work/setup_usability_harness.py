from pathlib import Path
import shutil
r=Path('outputs/BogotaVoxel/Source/BogotaVoxel');b=Path('work/Backups/Usability_20261014');b.mkdir(parents=True,exist_ok=True)
for n in ['DeliverySystem.h','DeliverySystem.cpp','DeliveryUI.cpp']:shutil.copy2(r/n,b/n)
p=r/'DeliverySystem.h';s=p.read_text();s=s.replace(' void UpdateValidation(float Dt);',' void UpdateValidation(float Dt);\n void UpdateUsabilityValidation(float Dt);');s=s.replace(' UPROPERTY(BlueprintReadWrite) UDeliveryComponent* Delivery=nullptr;\n virtual void NativeConstruct()', ' friend class UDeliveryComponent;\n UPROPERTY(BlueprintReadWrite) UDeliveryComponent* Delivery=nullptr;\n virtual void NativeConstruct()');p.write_text(s)
p=r/'DeliverySystem.cpp';s=p.read_text();s=s.replace('bValidation=FParse::Param(FCommandLine::Get(),TEXT("DeliveryTest"));','bValidation=FParse::Param(FCommandLine::Get(),TEXT("DeliveryTest"))||FParse::Param(FCommandLine::Get(),TEXT("UsabilityTest"));');s=s.replace('void UDeliveryComponent::UpdateValidation(float Dt){','void UDeliveryComponent::UpdateValidation(float Dt){\n if(FParse::Param(FCommandLine::Get(),TEXT("UsabilityTest"))){UpdateUsabilityValidation(Dt);return;}');p.write_text(s)
print('Regression harness connected to the real game/UI, isolated automation save slot.')
