using UnrealBuildTool;
public class BogotaVoxelEditor:ModuleRules {
 public BogotaVoxelEditor(ReadOnlyTargetRules Target):base(Target){PCHUsage=PCHUsageMode.UseExplicitOrSharedPCHs;PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","BogotaVoxel"});PrivateDependencyModuleNames.AddRange(new string[]{"UnrealEd","Kismet","KismetCompiler","BlueprintGraph","Json","AnimGraph","AnimGraphRuntime","AssetTools","UMG","UMGEditor","Slate","SlateCore"});}
}


