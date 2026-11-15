import bpy,random,math,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Surfaces';out.mkdir(exist_ok=True)
random.seed(87)
# Authored pixel surfaces, deliberately restrained so voxel silhouettes remain legible.
for name,kind in [('Masonry','brick'),('Timber','wood'),('Paper','paper'),('Metal','metal')]:
 im=bpy.data.images.new(name,width=128,height=128);pixels=[]
 for y in range(128):
  for x in range(128):
   n=random.uniform(-.035,.035);v=.78+n
   if kind=='wood':v+=.10*math.sin(x*.35+math.sin(y*.08))+.045*math.sin(x*.9)
   elif kind=='brick':v-=.16 if y%32<2 or (x+(y//32%2)*32)%64<2 else 0
   elif kind=='paper':v+=.035 if x%32==0 else 0
   elif kind=='metal':v+=.045*math.sin(y*.4)
   pixels.extend((v,v,v,1))
 im.pixels=pixels;im.filepath_raw=str(out/(name+'.png'));im.file_format='PNG';im.save()
# Face projection keeps texel density stable on all voxel sides.
for folder,pattern in [('Shops','*.blend'),('HighFidelity','SM_*.blend')]:
 for file in (root/'outputs/DeliveryArt'/folder).glob(pattern):
  if folder=='HighFidelity' and (file.stem.endswith('Interior') or file.stem in ['SM_Cashier','SM_Chef','SM_TechClerk','SM_Pharmacist','SM_Florist'] or 'Customer' in file.stem):continue
  bpy.ops.wm.open_mainfile(filepath=str(file));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
  for o in obs:
   uv=o.data.uv_layers.get('Surface') or o.data.uv_layers.new(name='Surface');o.data.uv_layers.active=uv
   for p in o.data.polygons:
    axis=max(range(3),key=lambda i:abs(p.normal[i]));a,b=[i for i in range(3) if i!=axis]
    for li in p.loop_indices:
     v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[a]*2,v[b]*2)
   o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.export_scene.fbx(filepath=str(file.with_suffix('.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
print('SURFACE_UVS_AND_TEXTURES_AUTHORED')
