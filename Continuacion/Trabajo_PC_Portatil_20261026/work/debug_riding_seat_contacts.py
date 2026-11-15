import bpy,math,json
from pathlib import Path
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");out=r/'outputs/DeliveryArt/AnimationRebuild';reports=[]
for clip,seat,sole in [('HeroBikePedal',83.5,35.5),('HeroMotoRide',85.5,36.5),('CrowdMotoRide',88,40)]:
 bpy.ops.wm.open_mainfile(filepath=str(out/('AN_'+clip+'_Rebuilt.blend')));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH');sc=bpy.context.scene;ids={}
 for n in ['pelvis','foot_l','foot_r']:
  gi=mesh.vertex_groups[n].index;ids[n]=[v.index for v in mesh.data.vertices if any(g.group==gi for g in v.groups)]
 errors=[];seaterrors=[];knees=[]
 for f in range(sc.frame_start,sc.frame_end+1):
  sc.frame_set(f);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());seaterrors.append(min(ev.data.vertices[i].co.z for i in ids['pelvis'])-seat)
  for sign,side in [(1,'l'),(-1,'r')]:
   expected=sole+(11*math.sin((f-1)/30*math.tau+(0 if sign==1 else math.pi)) if clip=='HeroBikePedal' else 0);actual=min(ev.data.vertices[i].co.z for i in ids['foot_'+side]);errors.append(abs(actual-expected));hip=rig.pose.bones['thigh_'+side].head;knee=rig.pose.bones['calf_'+side].head;ankle=rig.pose.bones['foot_'+side].head;t=(hip.z-knee.z)/max(.001,hip.z-ankle.z);knees.append((knee-hip.lerp(ankle,t)).y)
 item={'clip':clip,'frames_checked':sc.frame_end-sc.frame_start+1,'maximum_sole_support_error_cm':max(errors),'maximum_seat_contact_error_cm':max(abs(x) for x in seaterrors),'signed_seat_min':min(seaterrors),'signed_seat_max':max(seaterrors),'maximum_reverse_knee_cm':max(knees)};reports.append(item);print(item,flush=True)
assert all(x['maximum_sole_support_error_cm']<.25 and x['maximum_reverse_knee_cm']<.25 for x in reports),reports
(out/'riding_contact_validation.json').write_text(json.dumps({'status':'PASS','clips':reports},indent=2));print('ALL_RIDING_CONTACTS_AND_KNEES_PASS',flush=True)
