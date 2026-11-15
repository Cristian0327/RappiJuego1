import bpy,json,math,sys,hashlib,struct
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/TrafficDetailed'
report=json.loads((OUT/'blender_validation.json').read_text()) if (OUT/'blender_validation.json').exists() else {}
for file in OUT.glob('SK_*.blend'):
 if '--cars-only' in sys.argv and file.stem=='SK_TransMilenio':continue
 bpy.ops.wm.open_mainfile(filepath=str(file));scene=bpy.context.scene
 mesh=bpy.data.objects[file.stem];rig=mesh.parent
 assert len(mesh.data.materials)==1,file.name
 assert mesh.data.color_attributes.get('TrafficColor'),file.name
 assert not any(o.type=='FONT' for o in scene.objects)
 assert all(len(v.groups)==1 and abs(v.groups[0].weight-1)<1e-6 for v in mesh.data.vertices)
 # Every wheel is rigidly weighted; the rear body belongs to the articulation.
 weights={group.name:0 for group in mesh.vertex_groups}
 for v in mesh.data.vertices:weights[mesh.vertex_groups[v.groups[0].group].name]+=1
 assert all(count>0 for count in weights.values()),weights
 scene.frame_set(1);deps=bpy.context.evaluated_depsgraph_get();evaluated=mesh.evaluated_get(deps);a=[v.co.copy() for v in evaluated.data.vertices]
 scene.frame_set(16);deps=bpy.context.evaluated_depsgraph_get();evaluated=mesh.evaluated_get(deps);moved={group:0 for group in weights}
 for i,v in enumerate(evaluated.data.vertices):
  group=mesh.vertex_groups[mesh.data.vertices[i].groups[0].group].name
  if (v.co-a[i]).length>.005:moved[group]+=1
 assert all(moved[n]>10 for n in moved if n.startswith('wheel_')),moved
 assert moved['root']==0,moved
 if 'articulation' in moved:assert moved['articulation']>100,moved
 scene.frame_set(1);scene.render.filepath=str(OUT/(file.stem[3:]+'_Review.png'));scene.cycles.samples=32
 if '--no-render' not in sys.argv:bpy.ops.render.render(write_still=True)
 assert mesh.data.uv_layers.get('TrafficUV'),file.stem
 geometry_hash=hashlib.sha256(b''.join(struct.pack('<fff',*v.co) for v in mesh.data.vertices)).hexdigest()
 report[file.stem]={'vertices':len(mesh.data.vertices),'faces':len(mesh.data.polygons),'rigid_weights':True,'one_material':True,'vertex_colors':True,'geometry_hash':geometry_hash,'text_objects':0,'vertices_by_bone':weights,'moving_vertices_frame_16':moved}
 (OUT/'blender_validation.json').write_text(json.dumps(report,indent=2))
 print('DETAILED_REVIEW_PASS',file.stem,flush=True)
if '--fleet20' in sys.argv:
 catalog=json.loads((OUT/'fleet20_catalog.json').read_text(encoding='utf-8'))
 assert len(catalog)==20 and len({report['SK_'+s['name']]['geometry_hash'] for s in catalog})==20
 assert len(report)==24 and not any('Willys' in n or 'SITP' in n for n in report)
print('ALL_DETAILED_RIGS_PASS',flush=True)
