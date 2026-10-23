import unreal
from pathlib import Path
import json
root = Path(unreal.Paths.project_dir()).parent
bp = unreal.load_asset('/Game/Delivery/Animation/ABP_DeliveryRider')
walk = unreal.load_asset('/Game/VoxelExplorer/AN_Walk_InPlace')
old = unreal.load_asset('/Game/VoxelExplorer/AN_MixamoWalk')
assert bp and walk and old
assert walk.get_editor_property('skeleton') == old.get_editor_property('skeleton'), 'Hero skeleton mismatch'
# Existing hero walk was retargeted from the same Mixamo Walk source as standard citizens.
# Replace only the locomotion sequence; retain mount, idle, jump and elderly graphs.
changes = []
for obj in unreal.ObjectIterator():
    if obj.get_class().get_name() != 'AnimGraphNode_SequencePlayer':
        continue
    if not obj.get_path_name().startswith(bp.get_path_name() + ':'):
        continue
    node = obj.get_editor_property('node')
    if node.get_editor_property('sequence') == old:
        node.set_editor_property('sequence', walk)
        obj.set_editor_property('node', node)
        changes.append(obj.get_path_name())
assert changes, 'No hero running sequence found; refusing an unverified graph edit'
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
(root / 'work/hero_shared_walk_result.json').write_text(json.dumps({'changed_nodes': changes, 'animation': walk.get_path_name(), 'runtime_verified': False}, indent=2))
unreal.log('HERO_SHARED_NPC_WALK_SAVED_RUNTIME_VERIFICATION_REQUIRED')
