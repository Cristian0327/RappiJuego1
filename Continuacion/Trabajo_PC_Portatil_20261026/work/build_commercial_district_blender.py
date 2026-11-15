"""Editable Blender commercial architecture, human-scale fittings, no text or logos.
All measurements in metres. Front origin at doorway; interior origin at floor centre.
Run with Blender --background --python this_file.py. No old store meshes are reused.
"""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
exec((ROOT/'work/build_reference_storefronts.py').read_text().split('\nfor kind,label in enumerate')[0])
OUT=ROOT/'outputs/DeliveryArt/Shops'
CAT=json.loads((ROOT/'work/commercial_catalog.json').read_text())
BASE=dict(COL);REPORT=[];random.seed(61)

def reset():
 global V,F,M,library,COL
 bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];M=[];library={};COL=dict(BASE)

def finish(name,out=OUT,shift=0):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 for k,c in COL.items():
  mat=bpy.data.materials.new('ENV_'+k);mat.diffuse_color=c;mat.use_nodes=True;n=mat.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=c;n.inputs['Roughness'].default_value=.72
  if k=='glass':n.inputs['Transmission Weight'].default_value=1;n.inputs['Alpha'].default_value=.12;n.inputs['Roughness'].default_value=.08
  if k=='warm':n.inputs['Emission Color'].default_value=c;n.inputs['Emission Strength'].default_value=.4
  mesh.materials.append(mat)
 for p,i in zip(mesh.polygons,M):p.material_index=i
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.context.view_layer.objects.active=obj;bpy.ops.object.join()
 if shift:
  for v in obj.data.vertices:v.co.y+=shift
 # Collapse duplicate palette slots after joining products. UVs are explicit box maps.
 import bmesh
 bm=bmesh.new();bm.from_mesh(obj.data);uv=bm.loops.layers.uv.verify()
 for face in bm.faces:
  normal=face.normal;axis=max(range(3),key=lambda a:abs(normal[a]));axes=[a for a in range(3) if a!=axis]
  for l in face.loops:l[uv].uv=(l.vert.co[axes[0]],l.vert.co[axes[1]])
 bm.to_mesh(obj.data);bm.free()
 palette={};mats=[];remap={}
 for i,m in enumerate(obj.data.materials):
  key=m.name.split('.')[0] if m else 'ENV_ivory'
  if key not in palette:palette[key]=len(mats);mats.append(m)
  remap[i]=palette[key]
 indices=[remap[p.material_index] for p in obj.data.polygons];obj.data.materials.clear()
 for m in mats:obj.data.materials.append(m)
 for p,i in zip(obj.data.polygons,indices):p.material_index=i
 sc=bpy.context.scene;sc['authoring']='Blender 5.2 / original voxel architecture';sc['no_text_or_logos']=True;sc['scale']='metres; human furniture dimensions';sc['references']='REFERENCIAS_COMERCIOS.md'
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 REPORT.append({'asset':name,'vertices':len(obj.data.vertices),'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons),'materials':len(mats)})
 print('COMMERCIAL_BUILT',name,flush=True)

def stock(x,y,z,tint='blue',shape=0):
 if shape%3==0:
  box((x,y,z+.14),(.13,.12,.28),tint);box((x,y-.064,z+.15),(.09,.009,.11),'ivory');box((x,y,z+.30),(.065,.07,.04),'ivory')
 elif shape%3==1:
  box((x,y,z+.12),(.18,.11,.24),'ivory');box((x,y-.058,z+.08),(.17,.012,.055),tint);box((x,y-.058,z+.19),(.09,.012,.025),tint)
 else:
  box((x,y,z+.16),(.20,.13,.27),tint);box((x,y,z+.31),(.15,.08,.04),tint);box((x,y-.07,z+.16),(.12,.012,.14),'cream')

def shelf(x,y,length=3.2,accent='leaf',pharmacy=False):
 box((x,y,1.05),(.065,length,2.1),'ivory' if pharmacy else 'graphite')
 for yy in [-length/2+.06,length/2-.06]:box((x,y+yy,1.10),(.09,.07,2.2),'steel')
 for z in [.22,.70,1.18,1.66]:
  box((x,y,z),(1.05,length,.065),'ivory')
  for s in [-1,1]:
   box((x+s*.53,y,z+.025),(.04,length,.09),accent)
   for j in range(int(length/.28)):
    for col in range(2):stock(x+s*(.15+col*.22),y-length/2+.16+j*.28,z+.04,['blue','pink','sage','gold','red'][(j+int(z*10))%5],j)

def table(x,y,c='oak',long=False):
 length=2.8 if long else 1.25
 box((x,y,.79),(length,.90,.10),'honey')
 for dx in [-length*.35,length*.35]:box((x+dx,y,.38),(.07,.60,.76),'ink')
 for dy in [-.86,.86]:
  for dx in ([-.85,0,.85] if long else [0]):
   box((x+dx,y+dy,.46),(.46,.46,.075),c);box((x+dx,y+dy+( .20 if dy>0 else -.20),.73),(.46,.065,.48),c)
   for a in [-.17,.17]:
    for b in [-.17,.17]:box((x+dx+a,y+dy+b,.23),(.035,.035,.46),'ink')

def register(x,y):
 box((x,y,1.12),(.50,.40,.06),'graphite');box((x,y+.06,1.3),(.08,.08,.30),'steel');box((x,y+.10,1.45),(.43,.07,.32),'ink');box((x,y+.055,1.45),(.36,.018,.24),'cyan')
 box((x-.5,y-.05,1.11),(.22,.3,.13),'ink')
 for a in range(3):
  for b in range(3):box((x-.57+a*.06,y-.14+b*.07,1.18),(.035,.035,.012),'ivory')

def counter(x,y,w=2.8,c='oak'):
 box((x,y,.50),(w,.8,1),c);box((x,y,1.04),(w+.12,.94,.09),'ink')
 for i in range(int(w/.12)):box((x-w/2+.06+i*.12,y-.412,.5),(.065,.04,.84),'honey' if c=='oak' else c)
 register(x+.7,y)

def produce(x,y,item):
 box((x,y,.45),(2.5,1.6,.9),'oak')
 for yy in [-.78,.78]:
  for z in [.16,.42,.68]:box((x,y+yy,z),(2.6,.07,.16),'honey')
 for a in range(3):
  for b in range(2):
   px=x-.82+a*.82;py=y-.40+b*.80
   box((px,py,.95),(.78,.75,.14),'ink');product('SM_'+item,(px,py,1.02),.8)

def fridge(x,y):
 box((x,y+.40,1.25),(2.45,.12,2.5),'graphite');box((x,y,.14),(2.45,.85,.28),'steel');box((x,y,2.5),(2.45,.85,.15),'graphite')
 for dx in [-1.18,1.18]:box((x+dx,y,1.3),(.085,.85,2.45),'steel')
 for z in [.40,.9,1.4,1.9]:
  box((x,y,z),(2.28,.70,.055),'ivory')
  for j in range(8):stock(x-1+j*.28,y-.12,z+.035,'blue',j)
 for dx in [-.58,.58]:
  box((x+dx,y-.45,1.3),(1.10,.025,2.22),'glass');box((x+dx+.40,y-.51,1.3),(.035,.055,.35),'steel')

def kitchen(W,D,cafe=False,bakery=False):
 y=D-2
 for x in [-8,-4,0,4,8]:
  box((x,y,.5),(3.4,.9,1),'steel');box((x,y,1.05),(3.5,1,.08),'ink')
  for a in [-1.0,0,1.0]:
   box((x+a,y-.46,.55),(.85,.03,.70),'graphite');box((x+a,y-.5,.83),(.25,.045,.04),'steel')
  if cafe:
   box((x,y,1.45),(.95,.6,.75),'steel');box((x,y-.32,1.45),(.76,.04,.3),'ink')
   for a in [-.25,.25]:box((x+a,y-.40,1.32),(.10,.15,.10),'steel');product('SM_Coffee',(x+a,y-.3,1.11),.6)
  elif bakery:
   box((x,y,1.7),(2.4,.8,1.2),'graphite')
   for z in [1.3,1.7,2.1]:
    box((x,y-.42,z),(2.2,.04,.25),'ink');box((x,y-.45,z),(2.05,.025,.18),'warm');product('SM_Bread',(x,y-.3,z-.05),.7)
  else:
   for a in [-.6,0,.6]:
    for b in range(6):box((x+a,y-.25+b*.10,1.14),(.40,.035,.035),'steel')
   box((x,y,2.7),(3.4,1.1,.35),'steel');box((x,y,3.5),(.8,.7,1.3),'steel')

def new_products():
 for name in ['Drill','PaintCan','PetFood','PetBowl','PetToy']:
  reset()
  if name=='Drill':
   box((0,0,.25),(.13,.12,.15),'gold');box((0,0,.11),(.09,.09,.21),'graphite');box((0,0,.035),(.15,.16,.07),'gold');box((.1,0,.27),(.10,.075,.075),'steel');box((.18,0,.27),(.09,.025,.025),'ink')
   for i in range(4):box((-.065,-.065,.23+i*.025),(.08,.015,.01),'ink')
  elif name=='PaintCan':
   disk((0,0,0),.16,.35,'ivory');disk((0,0,.35),.165,.025,'steel');disk((0,0,.025),.164,.07,'cobalt');box((0,-.165,.20),(.16,.014,.12),'cobalt')
   for x in [-.175,.175]:box((x,0,.24),(.018,.025,.28),'steel')
   box((0,0,.38),(.36,.025,.02),'steel')
  elif name=='PetFood':
   box((0,0,.25),(.30,.18,.46),'pink');box((0,0,.49),(.24,.10,.03),'cream');box((0,-.095,.25),(.23,.02,.28),'cream');box((0,-.112,.25),(.085,.015,.065),'oak')
   for x,z in [(-.06,.31),(0,.34),(.06,.31)]:box((x,-.112,z),(.04,.015,.05),'oak')
  elif name=='PetBowl':
   disk((0,0,0),.20,.035,'cobalt')
   for i in range(16):
    a=i*math.pi/8;box((math.cos(a)*.17,math.sin(a)*.17,.075),(.065,.065,.12),'cobalt')
   disk((0,0,.035),.13,.015,'steel')
  else:
   box((0,0,.07),(.30,.06,.07),'gold')
   for x in [-.15,.15]:
    for y in [-.04,.04]:box((x,y,.075),(.08,.075,.08),'gold')
  finish('SM_'+name,ROOT/'outputs/DeliveryArt/HighFidelity')

def exterior(row):
 reset();W,D=row['width'],row['depth'];label=row['label'];accent=row['accent'];H=6.2;warm=label in ['Restaurant','Cafe','Bakery','Florist'];surface='brick' if warm else 'tile' if label in ['FreshMarket','Pharmacy'] else 'graphite'
 for side in [-1,1]:
  box((side*W/2,D/2,H/2),(.18,D,H),surface)
  # Individual masonry courses / cladding battens, not a featureless stretched wall.
  if warm:
   for r in range(24):
    for j in range(int(D/.6)):
     y=.25+j*.6+(r%2)*.3
     if y<D-.1:box((side*(W/2+.11),y,.12+r*.25),(.045,.56,.21),'bricklight' if (r+j)%7==0 else 'brick')
  else:
   for j in range(int(D/.3)):box((side*(W/2+.11),.15+j*.3,3),(.05,.06,5.8),'steel' if label in ['Tech','Components','Hardware'] else 'ivory')
 box((0,D,H/2),(W,.18,H),surface)
 # Wide glazed frontage with an unobstructed 3m door.
 for side in [-1,1]:
  span=W/2-1.6;x=side*(1.6+span/2)
  box((x,0,.18),(span,.22,.36),'graphite');box((x,0,2.0),(span-.1,.025,3.60),'glass')
  for i in range(6):box((side*(1.6+i*span/5),-.07,2.0),(.10,.16,3.9),'ink')
 box((0,0,4.65),(W,.28,1.7),surface)
 for x in [-1.55,1.55]:box((x,-.13,1.9),(.09,.18,3.8),'steel')
 box((0,-.9,3.95),(W+.15,1.9,.18),accent);box((0,-1.85,3.85),(W,.08,.08),'warm' if warm else 'ivory')
 box((0,D/2,6.28),(W+.25,D+.25,.18),'graphite')
 for x in [-W/2,W/2]:box((x,D/2,6.55),(.18,D,.5),accent)
 box((0,D,6.55),(W,.18,.5),'graphite')
 if label=='FreshMarket':
  for x in range(-11,12):box((x,-.19,5.05),(.08,.13,1.8),'ivory')
  # Original pixel produce mural, no letters or brand glyphs.
  for ox,c in [(-8,'gold'),(-4,'red'),(4,'leaf'),(8,'pink')]:
   for ix,iz,sz in [(-.5,0,.65),(0,.15,1),(.5,0,.65)]:box((ox+ix,-.3,4.95+iz),(.6,.10,sz),c)
   box((ox+.1,-.3,5.8),(.13,.1,.35),'sage');box((ox+.4,-.3,5.7),(.45,.1,.18),'leaf')
 elif label=='FastFood':
  # A tall corner volume and a roof garden recall the Parque 93 urban restaurant.
  box((8.2,2.3,6.0),(5.7,4.6,4.2),'graphite')
  for x in [5.6,6.9,8.2,9.5,10.8]:box((x,-.09,6.3),(.13,.12,3.4),'gold')
  box((-3,4,6.55),(15,7,.25),'tile')
  for x in [-10.3,4.3]:box((x,3.7,7.3),(.1,7.2,1.4),'ink')
  for x in range(-10,5):box((x,.2,7.25),(.065,.065,1.4),'ink')
  box((-3,.2,7.96),(14.8,.10,.10),'gold')
  for x in [-8,-4,0,3]:planter(x,1,6.68)
 elif label=='Restaurant':
  for x in [-9,-5,5,9]:
   for z,width in [(4.3,2.3),(4.6,1.9),(4.9,1.5),(5.2,.9)]:box((x,-.2,z),(width,.10,.22),'honey')
  for x in range(-11,12):box((x,-1,4.2),(.13,1.9,.15),'oak')
 elif label in ['Pharmacy','Tech','Components','Hardware','PetShop']:
  for j in range(12):box((-11+j*2,-.2,5.35),(1.88,.12,.55),accent)
  if label=='Pharmacy':
   # Pharmacy icon only, no names or signage text.
   box((8,-.29,4.7),(1.4,.12,.38),'cyan');box((8,-.29,4.7),(.38,.12,1.4),'cyan')
  if label in ['Tech','Components']:
   for x in [-7,7]:
    box((x,-.3,4.65),(2.3,.08,1.35),'ink')
    for j in range(7):box((x-.9+j*.3,-.36,4.65),(.035,.04,1.0),'cyan')
 elif label in ['Cafe','Bakery','Florist']:
  for x in range(-11,12):box((x,-.20,4.95),(.08,.08,1.5),'honey')
  for x in [-8,-4,4,8]:
   for i in range(10):box((x-1+i*.2,-.9,3.96),(.18,1.95,.22),accent if i%2 else 'cream')
 for x in [-10.5,10.5]:
  box((x,-1.1,.35),(1.5,1,.7),'graphite')
  for k in range(10):planter(x-.5+(k%3)*.5,-1+(k//3)*.12,.55)
 for x in [-8,-4,4,8]:
  box((x,-.23,3.1),(.20,.22,.42),'ink');box((x,-.36,3.1),(.12,.04,.25),'warm')
 for x in [-8,0,8]:
  box((x,D-3,6.7),(2.4,1.5,.65),'steel')
  for j in range(12):box((x-1.05+j*.19,D-3.78,6.72),(.06,.04,.46),'ink')
 finish('SM_'+label+'Front')

def interior(row):
 reset();W,D=row['width'],row['depth'];L=row['label'];a=row['accent'];food=row['category']==1
 box((0,D/2,-.06),(W,D,.12),'cream')
 for x in range(-int(W/2),int(W/2)):
  for y in range(int(D)):box((x+.5,y+.5,.012),(.986,.986,.024),'ivory' if (x+y)%5 else 'tile')
 for s in [-1,1]:
  box((s*(W/2-.14),D/2,3),(.065,D,6),'ivory' if not food else 'oak')
  box((s*(W/2-.18),D/2,.13),(.07,D,.25),'graphite')
 box((0,D-.14,3),(W,.07,6),'ivory' if not food else 'brick');box((0,D/2,6.12),(W,D,.10),'graphite' if food or L in ['Tech','Components'] else 'ivory')
 for y in range(4,int(D),4):
  box((0,y,5.85),(W,.16,.22),'steel' if not food else 'ink')
  for x in [-8,-2,4,9]:box((x,y,5.65),(2.4,.35,.07),'warm' if food else 'ivory')
 if food:
  for x in range(-11,12):box((x,D/2,5.70),(.12,D-.5,.18),'honey')
 # Dedicated collection desk stays accessible from a 3m central spine.
 counter(2.7,row.get('counter_y',D-8 if food else 6),4.8 if food else 2.6,'oak' if food else a)
 if row['category']!=1:
  for x,y in [(-W/2+2.5,D/2),(W/2-2.5,D/2),(0,D-2)]:
   # Reachable collection shelving, with a clear middle shelf for the order.
   for dx in [-.52,.52]:
    for dy in [-.43,.43]:box((x+dx,y+dy,1.05),(.065,.065,2.1),'steel')
   for z in [.16,.65,1.0,1.65,2.08]:
    box((x,y,z),(1.12,.96,.07),'ivory')
    box((x,y-.49,z+.025),(1.12,.045,.1),a)
   for z in [.21,.70,1.70]:
    for dx in [-.35,0,.35]:stock(x+dx,y,z,a,int((dx+1)*10))
 if L in ['Market','FreshMarket','Pharmacy','PetShop','Hardware']:
  # Two front-to-back aisles either side of the central and customer walk lanes.
  for x in [-7,-2.5,2.5,7]:
   for y in range(9,int(D)-3,5):shelf(x,y,3.2,a,L=='Pharmacy')
  # Perimeter stock remains interrupted at the three interactive collection bays.
  for side in [-1,1]:
   for y in range(7,int(D)-3,4):
    if abs(y-D/2)<2.4:continue
    x=side*(W/2-1)
    for z in [.25,.80,1.35,1.9,2.45]:
     box((x,y,z),(.8,2.7,.07),'ivory')
     for j in range(9):stock(x,y-1.05+j*.25,z+.05,['sage','red','gold','blue'][j%4],j)
  if L in ['Market','FreshMarket']:
   for x in [-9,-6,6,9]:
    produce(x,5.5,'Apples' if x<0 else 'Bananas')
   for x in [-8,-5,5,8]:fridge(x,D-1)
   for x in [-8,-4]:counter(x,2.8,2.6,'sage');box((x-1.4,2.8,.85),(1,.8,.16),'ink')
   if L=='FreshMarket':
    for x in [-9,9]:
     for y in [11,20,27]:planter(x,y,2.4)
    for x in [-7,7]:
     box((x,D-5,2.8),(3.6,.12,.6),'honey')
     for z in [.5,1,1.5]:
      box((x,D-4,z),(3,.8,.08),'oak')
      for dx in [-.8,0,.8]:product('SM_Bread',(x+dx,D-4,z+.05),.8)
  elif L=='Pharmacy':
   for x in [-8,-4,4,8]:
    counter(x,D-3,2.8,'ivory')
    for z in [.5,1,1.5,2,2.5]:
     box((x,D-.5,z),(3.3,.6,.06),'ivory')
     for j in range(11):stock(x-1.4+j*.27,D-.6,z+.04,['blue','sage','pink'][j%3],j)
   for x,c in [(-7,'pink'),(7,'cyan')]:
    box((x,11,4.25),(3,.12,.8),c)
    for xx in [-.2,.2]:box((x+xx,10.9,4.25),(.12,.12,.44),'ivory')
  elif L=='PetShop':
   for x in [-8,-4,4,8]:
    box((x,D-2,.4),(2.1,1.5,.8),'sage')
    for dx in [-.6,0,.6]:product('SM_PetFood',(x+dx,D-2,.85),1)
   for x in [-8,8]:
    for y in [5,22]:
     box((x,y,.16),(1.5,1.2,.32),'pink');box((x,y+.5,.4),(1.5,.20,.4),'cream');box((x,y,.33),(1.1,.8,.08),'cream')
  else:
   for x in [-9,-5,5,9]:
    box((x,D-1.0,1.3),(3,.10,2.6),'honey')
    for j in range(7):
     for z in [.4,1.1,1.8]:product('SM_Drill',(x-1.1+j*.35,D-1.25,z),.9)
   for x in [-9,9]:
    for y in [5,24]:
     for j in range(3):product('SM_PaintCan',(x-.4+j*.4,y,.04),1.2)
 elif L in ['Tech','Components']:
  for x in [-7,-2.5,2.5,7]:
   for y in [7,12,20,25]:
    box((x,y,.50),(2.3,1.4,1),'graphite');box((x,y,1.04),(2.4,1.5,.08),'ivory');box((x,y, .12),(2.35,1.45,.055),'cyan')
    for dx in [-.6,.6]:product('SM_'+('CircuitBoard' if L=='Components' else 'Keyboard'),(x+dx,y,1.1),1)
    if L=='Tech':
     box((x,y+.4,1.45),(.08,.08,.6),'steel');box((x,y+.4,1.8),(1.1,.08,.65),'ink');box((x,y+.35,1.8),(1,.02,.54),'blue')
  for x in [-8,-4,4,8]:
   box((x,D-.5,2),(3,.1,3.4),'graphite')
   for z in [.4,1.1,1.8,2.5]:
    box((x,D-1,z),(3,1,.07),'steel')
    for dx in [-.8,0,.8]:product('SM_'+('GPU' if L=='Components' else 'Headphones'),(x+dx,D-1,z+.05),1)
 elif food:
  kitchen(W,D,L=='Cafe',L=='Bakery')
  for x in [-7,-2.7,2.7,7]:
   for y in [7,13]:
    table(x,y,'blue' if L=='FastFood' else 'red' if L=='Restaurant' else 'sage',L=='Cafe' and abs(x)>5)
    product('SM_'+('Coffee' if L=='Cafe' else 'Bread' if L=='Bakery' else 'Burger'),(x,y,.85),.65)
  # Upholstered perimeter benches, framed voxel still lifes and pendant lamps.
  for side in [-1,1]:
   for y in [7,13]:
    x=side*(W/2-1)
    box((x,y,.42),(1.1,2.7,.8),'blue' if L=='FastFood' else 'red');box((x+side*.46,y,1),(.16,2.7,1.05),'blue' if L=='FastFood' else 'oak')
    box((side*(W/2-.23),y,3.0),(.08,2.1,1.55),'ink');box((side*(W/2-.29),y,3.0),(.05,1.9,1.35),'cream')
    for j,c in enumerate(['gold','sage','red','honey']):box((side*(W/2-.34),y-.6+j*.4,2.85+(j%2)*.35),(.04,.32,.55),c)
  for x in [-7,7]:
   for y in [7,13]:
    box((x,y,4.8),(.025,.025,1.5),'ink');box((x,y,4),(.65,.65,.18),'graphite');box((x,y,3.89),(.55,.55,.035),'warm')
  if L=='Bakery':
   for x in [-8,-4,4,8]:
    for z in [.5,.95,1.4]:
     box((x,D-5,z),(2.7,.85,.07),'honey')
     for dx in [-.8,0,.8]:product('SM_Bread',(x+dx,D-5,z+.05),.85)
  elif L=='Cafe':
   for x in [-9,9]:
    for y in [5,11,17,22]:planter(x,y,0)
  elif L=='FastFood':
   for x in [-8,-5]:
    box((x,3.5,.8),(.35,.3,1.6),'ivory');box((x,3.5,1.7),(.8,.12,1.1),'ink');box((x,3.42,1.7),(.68,.025,.95),'gold')
  else:
   for x in [-10.5,10.5]:
    for y in [8,14,20]:
     box((x,y,.36),(1.6,2.4,.72),'red');box((x+(-.72 if x<0 else .72),y,.85),(.16,2.4,1),'red')
 elif L=='Florist':
  for x in [-7,7]:
   for y in [6,12,18]:
    for z,width in [(.3,2.5),(.7,1.8),(1.1,1.1)]:
     box((x,y,z),(width,1.1,.12),'honey')
     for dx in [-width*.3,0,width*.3]:product('SM_Bouquet',(x+dx,y,z+.08),.8)
  for x in [-10,10]:
   for y in range(4,int(D)-2,3):planter(x,y,0)
  for x in [-2.7,2.7]:
   for y in [8,15]:
    box((x,y,.48),(2,1.4,.96),'oak')
    for dx in [-.6,0,.6]:product('SM_Bouquet',(x+dx,y,1),1)
 finish('SM_'+L+'Interior',shift=-D/2)

new_products()
for row in CAT:
 if row['label']!='Pizza':exterior(row);interior(row)
if any(row['label']=='Pizza' for row in CAT):
 import runpy
 runpy.run_path(str(ROOT/'work/build_pizza_product.py'),run_name='__main__')
 runpy.run_path(str(ROOT/'work/build_pizzeria_blender.py'),run_name='__main__')
 REPORT.extend(json.loads((ROOT/'work/pizzeria_blender_manifest.json').read_text()))
(ROOT/'work/commercial_blender_manifest.json').write_text(json.dumps(REPORT,indent=2))
print('ALL_COMMERCIAL_MODELS_COMPLETE',len(REPORT),flush=True)
