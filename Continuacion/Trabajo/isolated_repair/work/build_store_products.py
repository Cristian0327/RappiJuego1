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

SOURCE="import bpy, math\nfrom pathlib import Path\nfrom mathutils import Vector\nout=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Stores';out.mkdir(parents=True,exist_ok=True)\nbpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)\ncolors={'cream':(.83,.76,.56,1),'dark':(.035,.055,.06,1),'green':(.08,.38,.18,1),'orange':(.95,.22,.035,1),'red':(.65,.035,.02,1),'white':(.9,.92,.85,1),'steel':(.30,.37,.39,1),'wood':(.33,.16,.06,1),'skin':(.56,.31,.16,1),'bread':(.78,.42,.12,1),'lettuce':(.22,.57,.035,1),'milk':(.12,.43,.72,1)}\nmats={}\nfor n,c in colors.items():\n m=bpy.data.materials.new('Store_'+n);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mats[n]=m\n\ndef box(n,p,s,m):\n bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[m]);return o\n\ndef export(n):\n obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')\n for o in obs:o.select_set(True)\n bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();bpy.context.object.name=n;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')\n bpy.ops.wm.save_as_mainfile(filepath=str(out/(n+'.blend')))\n bpy.ops.export_scene.fbx(filepath=str(out/(n+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')\n for o in obs:\n  if o.name in bpy.data.objects:bpy.data.objects.remove(o,do_unlink=True)\n for o in list(bpy.context.scene.objects):\n  if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)\n\ndef product(kind,p=(0,0,0)):\n x,y,z=p\n def b(n,d,s,m):box(n,(x+d[0],y+d[1],z+d[2]),s,m)\n if kind==0:\n  b('Carton',(0,0,.17),(.16,.16,.34),'white');b('BlueLabel',(0,-.085,.15),(.14,.012,.14),'milk');b('Fold',(0,0,.37),(.12,.14,.06),'milk')\n elif kind==1:\n  b('RiceBag',(0,0,.15),(.25,.12,.30),'cream');b('RiceStripe',(0,-.065,.16),(.23,.012,.09),'red');b('Seal',(0,0,.32),(.27,.13,.03),'white')\n elif kind==2:\n  for a in [-.09,.09]:\n   for c in [-.08,.08]:b('Apple',(a,c,.09),(.15,.14,.15),'red');b('Leaf',(a,c,.18),(.04,.05,.03),'lettuce')\n else:\n  b('Tray',(0,0,.02),(.50,.42,.04),'white')\n  for zz,s,m in [(.07,.29,'bread'),(.11,.32,'lettuce'),(.15,.28,'wood'),(.19,.30,'red'),(.24,.29,'bread'),(.28,.23,'bread')]:b('Burger',(0,0,zz),(s,s,.045),m)\n  for a in [-.07,.02,.09]:b('Sesame',(a,-.03,.31),(.025,.045,.012),'cream')\nfor i,n in enumerate(['SM_Milk','SM_Rice','SM_Apples','SM_Burger']):product(i);export(n)\nfor chef in [False,True]:\n for x in [-.17,.17]:box('Shoe',(x,-.04,.09),(.24,.38,.18),'dark');box('Leg',(x,0,.39),(.21,.24,.48),'dark')\n box('Shirt',(0,0,.98),(.66,.35,.70),'white' if chef else 'green');box('Apron',(0,-.20,.85),(.48,.04,.73),'orange' if chef else 'cream')\n box('Head',(0,0,1.52),(.42,.37,.43),'skin');box('Hair',(0,.04,1.75),(.46,.38,.12),'dark')\n for x in [-.11,.11]:box('Eye',(x,-.195,1.56),(.055,.025,.055),'dark')\n box('Nose',(0,-.22,1.48),(.08,.09,.09),'skin')\n for x in [-.43,.43]:box('Arm',(x,0,1.06),(.18,.27,.48),'white' if chef else 'green');box('Hand',(x,-.04,.78),(.18,.22,.20),'skin')\n if chef:box('ChefHat',(0,0,1.9),(.49,.40,.25),'white');box('HatTop',(0,0,2.05),(.58,.46,.12),'white')\n else:box('Cap',(0,0,1.84),(.48,.42,.10),'green');box('CapBill',(0,-.27,1.79),(.48,.22,.06),'green')\n export('SM_Chef' if chef else 'SM_Cashier')\nfor food in [False,True]:\n accent='orange' if food else 'green'\n # Exterior facade faces -X, with a recessed doorway and striped awning.\n for y in [-1.65,1.65]:box('Facade',(1.05,y,1.45),(.25,1.4,2.9),'cream')\n box('DoorLintel',(1.05,0,2.75),(.3,1.9,.3),accent);box('DoorGlass',(1.12,0,1.23),(.06,1.35,2.46),'dark');box('Handle',(.98,-.43,1.15),(.08,.06,.38),'steel')\n box('Sign',(1,0,3.3),(.25,4.8,.7),accent)\n for i in range(12):box('Awning',(.40,-2.2+i*.4,2.75),(1.4,.39,.12),accent if i%2 else 'cream')\n for y in [-2.15,2.15]:box('Post',(-.15,y,1.3),(.10,.10,2.6),accent)\n export('SM_RestaurantFront' if food else 'SM_MarketFront')\n # Walkable room: wall collisions preserve the doorway instead of one convex hull.\n box('Floor',(0,0,-.08),(10,8,.16),'cream')\n for x in [-5,5]:box('Wall',(x,0,1.8),(.16,8,3.6),'cream')\n box('Back',(0,4,1.8),(10,.16,3.6),'cream');box('Ceiling',(0,0,3.65),(10,8,.12),'white')\n for x in [-3,3]:box('Front',(x,-4,1.8),(4,.16,3.6),'cream')\n box('DoorTop',(0,-4,3.1),(2,.16,1),'cream')\n for x in range(-4,5):\n  for y in range(-3,4):box('Tile',(x,y,.006),(.97,.97,.012),'cream' if (x+y)%2 else 'white')\n for x in [-4.86,4.86]:box('WallStripe',(x,0,1.5),(.03,7.8,.18),accent)\n box('Checkout',(2.7,-1.25,.50),(2.6,.75,1),'wood');box('CounterTop',(2.7,-1.25,1.03),(2.75,.90,.10),'dark');box('Register',(3.2,-1.22,1.25),(.45,.32,.34),'steel');box('Screen',(3.2,-1.40,1.30),(.34,.02,.18),'green')\n if not food:\n  for x in [-3.5,3.5]:\n   box('ShelfBack',(x,.6,1.10),(.9,3.6,2.2),'green')\n   for z in [.35,1,1.65]:\n    box('Shelf',(x,.6,z),(1.15,3.8,.08),'wood')\n    for y in [-.8,-.3,.2,.7,1.2,1.7]:product(0 if x<0 else 1,(x,y,z+.05))\n  for x in [-.8,0,.8]:box('ProduceCrate',(x,2.8,.48),(.75,.8,.8),'wood');product(2,(x,2.8,.90))\n else:\n  box('KitchenCounter',(0,3.35,.55),(8,1,1.1),'steel')\n  for x in [-2,0,2]:box('Grill',(x,3.2,1.15),(1.4,.7,.08),'dark');product(3,(x,3.2,1.20))\n  box('Hood',(0,3.4,2.6),(5,1.3,.4),'steel')\n  for y in [-1.8,1.0]:\n   box('Table',(-3,y,.80),(1.4,1,.12),'wood');box('TableLeg',(-3,y,.4),(.15,.15,.8),'dark')\n   for x in [-4.1,-1.9]:box('ChairSeat',(x,y,.43),(.5,.55,.12),accent);box('ChairBack',(x,y+.25,.75),(.5,.10,.7),accent)\n export('SM_RestaurantInterior' if food else 'SM_MarketInterior')\nprint('VOXEL_STORES_EXPORTED')\n"

