from pathlib import Path
for file in ['work/retarget_main_mixamo.py','work/retarget_mixamo_walk.py','work/retarget_mixamo_idle.py']:
 p=Path(file);s=p.read_text();s=s.replace('from mathutils import Quaternion','from mathutils import Quaternion,Vector').replace('from mathutils import Matrix','from mathutils import Matrix,Vector')
 needle=" target.animation_data.action.name=";i=s.index(needle)
 s=s[:i]+'''  rootbone=target.pose.bones['root'];rootbone.location=(0,0,0);bpy.context.view_layer.update()
  mesh=next(o for o in before if o.type=='MESH' and o.parent==target);evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());floor=min((evaluated.matrix_world@v.co).z for v in evaluated.data.vertices)
  rootbone.location=rootbone.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,-floor));rootbone.keyframe_insert('location',frame=f,group='root');bpy.context.view_layer.update()
'''+s[i:];p.write_text(s)
