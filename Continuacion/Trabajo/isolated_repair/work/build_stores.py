import bpy, math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Stores';out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
colors={'cream':(.83,.76,.56,1),'dark':(.035,.055,.06,1),'green':(.08,.38,.18,1),'orange':(.95,.22,.035,1),'red':(.65,.035,.02,1),'white':(.9,.92,.85,1),'steel':(.30,.37,.39,1),'wood':(.33,.16,.06,1),'skin':(.56,.31,.16,1),'bread':(.78,.42,.12,1),'lettuce':(.22,.57,.035,1),'milk':(.12,.43,.72,1)}
mats={}
for n,c in colors.items():
 m=bpy.data.materials.new('Store_'+n);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mats[n]=m

def box(n,p,s,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[m]);return o

def export(n):
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();bpy.context.object.name=n;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(n+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/(n+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 for o in list(bpy.context.scene.objects):
  if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)

def product(kind,p=(0,0,0)):
 x,y,z=p
 def b(n,d,s,m):box(n,(x+d[0],y+d[1],z+d[2]),s,m)
 if kind==0:
  b('Carton',(0,0,.17),(.16,.16,.34),'white');b('BlueLabel',(0,-.085,.15),(.14,.012,.14),'milk');b('Fold',(0,0,.37),(.12,.14,.06),'milk')
 elif kind==1:
  b('RiceBag',(0,0,.15),(.25,.12,.30),'cream');b('RiceStripe',(0,-.065,.16),(.23,.012,.09),'red');b('Seal',(0,0,.32),(.27,.13,.03),'white')
 elif kind==2:
  for a in [-.09,.09]:
   for c in [-.08,.08]:b('Apple',(a,c,.09),(.15,.14,.15),'red');b('Leaf',(a,c,.18),(.04,.05,.03),'lettuce')
 else:
  b('Tray',(0,0,.02),(.50,.42,.04),'white')
  for zz,s,m in [(.07,.29,'bread'),(.11,.32,'lettuce'),(.15,.28,'wood'),(.19,.30,'red'),(.24,.29,'bread'),(.28,.23,'bread')]:b('Burger',(0,0,zz),(s,s,.045),m)
  for a in [-.07,.02,.09]:b('Sesame',(a,-.03,.31),(.025,.045,.012),'cream')
for i,n in enumerate(['SM_Milk','SM_Rice','SM_Apples','SM_Burger']):product(i);export(n)
for chef in [False,True]:
 for x in [-.17,.17]:box('Shoe',(x,-.04,.09),(.24,.38,.18),'dark');box('Leg',(x,0,.39),(.21,.24,.48),'dark')
 box('Shirt',(0,0,.98),(.66,.35,.70),'white' if chef else 'green');box('Apron',(0,-.20,.85),(.48,.04,.73),'orange' if chef else 'cream')
 box('Head',(0,0,1.52),(.42,.37,.43),'skin');box('Hair',(0,.04,1.75),(.46,.38,.12),'dark')
 for x in [-.11,.11]:box('Eye',(x,-.195,1.56),(.055,.025,.055),'dark')
 box('Nose',(0,-.22,1.48),(.08,.09,.09),'skin')
 for x in [-.43,.43]:box('Arm',(x,0,1.06),(.18,.27,.48),'white' if chef else 'green');box('Hand',(x,-.04,.78),(.18,.22,.20),'skin')
 if chef:box('ChefHat',(0,0,1.9),(.49,.40,.25),'white');box('HatTop',(0,0,2.05),(.58,.46,.12),'white')
 else:box('Cap',(0,0,1.84),(.48,.42,.10),'green');box('CapBill',(0,-.27,1.79),(.48,.22,.06),'green')
 export('SM_Chef' if chef else 'SM_Cashier')
for food in [False,True]:
 accent='orange' if food else 'green'
 # Exterior facade faces -X, with a recessed doorway and striped awning.
 for y in [-1.65,1.65]:box('Facade',(1.05,y,1.45),(.25,1.4,2.9),'cream')
 box('DoorLintel',(1.05,0,2.75),(.3,1.9,.3),accent);box('DoorGlass',(1.12,0,1.23),(.06,1.35,2.46),'dark');box('Handle',(.98,-.43,1.15),(.08,.06,.38),'steel')
 box('Sign',(1,0,3.3),(.25,4.8,.7),accent)
 for i in range(12):box('Awning',(.40,-2.2+i*.4,2.75),(1.4,.39,.12),accent if i%2 else 'cream')
 for y in [-2.15,2.15]:box('Post',(-.15,y,1.3),(.10,.10,2.6),accent)
 export('SM_RestaurantFront' if food else 'SM_MarketFront')
 # Walkable room: wall collisions preserve the doorway instead of one convex hull.
 box('Floor',(0,0,-.08),(10,8,.16),'cream')
 for x in [-5,5]:box('Wall',(x,0,1.8),(.16,8,3.6),'cream')
 box('Back',(0,4,1.8),(10,.16,3.6),'cream');box('Ceiling',(0,0,3.65),(10,8,.12),'white')
 for x in [-3,3]:box('Front',(x,-4,1.8),(4,.16,3.6),'cream')
 box('DoorTop',(0,-4,3.1),(2,.16,1),'cream')
 for x in range(-4,5):
  for y in range(-3,4):box('Tile',(x,y,.006),(.97,.97,.012),'cream' if (x+y)%2 else 'white')
 for x in [-4.86,4.86]:box('WallStripe',(x,0,1.5),(.03,7.8,.18),accent)
 box('Checkout',(2.7,-1.25,.50),(2.6,.75,1),'wood');box('CounterTop',(2.7,-1.25,1.03),(2.75,.90,.10),'dark');box('Register',(3.2,-1.22,1.25),(.45,.32,.34),'steel');box('Screen',(3.2,-1.40,1.30),(.34,.02,.18),'green')
 if not food:
  for x in [-3.5,3.5]:
   box('ShelfBack',(x,.6,1.10),(.9,3.6,2.2),'green')
   for z in [.35,1,1.65]:
    box('Shelf',(x,.6,z),(1.15,3.8,.08),'wood')
    for y in [-.8,-.3,.2,.7,1.2,1.7]:product(0 if x<0 else 1,(x,y,z+.05))
  for x in [-.8,0,.8]:box('ProduceCrate',(x,2.8,.48),(.75,.8,.8),'wood');product(2,(x,2.8,.90))
 else:
  box('KitchenCounter',(0,3.35,.55),(8,1,1.1),'steel')
  for x in [-2,0,2]:box('Grill',(x,3.2,1.15),(1.4,.7,.08),'dark');product(3,(x,3.2,1.20))
  box('Hood',(0,3.4,2.6),(5,1.3,.4),'steel')
  for y in [-1.8,1.0]:
   box('Table',(-3,y,.80),(1.4,1,.12),'wood');box('TableLeg',(-3,y,.4),(.15,.15,.8),'dark')
   for x in [-4.1,-1.9]:box('ChairSeat',(x,y,.43),(.5,.55,.12),accent);box('ChairBack',(x,y+.25,.75),(.5,.10,.7),accent)
 export('SM_RestaurantInterior' if food else 'SM_MarketInterior')
print('VOXEL_STORES_EXPORTED')