def extra(kind,p=(0,0,0)):
 x,y,z=p
 def b(n,d,s,m):box(n,(x+d[0],y+d[1],z+d[2]),s,m)
 if kind=='SM_Headphones':
  b('RetailBox',(0,.05,.23),(.38,.13,.46),'dark')
  for a in [-.13,.13]:b('Earcup',(a,-.05,.19),(.10,.10,.16),'milk');b('Headband',(a,-.04,.31),(.035,.06,.18),'steel')
  b('TopBand',(0,-.04,.40),(.28,.06,.04),'steel')
 elif kind=='SM_Keyboard':
  b('Keyboard',(0,0,.025),(.48,.19,.05),'dark')
  for a in range(10):
   for c in range(3):b('Key',(-.21+a*.046,-.06+c*.055,.06),(.035,.042,.025),'cream' if a<8 else 'orange')
 elif kind=='SM_PhoneBox':
  b('Box',(0,0,.05),(.22,.39,.10),'white');b('Phone',(0,0,.12),(.15,.29,.04),'dark');b('Screen',(0,0,.145),(.12,.24,.008),'milk')
 elif kind=='SM_FirstAid':
  b('Case',(0,0,.16),(.38,.20,.32),'white');b('Cross',(0,-.11,.16),(.20,.025,.055),'red');b('CrossV',(0,-.11,.16),(.055,.025,.20),'red')
 elif kind=='SM_Medicine':
  b('SealedBox',(0,0,.12),(.28,.10,.24),'white');b('Label',(0,-.055,.12),(.25,.012,.08),'green')
 elif kind=='SM_Bouquet':
  b('Wrap',(0,0,.15),(.18,.18,.30),'cream')
  for a,c in [(-.12,0),(.12,0),(0,-.12),(0,.12),(0,0)]:b('Stem',(a,c,.30),(.035,.035,.32),'green');b('Bloom',(a,c,.48),(.15,.15,.12),'red' if a else 'orange')
for n in ['SM_Headphones','SM_Keyboard','SM_PhoneBox','SM_FirstAid','SM_Medicine','SM_Bouquet']:extra(n);export(n)
# Derive finished interiors from the supermarket, replace every shelf item.
for kind,names in [('Tech',['SM_Headphones','SM_Keyboard','SM_PhoneBox']),('Pharmacy',['SM_FirstAid','SM_Medicine','SM_FirstAid']),('Florist',['SM_Bouquet','SM_Bouquet','SM_Bouquet'])]:
 # Keep authored material library.
 # Rebuild via the original authoring program, omitting groceries and produce crates.
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 base=Path(__file__).read_text() if False else ''
 room=SOURCE[SOURCE.index(' # Walkable room:'):SOURCE.index(" export('SM_RestaurantInterior'")]
 room=room.replace('product(0 if x<0 else 1,(x,y,z+.05))',"extra(names[0 if x<0 else 1],(x,y,z+.05))").replace('product(2,(x,2.8,.90))',"extra(names[2],(x,2.8,.90))")
 food=False;accent='milk' if kind=='Tech' else 'green';exec('if True:\n'+room)
 export('SM_'+kind+'Interior')
