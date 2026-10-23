import unreal,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd';r=json.loads((out/'validation.json').read_text());assert r['status']=='PASS'
for i in range(40):
 good=unreal.load_asset('/Game/Crowd/People/SK_Citizen%02d'%i);assert good and good.get_editor_property('skeleton')==unreal.load_asset('/Game/Crowd/SKEL_Crowd')
 assert good.get_editor_property('materials')[0].material_interface
 old='/Game/Crowd/SK_Citizen%02d'%i
 if unreal.EditorAssetLibrary.does_asset_exist(old):unreal.EditorAssetLibrary.delete_asset(old)
rig=unreal.load_asset('/Game/Crowd/SK_CrowdRig');rig.modify();slots=rig.get_editor_property('materials');slot=slots[0];slot.material_interface=unreal.load_asset('/Game/Crowd/M_CrowdPixel');slots[0]=slot;rig.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(rig,only_if_is_dirty=False)
for path in ['/Game/Crowd/AN_CrowdWalk']:
 if unreal.EditorAssetLibrary.does_asset_exist(path):unreal.EditorAssetLibrary.delete_asset(path)
assert unreal.load_asset('/Game/Crowd/AN_CrowdWalk_Mixamo').get_editor_property('skeleton')==unreal.load_asset('/Game/Crowd/SKEL_Crowd')
unreal.log('CROWD_FINAL_ASSETS_PASS')
