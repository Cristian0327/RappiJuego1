exec((__import__('pathlib').Path(__file__).parent/'refine_hf_interiors.py').read_text().split("names=['SM_MarketInterior'")[0])
OUT=ROOT/'outputs/DeliveryArt/Shops';OUT.mkdir(exist_ok=True)
def finalize(name,interior):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 for k,c in COL.items():
  mat=bpy.data.materials.new('ENV_'+k);mat.diffuse_color=c;mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mesh.materials.append(mat)
 for p,i in zip(mesh.polygons,M):p.material_index=i
 # Product duplicates share source mesh until the single optimized export join.
 bpy.ops.object.select_all(action='DESELECT');obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 sc=bpy.context.scene;sc['reference']='../References/Locales_Estilo_Protagonista.png';sc['original_branding']=True
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=1200;sc.render.resolution_y=800;sc.render.resolution_percentage=100
 sc.world=bpy.data.worlds.new('Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 pos=(0,-3.75,2.35) if interior else (-8,-7,5)
 target=(0,1,1.3) if interior else (.6,0,1.7)
 bpy.ops.object.camera_add(location=pos);cam=bpy.context.object;cam.data.lens=17 if interior else 46;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
 for x in [-2.5,2.5]:
  bpy.ops.object.light_add(type='AREA',location=(x,-1,3.25) if interior else (x-4,-3,7));l=bpy.context.object;l.data.energy=450 if interior else 900;l.data.size=4
 sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);print('SHOP_DONE',name,flush=True)
def product(n,p,scale=1):
 if n not in library:
  with bpy.data.libraries.load(str(ROOT/'outputs/DeliveryArt/HighFidelity'/(n+'.blend')),link=False) as (a,b):b.meshes=[n]
  library[n]=b.meshes[0]
 ob=bpy.data.objects.new(n,library[n]);bpy.context.collection.objects.link(ob);ob.location=p;ob.scale=(scale,)*3
 return ob
def planter(x,y,z):
 box((x,y,z+.22),(.42,.42,.44),'oak')
 for i in range(8):
  a=i*2.4;box((x+math.cos(a)*.14,y+math.sin(a)*.14,z+.45+(i%3)*.09),(.15,.15,.22),'leaf' if i%2 else 'sage')
