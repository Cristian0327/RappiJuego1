import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;out={}
for path in ['/Game/VoxelExplorer/AN_BikePedal','/Game/VoxelExplorer/AN_MotoRide','/Game/VoxelExplorer/AN_Walk_InPlace','/Game/Crowd/AN_CrowdBikePedal','/Game/Traffic/Services/AN_MotorcycleRider']:
 a=unreal.load_asset(path);pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(a,0,unreal.AnimPoseEvaluationOptions());p={}
 for n in ['pelvis','head','hand_l','hand_r','foot_l','foot_r']:
  t=unreal.AnimPoseExtensions.get_bone_pose(pose,n,unreal.AnimPoseSpaces.WORLD).translation;p[n]=[t.x,t.y,t.z]
 out[path]=p
for name in ['AnimSingleNodeInstance','SkeletalMeshComponent','AnimInstance']:
 c=getattr(unreal,name);out[name]=[x for x in dir(c) if any(t in x for t in ['asset','animation','play_rate','play_length','position'])]
(r/'work/ride_pose_coordinates.json').write_text(json.dumps(out,indent=2));unreal.log('RIDE_POSE_COORDINATES_PASS')
