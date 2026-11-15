using UnrealBuildTool;

public class BogotaPhonePreview : ModuleRules
{
    public BogotaPhonePreview(ReadOnlyTargetRules Target) : base(Target)
    {
        PrivateDependencyModuleNames.AddRange(new[] {
            "Core", "CoreUObject", "Engine", "ApplicationCore", "UMG", "InputCore", "Slate", "SlateCore", "Projects", "ImageWrapper", "FMODStudio"
        });
        RuntimeDependencies.Add("$(PluginDir)/Resources/...", StagedFileType.NonUFS);
        ExternalDependencies.AddRange(System.IO.Directory.GetFiles(System.IO.Path.Combine(PluginDirectory, "Resources")));
    }
}
