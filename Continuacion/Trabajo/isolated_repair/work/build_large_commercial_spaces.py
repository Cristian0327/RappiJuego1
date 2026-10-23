import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/Shops'
exec((ROOT/'work/build_reference_storefronts.py').read_text().split('\nfor kind,label in enumerate')[0])
PALETTE=dict(COL)
SIZES={'Market':(20,18),'FreshMarket':(20,18),'Restaurant':(20,16),'FastFood':(20,16),'Tech':(20,16),'Components':(20,16),'Pharmacy':(20,18),'Florist':(14,12)}
def cube_groups(mesh):
 parent=list(range(len(mesh.vertices)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for edge in mesh.edges:
  a,b=map(find,edge.vertices)
  if a!=b:parent[b]=a
 groups={}
 for p in mesh.polygons:groups.setdefault(find(p.vertices[0]),[]).append(p)
 for polys in groups.values():
  ids={v for p in polys for v in p.vertices};pts=[mesh.vertices[v].co.copy() for v in ids];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
  yield polys,ids,(lo+hi)*.5,hi-lo

def keep_geometry(mesh,interior,W,D):
 global V,F,M
 for polys,ids,c,s in cube_groups(mesh):
  if interior:
   if (c.z<.12 and s.z<.3) or (c.z>3.40 and s.x>2) or (abs(c.x)>4.74 and s.x<.4) or (c.y>3.84 and s.x>8):continue
  else:
   if (abs(c.x)>4.96 and s.y>6) or (c.y>7.8 and s.x>8) or (c.z>3.43 and s.x>8) or (abs(c.x)>4.95 and s.y>6):continue
   if c.y>7.75:continue
  mapping={}
  for v in ids:
   p=mesh.vertices[v].co.copy()
   if interior:p.y-=D/2-4
   elif c.z>2.80:p.z+=1.2
   mapping[v]=len(V);V.append(tuple(p))
  for p in polys:
   F.append(tuple(mapping[v] for v in p.vertices));name=mesh.materials[p.material_index].name.removeprefix('ENV_').split('.')[0];M.append(list(COL).index(name) if name in COL else list(COL).index('ivory'))

def aisle(x,y,kind):
 box((x,y,1.0),(1.2,2.6,2),'ink' if kind==2 else 'ivory');
 for z in [.35,.9,1.45,2.0]:
  box((x,y,z),(1.38,2.72,.065),'ivory');box((x,y-1.38,z+.03),(1.38,.025,.09),'blue' if kind==3 else 'leaf' if kind==0 else 'red')
  for j in range(5):
   for side in [-1,1]:product(['SM_Milk','SM_Rice','SM_Apples'][j%3] if kind==0 else 'SM_Medicine' if kind==3 else ['SM_Keyboard','SM_PhoneBox','SM_Headphones'][j%3],(x+side*.43,y-.9+j*.45,z+.04),.7)
def dining(x,y):
 box((x,y,.79),(1.25,1.0,.10),'honey');box((x,y,.39),(.10,.10,.78),'steel')
 for dx in [-.94,.94]:
  box((x+dx,y,.45),(.5,.5,.08),'gold');box((x+dx+(-.23 if dx<0 else .23),y,.75),(.065,.50,.52),'gold')
  for a in [-.18,.18]:
   for b in [-.18,.18]:box((x+dx+a,y+b,.22),(.035,.035,.44),'ink')
 product('SM_Burger',(x,y,.85),.65)
report=[]
for label,(W,D) in SIZES.items():
 kind=0 if label in ['Market','FreshMarket'] else 1 if label in ['Restaurant','FastFood'] else 2 if label in ['Tech','Components'] else 3 if label=='Pharmacy' else 4
 accent='leaf' if label=='FreshMarket' else 'red' if kind in [0,1] or label=='Components' else 'cobalt' if kind in [2,3] else 'sage'
 for suffix in ['Interior','Front']:
  file=OUT/('SM_'+label+suffix+'.blend');bpy.ops.wm.open_mainfile(filepath=str(file));source=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SM_'+label+suffix)).data;V=[];F=[];M=[];library={};COL=dict(PALETTE)
  keep_geometry(source,suffix=='Interior',W,D);bpy.ops.wm.read_factory_settings(use_empty=True)
  if suffix=='Interior':
   box((0,0,-.04),(W,D,.10),'cream');
   for ix in range(int(W*2)):
    for iy in range(int(D*2)):box((-W/2+.25+ix*.5,-D/2+.25+iy*.5,.025),(.485,.485,.035),'ivory' if (ix+iy)%5 else 'cream')
   for x in [-W/2,W/2]:box((x,0,2.4),(.16,D,4.8),'oak' if kind==1 else 'ivory')
   box((0,D/2,2.4),(W,.16,4.8),'oak' if kind==1 else 'ivory');box((0,0,4.85),(W,D,.10),'ivory')
   for x in [-W/2+.13,W/2-.13]:box((x,0,3.8),(.05,D,.30),accent)
   for x in [-6,0,6]:
    for y in [-D/2+3,1,D/2-2]:box((x,y,4.4),(1.5,.42,.08),'ink');box((x,y,4.35),(1.38,.32,.02),'ivory')
   if kind in [0,2,3]:
    for x in [-5,5]:
     for y in [.2,4.4]:aisle(x,y,kind)
    for x in [-W/2+2.5,W/2-2.5]:
     box((x,0,.48),(1.5,1.2,.96),'oak' if kind==0 else 'ivory');box((x,0,.99),(1.55,1.25,.06),accent)
    box((0,D/2-2,.48),(1.6,1.2,.96),'ivory');box((0,D/2-2,.99),(1.68,1.3,.06),accent)
    for x in [-W/2+.75,W/2-.75]:
     for y in [-2,1,4,7] if D>=18 else [-2,1,4]:
      box((x,y,1.3),(1.1,2.5,2.6),'steel');box((x,y-1.28,1.3),(.98,.025,2.3),'glass');box((x+.39,y-1.31,1.3),(.055,.045,.70),'ink')
    if kind==0:
     for x in [-2.7,2.7]:
      for y in [2,5.3]:
       box((x,y,.47),(1.8,1.4,.94),'oak')
       for dx in [-.55,0,.55]:
        for dy in [-.4,.4]:product(['SM_Apples','SM_Bananas','SM_Carrots'][int(abs(dx)*10)%3],(x+dx,y+dy,.98),1)
   elif kind==1:
    for x in [-6.4,6.4]:
     for y in [-1,2.4,5.8]:dining(x,y)
    box((0,6.8,.55),(8,1.1,1.1),'steel');box((0,6.8,1.13),(8,1.1,.06),'ink')
    for x in [-2.5,0,2.5]:
     box((x,7.1,3.05),(2.1,1.2,.35),'steel')
     for i in range(10):box((x-.95+i*.2,6.48,3.05),(.075,.03,.20),'ink')
   else:
    for x in [-5.4,5.4]:
     for y in [0,2.8,4.4]:planter(x,y,0)
  else:
   surface='brick' if kind==1 else 'graphite' if kind==2 else 'tile'
   for x in [-W/2,W/2]:
    box((x,D/2,2.4),(.16,D,4.8),surface)
    for row in range(24 if kind==1 else 12):
     pitchz=.20 if kind==1 else .40;pitchy=.40 if kind==1 else .75
     for j in range(int(D/pitchy)):
      y=.2+j*pitchy+(pitchy*.5 if row%2 else 0)
      if y<D-.1:box((x+(.10 if x>0 else -.10),y,.10+row*pitchz),(.03,pitchy-.025,pitchz-.02),surface)
   box((0,D,2.4),(W,.16,4.8),surface);box((0,D/2,4.91),(W+.2,D+.2,.14),'graphite')
   for x in [-W/2,W/2]:box((x,D/2,5.10),(.18,D+.2,.30),accent)
   for y in [0,D]:box((0,y,5.10),(W+.2,.18,.30),accent)
   for side in [-1,1]:
    x=side*(W/2+5)/2;span=W/2-5
    box((x,0,.22),(span,.20,.44),'steel');box((x,0,2.20),(span-.18,.025,3.5),'glass')
    for dx in [-span*.48,0,span*.48]:box((x+dx,-.1,2.2),(.085,.12,3.55),'ink')
    box((x,-.05,4.25),(span,.22,.6),surface)
   for x in [-3,3]:box((x,0,3.35),(3.62,.025,1.28),'glass')
   for i in range(int(W*2)):box((-W/2+.25+i*.5,-.48,4.25),(.49,1.1,.36),accent)
   box((0,-1.06,4.09),(W,.075,.085),'warm' if kind==1 else 'ivory')
   for x in [-W/2+1.0,W/2-1.0]:
    box((x,-.5,.3),(.85,.85,.6),'steel')
    for j in range(12):box((x+math.cos(j*2.4)*.22,-.5+math.sin(j*2.4)*.22,.73+(j%4)*.1),(.20,.20,.20),'leaf')
   for x in [-W/2+2,W/2-2]:box((x,D-2,5.35),(1.6,1,.65),'steel')
  name='SM_'+label+suffix;mesh=bpy.data.meshes.new(name);mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
  for key,c in COL.items():
   mat=bpy.data.materials.new('ENV_'+key);mat.diffuse_color=c;mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mesh.materials.append(mat)
  for poly,index in zip(mesh.polygons,M):poly.material_index=index
  obj.select_set(True);bpy.context.view_layer.objects.active=obj;sc=bpy.context.scene;sc['commercial_dimensions']=f'{W}x{D}x4.8m';sc['real_references']='Farmatodo Calle 100 / Carulla Rosales-Retiro / McDonalds Calle138 / Sigma Bogota';sc['human_scale_preserved']=True
  bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.export_scene.fbx(filepath=str(file.with_suffix('.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z');report.append({'asset':name,'dimensions':[W,D,4.8],'faces':len(F)})
  print('COMMERCIAL_REBUILT',name,W,D,flush=True)
(ROOT/'work/large_commercial_manifest.json').write_text(json.dumps(report,indent=2))
