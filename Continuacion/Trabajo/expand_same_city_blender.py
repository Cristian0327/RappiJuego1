import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Matrix
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');m=json.loads((W/'manifest.json').read_text());f=m['spacing_expansion'];base=json.loads((W/'before_spacing_expansion/manifest.json').read_text());done=set()
for item in base['instances']:
 name=item['source'];o=bpy.data.objects.get(name)
 if not o or name in done or name.startswith('SM_Mapa_Road_'):continue
 done.add(name)
 if name.startswith('Relieve'):o.matrix_world=Matrix.Diagonal((f,f,1,1))@o.matrix_world
 else:
  t=o.matrix_world.copy();t.translation.x*=f;t.translation.y*=f;o.matrix_world=t
mat=bpy.data.materials.get('Mapa_ColorVoxel');assert mat
for ri,rd in enumerate(m['roads']):
 name='SM_Mapa_Road_%d'%ri;old=bpy.data.objects.get(name)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 verts=[];faces=[];colors=[]
 for i,(c,side,half,inner) in enumerate(zip(rd['center'],rd['side'],rd['halfwidth'],rd['innerwidth'])):
  for width,z in [(-half,0),(-half,.20),(-inner,.20),(-inner,.04),(inner,.04),(inner,.20),(half,.20),(half,0)]:verts.append((c[0]+side[0]*width,c[1]+side[1]*width,z))
  if i:
   for j in range(7):faces.append(((i-1)*8+j,(i-1)*8+j+1,i*8+j+1,i*8+j));colors.append((.12,.15,.17) if j==3 else (.55,.57,.58) if j in [1,5] else (.68,.69,.66))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(mat);a=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');arr=[]
 for p,col in zip(mesh.polygons,colors):arr.extend(list(col)+[1] for _ in p.loop_indices)
 a.data.foreach_set('color',np.asarray(arr,dtype=np.float32).ravel());mesh.color_attributes.active_color=a;o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(W/'export'/(name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR')
bpy.context.scene['CitySpacingExpansion']=f;bpy.ops.wm.save_as_mainfile(filepath=str(W/'Mapa_Completo_Andenes_Ampliado.blend'));print('SAME_CITY_EXPANDED',len(done),f)
