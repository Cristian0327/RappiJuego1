import bpy, math, json, random
import numpy as np
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/HighFidelity';OUT.mkdir(exist_ok=True)
# 1.25 cm authoring lattice: half the old lattice, but silhouette is authored first.
U=.0125
COL={'skin':(.77,.47,.29,1),'skinLight':(.94,.67,.44,1),'skinShade':(.64,.34,.21,1),'darkSkin':(.40,.22,.12,1),'darkHighlight':(.52,.30,.17,1),'hair':(.065,.035,.022,1),'curl':(.105,.055,.029,1),'silver':(.59,.60,.57,1),'silverLight':(.78,.79,.74,1),'white':(.89,.87,.79,1),'cream':(.75,.69,.53,1),'plum':(.30,.055,.13,1),'plumLight':(.42,.08,.19,1),'skirt':(.24,.12,.25,1),'navy':(.025,.065,.145,1),'navyLight':(.045,.105,.22,1),'teal':(.02,.43,.48,1),'cyan':(.035,.64,.79,1),'ink':(.023,.027,.033,1),'charcoal':(.07,.075,.08,1),'rust':(.62,.12,.045,1),'rustLight':(.78,.22,.075,1),'gold':(.88,.52,.12,1),'mustard':(.67,.37,.04,1),'sage':(.24,.33,.105,1),'sageLight':(.34,.43,.16,1),'olive':(.20,.235,.12,1),'brown':(.22,.105,.045,1),'sole':(.36,.21,.105,1),'metal':(.40,.44,.45,1),'red':(.73,.045,.03,1),'pink':(.77,.29,.30,1),'eye':(.065,.027,.02,1)}
KEYS=list(COL);IDS={k:i+1 for i,k in enumerate(KEYS)}
# x [-.8,.8], y [-.6,.6], z [0,2.3]
SH=(128,96,184);OR=np.array([-.8,-.6,0.]);grid=None

def shape(c,center,radius,power=2):
 center=np.array(center);radius=np.array(radius);lo=np.maximum(0,np.floor((center-radius-OR)/U).astype(int));hi=np.minimum(SH,np.ceil((center+radius-OR)/U).astype(int));
 if np.any(hi<=lo):return
 axes=[(np.arange(lo[i],hi[i])+.5)*U+OR[i] for i in range(3)];x,y,z=np.meshgrid(*axes,indexing='ij');d=[abs((x-center[0])/radius[0]),abs((y-center[1])/radius[1]),abs((z-center[2])/radius[2])];mask=(sum(t**power for t in d)<=1) if power<99 else ((d[0]<=1)&(d[1]<=1)&(d[2]<=1));part=grid[tuple(slice(lo[i],hi[i]) for i in range(3))];part[mask]=IDS[c] if c else 0

def box(c,p,s):shape(c,p,np.array(s)*.5,100)
def ell(c,p,s,power=2):shape(c,p,np.array(s)*.5,power)
def link(c,a,b,width,depth=None):
 a=np.array(a);b=np.array(b);n=max(2,int(np.linalg.norm(b-a)/(U*1.7)))
 for t in np.linspace(0,1,n):ell(c,a*(1-t)+b*t,(width,depth or width,width),4)
def plate(c,x,y,z,w,h,d=.025):box(c,(x,y,z),(w,d,h))
def eye(x,y,z,skin):
 plate('white',x,y,z,.10,.105);plate('eye',x+.012,y-.017,z-.005,.051,.078,.014);plate('white',x+.023,y-.026,z+.025,.015,.018,.01);plate('hair',x,y-.026,z+.057,.11,.015)
def boot(x,z,role):
 base='brown' if role in [0,4] else 'ink' if role==1 else 'navy' if role==2 else 'white'
 ell('sole' if role in [0,4] else 'ink',(x,-.055,z+.037),(.205,.36,.075),6)
 ell('white' if role in [2,3] else base,(x,-.055,z+.073),(.20,.35,.085),6)
 ell(base,(x,-.035,z+.12),(.18,.30,.15),4);ell(base,(x,.035,z+.19),(.15,.19,.17),5)
 for yy in [-.12,-.075,-.03]:box('cream' if role in [0,4] else 'white',(x,yy,z+.191),(.10,.017,.015))
 if role==2:plate('cyan',x,-.177,z+.13,.12,.055)
 if role==1:
  for dx in [-.05,0,.05]:box('charcoal',(x+dx,-.11,z+.19),(.025,.025,.012))

