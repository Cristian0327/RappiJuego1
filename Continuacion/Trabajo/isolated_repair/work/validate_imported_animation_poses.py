import unreal,json,math,hashlib
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;items=json.loads((r/'work/compatible_role_animation_import_validation.json').read_text())['clips'];report=[];L=unreal.AnimPoseExtensions
for item in items:
 asset=unreal.load_asset(item['asset']);idle=item['asset'].endswith(('_Work','AN_Idle','AN_CrowdIdle'));length=asset.get_play_length();stats=[]
 for kind in [unreal.AnimDataEvalType.RAW,unreal.AnimDataEvalType.COMPRESSED]:
  opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_property('evaluation_type',kind);maximum=0.;head_heights=[];foot_heights=[];samples=0
  for frame in range(round(length*30)+1):
   pose=L.get_anim_pose_at_time(asset,min(length,frame/30),opts);assert L.is_valid(pose),(item['asset'],frame);names=[str(x) for x in L.get_bone_names(pose)]
   for side in (['l','r'] if 'thigh_l' in names else ['L','R']):
    bones=['thigh_'+side,('calf_' if 'calf_'+side in names else 'shin_')+side,'foot_'+side];points=[L.get_bone_pose(pose,n,unreal.AnimPoseSpaces.WORLD).translation for n in bones];h,k,a=points;u=[k.x-h.x,k.y-h.y,k.z-h.z];v=[a.x-k.x,a.y-k.y,a.z-k.z];den=math.sqrt(sum(x*x for x in u)*sum(x*x for x in v));assert den>.00001,(item['asset'],bones,points);angle=math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(u,v))/den))));maximum=max(maximum,angle);foot_heights.append(a.z)
   head_heights.append(L.get_bone_pose(pose,'head',unreal.AnimPoseSpaces.WORLD).translation.z);samples+=1
  assert not idle or maximum<10.6,(item['asset'],str(kind),maximum);assert min(head_heights)>90 and max(head_heights)<230,(item['asset'],min(head_heights),max(head_heights));assert min(foot_heights)>-5 and max(foot_heights)<70,(item['asset'],min(foot_heights),max(foot_heights));stats.append({'evaluation':str(kind),'frames':samples,'max_knee_flexion_degrees':maximum,'head_height_range_cm':[min(head_heights),max(head_heights)],'foot_joint_range_cm':[min(foot_heights),max(foot_heights)]})
 report.append({'asset':item['asset'],'idle':idle,'samples':stats});unreal.log('IMPORTED_POSE_VERIFIED '+item['asset'])
cane=hashlib.sha256((r/'RappiJuego1/Content/Crowd/AN_CrowdCane.uasset').read_bytes()).hexdigest();assert cane=='1742c809c0799c7abc0b7167d415febafb2dd6290787335d39536e9bccfc461e';(r/'work/imported_animation_pose_validation.json').write_text(json.dumps({'status':'PASS','clips':report,'count':len(report),'elderly_cane_sha256':cane},indent=2));unreal.log('IMPORTED_ANIMATION_POSE_VALIDATION_PASS clips='+str(len(report)))
