import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/People';report=[]
for file in sorted(out.glob('SK_*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(file));mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH');rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
 bad=sum(1 for v in mesh.data.vertices if len(v.groups)!=1 or abs(sum(g.weight for g in v.groups)-1)>1e-5)
 spanning=sum(1 for p in mesh.data.polygons if len({mesh.data.vertices[v].groups[0].group for v in p.vertices})>1)
 row={'asset':file.stem,'bones':len(rig.data.bones),'triangles':sum(len(p.vertices)-2 for p in mesh.data.polygons),'rigid_weights':bad==0,'faces_crossing_joints':spanning,'walk':'Blender planted-foot IK','idle_duration_seconds':5}
 assert bad==0 and spanning==0,row;report.append(row)
(out/'rig_manifest.json').write_text(json.dumps(report,indent=2));print('RIG_GEOMETRY_VALIDATED',len(report))
