import bpy, math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Stores'
U=.025
# Modeling target: References/Encargados_Detallados.png, generated before this revision.
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
 # Sculpt against the concept: cheek/jaw steps, ears, brows and layered garments.
 # Erase the old flat helmet hair; rebuild in offset locks at varied heights.
 for q in list(v):
  if q[2]>=head+13:del v[q]
 for z,rx,ry in [(head-1,5,5),(head,6,6),(head+1,7,6),(head+12,7,6),(head+13,6,6)]:oval(skin,z,z+1,rx,ry)
 for side in [-1,1]:
  oval(skin,head+5,head+10,2,2,side*(10 if role==1 else 8),0)
  box('hair',side*4-2,side*4+2,-8,-7,head+12,head+13)
  x=side*(width+2)
  # Individual fingertips, cuff seam, elbow pad, shoulder layering.
  for j in range(3):box(skin,x-2+j,x-1+j,-5,-3,shoulder-22,shoulder-19)
  box('white' if role in [1,3] else shirt,x-3,x+3,-4,5,shoulder-14,shoulder-12)
  for dz in range(3):box(shirt,x-3+dz,x+3-dz,-3,4,shoulder-2+dz,shoulder-1+dz)
  # Feet have toe, heel, sole, tongue and laces rather than a single block.
  x=side*5
  box('white' if role in [2,3] else 'hair',x-4,x+4,-8,5,1,3)
  box('white' if role==3 else 'blue' if role==2 else 'hair',x-3,x+3,-8,3,3,6)
  box('ink',x-2,x+2,-6,-1,5,7)
  for yy in [-5,-3,-1]:box('gold' if role==4 else 'white',x-2,x+2,yy,yy+1,7,8)
  box('denim',x-4,x+4,-4,5,8,10)
 if role==0:
  # Swept locks and low bun, cardigan lapels, brass buttons, floral blouse.
  for x in range(-9,9,3):oval('gray',head+13,head+17+(9-abs(x))//3,3,7,x,1)
  for z in range(head+3,head+14,3):oval('gray',z,z+3,4,4,-7,5)
  oval('gray',head+5,head+13,5,4,-5,8)
  box('white',-5,5,-8,-6,38,shoulder)
  for x,z in [(-3,40),(2,44),(-1,47),(3,39)]:box('green',x,x+1,-9,-8,z,z+3);box('red',x-1,x+2,-10,-9,z+2,z+4)
  for x in [-8,6]:box('purple',x,x+2,-9,-7,36,shoulder)
  for z in [38,42,46]:box('gold',-8,-6,-10,-9,z,z+2)
  for x in [-6,3]:box('white',x,x+4,-10,-8,24,31);box('gold',x,x+4,-11,-10,29,30)
  for x in [-5,4]:box('blue',x,x+1,-10,-9,30,34)
  box('white',width+1,width+7,-7,-5,shoulder-22,shoulder-9)
  for z in range(shoulder-21,shoulder-10,3):box('gray',width+2,width+5,-8,-7,z,z+1)
 elif role==1:
  # Bald crown is rounded in steps, side hair asymmetric; collar and apron ties.
  oval(skin,head+13,head+15,8,6);oval(skin,head+15,head+16,6,5)
  for side in [-1,1]:
   oval('hair',head+10,head+15,3,5,side*8,2)
   for j in range(4):box('white',side*j-2,side*j+2,-8,-6,shoulder+1-j,shoulder+3-j)
  for x in [-5,4]:box('ink',x,x+2,-9,-8,shoulder-4,shoulder-2)
  box('red',-14,14,5,7,waist+5,waist+7)
  for x,z in [(-7,30),(3,42),(-4,46),(6,24)]:box('gold',x,x+3,-9,-8,z,z+2)
  box('white',5,10,-10,-8,25,40)
  for z in [27,29]:box('red',5,10,-11,-10,z,z+1)
  box('ink',-10,-3,-10,-8,29,38)
  for x in [-9,-7,-5]:box('gold',x,x+1,-10,-9,36,44)
 elif role==2:
  # Dense independent curls with deliberate uneven hairline.
  for x in range(-9,10,3):
   for y in range(-6,8,3):oval('hair',head+12+(abs(x+y)%3),head+18+(x*y%4),2,2,x,y)
  # Headphones rest on shoulders, open head silhouette.
  for q in list(v):
   if abs(q[0])>=10 and q[2]>head:del v[q]
  for side in [-1,1]:
   box('ink',side*6-2,side*6+2,-7,-3,shoulder-2,shoulder+5);box('blue',side*6-1,side*6+1,-8,-7,shoulder-1,shoulder+4)
   box('blue',side*6-1,side*6+1,-8,-7,waist+1,shoulder-6)
   box('denim',side*6-3,side*6+3,-6,-3,waist-11,waist-3)
  for z in range(shoulder-10,shoulder-2):
   a=(z-(shoulder-10))//2+1;box('blue',-a,-a+1,-9,-8,z,z+1);box('blue',a,a+1,-9,-8,z,z+1)
  box('white',-2,3,-10,-8,shoulder-15,shoulder-10);box('gray',-1,2,-11,-10,shoulder-14,shoulder-12)
  box('ink',width,width+5,-8,-3,shoulder-23,shoulder-12);box('ink',width-1,width+6,-12,-4,shoulder-13,shoulder-9);box('red',width,width+4,-13,-12,shoulder-12,shoulder-10)
 elif role==3:
  # Bob with cheek framing tips, coat collar, folded lapels and pocket contents.
  for x in range(-9,9,3):oval('hair',head+12,head+17+(8-abs(x))//3,3,7,x,1)
  for side in [-1,1]:
   for z in range(head-1,head+13,3):oval('hair',z,z+3,2,5,side*8,2)
   for j in range(5):box('white',side*(j+2)-1,side*(j+2)+2,-9,-7,shoulder-5+j,shoulder-3+j)
   box('white',side*6-3,side*6+3,-9,-7,waist-5,waist+1)
  box('white',4,9,-10,-8,shoulder-11,shoulder-4)
  box('green',6,7,-11,-10,shoulder-10,shoulder-5);box('green',4,9,-11,-10,shoulder-8,shoulder-7)
  for x in [5,7]:box('red' if x==5 else 'blue',x,x+1,-10,-9,shoulder-4,shoulder)
 else:
  for x in range(-9,10,3):
   for y in range(-6,8,3):oval('red',head+11,head+17+(x*y%3),2,2,x,y)
  for z in range(head-2,head+10,3):oval('red',z,z+3,3,3,7,6)
  for z in range(head+7,head+20):box('white',4,7,2,7,z,z+1)
  for z in range(head+8,head+20,4):box('green',4,7,1,2,z,z+2)
  for side in [-1,1]:
   box('green',side*7-1,side*7+1,-8,-6,shoulder-3,shoulder+2)
   box('gold',side*5-4,side*5+4,-5,5,9,13)
  box('gold',-7,0,-10,-8,25,32);box('white',-6,-4,-11,-10,30,35)
  for x in [4,7]:box('red',x,x+2,-11,-9,24,32);box('gray',x,x+1,-11,-10,32,37)
 # Three-view pass: silhouette, side volume and back construction follow the turnaround.
 # Replace the generic legs on Rosalba with a stepped skirt and short visible calves.
 if role==0:
  for q in list(v):
   if 9<=q[2]<27:del v[q]
  for z in range(10,29):oval('purple',z,z+1,12-(z-10)//7,7)
  for side in [-1,1]:box('skinLight',side*5-2,side*5+2,-2,3,5,11)
  # Bun now sits at the back rather than becoming a crest on top.
  for q in list(v):
   if q[2]>head+18:del v[q]
  for z,r in [(head+5,3),(head+6,4),(head+8,5),(head+11,4),(head+13,3)]:oval('gray',z,z+2,r,3,0,8)
  box('white',-10,10,6,8,waist+6,waist+8)
 if role in [0,1,4]:
  tie='white' if role==0 else 'red' if role==1 else 'green';z=waist+7
  box(tie,-width,width,6,8,z,z+2)
  for side in [-1,1]:
   box(tie,side*3-2,side*3+2,8,10,z-1,z+3)
   for j in range(7):box(tie,side*(1+j//3),side*(1+j//3)+2,8,9,z-j-1,z-j)
 if role==1:
  for side in [-1,1]:
   x=side*(width+2);box('denim',x-3,x+3,-4,4,shoulder-15,shoulder-8)
  # Back neck strap and stepped collar, pocket towel visible from profile.
  for j in range(8):box('red',-7+j,-5+j,6,8,shoulder-j//2,shoulder+2-j//2)
  box('white',width-2,width+1,-2,4,waist,waist+12)
 if role==2:
  # Navy overshirt has real thickness and cyan cuff/hem detail on sides and back.
  for q,c in list(v.items()):
   if c=='blue' and waist<q[2]<shoulder and q[1]>=-6:v[q]='denim'
  box('blue',-8,8,6,7,waist,waist+2)
  for side in [-1,1]:
   x=side*(width+2);box('blue',x-3,x+3,-4,5,shoulder-10,shoulder-8)
   box('ink',side*8-1,side*8+2,-2,3,waist-10,waist-3)
  box('denim',-7,7,5,7,shoulder-3,shoulder-1)
 if role==3:
  # Coat back yoke, belt and central split are visible in rear view.
  box('white',-9,9,5,7,22,shoulder-2);box('gray',-1,1,7,8,22,30)
  box('white',-8,8,7,8,waist+5,waist+7)
  for side in [-1,1]:box('blue',side*(width+2)-2,side*(width+2)+2,-4,4,shoulder-15,shoulder-13)
  # Complete square eyeglass frames including side temples.
  for x in [-6,2]:
   for xx in [x,x+4]:box('ink',xx,xx+1,-9,-8,head+8,head+12)
  for side in [-1,1]:box('ink',side*7,side*7+1,-8,1,head+11,head+12)
 if role==4:
  # Fabric scarf trails down back, with voxel floral pattern and knot.
  for z in range(head-2,head+15):box('white',3,7,8,9,z,z+1)
  for z in range(head,head+15,4):box('red',4,6,9,10,z,z+2);box('green',3,4,9,10,z-1,z+1)
  box('white',2,8,8,11,head+6,head+9)
  for side in [-1,1]:box('green',side*7-1,side*7+1,5,7,waist+6,shoulder)
 # Taper sleeve/hand silhouettes at the sides instead of rectangular straight arms.
 for side in [-1,1]:
  x=side*(width+2)
  for q in list(v):
   if shoulder-21<=q[2]<shoulder-14 and abs(q[0]-x)>1 and abs(q[0]-x)<=3 and q[1]>=3:del v[q]
 # Small color variation makes voxel planes legible without coarse giant surfaces.
 import random
 rng=random.Random(410+role)
 for key,c in list(v.items()):
  if key[0]%2==0 and key[2]%2==0 and rng.random()<.25 and c not in ['ink','skin','skinDark','skinLight']:
   variant=c+'_shade'
   if variant not in palette:palette[variant]=tuple(t*.91 for t in palette[c][:3])+(1,)
   v[key]=variant
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
 ref=bpy.data.images.load(str(out.parent/'References/Bogota_Encargados_TresVistas.png'),check_existing=True);ref.pack();guide=bpy.data.objects.new('REFERENCE - three views',None);bpy.context.collection.objects.link(guide);guide.empty_display_type='IMAGE';guide.data=ref;guide.hide_render=True;guide.hide_viewport=True;
 o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.context.scene['modeling_reference']='../References/Bogota_Encargados_TresVistas.png';bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=440;scene.render.resolution_y=560;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.22,.22,.22);scene.view_settings.view_transform='Standard'
 bpy.ops.object.camera_add(location=(2,-4,2.5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.5;scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(1,-3,4));bpy.context.object.data.energy=450;bpy.context.object.data.size=4;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 (out/'Turnarounds').mkdir(exist_ok=True)
 for label,pos in [('Front',(0,-6,1)),('Side',(6,0,1)),('Back',(0,6,1))]:
  bpy.context.object.location=(pos[0]*.6,pos[1]*.6,4);cam.location=pos;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/'Turnarounds'/(name+'_'+label+'.png'));bpy.ops.render.render(write_still=True)
print('FIVE_DISTINCT_STAFF_COMPLETE')
