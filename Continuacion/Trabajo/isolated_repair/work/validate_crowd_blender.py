import bpy,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd';catalog=json.loads((out/'catalog.json').read_text());report={}
for c in catalog:
 bpy.ops.wm.open_mainfile(filepath=str(out/('SK_'+c['name']+'.blend')))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH');assert len(rig.data.bones)==24 and len(mesh.data.materials)==1
 assert rig.animation_data.action.name.startswith(('AN_CrowdWalk','AN_CrowdCane'))
 assert all(v.groups and abs(sum(g.weight for g in v.groups)-1)<.001 for v in mesh.data.vertices)
 heights=[]
 for f in range(1,bpy.context.scene.frame_end+1,3):
  bpy.context.scene.frame_set(f);ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());heights.append(min(v.co.z for v in ev.data.vertices)*c['scale'])
 report[c['name']]={'bones':24,'triangles':c['triangles'],'height_m':c['height_m'],'foot_minimum_cm':min(heights),'foot_maximum_cm':max(heights),'animation':'Mixamo walk, adapted and grounded'}
 assert (min(heights)>-5 and min(heights)<5),(c['name'],heights)
report['status']='PASS';(out/'blender_validation.json').write_text(json.dumps(report,indent=2));print('CROWD_BLENDER_VALIDATION_PASS')
