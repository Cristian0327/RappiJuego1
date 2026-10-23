from pathlib import Path
import bpy, math, copy
from mathutils import Vector
base=Path(__file__).resolve().parents[1]
code=(base/'work/build_character.py').read_text(encoding='utf-8');exec(code[:code.index('# Remove overlaps')])
original=copy.deepcopy(parts);out=base/'outputs/DeliveryArt/Stores'
for chef in [False,True]:
 parts=copy.deepcopy(original)
 parts={k:v for k,v in parts.items() if not k.startswith(('06 |','14 |'))}
 if chef:
  parts={k:v for k,v in parts.items() if not k.startswith('03 |')}
  p=part('Chef toque','head');ellipse(p,'white',69,74,10,9,cy=1);ellipse(p,'white',74,82,12,10,cy=1);ellipse(p,'ice_light',82,85,10,9,cy=1)
 p=part('Work apron','chest');box(p,'white' if chef else 'ice',-8,8,-6,-5,29,50);box(p,'teal_dark',-5,5,-7,-6,34,40)
 vox={q:m for v in parts.values() for q,m in v.items()}
 materials=[]
 for n,col in rgb.items():
  if n.startswith('teal'):col=(.83,.83,.76) if chef else (.16,.38,.17)
  if n.startswith('orange'):col=(.83,.83,.76) if chef else (.23,.48,.21)
  m=bpy.data.materials.new(('Chef_' if chef else 'Cashier_')+n);m.diffuse_color=(*col,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);materials.append(m)
 keys=list(rgb);verts=[];faces=[];ids=[]
 for q,m in vox.items():
  for ax in range(3):
   for sign in [-1,1]:
    neighbor=list(q);neighbor[ax]+=sign
    if tuple(neighbor) in vox:continue
    a=(ax+1)%3;b=(ax+2)%3;corners=[(0,0),(1,0),(1,1),(0,1)]
    if sign<0:corners.reverse()
    f=[]
    for u,v in corners:
     r=list(q);r[ax]+=sign==1;r[a]+=u;r[b]+=v;f.append(len(verts));verts.append(tuple(t*UNIT for t in r))
    faces.append(f);ids.append(keys.index(m))
 for name,m,(x0,x1,y0,y1,z0,z1),bone in details:
  if chef and 'Cap' in name:continue
  k=len(verts);verts.extend([(x*UNIT,y*UNIT,z*UNIT) for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]])
  for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:faces.append([k+j for j in f]);ids.append(keys.index(m))
 mesh=bpy.data.meshes.new('Same_player_voxel_grid');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('SM_Chef' if chef else 'SM_Cashier',mesh);bpy.context.collection.objects.link(o)
 for m in materials:mesh.materials.append(m)
 for poly,idx in zip(mesh.polygons,ids):poly.material_index=idx
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(o.name+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=500;scene.render.resolution_y=600;scene.render.resolution_percentage=100
 bpy.ops.object.camera_add(location=(2,-4,2.5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.9))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.2;scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(1,-3,4));bpy.context.object.data.energy=450;bpy.context.object.data.size=4
 scene.render.filepath=str(out/(o.name+'.png'));bpy.ops.render.render(write_still=True)
 for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
print('STAFF_MATCH_PLAYER_GRID',UNIT)
