using UnrealBuildTool;
public class BogotaVoxelTarget : TargetRules {
 public BogotaVoxelTarget(TargetInfo Target):base(Target) {Type=TargetType.Game;DefaultBuildSettings=BuildSettingsVersion.Latest;IncludeOrderVersion=EngineIncludeOrderVersion.Latest;ExtraModuleNames.Add("BogotaVoxel");}
}