def character(role):
 global grid
 grid=np.zeros(SH,dtype=np.uint8);rng=random.Random(501+role)
 # Proportions: individually sculpted body build; larger expressive head like courier.
 leg=[.49,.58,.73,.67,.60][role];shoulder=[1.15,1.28,1.39,1.32,1.26][role];w=[.50,.69,.44,.43,.48][role];head=shoulder+.30;skin=['skinLight','skin','darkSkin','skinLight','skin'][role];shirt=['plum','white','navy','white','mustard'][role];trouser=['skirt','charcoal','charcoal','navy','olive'][role]
 for side in [-1,1]:
  x=side*(.105 if role!=1 else .145);boot(x,0,role)
  link(trouser,(x,.025,.22),(x,.025,leg+.19),.175 if role!=1 else .23,.21)
  ell(trouser,(x,-.015,.40),(.185,.24,.18),5)
  if role in [1,2,4]:box('charcoal' if role!=4 else 'cream',(x,0,.24),(.19,.24,.075))
 ell(shirt,(0,.01,(leg+shoulder)*.5),(w,.36 if role!=1 else .48,shoulder-leg+.10),4)
 ell(shirt,(0,.01,shoulder-.065),(w*.97,.33 if role!=1 else .43,.22),3)
 ell(skin,(0,0,shoulder+.065),(.17,.19,.16),4)
 # Distinct tapered, stepped chin/cheeks and forehead; all fully volumetric.
 hw=.44 if role!=1 else .48
 ell(skin,(0,-.01,head),(hw,.37,.41),5);ell(skin,(0,-.035,head-.15),(hw*.80,.30,.12),4)
 for side in [-1,1]:ell(skin,(side*hw*.5,-.005,head-.025),(.075,.11,.13),4);ell('skinShade' if role!=2 else 'darkHighlight',(side*hw*.53,-.045,head-.025),(.026,.038,.060),4)
 eye(-.092,-.204,head+.012,skin);eye(.092,-.204,head+.012,skin)
 plate('hair',-.094,-.213,head+.093,.11,.025);plate('hair',.094,-.213,head+.099,.11,.025)
 ell('darkHighlight' if role==2 else 'skinLight',(0,-.215,head-.045),(.065,.075,.06),5)
 plate('skinShade' if role!=2 else 'hair',0,-.198,head-.113,.083,.014);plate(skin,0,-.205,head-.125,.057,.015)
 for side in [-1,1]:
  # Sloped shoulders and gently bent arm, exposed separated fingers and thumb.
  start=(side*(w*.47),0,shoulder-.06);elbow=(side*(w*.60),-.012,shoulder-.24);wrist=(side*(w*.64),-.055,shoulder-.40)
  link(shirt,start,elbow,.17 if role!=1 else .23,.20);link('navy' if role==1 else shirt,elbow,wrist,.13 if role!=1 else .18,.16)
  ell('cream' if role in [0,1,3] else 'cyan' if role==2 else 'gold',wrist,(.145,.18,.065),5)
  hand=(wrist[0],-.063,wrist[2]-.083);ell(skin,hand,(.12,.14,.15),4)
  for i in range(3):ell(skin,(hand[0]+(i-1)*.028,-.096,hand[2]-.057),(.026,.071,.064),5)
  ell(skin,(hand[0]-side*.065,-.07,hand[2]+.01),(.05,.08,.08),4)
 # Side and rear garment construction is included before occupation details.
 for z in np.arange(leg+.03,shoulder-.10,.075):
  for side in [-1,1]:box(shirt,(side*w*.46,.10,z),(.03,.06,.045))
 if role==0:
  # Flared skirt separate from cardigan; apron's contours wrap the belly.
  for z in np.arange(.25,leg+.17,U):ell('skirt',(0,.025,z),(.58-(z-.25)*.15,.40,U*1.2),5)
  ell('plum',(0,.015,leg+.22),(.55,.40,.38),4)
  plate('cream',0,-.211,leg+.18,.42,.34,.03)
  plate('white',0,-.196,shoulder-.16,.24,.31)
  for i in range(15):
   x=rng.uniform(-.09,.09);z=rng.uniform(shoulder-.27,shoulder-.035);plate('pink',x,-.214,z,.028,.022,.012);plate('sage',x+.012,-.216,z-.017,.012,.025,.012)
  for side in [-1,1]:
   link('plumLight',(side*.13,-.202,shoulder+.015),(side*.18,-.218,leg+.34),.055,.04)
   plate('cream',side*.105,-.24,leg+.14,.13,.125,.04);plate('white',side*.105,-.265,leg+.195,.13,.015)
  for z in [leg+.34,leg+.43,leg+.52]:plate('gold',-.175,-.238,z,.026,.026)
  # Swept hairstyle: caps of diminishing sections, individual locks and low bun.
  ell('silver',(0,.02,head+.125),(.48,.40,.23),3)
  for i in range(9):
   x=-.21+i*.051;zz=head+.18+.045*math.cos(i*.42);ell('silverLight' if i%3==0 else 'silver',(x,-.055,zz),(.09,.31,.10),4)
  for side in [-1,1]:
   for j in range(3):ell('silver',(side*.218,.065,head+.055-j*.058),(.075,.22,.10),4)
  ell('silver',(0,.224,head-.01),(.24,.18,.22),3)
  for k in range(7):ell('silverLight' if k%2 else 'silver',(.075*math.cos(k),.296,head-.01+.072*math.sin(k)),(.065,.04,.065),4)
  for x in [-.095,.095]:
   for xx in [x-.064,x+.064]:plate('gold',xx,-.244,head+.009,.014,.126,.014)
   for z in [head-.055,head+.072]:plate('gold',x,-.244,z,.142,.014,.014)
  plate('gold',0,-.244,head+.025,.05,.012,.014)
 elif role==1:
  # Heavy brow, bald crown, sculpted sideburns and bushy mustache.
  ell(skin,(0,.0,head+.17),(.40,.32,.12),3)
  for side in [-1,1]:
   for j in range(5):ell('hair',(side*.20,.025+j*.03,head+.10),(.07,.085,.16-j*.012),4)
   link('white',(side*.035,-.18,shoulder+.04),(side*.11,-.22,shoulder-.025),.06,.045)
  for i in range(7):ell('hair',(-.09+i*.03,-.235,head-.076),(.047,.043,.044+(.02 if i in [0,6] else 0)),4)
  ell('rust',(0,-.245,leg+.31),(.54,.05,.63),5)
  for side in [-1,1]:link('rust',(side*.18,-.22,shoulder+.015),(side*.19,-.27,leg+.59),.037,.03)
  plate('rustLight',0,-.279,leg+.20,.29,.20,.04)
  for i in range(18):plate('rustLight',rng.uniform(-.21,.21),-.279,rng.uniform(leg+.06,leg+.54),.025,.025,.012)
  plate('white',.22,-.29,leg+.24,.11,.29,.027)
  for z in [leg+.12,leg+.15]:plate('rust',.22,-.308,z,.11,.013,.01)
  for x in [-.18,-.13]:link('brown',(x,-.30,leg+.24),(x,-.30,leg+.49),.022);ell('sole',(x,-.30,leg+.51),(.045,.025,.08),5)
 elif role==2:
  # Dense curls shape the top and asymmetrical fringe, not a flat helmet.
  ell('hair',(0,.018,head+.145),(.48,.40,.20),3)
  for i in range(54):
   a=rng.uniform(0,math.tau);r=rng.uniform(.04,.24);x=math.cos(a)*r;y=math.sin(a)*r*.8;z=head+.18+max(0,.24-r)*.33;ell('curl' if i%5==0 else 'hair',(x,y,z),(.075,.075,.075),4)
  for x in [-.17,-.10,-.03]:ell('hair',(x,-.176,head+.10),(.07,.08,.10),4)
  plate('charcoal',0,-.20,shoulder-.27,.16,.37)
  for side in [-1,1]:
   plate('navyLight',side*.12,-.205,shoulder-.24,.10,.39,.04);plate('cyan',side*.17,-.231,shoulder-.23,.018,.37)
   plate('navyLight',side*.13,-.235,shoulder-.10,.095,.07,.035)
   ell('ink',(side*.14,-.11,shoulder+.04),(.10,.14,.15),5);ell('cyan',(side*.14,-.173,shoulder+.04),(.075,.03,.12),5)
   plate('charcoal',side*.16,-.12,leg-.20,.13,.14,.07)
  link('navy',( -.14,.01,shoulder+.10),(.14,.01,shoulder+.10),.045)
  link('cyan',(-.075,-.235,shoulder-.045),(0,-.24,shoulder-.24),.017);link('cyan',(.075,-.235,shoulder-.045),(0,-.24,shoulder-.24),.017)
  plate('white',0,-.263,shoulder-.27,.065,.085);plate('navy',0,-.279,shoulder-.26,.03,.026,.01)
  box('ink',(.28,.01,leg+.10),(.08,.14,.20));box('gold',(.285,-.065,leg+.19),(.055,.05,.04))
 elif role==3:
  # Bob: rounded stepped crown, tapered cheeks, back hair curtain.
  ell('hair',(0,.018,head+.12),(.48,.41,.26),4)
  for q in [(side*.205,.035,head-.015) for side in [-1,1]]:ell('hair',q,(.10,.32,.29),4)
  ell('hair',(0,.16,head+.005),(.43,.15,.37),4)
  for i in range(7):ell('curl' if i==5 else 'hair',(-.19+i*.055,.02,head+.205),(.075,.31,.08),4)
  plate('teal',0,-.19,shoulder-.18,.17,.30)
  for side in [-1,1]:
   for j in range(5):plate('white',side*(.04+j*.015),-.22,shoulder-.02-j*.028,.085,.045)
   plate('white',side*.115,-.204,leg+.04,.13,.37,.05);plate('white',side*.13,-.239,leg+.12,.11,.09,.03)
  plate('white',.13,-.241,shoulder-.115,.10,.10,.028)
  for x in [.11,.145]:plate('red' if x==.11 else 'teal',x,-.262,shoulder-.065,.012,.045)
  for x in [-.095,.095]:
   for xx in [x-.063,x+.063]:plate('ink',xx,-.238,head+.01,.012,.12,.012)
   for z in [head-.05,head+.069]:plate('ink',x,-.238,z,.138,.012,.012)
  plate('ink',0,-.238,head+.025,.05,.012,.012)
 else:
  ell('rust',(0,.025,head+.135),(.47,.41,.24),3)
  for i in range(55):
   a=rng.uniform(0,math.tau);r=rng.uniform(.07,.24);ell('rustLight' if i%4==0 else 'rust',(math.cos(a)*r,math.sin(a)*r*.8,head+.15+rng.uniform(-.04,.07)),(.065,.065,.07),4)
  for side in [-1,1]:
   for j in range(3):ell('rust',(side*.21,.09,head+.05-j*.062),(.09,.12,.085),4)
  # Scarf follows curved scalp, knot and tails at rear.
  for a in np.linspace(-1.3,1.3,24):ell('cream',(.17*math.sin(a),.12,head+.17*math.cos(a)),(.075,.12,.055),4)
  ell('cream',(.045,.235,head+.035),(.13,.09,.085),4);plate('cream',.08,.25,head-.065,.07,.20)
  for z in [head-.1,head-.04,head+.03]:plate('pink',.08,.267,z,.026,.026,.01)
  ell('sage',(0,-.21,leg+.28),(.40,.045,.52),5)
  for side in [-1,1]:link('sage',(side*.15,-.19,shoulder+.015),(side*.15,-.24,leg+.49),.035,.024);plate('sageLight',side*.11,-.248,leg+.16,.14,.15,.045)
  for x in [-.12,-.07]:plate('cream',x,-.276,leg+.25,.034,.095)
  for x in [.08,.13]:ell('red',(x,-.287,leg+.27),(.044,.025,.073),4);link('metal',(x,-.28,leg+.3),(x,-.28,leg+.39),.013)
  for side in [-1,1]:
   for x in [.11,.145,.175]:plate('skinShade',side*x,-.199,head-.048,.012,.012,.009)
 # Back ties, seams, shoulder yokes and collar shapes matter in three views.
 tie='cream' if role==0 else 'rust' if role==1 else 'sage' if role==4 else None
 if tie:
  link(tie,(-w*.45,.185,leg+.32),(w*.45,.185,leg+.32),.026)
  for side in [-1,1]:ell(tie,(side*.045,.212,leg+.32),(.085,.028,.044),5);link(tie,(side*.017,.212,leg+.30),(side*.045,.22,leg+.15),.023)
 if role in [2,3]:
  plate('navyLight' if role==2 else 'cream',0,.19,shoulder-.095,w*.8,.035)
  plate('cyan' if role==2 else 'white',0,.196,leg+.04,w*.85,.025)
 # Palette variation on the surface in 2x2 voxel patches, not thousands of objects.
 return grid

