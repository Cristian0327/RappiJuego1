import unreal,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd';mel=unreal.MaterialEditingLibrary
parent=unreal.load_asset('/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB');tex=unreal.load_asset('/Game/Crowd/T_CrowdPixelAtlas');assert parent and tex
mi=unreal.load_asset('/Game/Crowd/MI_Crowd') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('MI_Crowd','/Game/Crowd',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi,parent);mel.update_material_instance(mi);(out/'material_parameters.json').write_text(json.dumps({'textures':[str(n) for n in mel.get_texture_parameter_names(parent)],'scalars':[str(n) for n in mel.get_scalar_parameter_names(parent)],'class':parent.get_class().get_name()}));mel.set_material_instance_texture_parameter_value(mi,'BaseColorTexture',tex);assert mel.get_material_instance_texture_parameter_value(mi,'BaseColorTexture')==tex;mel.set_material_instance_scalar_parameter_value(mi,'Roughness',.9);mel.set_material_instance_scalar_parameter_value(mi,'Specular',.08);mel.update_material_instance(mi);unreal.EditorAssetLibrary.save_loaded_asset(mi,only_if_is_dirty=False)
for name in ['SK_CrowdRig']+['People/SK_Citizen%02d'%i for i in range(60)]:
 mesh=unreal.load_asset('/Game/Crowd/'+name);assert mesh;mesh.modify();slots=mesh.get_editor_property('materials');s=slots[0];s.material_interface=mi;slots[0]=s;mesh.set_editor_property('materials',slots);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
r=json.loads((out/'unreal_import.json').read_text());r['shared_material_parent']=parent.get_path_name()
for k,v in r.items():
 if isinstance(v,dict):v['material']='MI_Crowd'
(out/'unreal_import.json').write_text(json.dumps(r,indent=2));unreal.log('CROWD_HARMONY_PASS')



