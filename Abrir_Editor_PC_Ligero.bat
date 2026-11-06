@echo off
set "BOGOTA_EDITOR=C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
if exist "%BOGOTA_EDITOR%" (
    start "" "%BOGOTA_EDITOR%" "%~dp0BogotaVoxel.uproject" -d3d11 -NoSplash -NoLiveCoding -ini:Engine:[ConsoleVariables]:Editor.AsyncAssetCompilationMaxConcurrency=2 -ini:Engine:[ConsoleVariables]:Editor.AsyncAssetCompilationMaxMemoryUsage=2 -ini:Engine:[DevOptions.Shaders]:NumUnusedShaderCompilingThreads=6 -ini:Engine:[DevOptions.Shaders]:NumUnusedShaderCompilingThreadsDuringGame=6
) else (
    start "" "%~dp0BogotaVoxel.uproject"
)
