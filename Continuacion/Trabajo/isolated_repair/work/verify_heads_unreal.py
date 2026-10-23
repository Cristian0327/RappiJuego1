import unreal,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];report={}
skeleton=unreal.load_asset('/Game/Crowd/SKEL_Crowd')
tex=unreal.load_asset('/Game/Crowd/T_CrowdPixelAtlas');tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);tex.set_editor_property('never_stream',True);unreal.EditorAssetLibrary.save_loaded_asset(tex,only_if_is_dirty=False)
for i in range(60):
 mesh=unreal.load_asset('/Game/Crowd/People/SK_Citizen%02d'%i);assert mesh.get_editor_property('skeleton')==skeleton
 comp=unreal.new_object(unreal.SkeletalMeshComponent);comp.set_skeletal_mesh_asset(mesh);assert comp.get_num_bones()==24;assert comp.get_bone_index('head')>=0 and comp.get_bone_index('cane')>=0
 assert mesh.get_editor_property('materials')[0].material_interface==unreal.load_asset('/Game/Crowd/MI_Crowd')
 report[str(i)]={'bones':24,'head':True,'cane':True,'material':True}
for name in ['AN_CrowdWalk_Mixamo','AN_CrowdCane','AN_CrowdIdle','AN_CrowdEnterCar','AN_CrowdBoard']:
 a=unreal.load_asset('/Game/Crowd/'+name);assert a.get_editor_property('skeleton')==skeleton
unreal.EditorAssetLibrary.save_loaded_asset(skeleton,only_if_is_dirty=False)
report['status']='PASS';(r/'work/unreal_heads_validation.json').write_text(json.dumps(report,indent=2));unreal.log('UNREAL_HEADS_ALL_60_PASS')
