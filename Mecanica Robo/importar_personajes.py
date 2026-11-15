from pathlib import Path

import unreal

project = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
source = project / "SourceArt" / "PersonajesVoxel" / "Rigs"
tools = unreal.AssetToolsHelpers.get_asset_tools()
assets = unreal.EditorAssetLibrary
material_path = "/Game/Robbery/M_RobberyVertex"
material = unreal.load_asset(material_path) if assets.does_asset_exist(material_path) else None
if not material:
    material = tools.create_asset("M_RobberyVertex", "/Game/Robbery", unreal.Material, unreal.MaterialFactoryNew())
    graph = unreal.MaterialEditingLibrary
    colors = graph.create_material_expression(material, unreal.MaterialExpressionVertexColor, -300, 0)
    graph.connect_material_property(colors, "", unreal.MaterialProperty.MP_BASE_COLOR)
    roughness = graph.create_material_expression(material, unreal.MaterialExpressionConstant, -300, 150)
    roughness.set_editor_property("r", .85)
    graph.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
    graph.recompile_material(material)
    if not assets.save_loaded_asset(material):
        raise RuntimeError("Could not save the robbery vertex color material")


def import_fbx(name, destination, skeleton=None):
    options = unreal.FbxImportUI()
    options.automated_import_should_detect_type = False
    options.import_as_skeletal = True
    options.import_mesh = skeleton is None
    options.import_animations = skeleton is not None
    options.import_materials = False
    options.import_textures = False
    if skeleton:
        options.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION
        options.skeleton = skeleton
    else:
        options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
        options.skeletal_mesh_import_data.vertex_color_import_option = unreal.VertexColorImportOption.REPLACE
    task = unreal.AssetImportTask()
    task.filename = str(source / (name + ".fbx"))
    task.destination_path = destination
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.replace_existing_settings = True
    task.save = True
    task.options = options
    tools.import_asset_tasks([task])
    asset = unreal.load_asset(f"{destination}/{name}")
    if not asset:
        raise RuntimeError(f"Import failed for {name}: {task.imported_object_paths}")
    if not task.imported_object_paths:
        raise RuntimeError(f"No FBX objects imported for {name}")
    unreal.log(f"ROBBERY_IMPORT {asset.get_path_name()} {asset.get_class().get_name()}")
    return asset


for name in ("Rayas", "Hornets"):
    folder = f"/Game/Robbery/{name}"
    mesh = import_fbx(f"SK_{name}", folder)
    slots = mesh.get_editor_property("materials")
    if not slots:
        slots = [unreal.SkeletalMaterial(material_interface=material)]
    for index, slot in enumerate(slots):
        slot.material_interface = material
        slots[index] = slot
    mesh.set_editor_property("materials", slots)
    skeleton = mesh.get_editor_property("skeleton")
    if not skeleton or not unreal.EditorAssetLibrary.save_loaded_asset(skeleton, only_if_is_dirty=False):
        raise RuntimeError(f"Could not save skeleton for {name}")
    clips = ("Walk", "Run", "Prompt")
    if name == "Hornets":
        clips += ("MountBike", "MountBikeLeft", "MountMoto", "MountMotoLeft", "BikePedal", "MotoRide")
    for clip in clips:
        animation = import_fbx(f"AN_{name}_{clip}", folder, skeleton)
        if animation.get_editor_property("skeleton") != skeleton:
            raise RuntimeError(f"Wrong skeleton for {name} {clip}")
    if not unreal.EditorAssetLibrary.save_directory(folder, only_if_is_dirty=False, recursive=True):
        raise RuntimeError(f"Could not save all imported assets in {folder}")
    skeleton_package = skeleton.get_path_name().split(".", 1)[0]
    skeleton_file = project / (skeleton_package.replace("/Game/", "Content/", 1) + ".uasset")
    if not skeleton_file.is_file():
        raise RuntimeError(f"Missing saved skeleton package: {skeleton_file}")
    unreal.log(f"ROBBERY_IMPORT_SAVED {skeleton_file}")
