import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/Shops'
# Geometry is already remodeled; join product instances and keep interior/exterior wall layers separate.
for label,W,D in [('Market',20,18),('FreshMarket',20,18),('Restaurant',20,16),('FastFood',20,16),('Tech',20,16),('Components',20,16),('Pharmacy',20,18),('Florist',14,12)]:
 for suffix in ['Interior','Front']:
  file=OUT/('SM_'+label+suffix+'.blend');bpy.ops.wm.open_mainfile(filepath=str(file));sc=bpy.context.scene
  if sc.get('export_finalized',False):continue
  obj=bpy.data.objects['SM_'+label+suffix]
  if suffix=='Front':
   # Boundary cuboids use unshared vertices, so move complete wall pieces, preserving texel/voxel size.
   for i in range(0,len(obj.data.vertices),8):
    group=list(obj.data.vertices[i:i+8]);c=sum((v.co for v in group),__import__('mathutils').Vector())/len(group)
    if abs(c.x)>W/2-.08 and c.y>1:
     for v in group:v.co.x+=.16 if c.x>0 else -.16
    if c.y>D-.2 and c.z<4.7:
     for v in group:v.co.y+=.16
  bpy.ops.object.select_all(action='DESELECT')
  for mesh in [o for o in sc.objects if o.type=='MESH']:mesh.select_set(True)
  bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
  colors={};indices=[]
  for p in obj.data.polygons:
   m=obj.data.materials[p.material_index];key=m.name.split('.')[0];colors.setdefault(key,tuple(m.diffuse_color));indices.append(key)
  obj.data.materials.clear();ordered=list(colors)
  for name in ordered:
   m=bpy.data.materials.new(name);m.diffuse_color=colors[name];m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=colors[name];obj.data.materials.append(m)
  for p,key in zip(obj.data.polygons,indices):p.material_index=ordered.index(key)
  sc['export_finalized']=True;bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.export_scene.fbx(filepath=str(file.with_suffix('.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z');print('FINALIZED_COMMERCIAL',label,suffix,len(obj.data.polygons),len(ordered),flush=True)
