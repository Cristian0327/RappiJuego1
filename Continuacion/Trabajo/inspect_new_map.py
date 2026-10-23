import bpy,json,math
from mathutils import Vector
from pathlib import Path
p=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');p.mkdir(exist_ok=True)
a=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 b=[o.matrix_world@Vector(x) for x in o.bound_box];lo=[min(v[i] for v in b) for i in range(3)];hi=[max(v[i] for v in b) for i in range(3)]
 a.append({'name':o.name,'min':lo,'max':hi,'polygons':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials]})
(p/'objects.json').write_text(json.dumps({'units':bpy.context.scene.unit_settings.scale_length,'objects':a},indent=2))
print('MAP_AUDIT',len(a),'objects',sum(x['polygons'] for x in a),'polygons')
lo=Vector([min(o['min'][i] for o in a) for i in range(3)]);hi=Vector([max(o['max'][i] for o in a) for i in range(3)]);c=(lo+hi)/2
bpy.ops.object.camera_add(location=(c.x,c.y,hi.z+max(hi.x-lo.x,hi.y-lo.y)*1.5));cam=bpy.context.object;cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=max(hi.x-lo.x,hi.y-lo.y)*1.08;bpy.context.scene.camera=cam
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.filepath=str(p/'overview.png');bpy.ops.render.render(write_still=True)
