using UnrealBuildTool;
public class BogotaRuntime : ModuleRules {
 public BogotaRuntime(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.NoPCHs;
  PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","UMG"});
 }
}

