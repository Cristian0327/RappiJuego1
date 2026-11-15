import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/build_locomotion_anim_blueprint.py').read_text(encoding='utf-8-sig'))
for role in ['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']:
 mesh=unreal.load_asset('/Game/Delivery/People/SK_'+role)
 idle=unreal.load_asset('/Game/Delivery/People/A_'+role+'_Work')
 walk=unreal.load_asset('/Game/Delivery/People/A_'+role+'_Walk')
 assert mesh and idle and walk,role
 bp=unreal.DeliveryEditorLibrary.build_character_animation_blueprint('ABP_'+role,mesh.get_editor_property('skeleton'),idle,walk,idle,idle,idle)
 assert bp,role
 unreal.EditorAssetLibrary.save_loaded_asset(bp)
unreal.log('NINE_CHARACTER_ANIMATION_BLUEPRINTS_SAVED')
