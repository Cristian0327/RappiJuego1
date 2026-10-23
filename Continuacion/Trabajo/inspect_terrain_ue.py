import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.EditorAssetLibrary;ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');mesh=unreal.load_asset('/Game/Maps/MapaCompleto/Geometry/SM_Mapa_081');sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);out={'lods':mesh.get_num_lods(),'materials':[str(x.material_interface) for x in mesh.static_materials]}
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp);n=str(lib.get_variable_name(lib.get_data(h)))
 if n=='Part081':out['component']={'mesh':o.static_mesh.get_path_name(),'mat':o.get_material(0).get_path_name(),'override':str(o.get_editor_property('override_materials'))};o.set_forced_lod_model(1) if hasattr(o,'set_forced_lod_model') else o.set_editor_property('forced_lod_model',1)
unreal.log('TERRAIN_DETAILS '+json.dumps(out));(r/'outputs/MapRebuild/terrain_details.json').write_text(json.dumps(out,indent=2));assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert E.save_loaded_asset(bp,only_if_is_dirty=False)

