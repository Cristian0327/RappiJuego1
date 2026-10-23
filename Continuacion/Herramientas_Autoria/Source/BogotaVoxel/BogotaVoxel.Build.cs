using UnrealBuildTool;
public class BogotaVoxel : ModuleRules {
 public BogotaVoxel(ReadOnlyTargetRules Target):base(Target) {PCHUsage=PCHUsageMode.UseExplicitOrSharedPCHs;PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","InputCore","UMG","Slate","SlateCore","RenderCore","RHI","Json","JsonUtilities","AssetRegistry"});}
}