def mesh_grid(name,g):
 # Greedy coplanar merging while preserving stepped silhouette.
 verts=[];faces=[];mi=[]
 for ax in range(3):
  a=(ax+1)%3;b=(ax+2)%3
  for sign in [-1,1]:
   shifted=np.roll(g,-sign,axis=ax);sl=[slice(None)]*3;sl[ax]=-1 if sign==1 else 0;shifted[tuple(sl)]=0
   vis=(g!=0)&(shifted==0)
   for k in np.where(np.any(vis,axis=tuple(i for i in range(3) if i!=ax)))[0]:
    mask=np.take(np.where(vis,g,0),k,axis=ax)
    # axis remaining ordering corrected to (a,b)
    remaining=[i for i in range(3) if i!=ax]
    if remaining!=[a,b]:mask=mask.T
    mask=mask.copy()
    for u in range(mask.shape[0]):
     for v in range(mask.shape[1]):
      c=int(mask[u,v])
      if not c:continue
      w=1
      while u+w<mask.shape[0] and mask[u+w,v]==c:w+=1
      h=1
      while v+h<mask.shape[1] and np.all(mask[u:u+w,v+h]==c):h+=1
      mask[u:u+w,v:v+h]=0;corners=[(0,0),(w,0),(w,h),(0,h)]
      if sign<0:corners.reverse()
      f=[]
      for du,dv in corners:
       q=[0,0,0];q[ax]=k+(sign==1);q[a]=u+du;q[b]=v+dv;f.append(len(verts));verts.append(tuple(np.array(q)*U+OR))
      faces.append(f);mi.append(c-1)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 for key,c in COL.items():
  mat=bpy.data.materials.new('HF_'+key);mat.diffuse_color=c;mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.83;mesh.materials.append(mat)
 for p,i in zip(mesh.polygons,mi):p.material_index=i
 return obj

