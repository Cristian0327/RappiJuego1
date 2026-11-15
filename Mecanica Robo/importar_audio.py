from pathlib import Path

import unreal

project = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
folder = "/Game/Robbery/Audio"

for variant, extension in (("Rayas", "mp3"), ("Hornets", "mp3")):
    source = project / "SourceArt" / "PersonajesVoxel" / f"Robbery_{variant}.{extension}"
    if not source.is_file():
        continue
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_path = folder
    task.destination_name = f"S_Robbery_{variant}"
    task.automated = True
    task.replace_existing = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if not task.imported_object_paths:
        raise RuntimeError(f"Audio import failed: {source}")
