import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;out={};L=unreal.AnimPoseExtensions
for p in ['/Game/VoxelExplorer/AN_Walk_InPlace','/Game/Crowd/AN_CrowdWalk_Mixamo','/Game/VoxelExplorer/AN_BikePedal','/Game/Crowd/AN_CrowdBikePedal']:
 a=unreal.load_asset(p);row={'length':a.get_play_length(),'rate_scale':a.get_editor_property('rate_scale'),'skeleton':a.get_editor_property('skeleton').get_path_name()};opts=unreal.AnimPoseEvaluationOptions();samples=[]
 if 'Pedal' in p:
  for i in range(32):
   t=a.get_play_length()*i/32;pose=L.get_anim_pose_at_time(a,t,opts);d={}
   for n in ['foot_l','foot_r','pelvis','hand_l','hand_r']:
    v=L.get_bone_pose(pose,n,unreal.AnimPoseSpaces.WORLD).translation;d[n]=[v.x,v.y,v.z]
   samples.append(d)
  forward=[sum((s['hand_l'][j]+s['hand_r'][j])*.5-s['pelvis'][j] for s in samples)/32 for j in [0,1]];length=math.hypot(*forward);forward=[v/length for v in forward];score=0
  for side in ['l','r']:
   name='foot_'+side;mean=[sum(s[name][j] for s in samples)/32 for j in [0,1]]
   for i,sample in enumerate(samples):
    front=sum((sample[name][j]-mean[j])*forward[j] for j in [0,1]);dz=samples[(i+1)%32][name][2]-samples[(i-1)%32][name][2];score+=front*dz
  row.update(forward=forward,front_down_score=score,expected_score='negative for forward pedaling',samples=samples)
 out[p]=row
assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);out['patrols']=[]
for a in actors.get_all_level_actors():
 if 'VoxelRoadVehicle' in a.get_class().get_name():
  model=a.get_editor_property('DriveModel')
  if model and 'Patrol' in model.get_name():
   row={'actor':a.get_name(),'model':model.get_path_name(),'rider':str(a.get_editor_property('RiderModel')),'materials':[{'slot':str(s.material_slot_name),'mat':s.material_interface.get_path_name() if s.material_interface else None} for s in model.get_editor_property('materials')]};out['patrols'].append(row)
mesh=unreal.load_asset('/Game/Traffic/Detailed/SK_PrivateSUV')
if mesh:out['normal_suv_materials']=[{'slot':str(s.material_slot_name),'mat':s.material_interface.get_path_name() if s.material_interface else None} for s in mesh.get_editor_property('materials')]
(r/'work/bike_patrol_walk_diagnostic.json').write_text(json.dumps(out,indent=2));unreal.log('BIKE_PATROL_WALK_DIAGNOSTIC_READY')
