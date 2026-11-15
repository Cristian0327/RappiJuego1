import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/DeliveryArt/HighFidelity'
COL={'ink':(.035,.055,.075,1),'oak':(.32,.15,.065,1),'honey':(.65,.36,.12,1),'sage':(.20,.37,.24,1),'cream':(.84,.78,.61,1),'ivory':(.91,.90,.79,1),'red':(.63,.09,.05,1),'blue':(.045,.29,.38,1),'steel':(.4,.45,.46,1),'leaf':(.14,.34,.07,1),'pink':(.75,.20,.36,1),'gold':(.94,.58,.08,1)}
random.seed(142)
def box(p,s,c):
 x,y,z=p;a,b,d=[v/2 for v in s];off=len(V)
 V.extend([(x+i*a,y+j*b,z+k*d) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
 for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:F.append(tuple(off+i for i in q));M.append(list(COL).index(c))
def disk(p,r,h,c):
 x,y,z=p;step=.025
 for i in range(-math.ceil(r/step),math.ceil(r/step)):
  yy=(i+.5)*step
  if abs(yy)>=r:continue
  w=math.floor(math.sqrt(r*r-yy*yy)/step)*step
  if w:box((x,y+yy,z+h/2),(w*2,step,h),c)
def bottle(x,y,z,c):
 disk((x,y,z),.065,.20,c);disk((x,y,z+.20),.04,.06,c);disk((x,y,z+.26),.043,.035,'gold');box((x,y-.065,z+.12),(.075,.008,.075),'cream')
def bloom(x,y,z,c):
 box((x,y,z+.22),(.02,.02,.44),'leaf')
 for k in range(8):
  a=k*math.pi/4;box((x+.07*math.cos(a),y+.07*math.sin(a),z+.45),(.07,.07,.045),c)
 disk((x,y,z+.47),.04,.025,'gold');box((x+.045,y,z+.17),(.10,.04,.025),'sage')
names=['SM_MarketInterior','SM_RestaurantInterior','SM_TechInterior','SM_PharmacyInterior','SM_FloristInterior']
for kind,name in enumerate(names):
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'outputs/DeliveryArt/Stores'/f'{name}.blend'))
 V=[];F=[];M=[]
 # Fitted joinery, wall texture, service counter and raised panels.
 for x in [-4.88,4.88]:
  box((x,0,.11),(.06,7.8,.18),'oak')
  for y in range(26):box((x,-3.75+y*.30,.60),(.055,.022,.85),'honey')
  box((x,0,1.05),(.08,7.8,.055),'honey')
 for x in [1.55,2.1,2.65,3.2,3.75]:
  box((x,-1.638,.5),(.49,.025,.72),['sage','red','blue','ivory','sage'][kind]);box((x,-1.657,.84),(.45,.025,.025),'honey')
 for x in [-4,-2,0,2,4]:
  box((x,3.87,3.08),(1.94,.06,.065),'oak')
  for i in range(7):box((x-.85+i*.27,3.875,3.33),(.10,.06,.40),'oak')
 # A sculpted wall clock, utility conduit and switch plates.
 box((-1.8,3.82,2.7),(.49,.10,.49),'oak');box((-1.8,3.75,2.7),(.42,.025,.42),'cream')
 for i in range(12):
  a=i*math.pi/6;box((-1.8+.17*math.sin(a),3.731,2.7+.17*math.cos(a)),(.025,.018,.025),'ink')
 box((-1.8,3.72,2.78),(.025,.018,.16),'ink');box((-1.75,3.717,2.7),(.12,.018,.025),'ink')
 for side in [-1,1]:
  box((side*1.13,-3.88,1.4),(.16,.05,.23),'ivory');box((side*1.13,-3.915,1.4),(.055,.025,.12),'steel')
 if kind==0:
  # Bogotá corner shop: drinks refrigerator, hanging snacks, scale, woven baskets.
  box((-4.40,2.95,1.2),(.8,1.45,2.4),'ivory');box((-3.979,2.95,1.22),(.035,1.27,2.12),'ink')
  for z in [.35,.75,1.15,1.55,1.95]:
   box((-3.94,2.95,z),(.12,1.22,.025),'steel')
   for y in [2.48,2.72,2.96,3.20,3.44]:bottle(-3.89,y,z+.02,['red','blue','sage'][int(z*10)%3])
  box((-3.82,3.51,1.23),(.07,.045,.65),'steel')
  for x in [-.8,0,.8]:
   for z in [.18,.34,.50,.66,.82]:box((x,2.37,z),(.76,.025,.035),'honey')
   for i in range(8):box((x-.33+i*.095,2.365,.50),(.025,.03,.69),'oak')
  for i in range(8):
   for j in range(3):box((-4.84,-2.9+i*.18,1.65+j*.25),(.075,.15,.20),['red','gold','sage'][(i+j)%3])
  box((1.8,-1.25,1.16),(.40,.35,.19),'steel');box((1.8,-1.25,1.275),(.50,.45,.045),'ivory');box((1.8,-1.44,1.16),(.23,.02,.08),'ink')
 elif kind==1:
  # Kitchen details: burner grates, hanging utensils, vent baffles, condiments.
  for x in [-2,0,2]:
   for dx in [-.45,.45]:
    disk((x+dx,3.2,1.21),.16,.025,'steel')
    for d in [-.12,0,.12]:box((x+dx+d,3.2,1.245),(.025,.38,.025),'ink')
   for dx in [-.3,0,.3]:disk((x+dx,2.83,1.10),.04,.035,'ink')
  for i in range(24):box((-2.30+i*.20,2.77,2.56),(.075,.04,.29),'ink')
  box((3.8,3.8,2.25),(1.6,.055,.055),'steel')
  for i in range(5):
   x=3.2+i*.26;box((x,3.75,2.02),(.028,.025,.43),'steel');disk((x,3.71,1.77),.085,.035,'steel')
  for y in [-1.8,1]:
   box((-3,y,.89),(1.40,.24,.02),'cream')
   for x in [-3.3,-2.7]:disk((x,y,.92),.16,.02,'ivory');disk((x,y,.942),.11,.01,'cream')
   bottle(-3,y+.3,.88,'red');bottle(-2.8,y+.3,.88,'gold')
 elif kind==2:
  # Independent repair shop: cable spools, components, repair station and RGB keys.
  for x in [-.85,.85]:
   box((x,3.30,1.02),(.58,.42,.08),'blue')
   for i in range(5):
    for j in range(3):box((x-.22+i*.10,3.15+j*.12,1.075),(.06,.07,.015),'gold')
  for i in range(8):
   x=-1.05+i*.30;box((x,3.71,2.40),(.21,.05,.27),'cream');box((x,3.673,2.39),(.15,.025,.18),'ink')
  for y in [-.7,.2,1.1]:
   for z in [.45,1.10,1.75]:
    box((-2.89,y,z+.06),(.05,.42,.12),'ink')
    for j in range(9):box((-2.857,y-.18+j*.043,z+.09),(.02,.025,.045),['blue','gold','pink'][j%3])
  box((2.1,-1.25,1.15),(.5,.3,.06),'ink');box((2.1,-1.15,1.35),(.5,.035,.35),'blue')
 elif kind==3:
  # Apothecary storage: drawers, medicine bottles, small refrigerator and scales.
  for x in [-1.4,-.7,0,.7,1.4]:
   for z in [1.4,1.75,2.1]:
    box((x,3.79,z),(.67,.30,.31),'ivory');box((x,3.61,z),(.19,.045,.03),'steel');box((x,3.60,z+.08),(.13,.008,.055),'blue')
  for y in [-.7,0,.7,1.4]:
   for z in [.4,1.05,1.7]:bottle(-2.91,y,z,'honey');bottle(2.91,y,z,'ivory')
  box((-4.4,3.0,.88),(.8,1.30,1.76),'ivory');box((-3.98,3,1.0),(.03,1.1,1.40),'blue');box((-3.95,3.45,1.05),(.06,.04,.42),'steel')
 else:
  # Flower workshop: densely layered blooms, wrapping rolls, lattice and baskets.
  for x in [-3.8,-2.8,-1.8,1.8,2.8,3.8]:
   for i in range(14):bloom(x+random.uniform(-.18,.18),3+random.uniform(-.20,.20),random.uniform(.40,.66),['pink','ivory','gold','red'][i%4])
  for i in range(19):box((-4.5+i*.5,3.79,2.2),(.04,.04,1.5),'oak')
  for z in [1.5,1.8,2.1,2.4,2.7,2.95]:box((0,3.79,z),(9,.04,.035),'honey')
  for i in range(24):
   x=random.uniform(-4.5,4.5);z=random.uniform(1.6,2.9);box((x,3.73,z),(.12,.05,.06),'leaf');box((x+.07,3.74,z+.07),(.065,.055,.10),'sage')
  for x in [1.7,2.0,2.3]:disk((x,-1.25,1.1),.09,.38,'cream')
 mesh=bpy.data.meshes.new('Crafted fittings');mesh.from_pydata(V,[],F);mesh.update();o=bpy.data.objects.new('Crafted fittings',mesh);bpy.context.collection.objects.link(o)
 for key,c in COL.items():
  mat=bpy.data.materials.new('ENV_'+key);mat.diffuse_color=c;mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mesh.materials.append(mat)
 for p,i in zip(mesh.polygons,M):p.material_index=i
 bpy.ops.object.select_all(action='DESELECT');objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 # Interior camera, no roof removal or altered geometry in the exported model.
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1280;sc.render.resolution_y=900;sc.render.resolution_percentage=100
 sc.world=bpy.data.worlds.new('Interior studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.3
 bpy.ops.object.camera_add(location=(0,-3.78,2.35));cam=bpy.context.object;cam.data.lens=17;cam.rotation_euler=(Vector((0,1.0,1.30))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
 for x in [-2.5,2.5]:
  bpy.ops.object.light_add(type='AREA',location=(x,-.5,3.3));lamp=bpy.context.object;lamp.data.energy=350;lamp.data.size=4
 sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);print('HF_INTERIOR_DONE',name,flush=True)
p=OUT/'palette.json';colors=json.loads(p.read_text());colors.update({'ENV_'+k:v for k,v in COL.items()});p.write_text(json.dumps(colors))
