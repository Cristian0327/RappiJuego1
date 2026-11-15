import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;L=unreal.AnimPoseExtensions;out={}
for name in ['AN_Idle','AN_MixamoWalk','AN_HeroMountBike','AN_HeroMountMoto','AN_BikePedal','AN_MotoRide','AN_MixamoJump']:
 a=unreal.load_asset('/Game/VoxelExplorer/'+name);assert a,name;opts=unreal.AnimPoseEvaluationOptions();pose=L.get_anim_pose_at_time(a,0,opts);names=[str(x) for x in L.get_bone_names(pose)];samples=[]
 for t in [0,a.get_play_length()*.5,a.get_play_length()*.95]:
  pose=L.get_anim_pose_at_time(a,t,opts);points={}
  for n in ['upperarm_l','upperarm_r','hand_l','hand_r','pelvis','head']:
   if n in names:
    p=L.get_bone_pose(pose,n,unreal.AnimPoseSpaces.WORLD).translation;points[n]=[p.x,p.y,p.z]
  shoulder=None
  if 'upperarm_l' in points and 'upperarm_r' in points:
   l=points['upperarm_l'];rr=points['upperarm_r'];shoulder=math.degrees(math.atan2(-(rr[0]-l[0]),rr[1]-l[1]))
  l=points['hand_l'];rr=points['hand_r'];p=points['pelvis'];handyaw=math.degrees(math.atan2((l[1]+rr[1])*.5-p[1],(l[0]+rr[0])*.5-p[0]));samples.append({'time':t,'shoulder_forward_yaw':shoulder,'hands_forward_yaw':handyaw,'points':points})
 out[name]={'bones':names if name=='AN_Idle' else None,'samples':samples}
for path in ['/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider','/Game/Delivery/Vehicles/BP_DeliveryRider']:
 bp=unreal.load_asset(path);rot=unreal.get_default_object(bp.generated_class()).get_editor_property('mesh').get_editor_property('relative_rotation');out[path]={'pitch':rot.pitch,'yaw':rot.yaw,'roll':rot.roll}
(r/'work/hero_animation_body_axes.json').write_text(json.dumps(out,indent=2));unreal.log('HERO_ANIMATION_BODY_AXES_MEASURED')
