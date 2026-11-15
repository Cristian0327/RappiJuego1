using UnrealBuildTool;
public class BogotaRuntime : ModuleRules {
 public BogotaRuntime(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.NoPCHs;
  PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","UMG","InputCore"});
  PrivateDependencyModuleNames.AddRange(new string[]{"Slate","SlateCore","ImageWrapper"});
  if (Target.Platform == UnrealTargetPlatform.Win64)
  {
   PrivateDependencyModuleNames.Add("FMODStudio");
   PrivateDefinitions.Add("BOGOTA_WITH_FMOD=1");
  }
 }
}

