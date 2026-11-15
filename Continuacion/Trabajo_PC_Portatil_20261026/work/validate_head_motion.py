import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];out=r/'outputs/DeliveryArt/Crowd';report={}
for f in sorted(out.glob('SK_Citizen*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(f));o=next(o for o in bpy.data.objects if o.type=='MESH');rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
 head=rig.data.bones['head'];ids=[v.index for v in o.data.vertices if any(o.vertex_groups[g.group].name=='head' for g in v.groups)]
 assert ids
 for vi in ids:
  g=o.data.vertices[vi].groups;assert len(g)==1 and o.vertex_groups[g[0].group].name=='head' and abs(g[0].weight-1)<1e-6
 deviation=0;positions=[]
 for frame in [1,8,16,24]:
  bpy.context.scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);deform=rig.pose.bones['head'].matrix@head.matrix_local.inverted()
  for vi in ids:deviation=max(deviation,(ev.data.vertices[vi].co-deform@o.data.vertices[vi].co).length)
  positions.append(tuple(ev.data.vertices[ids[0]].co))
 assert deviation<.001,(f.name,deviation)
 assert max((Vector(p)-Vector(positions[0])).length for p in positions)>.01
 report[f.stem]={'head_vertices':len(ids),'max_attachment_error_cm':deviation,'walk_head_moves':True}
report['status']='PASS';(r/'work/head_motion_validation.json').write_text(json.dumps(report,indent=2));print('HEAD_MOTION_ALL_60_PASS')
