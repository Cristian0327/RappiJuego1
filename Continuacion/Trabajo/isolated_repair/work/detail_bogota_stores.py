import bpy, math, random
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Stores'
random.seed(77)
colors={'brick':(.43,.16,.07,1),'brickLight':(.61,.26,.12,1),'mortar':(.48,.45,.36,1),'sage':(.16,.30,.15,1),'ochre':(.67,.38,.08,1),'navy':(.035,.09,.22,1),'mint':(.35,.64,.53,1),'wood':(.30,.13,.045,1),'cream':(.82,.75,.56,1),'white':(.88,.88,.80,1),'metal':(.35,.40,.42,1),'black':(.028,.033,.04,1),'red':(.72,.045,.025,1),'gold':(.90,.56,.04,1),'leaf':(.16,.42,.06,1),'pink':(.81,.25,.40,1),'coffee':(.08,.032,.013,1)}
def setup():
 global mats
 mats={}
 for n,c in colors.items():
  m=bpy.data.materials.get('Detail_'+n) or bpy.data.materials.new('Detail_'+n);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mats[n]=m

def box(n,p,s,m):
 x,y,z=p;dx,dy,dz=[v*.5 for v in s];verts=[(x+a*dx,y+b*dy,z+c*dz) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.materials.append(mats[m]);o=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(o);return o

def stepped(n,p,r,h,m):
 # Octagonal / circular forms remain authored square voxels.
 x,y,z=p;step=.035
 for i in range(-math.ceil(r/step),math.ceil(r/step)):
  for j in range(-math.ceil(r/step),math.ceil(r/step)):
   if ((i+.5)*step)**2+((j+.5)*step)**2<r*r:box(n,(x+(i+.5)*step,y+(j+.5)*step,z+h/2),(step,step,h),m)

def flower(p,color):
 x,y,z=p;box('Stem',(x,y,z+.17),(.018,.018,.34),'leaf')
 for a in range(6):
  t=a*math.pi/3;box('Petal',(x+math.cos(t)*.045,y+math.sin(t)*.045,z+.35),(.055,.055,.045),color)
 box('Pollen',(x,y,z+.385),(.035,.035,.035),'gold')
 box('Leaf',(x+.035,y,z+.23),(.075,.035,.025),'leaf')

def packet(p,kind):
 x,y,z=p;box('Sealed goods',(x,y,z+.12),(.16,.13,.24),'cream' if kind==0 else 'white');box('Color band',(x,y-.07,z+.12),(.14,.012,.075),['red','mint','navy'][kind%3]);box('Folded seal',(x,y,z+.245),(.18,.14,.025),'white')

def export(name):
 mesh=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in mesh:o.select_set(True)
 bpy.context.view_layer.objects.active=mesh[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.context.scene['modeling_reference']='../References/Bogota_Comercios_SinTexto.png'
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')

for kind,name in enumerate(['SM_MarketInterior','SM_RestaurantInterior','SM_TechInterior','SM_PharmacyInterior','SM_FloristInterior']):
 if name=='SM_MarketInterior':continue
 bpy.ops.wm.open_mainfile(filepath=str(out/(name+'.blend')));setup()
 # Skirting, tiled backsplash, visible lamps and payment terminal.
 for x in [-4.87,4.87]:box('Skirting',(x,0,.13),(.07,7.8,.22),'wood')
 for x in [-3,0,3]:box('Ceiling light',(x,0,3.48),(1.3,.3,.08),'white')
 box('Card terminal',(2.45,-1.65,1.12),(.18,.25,.12),'black');box('Terminal screen',(2.45,-1.68,1.185),(.13,.13,.01),'mint')
 for j in range(3):
  for i in range(3):box('Key',(2.40+i*.045,-1.59+j*.025,1.19),(.027,.017,.01),'white')
 if kind==1:
  for x in [-3,-1,1,3]:
   for z in [1.3,1.6,1.9]:box('Kitchen tile',(x,3.86,z),(1.96,.02,.28),'white')
  for x in [-4.1,-1.9]:
   for y in [-1.8,1]:
    for dx in [-.19,.19]:
     for dy in [-.2,.2]:box('Chair leg',(x+dx,y+dy,.19),(.065,.065,.38),'metal')
  # Bakery glass-frame display and Colombian breads on metal trays.
  box('Bakery cabinet',(-3.6,2.25,.50),(1.8,.85,1),'wood')
  for z in [1.04,1.40]:
   box('Tray',(-3.6,2.25,z),(1.75,.8,.045),'metal')
   for x in [-4.2,-3.8,-3.4,-3]:
    for y in [2.05,2.4]:stepped('Almojabana',(x,y,z+.025),.12,.09,'gold');stepped('Bread crown',(x,y,z+.115),.09,.035,'cream')
  for x in [-4.5,-2.7]:box('Cabinet post',(x,2.25,1.25),(.045,.85,.65),'metal')
  for x in [-.6,0]:
   stepped('Tinto thermos',(x,3.1,1.2),.13,.42,'metal');stepped('Lid',(x,3.1,1.62),.14,.055,'black');box('Spout',(x,2.92,1.5),(.07,.16,.06),'black')
  for x in [.4,.6,.8]:stepped('Tinto cup',(x,2.95,1.2),.065,.1,'white');stepped('Coffee',(x,2.95,1.29),.05,.008,'coffee')
  stepped('Ajiaco pot',(1.3,3.15,1.2),.23,.2,'metal');stepped('Soup',(1.3,3.15,1.39),.20,.012,'cream')
  for i in range(7):box('Papa',(1.3+random.uniform(-.13,.13),3.15+random.uniform(-.13,.13),1.41),(.04,.04,.02),'gold')
 else:
  # Stock on exposed front edge of shelving, not buried inside shelf backs.
  for side in [-1,1]:
   for y in [-.8,-.3,.2,.7,1.2,1.7]:
    for z in [.42,1.07,1.72]:
     x=side*2.95
     if kind==4:
      stepped('Flower pot',(x,y,z),.10,.12,'wood')
      for i in range(3):flower((x+(i-1)*.05,y,z+.1),['red','pink','white'][(i+int(y*10))%3])
     else:
      packet((x,y,z),kind)
      if kind==2:box('Phone display',(x-side*.085,y,z+.13),(.015,.09,.17),'black');box('Screen',(x-side*.10,y,z+.14),(.01,.07,.12),'navy')
  if kind==0:
   for x in [-.8,0,.8]:
    for y in [2.55,2.75,2.95]:
     for dx in [-.2,0,.2]:stepped('Papa criolla',(x+dx,y,.92),.075,.10,'gold' if x<0 else 'cream')
   for i in range(5):box('Rice sack',(-4.4,-2.7,.12+i*.18),(.48,.65,.17),'cream')
  elif kind==2:
   box('Repair pegboard',(0,3.83,1.9),(3,.06,1.9),'navy')
   for x in [-1,-.5,0,.5,1]:
    for z in [1.3,1.6,1.9,2.2,2.5]:box('Peg hole',(x,3.79,z),(.035,.02,.035),'black')
    box('Screwdriver',(x,3.72,1.9),(.055,.055,.38),'metal');box('Tool grip',(x,3.72,2.11),(.11,.07,.16),'gold')
   box('Repair bench',(0,3.25,.9),(2.8,.9,.12),'wood');box('Laptop',(0,3.20,1),(0.6,.42,.04),'black');box('Laptop screen',(0,3.4,1.2),(.6,.04,.4),'navy')
  elif kind==3:
   for x in [-1.4,-.7,0,.7,1.4]:
    for z in [.3,.65,1]:box('Drawer',(x,3.78,z),(.67,.35,.32),'mint');box('Drawer handle',(x,3.57,z),(.18,.06,.025),'metal')
  else:
   for x in [-3.8,-2.8,-1.8,1.8,2.8,3.8]:
    stepped('Flower bucket',(x,3,.03),.2,.4,'metal')
    for i in range(8):flower((x+random.uniform(-.15,.15),3+random.uniform(-.15,.15),.38),['red','gold','white','pink'][i%4])
 export(name)
# Replace empty generic façades with brick, plaster patches, grilles and corrugated awnings.
for kind,name in enumerate(['SM_MarketFront','SM_RestaurantFront']):
 bpy.ops.wm.open_mainfile(filepath=str(out/(name+'.blend')));setup()
 for side in [-1,1]:
  for z in range(14):
   for y in range(3):box('Bogota brick',(1.215,side*(1.06+y*.39+(z%2)*.08),.12+z*.23),(.08,.37,.21),'brickLight' if (y+z)%3 else 'brick')
  for y in range(6):box('Folded grille',(.8,side*(1.0+y*.055),1.25),(.07,.025,2.5),'metal')
 for y in range(31):box('Corrugated awning',(.40,-2.4+y*.16,2.84),(1.5,.10,.07),'metal')
 box('Doorframe top',(.91,0,2.57),(.12,1.56,.09),'metal')
 for side in [-1,1]:box('Doorframe',(.91,side*.74,1.28),(.12,.07,2.57),'metal')
 export(name)
print('BOGOTA_REFERENCE_ENVIRONMENTS_COMPLETE')
