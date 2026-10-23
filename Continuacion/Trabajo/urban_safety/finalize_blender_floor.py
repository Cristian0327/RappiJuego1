import bpy,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_safety');m=json.loads((P/'leveled_manifest.json').read_text())
for row in m['instances']:
 if row['mesh'].startswith('SM_Mapa_') and row['mesh'][8:].isdigit():
  o=bpy.data.objects.get(row['source'])
  if o and not 'Relieve' in row['source']:o.location.z=.2;row['location'][2]=.2
verts=[];faces=[]
for x0,y0,x1,y1 in json.loads((P/'safety_floor_rects.json').read_text()):
 i=len(verts);verts += [(x0/100,-y0/100,-.02),(x0/100,-y1/100,-.02),(x1/100,-y1/100,-.02),(x1/100,-y0/100,-.02)];faces.append([i,i+1,i+2,i+3])
me=bpy.data.meshes.new('SM_Bogota_UrbanSolidFloor');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);ob.hide_render=True;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(P/'export/SM_Bogota_UrbanSolidFloor.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE');(P/'leveled_manifest.json').write_text(json.dumps(m));bpy.ops.wm.save_as_mainfile(filepath=str(P/'Mapa_Bogota_Nivelado.blend'));print('FLUSH_BASES_AND_SOLID_CITY_FLOOR_READY',len(faces))
