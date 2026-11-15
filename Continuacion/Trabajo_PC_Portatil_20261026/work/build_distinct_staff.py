import bpy, math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Stores'
U=.025
palette={'skin':(.72,.43,.26,1),'skinDark':(.38,.19,.10,1),'skinLight':(.91,.66,.45,1),'hair':(.065,.038,.025,1),'gray':(.46,.46,.43,1),'white':(.89,.88,.79,1),'ink':(.028,.035,.05,1),'purple':(.33,.13,.38,1),'red':(.68,.07,.05,1),'blue':(.03,.43,.57,1),'green':(.20,.39,.12,1),'gold':(.91,.57,.12,1),'denim':(.08,.13,.25,1)}
for role in range(5):
 bpy.ops.wm.read_factory_settings(use_empty=True);v={}
 def box(c,x0,x1,y0,y1,z0,z1):
  for x in range(x0,x1):
   for y in range(y0,y1):
    for z in range(z0,z1):v[x,y,z]=c
 def oval(c,z0,z1,rx,ry,cx=0,cy=0):
  for x in range(cx-rx,cx+rx):
   for y in range(cy-ry,cy+ry):
    if ((x+.5-cx)/rx)**2+((y+.5-cy)/ry)**2<=1:box(c,x,x+1,y,y+1,z0,z1)
 # Individually authored height, build, stance, face and occupation accessories.
 width=[10,14,8,9,10][role];waist=[27,29,35,32,29][role];shoulder=[47,53,56,54,49][role];head=shoulder+3;skin=['skinLight','skin','skinDark','skinLight','skin'][role];shirt=['purple','white','blue','white','gold'][role]
 for x in [-5,5]:box('ink',x-4,x+4,-8,5,0,4);box('denim',x-3,x+3,-3,4,4,waist)
 oval(shirt,waist,shoulder,width,6)
 for side in [-1,1]:
  x=side*(width+2);box(shirt,x-3,x+3,-3,4,shoulder-13,shoulder-2);box(skin,x-2,x+2,-4,2,shoulder-20,shoulder-13)
 oval(skin,head,head+15,8 if role!=1 else 10,7)
 box(skin,-2,2,-9,-6,head+5,head+9)
 for x in [-5,4]:box('white',x,x+3,-7,-6,head+8,head+11);box('ink',x+1,x+2,-8,-7,head+8,head+10)
 box('skinDark',-3,3,-7,-6,head+3,head+4)
 if role==0:
  # Doña Rosalba: silver bun, round spectacles, broad purple dress and patterned apron.
  oval('gray',head+13,head+17,9,8);oval('gray',head+16,head+23,5,5,cy=5)
  for x in [-6,2]:
   box('gold',x,x+5,-9,-8,head+6,head+7);box('gold',x,x+5,-9,-8,head+12,head+13)
   for xx in [x,x+4]:box('gold',xx,xx+1,-9,-8,head+7,head+12)
  box('gold',-1,2,-9,-8,head+10,head+11);oval('purple',16,waist,12,7);box('white',-8,8,-8,-6,22,44)
  for x in range(-7,8,3):box('purple',x,x+1,-9,-8,24,35)
 elif role==1:
  # Beto: stocky cook, bald forehead, sideburns, black moustache and red apron.
  for x in [-10,8]:box('hair',x,x+2,-2,6,head+4,head+15)
  box('hair',-6,6,-9,-8,head+4,head+6);box('red',-11,11,-8,-6,22,49)
  for x in [-7,6]:box('red',x,x+2,-7,-6,49,54)
  box('white',4,10,-9,-8,28,40);box('gray',-8,-4,-9,-8,31,37)
 elif role==2:
  # Nico: tall, dark skin, asymmetric curls, headphones and utility vest.
  for x in range(-8,9,4):
   for y in range(-5,7,4):oval('hair',head+13,head+19+(x%3),3,3,x,y)
  for x in [-11,9]:box('ink',x,x+2,-2,5,head+4,head+13);box('gold',x-1,x+3,-1,4,head+6,head+11)
  box('ink',-10,11,0,2,head+20,head+22);box('ink',-6,6,-7,-6,waist+1,shoulder-3);box('blue',-2,2,-8,-7,waist+9,shoulder-8)
 elif role==3:
  # Inés: straight bob, white lab coat, teal blouse, square glasses and name badge.
  oval('hair',head+13,head+17,9,8)
  for x in [-9,7]:box('hair',x,x+2,-2,6,head,head+14)
  box('blue',-4,4,-7,-6,waist+2,shoulder-1);box('white',-10,10,-5,5,21,waist)
  for x in [-6,2]:box('ink',x,x+5,-9,-8,head+7,head+8);box('ink',x,x+5,-9,-8,head+11,head+12)
  box('gold',4,8,-8,-7,shoulder-7,shoulder-4)
 else:
  # Mar: short curly auburn hair, freckles, green gardening apron and flower pin.
  for x in range(-8,9,4):
   for y in [-3,1,5]:oval('red',head+12,head+18,3,3,x,y)
  box('green',-9,9,-8,-6,19,shoulder-3);box('wood' if 'wood' in palette else 'gold',-6,6,-9,-8,27,34)
  for x in [-6,-4,4,6]:box('skinDark',x,x+1,-8,-7,head+6,head+7)
  box('white',6,10,-9,-8,shoulder-5,shoulder-1);box('gold',7,9,-10,-9,shoulder-4,shoulder-2)
 mats=[];keys=list(palette)
 for n,c in palette.items():
  m=bpy.data.materials.new('NPC_'+n);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mats.append(m)
 verts=[];faces=[];ids=[]
 for q,c in v.items():
  for ax in range(3):
   for sign in [-1,1]:
    nn=list(q);nn[ax]+=sign
    if tuple(nn) in v:continue
    corners=[(0,0),(1,0),(1,1),(0,1)]
    if sign<0:corners.reverse()
    f=[]
    for a,b in corners:
     r=list(q);r[ax]+=sign==1;r[(ax+1)%3]+=a;r[(ax+2)%3]+=b;f.append(len(verts));verts.append(tuple(j*U for j in r))
    faces.append(f);ids.append(keys.index(c))
 name=['SM_Cashier','SM_Chef','SM_TechClerk','SM_Pharmacist','SM_Florist'][role];mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
 for m in mats:mesh.materials.append(m)
 for poly,i in zip(mesh.polygons,ids):poly.material_index=i
 o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=440;scene.render.resolution_y=560;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.22,.22,.22);scene.view_settings.view_transform='Standard'
 bpy.ops.object.camera_add(location=(2,-4,2.5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.5;scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(1,-3,4));bpy.context.object.data.energy=450;bpy.context.object.data.size=4;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('FIVE_DISTINCT_STAFF_COMPLETE')
