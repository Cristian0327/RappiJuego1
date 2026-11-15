import unreal,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;K='/Script/Engine.KismetSystemLibrary';A='/Script/Engine.Actor';P='/Game/World/BlueprintWorld/Crowd/BP_StreetCitizen';bp=unreal.load_asset(P)
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/fix_solid_vehicles_npc_recovery.py').read_text();exec(compile(s[s.index("s=(r/'work/optimize_pure_crowd_active_bubble.py')"):],'FinalNearControllerGuard','exec'))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/SolidWorldRecovery')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 name=a.get_class().get_name().lower()
 if 'sky' in name or 'cloud' in name:actors.destroy_actor(a)
 if isinstance(a,unreal.CameraActor):
  a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(a.get_actor_location(),unreal.Vector(87300,82500,0)),False)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
unreal.log('FINAL_CONTROLLER_GALLERY_PASS')
