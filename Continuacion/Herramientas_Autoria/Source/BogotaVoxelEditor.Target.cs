using UnrealBuildTool;
public class BogotaVoxelEditorTarget : TargetRules {
 public BogotaVoxelEditorTarget(TargetInfo Target):base(Target) {Type=TargetType.Editor;DefaultBuildSettings=BuildSettingsVersion.Latest;IncludeOrderVersion=EngineIncludeOrderVersion.Latest;ExtraModuleNames.AddRange(new string[]{"BogotaVoxel","BogotaVoxelEditor"});}
}
