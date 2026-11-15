import bpy, json, struct, math
from pathlib import Path
from mathutils import Vector
out=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs')
raw=(out/'voxel_explorer.glb').read_bytes()
magic,version,length=struct.unpack_from('<III',raw,0)
n,kind=struct.unpack_from('<II',raw,12)
gltf=json.loads(raw[20:20+n])
assert magic==0x46546c67 and version==2 and length==len(raw)
assert len(gltf['meshes'])==1
assert len(gltf['meshes'][0]['primitives'])==1
assert len(gltf['materials'])==1
assert len(gltf['skins'])==1
assert len(gltf['images'])==1 and 'bufferView' in gltf['images'][0]
assert not gltf.get('animations')
triangles=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives'])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(out/'voxel_explorer.glb'))
mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
assert all(len(v.groups)==1 and abs(v.groups[0].weight-1)<1e-5 for v in mesh.data.vertices)
assert all(p.area>1e-12 for p in mesh.data.polygons)
assert all(math.isfinite(c) for v in mesh.data.vertices for c in v.co)
assert all(math.isfinite(c) for uv in mesh.data.uv_layers.active.data for c in uv.uv)
deps=bpy.context.evaluated_depsgraph_get()
before=[(mesh.matrix_world @ v.co).copy() for v in mesh.evaluated_get(deps).data.vertices]
rig.pose.bones['forearm.L'].rotation_mode='XYZ'
rig.pose.bones['forearm.L'].rotation_euler.x=.4
bpy.context.view_layer.update()
after=[mesh.matrix_world @ v.co for v in mesh.evaluated_get(deps).data.vertices]
moved=sum((a-b).length>1e-5 for a,b in zip(after,before))
assert moved>0 and moved<len(before)
report={'result':'PASS','glb_meshes':1,'glb_primitives':1,'materials':1,'embedded_textures':1,'triangles':triangles,'skin_joints':len(gltf['skins'][0]['joints']),'all_vertices_have_one_full_weight':True,'zero_area_faces':0,'rig_pose_check':'PASS','vertices_moved_in_forearm_test':moved,'animation_clips':0,'note':'Validated by importing exported GLB into Blender. No game-engine integration test performed.'}
(out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('VALIDATION',json.dumps(report),flush=True)
