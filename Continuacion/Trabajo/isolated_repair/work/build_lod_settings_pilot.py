import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;t=unreal.AssetToolsHelpers.get_asset_tools();path='/Game/World/BlueprintWorld/Optimization/DA_VoxelLOD';settings=unreal.load_asset(path)
if not settings:
 f=unreal.DataAssetFactory();f.set_editor_property('data_asset_class',unreal.SkeletalMeshLODSettings);settings=t.create_asset('DA_VoxelLOD',path.rsplit('/',1)[0],unreal.SkeletalMeshLODSettings,f)
groups=[]
for ratio,size in [(1.,1.),(.55,.12),(.25,.055)]:
 g=unreal.SkeletalMeshLODGroupSettings();red=g.get_editor_property('reduction_settings');red.set_editor_property('num_of_triangles_percentage',ratio);red.set_editor_property('recalc_normals',False);red.set_editor_property('enforce_bone_boundaries',True);red.set_editor_property('lock_color_bounaries',True);g.set_editor_property('reduction_settings',red);current=g.get_editor_property('screen_size');g.set_editor_property('screen_size',unreal.PerPlatformFloat(default=size) if isinstance(current,unreal.PerPlatformFloat) else size);groups.append(g)
settings.set_editor_property('lod_groups',groups);assert unreal.EditorAssetLibrary.save_loaded_asset(settings,only_if_is_dirty=False);m=unreal.load_asset('/Game/Crowd/People/SK_Citizen00');m.set_editor_property('lod_settings',settings);sub=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem);ok=sub.regenerate_lod(m,3,False,False);assert ok and sub.get_lod_count(m)==3;assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False);(r/'work/lod_settings_pilot.json').write_text(json.dumps({'status':'PASS','asset':path,'lods':sub.get_lod_count(m)}));unreal.log('LOD_SETTINGS_PILOT_PASS')