for kind,label in enumerate(['Market','Restaurant','Tech','Pharmacy','Florist']):
 accent=['red','red','blue','blue','sage'][kind]
 bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];M=[];library={}
 box((0,0,-.08),(10,8,.16),'steel')
 for x in range(20):
  for y in range(16):box((-4.75+x*.5,-3.75+y*.5,.005),(.48,.48,.01),'ivory' if (x+y)%2 else 'cream')
 for x in [-5,5]:box((x,0,1.8),(.16,8,3.6),'ink' if kind==2 else 'ivory' if kind==3 else 'oak' if kind==1 else 'cream')
 box((0,4,1.8),(10,.16,3.6),'oak' if kind==1 else 'cream');box((0,0,3.65),(10,8,.12),'ivory')
 for x in [-4.90,4.90]:box((x,-4,1.8),(.20,.16,3.6),'cream')
 box((0,-4,3.1),(2,.16,1),'cream')
 for x in [-4.89,4.89]:
  box((x,0,.13),(.07,7.8,.22),'ink');box((x,0,2.82),(.06,7.8,.35),accent);box((x,0,3.05),(.06,7.8,.09),'ivory')
 box((0,3.88,2.82),(9.8,.06,.35),accent)
 for x in [-3,0,3]:box((x,0,3.46),(1.4,.35,.09),'ink');box((x,0,3.40),(1.2,.28,.035),'ivory')
 # Dedicated delivery service and register, with clear frontal approach.
 box((2.7,-1.25,.5),(2.6,.75,1),accent);box((2.7,-1.25,1.04),(2.75,.9,.10),'ink')
 for x in [1.6,2.15,2.7,3.25,3.8]:box((x,-1.64,.52),(.49,.03,.75),accent);box((x,-1.66,.13),(.45,.035,.04),'ivory')
 box((3.2,-1.25,1.13),(.5,.38,.09),'steel');box((3.2,-1.12,1.34),(.42,.06,.36),'ink');box((3.2,-1.158,1.35),(.34,.015,.26),'blue')
 box((2.45,-1.5,1.16),(.18,.25,.13),'ink')
 for i in range(3):
  for j in range(3):box((2.40+i*.045,-1.5+j*.028,1.23),(.028,.020,.01),'ivory')
 if kind==1:
  box((0,3.35,.55),(8,1,1.1),'steel');box((0,3.35,1.13),(8,1,.06),'ink')
  for x in [-3,-1,1,3]:
   for z in [1.4,1.75,2.1]:box((x,3.87,z),(1.95,.03,.32),'ivory')
   for dx in [-.35,.35]:
    disk((x+dx,3.20,1.18),.15,.025,'steel')
    for a in [-.12,0,.12]:box((x+dx+a,3.20,1.22),(.025,.35,.02),'ink')
  for x in [-2,0,2]:
   box((x,3.45,2.7),(1.95,1,.3),'steel');box((x,3.6,3.10),(.65,.65,.55),'steel')
   for i in range(8):box((x-.82+i*.23,2.935,2.68),(.11,.03,.19),'ink')
   product('SM_Burger',(x,2.99,1.17),1)
  for y in [-1.6,1.1]:
   box((-3.5,y,.82),(1.5,1,.12),'honey')
   for dy in [-.85,.85]:
    box((-3.5,y+dy,.34),(1.5,.55,.68),'red');box((-3.5,y+dy+(.24 if dy>0 else -.24),.77),(1.5,.14,.72),'red')
   product('SM_Burger',(-3.5,y,.9),.8);bottle(-3.9,y,.9,'red')
 elif kind in [0,2,3]:
  for side in [-1,1]:
   x=side*3.7;box((side*4.25,.5,1.25),(.10,4.6,2.5),'ink' if kind!=3 else 'ivory')
   for z in [.3,.88,1.46,2.04]:
    box((x,.5,z),(1.15,4.7,.07),'ivory')
    for j in range(10):
     y=-1.5+j*.44
     if kind==0:product(['SM_Milk','SM_Rice','SM_Apples'][(j+int(z*10)+side)%3],(x,y,z+.04),.8)
     elif kind==2:product(['SM_Headphones','SM_Keyboard','SM_PhoneBox'][j%3],(x,y,z+.04),.85)
     else:
      item=product('SM_Medicine' if j%3 else 'SM_FirstAid',(x,y,z+.04),.8)
      tint=['blue','red','sage','pink','gold'][(j+int(z*10)+side)%5]
      mat=bpy.data.materials.get('ENV_'+tint)
      if not mat:
       mat=bpy.data.materials.new('ENV_'+tint);mat.diffuse_color=COL[tint];mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=COL[tint]
      for slot in item.material_slots:
       if slot.material and slot.material.name.startswith('ENV_blue'):slot.link='OBJECT';slot.material=mat
  if kind==0:
   for x in [-.8,0,.8]:
    for z in [.14,.32,.50,.68,.86]:box((x,2.83,z),(.76,.8,.13),'oak')
    for i in range(4):product('SM_Apples',(x-.2+(i%2)*.4,2.62+(i//2)*.4,.95),1)
   box((-3.9,3.42,1.22),(1.75,.75,2.44),'ivory')
   for x in [-4.30,-3.50]:
    box((x,3.02,1.24),(.73,.025,2.10),'blue');box((x+.26,2.98,1.24),(.035,.05,.58),'steel')
  elif kind==2:
   box((0,3.38,.90),(3,.90,.14),'honey')
   for x in [-1.2,1.2]:box((x,3.38,.45),(.12,.7,.9),'ink')
   box((0,3.88,2.0),(3,.05,1.5),'blue')
   for i in range(8):box((-1.1+i*.31,3.81,2.05),(.04,.06,.4),'steel');box((-1.1+i*.31,3.81,2.30),(.09,.07,.16),'gold')
   product('SM_Keyboard',(0,3.2,1),1.3)
  else:
   for x in [-1.4,-.7,0,.7,1.4]:
    for z in [.4,.8,1.2,1.6,2]:box((x,3.62,z),(.66,.6,.36),'ivory');box((x,3.3,z),(.16,.05,.03),'steel')
 else:
  for side in [-1,1]:
   for y in [-1.3,-.3,.7,1.7,2.7]:
    x=side*3.5;box((x,y,.36),(.8,.8,.72),'oak')
    for i in range(5):product('SM_Bouquet',(x+random.uniform(-.2,.2),y+random.uniform(-.2,.2),.74),1.2)
  for x in [-1,0,1]:planter(x,3,0)
  for i in range(18):box((-4.5+i*.5,3.87,2.1),(.04,.04,1.5),'oak')
  for z in [1.5,1.8,2.1,2.4,2.7]:box((0,3.87,z),(9,.04,.04),'oak')
 # Reference-specific furnishings, keeping delivery targets and door aisle clear.
 if kind==1:
  for y in [-.6,1.8]:
   box((-.8,y,.78),(1.0,.85,.09),'honey');box((-.8,y,.39),(.12,.12,.78),'steel')
   for x in [-1.65,.05]:
    box((x,y,.45),(.42,.45,.07),'gold');box((x+(-.18 if x<0 else .18),y,.73),(.07,.45,.48),'gold')
    for dx in [-.16,.16]:
     for dy in [-.16,.16]:box((x+dx,y+dy,.22),(.035,.035,.44),'ink')
  for y in [-2.6,-.6,1.4,3.0]:
   box((-4.78,y,2.6),(.20,.28,.35),'ink');box((-4.65,y,2.55),(.05,.20,.22),'gold')
  for row in range(7):
   for col in range(18):box((-4.85,-3.7+col*.43,1.75+row*.22),(.03,.40,.19),'honey' if (row+col)%5 else 'oak')
 elif kind==3:
  for x in [-3.6,-2.9,-2.2]:
   box((x,-2.65,.43),(.54,.54,.09),'blue');box((x,-2.40,.69),(.54,.07,.49),'blue')
   for dx in [-.22,.22]:box((x+dx,-2.60,.20),(.04,.38,.4),'steel')
  for x in [-.95,.95]:
   box((x,1.45,.47),(.5,1.6,.94),'ivory');box((x,1.45,.96),(.57,1.65,.05),'blue')
   for y in [.90,1.40,1.90]:product('SM_Medicine',(x,y,1.01),.8)
 elif kind==2:
  for x in [-2.4,-.8,.8,2.4]:
   box((x,3.24,.77),(1.35,.7,.13),'steel');box((x,3.24,.39),(.12,.12,.78),'ink')
   box((x,3.2,.88),(.52,.34,.05),'ink');box((x,3.36,1.10),(.52,.045,.40),'ink');box((x,3.329,1.10),(.46,.008,.33),'blue')
   for i in range(6):box((x-.19+i*.065,3.324,1.02+(i%3)*.05),(.06,.006,.065),['blue','pink','ivory'][i%3])
   for i in range(10):box((x-.21+i*.045,3.10,.916),(.026,.12,.006),'steel')
 planter(-4.4,-3.3,0)
 finalize('SM_'+label+'Interior',True)

print('FIVE_REFERENCE_INTERIORS_EXPORTED')
