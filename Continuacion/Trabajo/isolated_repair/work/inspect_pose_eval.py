import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
out={}
for c,names in [(unreal.AnimPoseExtensions,['get_anim_pose_at_time','get_bone_pose']),(unreal.BlueprintEditorLibrary,['reparent_blueprint','remove_function_graph','add_member_variable'])]:
 for n in names:out[n]=str(getattr(c,n).__doc__)
out['AnimPoseSpaces']=str([x for x in dir(unreal.AnimPoseSpaces) if x.isupper()])
(r/'work/pose_eval_signatures.json').write_text(json.dumps(out,indent=2))
