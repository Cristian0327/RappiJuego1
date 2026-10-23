import unreal,json,shutil,hashlib
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
bp=unreal.load_asset('/Game/Delivery/Animation/ABP_DeliveryRider')
walk=unreal.load_asset('/Game/VoxelExplorer/AN_Walk_InPlace')
old=unreal.load_asset('/Game/VoxelExplorer/AN_MixamoWalk')
assert bp and walk and old
assert walk.get_editor_property('skeleton')==old.get_editor_property('skeleton')
rows=json.loads((r/'outputs/DeliveryArt/AnimationRebuild/Upright/posture_validation.json').read_text())
assert any(x['clip']=='AN_HeroWalk_Rebuilt' for x in rows)
assert any(x['clip']=='AN_CrowdWalk_Rebuilt' for x in rows)
hero=str(r/'outputs/DeliveryArt/Mixamo/Walk.fbx'); assert Path(hero).exists()
cane=r/'RappiJuego1/Content/Crowd/AN_CrowdCane.uasset';digest=hashlib.sha256(cane.read_bytes()).hexdigest()
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-19_hero_shared_walk';backup.mkdir(parents=True,exist_ok=True)
package=r/'RappiJuego1/Content/Delivery/Animation/ABP_DeliveryRider.uasset'
if not (backup/package.name).exists():shutil.copy2(package,backup/package.name)
clips=[unreal.load_asset('/Game/VoxelExplorer/'+n) for n in ['AN_Idle','AN_BikePedal','AN_MotoRide','AN_MixamoJump']]
assert all(clips)
assert unreal.DeliveryEditorLibrary.build_locomotion_blueprint(walk.get_editor_property('skeleton'),clips[0],walk,clips[1],clips[2],clips[3])
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
assert hashlib.sha256(cane.read_bytes()).hexdigest()==digest
audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp))
assert audit['parent']=='/Script/Engine.AnimInstance' and not any(g['native_calls'] for g in audit['graphs'])
(r/'work/hero_shared_walk_result.json').write_text(json.dumps({'status':'COMPILED_NOT_RUNTIME_VERIFIED','hero_clip':walk.get_path_name(),'same_mixamo_source_as_npc':hero,'elder_unchanged':True},indent=2))
unreal.log('HERO_SHARED_NPC_WALK_COMPILED')





