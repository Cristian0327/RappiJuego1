from pathlib import Path
r=Path('outputs/BogotaVoxel/Source/BogotaVoxel')
p=r/'DeliverySystem.cpp';s=p.read_text(encoding='utf-8-sig');needle=' if(bValidation)UpdateValidation(Dt);';assert needle in s
s=s.replace(needle,needle+'\n else {static const bool ResumeTest=FParse::Param(FCommandLine::Get(),TEXT("UsabilityResumeTest"));if(ResumeTest)UpdateUsabilityValidation(Dt);}')
p.write_text(s,encoding='utf-8')
p=r/'DeliveryUsability.cpp';s=p.read_text(encoding='utf-8-sig').replace('#include "Misc/Paths.h"','#include "Misc/Paths.h"\n#include "Misc/CommandLine.h"\n#include "Misc/Parse.h"')
needle=' if(ValidationStage==0&&ValidationTime>3){';assert needle in s
s=s.replace(needle,''' if(FParse::Param(FCommandLine::Get(),TEXT("UsabilityResumeTest"))){
  if(ValidationTime<3||ValidationStage>0)return;
  auto* Saved=Cast<UDeliverySave>(UGameplayStatics::LoadGameFromSlot(ProfileSlot(),0));
  Check(!bValidation&&Saved,TEXT("normal_startup_reads_qa_profile"));
  Check(Saved&&Balance==Saved->Balance,TEXT("restart_restores_wallet"));
  Check(Saved&&Purchased.Num()==Saved->Purchased.Num()&&Saved->Purchased.ContainsByPredicate([&](FName ID){return Owns(ID);}),TEXT("restart_restores_purchased_upgrades"));
  Check(Saved&&Vehicle==Saved->Vehicle&&BikeModel==Saved->BikeModel&&MotoModel==Saved->MotoModel,TEXT("restart_restores_equipped_vehicle"));
  Check(CargoCapacity(true)==5&&Owns(TEXT("CargoPanniers")),TEXT("restart_restores_cargo_capacity"));
  Check(ActiveOrders.IsEmpty()&&!SelectedIncoming()&&!bHolding,TEXT("restart_does_not_invent_active_orders"));
  Capture(TEXT("QA_Profile_Restart.png"));
  auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("status"),ValidationErrors.IsEmpty()?TEXT("PASS"):TEXT("FAIL"));R->SetArrayField(TEXT("checks"),Checks);R->SetNumberField(TEXT("total"),Checks.Num());TArray<TSharedPtr<FJsonValue>> Errors;for(const auto& E:ValidationErrors)Errors.Add(MakeShared<FJsonValueString>(E));R->SetArrayField(TEXT("failures"),Errors);R->SetNumberField(TEXT("viewport_width"),UWidgetLayoutLibrary::GetViewportSize(this).X);R->SetNumberField(TEXT("viewport_height"),UWidgetLayoutLibrary::GetViewportSize(this).Y);
  FString JSON;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&JSON));FFileHelper::SaveStringToFile(JSON,*(FPaths::ProjectSavedDir()/TEXT("usability_validation.json")));UE_LOG(LogTemp,Display,TEXT("USABILITY_RESUME_RESULT %s"),*JSON);ValidationStage++;
  GetWorld()->GetTimerManager().SetTimerForNextTick([](){FPlatformMisc::RequestExit(false);});return;
 }
'''+needle)
p.write_text(s,encoding='utf-8')