names=['SM_Cashier','SM_Chef','SM_TechClerk','SM_Pharmacist','SM_Florist'];reports=[]
for role,name in enumerate(names):
 bpy.ops.wm.read_factory_settings(use_empty=True);g=character(role);obj=mesh_grid(name,g);obj.select_set(True);bpy.context.view_layer.objects.active=obj
 scene=bpy.context.scene;scene['reference']='Bogota_Encargados_TresVistas.png';scene['grid_m']=U
 ref=bpy.data.images.load(str(ROOT/'outputs/DeliveryArt/References/Bogota_Encargados_TresVistas.png'));ref.pack();guide=bpy.data.objects.new('Reference - front side back',None);bpy.context.collection.objects.link(guide);guide.empty_display_type='IMAGE';guide.data=ref;guide.hide_render=True;guide.hide_viewport=True
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard';scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.20,.22,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 bpy.ops.object.camera_add(location=(2.7,-5,2.6));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.25;scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(1,-3,4));key=bpy.context.object;key.data.energy=350;key.data.size=4
 bpy.ops.object.light_add(type='AREA',location=(-2,2,3));fill=bpy.context.object;fill.data.energy=180;fill.data.size=3
 for label,pos in [('Hero',(2.7,-5,2.6)),('Front',(0,-6,1)),('Side',(6,0,1)),('Back',(0,6,1))]:
  cam.location=pos;cam.rotation_euler=(Vector((0,0,.98))-cam.location).to_track_quat('-Z','Y').to_euler();key.location=(pos[0]*.5,pos[1]*.5,4);key.rotation_euler=(Vector((0,0,1))-key.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'_'+label+'.png'));bpy.ops.render.render(write_still=True)
 reports.append({'name':name,'quads':len(obj.data.polygons),'grid_m':U})
 print('HF_CHARACTER_DONE',name,flush=True)
(OUT/'characters.json').write_text(json.dumps(reports,indent=2));(OUT/'palette.json').write_text(json.dumps({'HF_'+k:v for k,v in COL.items()}))
