import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
out={}
for n in ['BlueprintEditorLibrary','AnimPoseExtensions','AnimPoseEvaluationOptions','AnimationBlueprintLibrary']:
 c=getattr(unreal,n,None);out[n]={'members':[x for x in dir(c) if not x.startswith('_')],'doc':str(getattr(c,'__doc__',''))[:800]}
for n in ['AN_MixamoWalk','AN_Idle','AN_BikePedal','AN_MotoRide']:
 a=unreal.load_asset('/Game/VoxelExplorer/'+n);out[n]=str(a)
(r/'work/animation_inspection_api.json').write_text(json.dumps(out,indent=2));unreal.log('ANIMATION_API_INSPECTION_PASS')
