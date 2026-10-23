"""Deterministic, metre-scale Bogota environment; build with Blender in background."""
import bpy, math, random, json, os, sys, bisect
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto')
OUT = ROOT/'outputs'/'Ciudad_Bogota'
WORK = ROOT/'work'/'bogota_ciudad'
for p in (OUT, OUT/'Unreal', OUT/'Unreal'/'Mallas', OUT/'Unreal'/'Texturas', WORK): p.mkdir(parents=True, exist_ok=True)
random.seed(814)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.collections):
    if d.name != 'Collection': bpy.data.collections.remove(d)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1700; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=False
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.38,.55,.78,1)
scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.42

PALETTE = {
 'asphalt':'343e47','asphalt2':'3c464e','concrete':'acada0','paver':'c7bd9f','paver2':'b7a98b',
 'curb':'dbd2b9','white':'eee5cd','cream':'d9c39d','sand':'b79a72','ochre':'d7a437',
 'brick':'ad583a','brick2':'c57951','brickdark':'7f4636','terracotta':'b7603d','roof':'884732',
 'blue':'387886','teal':'287d76','greenpaint':'3d6653','redpaint':'a84336','plaster':'ded7bd',
 'glass':'294d5b','glasslit':'698b91','metal':'303d41','wood':'715343','woodlight':'a47c4d',
 'leaf':'59743b','leaflight':'7f923f','leafdark':'345944','grass':'7f8950','grassdark':'586946',
 'soil':'74634b','rock':'868270','rocklight':'a19a82','yellow':'f4c751','busred':'c23830',
 'busdark':'862d2c','black':'242b30','water':'4d8588','amber':'ffd88a','signalred':'f04432',
 'signalgreen':'64c67d','signaloff':'394743','cycle':'558e83','muralpink':'ce7868','muralblue':'438b9d',
 'cloud':'e3e1d1','steel':'788c92','darksoil':'4b4939'
}
COLORS=list(PALETTE); CI={n:i for i,n in enumerate(COLORS)}
def rgba(h):return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
atlas=bpy.data.images.new('T_Bogota_Paleta',128,128)
emission=bpy.data.images.new('T_Bogota_Emision',128,128)
pix=[]; epix=[]
for y in range(128):
 for x in range(128):
  idx=(y//16)*8+x//16; n=COLORS[idx] if idx<len(COLORS) else 'white'
  pix.extend(rgba(PALETTE[n])); epix.extend(rgba(PALETTE[n]) if n in ('amber','signalred','signalgreen') else (0,0,0,1))
atlas.pixels.foreach_set(pix); emission.pixels.foreach_set(epix)
for img in (atlas,emission):
 img.filepath_raw=str(OUT/'Unreal'/'Texturas'/(img.name+'.png')); img.file_format='PNG'; img.save(); img.pack()
mat=bpy.data.materials.new('M_Bogota_Paleta'); mat.use_nodes=True
nt=mat.node_tree; bs=nt.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.8
tx=nt.nodes.new('ShaderNodeTexImage'); tx.image=atlas; tx.interpolation='Closest'; nt.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
te=nt.nodes.new('ShaderNodeTexImage'); te.image=emission;te.interpolation='Closest';nt.links.new(te.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.45

collections={}
def collection(n):
 if n not in collections:
  c=bpy.data.collections.new(n);scene.collection.children.link(c);collections[n]=c
 return collections[n]
for n in ['01_Terreno_y_cerros','02_Calles_andenes_ciclorrutas','03_Centro_historico','04_Norte_residencial','05_Sur_y_laderas','06_Parques_y_arbolado','07_Mobiliario_y_transporte','08_Puntos_de_reparto','09_Camaras_e_iluminacion']:collection(n)
library=collection('90_Biblioteca_modular');library.hide_render=True;library.hide_viewport=True
placements=[]; assets={}; routes=[]; drops=[]; terrain_tiles=[]

class Geo:
 def __init__(self):self.v=[];self.f=[];self.c=[]
 def face(self,vs,c):
  k=len(self.v);self.v.extend(vs);self.f.append(tuple(range(k,k+len(vs))));self.c.append(CI[c])
 def box(self,p,s,c,faces=(0,1,2,3,4,5)):
  x,y,z=p;a,b,d=[v/2 for v in s]
  vs=[(x-a,y-b,z-d),(x+a,y-b,z-d),(x+a,y+b,z-d),(x-a,y+b,z-d),(x-a,y-b,z+d),(x+a,y-b,z+d),(x+a,y+b,z+d),(x-a,y+b,z+d)]
  inds=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
  for i in faces:self.face([vs[j] for j in inds[i]],c)
 def bar(self,a,b,width,c):
  a,b=Vector(a),Vector(b);v=b-a;axis=v.normalized();side=axis.cross(Vector((0,0,1)))
  if side.length<.01:side=axis.cross(Vector((0,1,0)))
  side.normalize();up=axis.cross(side).normalized();s=side*width*.5;u=up*width*.5
  vs=[tuple(p+q) for p in (a,b) for q in (-s-u,s-u,s+u,-s+u)]
  for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:self.face([vs[i] for i in f],c)
 def mesh(self,n):
  m=bpy.data.meshes.new(n);m.from_pydata(self.v,[],self.f);m.materials.append(mat);m.update()
  uv=m.uv_layers.new(name='UV_Paleta')
  for poly,color in zip(m.polygons,self.c):
   u=((color%8)+.5)/8;v=((color//8)+.5)/8
   for li in poly.loop_indices:uv.data[li].uv=(u,v)
  return m

def asset(n,g,collision=None):
 m=g.mesh(n);o=bpy.data.objects.new(n,m);library.objects.link(o)
 assets[n]={'object':o,'collision':collision or [],'tris':sum(len(f)-2 for f in g.f)}
 return n
def place(n,p,rot=0,scale=(1,1,1),col='07_Mobiliario_y_transporte'):
 o=bpy.data.objects.new(n,assets[n]['object'].data);collection(col).objects.link(o);o.location=p;o.rotation_euler[2]=math.radians(rot);o.scale=scale
 o['asset_unreal']=n
 placements.append({'asset':n,'position_m':list(p),'yaw_deg':rot,'scale':list(scale),'zone':col})
 return o
def unique(n,g,col,collision=None):
 asset(n,g,collision);return place(n,(0,0,0),col=col)

# Roads interpolate elevation continuously; scenic terrain is quantized outside their corridors.
XS=[-210,-140,-70,0,70,140,210]; YS=list(range(-420,421,70))
def elevation_raw(x,y):
 south=max(0,(-y-170)/250)
 return 3+.010*(y+420)+.032*max(0,x)+south*(8+36*max(0,(-x-45)/165)+9*max(0,x/210))
def elev(x,y):
 ix=max(0,min(len(XS)-2,bisect.bisect_right(XS,x)-1));iy=max(0,min(len(YS)-2,bisect.bisect_right(YS,y)-1))
 a,b=XS[ix],XS[ix+1];c,d=YS[iy],YS[iy+1];u=(x-a)/(b-a);v=(y-c)/(d-c)
 return (1-v)*((1-u)*elevation_raw(a,c)+u*elevation_raw(b,c))+v*((1-u)*elevation_raw(a,d)+u*elevation_raw(b,d))
def terrain_h(x,y):
 z=elev(x,y)
 if x>224:
  t=(x-224)/200; ridge=90+34*math.sin(y*.009)+20*math.sin(y*.025+1)+60*math.exp(-((y+5)/95)**2)
  z+=max(0,t)**.68*ridge + max(0,t)*7*math.sin(x*.1+y*.08)
 elif x<-222:
  z+=max(0,(-x-222)*.065)
 return math.floor(z/1.8)*1.8

# Coarse terrain outside engineered street strips; no buried voxel faces.
step=7; heights={}
for ix,x in enumerate(range(-252,428,step)):
 for iy,y in enumerate(range(-462,463,step)):heights[(ix,iy)]=terrain_h(x+step/2,y+step/2)
chunks={}
for (ix,iy),z in heights.items():
 x=-252+ix*step;y=-462+iy*step;key=(ix//16,iy//16);g=chunks.setdefault(key,Geo())
 c=random.choices(['grass','grassdark','leafdark','soil','rock'],[3,7,7,1,1] if x>224 else [3,3,1,1,0])[0]
 g.face([(x,y,z),(x+step,y,z),(x+step,y+step,z),(x,y+step,z)],c)
 for dx,dy,vs in [(1,0,[(x+step,y,z),(x+step,y+step,z)]),(-1,0,[(x,y+step,z),(x,y,z)]),(0,1,[(x+step,y+step,z),(x,y+step,z)]),(0,-1,[(x,y,z),(x+step,y,z)])]:
  nz=heights.get((ix+dx,iy+dy),-8)
  if nz<z:
   a,b=vs;g.face([a,(a[0],a[1],nz),(b[0],b[1],nz),b],'soil' if z-nz<5 else 'rock')
for key,g in chunks.items():
 n='SM_Terreno_%02d_%02d'%key;unique(n,g,'01_Terreno_y_cerros');terrain_tiles.append(n)

road_chunks={}; collision_by_road={}; max_grade=0
def roadgeo(y):return road_chunks.setdefault(int((y+462)//140),Geo())
def surf(g,x0,y0,x1,y1,offset,c):
 g.face([(x0,y0,elev(x0,y0)+offset),(x1,y0,elev(x1,y0)+offset),(x1,y1,elev(x1,y1)+offset),(x0,y1,elev(x0,y1)+offset)],c)
def patch(g,x0,y0,x1,y1,c,off=.09):surf(g,x0,y0,x1,y1,off,c)
for x in XS:
 w=10 if x==-70 else 6
 for ya,yb in zip(YS[:-1],YS[1:]):
  g=roadgeo((ya+yb)*.5)
  for y in range(ya,yb,5):
   patch(g,x-w,y,x+w,y+5,'asphalt')
   # Sidewalk ramps meet the crossing surface over the last 2 metres.
   for side in (-1,1):
    a,b=sorted((x+side*w,x+side*(w+3)))
    surf(g,a,y,b,y+5,.28,'concrete')
    if min(abs(y-r) for r in YS)>10:
     surf(g,x+side*(w-.2)-.10,y,x+side*(w-.2)+.1,y+5,.13,'curb')
   if min(abs(y-r) for r in YS)>10:
    if x==-70:
     for side in (-1,1):
      patch(g,x+side*3.15-.08,y,x+side*3.15+.08,y+5,'yellow',.13)
      patch(g,x+side*8.7-.7,y,x+side*8.7+.7,y+5,'cycle',.14)
    if y%10==0:patch(g,x-.07,y,x+.07,y+2.8,'yellow',.14)
  za,zb=elev(x,ya),elev(x,yb);max_grade=max(max_grade,abs(zb-za)/(yb-ya))
  routes.append({'a':[x,ya,za+.2],'b':[x,yb,zb+.2],'width_m':2*w,'kind':'bus_arterial' if x==-70 else 'street','grade':abs(zb-za)/(yb-ya)})
for y in YS:
 g=roadgeo(y)
 for xa,xb in zip(XS[:-1],XS[1:]):
  for x in range(xa,xb,5):
   # Intersections belong to the north-south road, so no coplanar road layers.
   if any(abs(x+2.5-r)<(10 if r==-70 else 6) for r in XS):continue
   patch(g,x,y-6,x+5,y+6,'asphalt')
   for side in (-1,1):surf(g,x,y+side*7.5-1.5,x+5,y+side*7.5+1.5,.28,'concrete')
   if min(abs(x-r) for r in XS)>12 and x%10==0:patch(g,x,y-.07,x+2.8,y+.07,'white',.14)
  za,zb=elev(xa,y),elev(xb,y);max_grade=max(max_grade,abs(zb-za)/(xb-xa))
  routes.append({'a':[xa,y,za+.2],'b':[xb,y,zb+.2],'width_m':12,'kind':'street','grade':abs(zb-za)/(xb-xa)})
for x in XS:
 for y in YS:
  g=roadgeo(y);w=10 if x==-70 else 6
  # Zebra markings and dropped crossings. Fine surfaces lie above the base terrain.
  for sign in (-1,1):
   yy=y+sign*9
   for xx in range(int(x-w+1),int(x+w),2):patch(g,xx,yy-1.2,xx+.8,yy+1.2,'white',.15)
   # continuous crossing ramps replace kerb steps with a 0.19m rise over 2m
   for side in (-1,1):
    xx=x+side*(w+1.5);surf(g,xx-1.5,yy-1.5,xx+1.5,yy+1.5,.16,'concrete')
for key,g in road_chunks.items():unique('SM_Vialidad_%02d'%key,g,'02_Calles_andenes_ciclorrutas')

# Tiny raised block lettering, merged into each asset.
FONT={
 'A':['01110','10001','10001','11111','10001','10001','10001'],'B':['11110','10001','10001','11110','10001','10001','11110'],
 'C':['01111','10000','10000','10000','10000','10000','01111'],'D':['11110','10001','10001','10001','10001','10001','11110'],
 'E':['11111','10000','10000','11110','10000','10000','11111'],'F':['11111','10000','10000','11110','10000','10000','10000'],
 'G':['01111','10000','10000','10111','10001','10001','01110'],'H':['10001','10001','10001','11111','10001','10001','10001'],
 'I':['111','010','010','010','010','010','111'],'J':['00111','00010','00010','00010','10010','10010','01100'],
 'K':['10001','10010','10100','11000','10100','10010','10001'],'L':['10000','10000','10000','10000','10000','10000','11111'],
 'M':['10001','11011','10101','10101','10001','10001','10001'],'N':['10001','11001','11001','10101','10011','10011','10001'],
 'O':['01110','10001','10001','10001','10001','10001','01110'],'P':['11110','10001','10001','11110','10000','10000','10000'],
 'Q':['01110','10001','10001','10001','10101','10010','01101'],'R':['11110','10001','10001','11110','10100','10010','10001'],
 'S':['01111','10000','10000','01110','00001','00001','11110'],'T':['11111','00100','00100','00100','00100','00100','00100'],
 'U':['10001','10001','10001','10001','10001','10001','01110'],'V':['10001','10001','10001','10001','10001','01010','00100'],
 'W':['10001','10001','10001','10101','10101','10101','01010'],'X':['10001','10001','01010','00100','01010','10001','10001'],
 'Y':['10001','10001','01010','00100','00100','00100','00100'],'Z':['11111','00001','00010','00100','01000','10000','11111'],
 '0':['01110','10001','10011','10101','11001','10001','01110'],'1':['010','110','010','010','010','010','111'],
 '2':['01110','10001','00001','00010','00100','01000','11111'],'3':['11110','00001','00001','01110','00001','00001','11110'],
 '9':['01110','10001','10001','01111','00001','00001','01110'],' ':['000']*7}
def letters(g,text,x,y,z,size,c):
 widths=[len(FONT.get(ch,FONT[' '])[0]) for ch in text];start=x-sum((w+1)*size for w in widths)/2
 for ch,w in zip(text,widths):
  for row,s in enumerate(FONT.get(ch,FONT[' '])):
   # merge consecutive pixels in a row into a single bar
   j=0
   while j<len(s):
    if s[j]=='0':j+=1;continue
    k=j+1
    while k<len(s) and s[k]=='1':k+=1
    g.box((start+(j+k)*size*.5,y,z+(6-row)*size),((k-j)*size,.07,size),c);j=k
  start+=(w+1)*size

def window(g,x,y,z,w=1.6,h=1.8,trim='cream',bars=False):
 g.box((x,y,z),(w+.3,.20,h+.35),trim)
 g.box((x,y-.13,z),(w,.08,h),'glass')
 g.box((x,y-.20,z),(.11,.11,h),'wood' if bars else 'metal')
 g.box((x,y-.2,z),(w,.11,.10),trim)
 g.box((x,y-.22,z-h/2-.09),(w+.48,.48,.18),trim)
 if bars:
  for d in (-.45,.45):g.box((x+d*w/2,y-.26,z),(.07,.08,h),'metal')

def house(style,i):
 g=Geo();r=random.Random(i*93+len(style));w=r.choice([9,10,11,12]);depth=r.choice([11,12,14]);floors=r.choice([2,2,3]) if style!='norte' else r.choice([4,5,6]);h=floors*3
 facade=r.choice(['cream','ochre','white','teal','redpaint']) if style=='centro' else r.choice(['brick','brick2','ochre','blue','cream']) if style=='sur' else r.choice(['brick','brick2','plaster','sand'])
 g.box((0,0,h/2),(w,depth,h),facade,faces=(1,2,3,4,5));g.box((0,0,.45),(w+.25,depth+.25,.9),'sand')
 # Floors and lintels give a readable modular rhythm instead of free-standing cubes.
 for fl in range(1,floors+1):g.box((0,0,fl*3),(w+.3,depth+.3,.22),'cream' if style=='centro' else 'sand')
 for fl in range(floors):
  z=fl*3+1.7
  for xx in [-w*.31,0,w*.31]:
   if fl==0 and abs(xx)<.1:continue
   window(g,xx,-depth/2-.08,z,1.7,1.7,'cream' if style=='centro' else 'plaster',style!='norte')
   # Back and side panels are cheap coloured quads, with solid building collision.
   g.box((xx,depth/2+.035,z),(1.7,.06,1.7),'glass')
  for sy in (-depth*.3,0,depth*.3):
   for side in (-1,1):g.box((side*(w/2+.025),sy,z),(.05,1.6,1.7),'glass')
 g.box((0,-depth/2-.13,1.25),(1.9,.20,2.5),'wood' if style=='centro' else 'metal')
 g.box((.6,-depth/2-.26,1.2),(.1,.1,.16),'amber')
 # Small brick accents retain the voxel scale without geometry for every brick.
 for k in range(30 if style=='sur' else 14):
  xx=r.uniform(-w/2+.4,w/2-.4);z=r.uniform(.6,h-.4)
  if abs(xx)%3>1.05:g.box((xx,-depth/2-.018,z),(.48,.05,.22),'brickdark' if style=='sur' else 'sand')
 if style=='centro':
  # Terracotta roof: stepped slopes, ridge and selected rows of tile ends.
  for s in range(7):g.box((0,0,h+.17+s*.29),(w+1,depth+1-s*(depth/7),.3),'terracotta' if s%2 else 'roof')
  for xx in range(-int(w/2),int(w/2)+1):g.box((xx,-depth/2-.54,h+.17),(.28,.30,.27),'brick2')
  if i%2==0:
   g.box((0,-depth/2-.75,3.7),(3.9,1.5,.25),'sand')
   g.box((0,-depth/2-1.40,4.35),(3.9,.18,.13),'greenpaint')
   for j in range(-6,7):g.box((j*.3,-depth/2-1.40,3.98),(.12,.13,.65),'greenpaint')
 elif style=='sur':
  g.box((0,0,h+.2),(w+.5,depth+.5,.4),'concrete')
  for sx in (-1,1):g.box((sx*(w/2-.15),0,h+.65),(.3,depth,1),'brick')
  g.box((w*.26,depth*.24,h+1.0),(1.7,1.7,1.5),'blue');g.box((w*.26,depth*.24,h+1.8),(1.9,1.9,.18),'metal')
  for xx in (-w*.4,w*.4):g.box((xx,depth*.4,h+1.1),(.12,.12,1.8),'metal')
 else:
  g.box((0,0,h+.2),(w+.7,depth+.7,.4),'plaster');g.box((2,1,h+.8),(3,4,1.4),'metal')
  for fl in range(1,floors):
   g.box((0,-depth/2-.75,fl*3+.1),(w*.8,1.5,.22),'plaster')
   g.box((0,-depth/2-1.4,fl*3+.7),(w*.8,.12,1),'glasslit')
 if i%3==0:
  word=r.choice(['TIENDA','CAFE','PAN','FRUTAS'])
  g.box((0,-depth/2-.27,2.85),(w*.85,.35,.9),'redpaint' if style=='sur' else 'greenpaint')
  letters(g,word,0,-depth/2-.5,2.56,.095,'white')
  for j in range(int(w)):
   g.box((-w/2+.5+j,-depth/2-1,2.3),(.97,1.8,.2),'white' if j%2 else 'redpaint')
 n='SM_'+style.capitalize()+'_%02d'%i
 asset(n,g,[{'center':[0,0,h/2],'size':[w,depth,h]}]);return n,w,depth,h

housing={s:[house(s,i) for i in range(9)] for s in ['centro','norte','sur']}
def tower(n,w,d,h,brick=False):
 g=Geo();g.box((0,0,h/2),(w,d,h),'brick' if brick else 'glass')
 for z in range(3,int(h),3):
  g.box((0,0,z),(w+.4,d+.4,.26),'sand' if brick else 'steel')
 for x in range(-int(w/2),int(w/2)+1,3):
  for sign in (-1,1):g.box((x,sign*(d/2+.13),h/2),(.32,.28,h),'plaster')
 for y in range(-int(d/2),int(d/2)+1,3):
  for sign in (-1,1):g.box((sign*(w/2+.13),y,h/2),(.28,.32,h),'plaster')
 g.box((0,0,h+.5),(w+1,d+1,1),'plaster');g.box((0,0,h+2),(w*.6,d*.5,3),'metal')
 g.box((0,0,1.8),(w+3,d+3,3.6),'sand');g.box((0,-d/2-1.6,1.7),(w*.7,.08,2.9),'glass')
 asset(n,g,[{'center':[0,0,h/2],'size':[w+1,d+1,h]}]);return n
tower('SM_Torre_Colpatria',17,18,92)
tower('SM_Oficinas_Calle100',19,21,54)
tower('SM_Torre_Ladrillo',16,18,36,True)

# Reusable urban elements.
for i in range(5):
 g=Geo();r=random.Random(700+i);g.box((0,0,2.2),(.6,.6,4.4),'wood');g.box((.6,0,3.6),(1.4,.35,.35),'wood')
 for z,w in [(3.7,3.3),(4.7,4.9),(5.7,4.1),(6.5,2.8)]:
  g.box((r.uniform(-.5,.5),r.uniform(-.5,.5),z),(w,w*.84,1.2),['leaf','leaflight','leafdark'][i%3])
  for j in range(2):g.box((r.uniform(-w*.4,w*.4),r.uniform(-w*.4,w*.4),z+.55),(.9,.9,.55),r.choice(['leaf','leaflight','leafdark']))
 asset('SM_Arbol_%02d'%i,g,[{'center':[0,0,2.1],'size':[.6,.6,4.2]}])
g=Geo();g.box((0,0,.13),(1,1,.26),'metal');g.box((0,0,2.45),(.22,.22,4.9),'metal');g.box((0,0,4.35),(.7,.7,.8),'amber');g.box((0,0,4.86),(1,1,.22),'metal');g.box((0,0,5.04),(.6,.6,.18),'metal')
for x in (-.36,.36):
 for y in (-.36,.36):g.box((x,y,4.37),(.10,.10,.9),'metal')
asset('SM_Farola_Centro',g,[{'center':[0,0,2.4],'size':[.35,.35,4.8]}])
g=Geo();g.box((0,0,3),(.2,.2,6),'metal');g.box((1,0,6),(2.3,.22,.2),'metal');g.box((1.65,0,5.83),(.9,.45,.16),'amber');asset('SM_Luz_Vial',g)
g=Geo();g.box((0,0,2),(.16,.16,4),'metal');g.box((0,0,3.5),(.65,.4,1.6),'metal')
for j,c in enumerate(['signalred','signaloff','signaloff']):g.box((0,-.225,4.0-j*.45),(.35,.06,.32),c)
asset('SM_Semaforo_Rojo',g,[{'center':[0,0,2],'size':[.25,.25,4]}])
g=Geo();g.box((0,0,2),(.16,.16,4),'metal');g.box((0,0,3.5),(.65,.4,1.6),'metal')
for j,c in enumerate(['signaloff','signaloff','signalgreen']):g.box((0,-.225,4.0-j*.45),(.35,.06,.32),c)
asset('SM_Semaforo_Verde',g,[{'center':[0,0,2],'size':[.25,.25,4]}])
g=Geo()
for x in (-.9,.9):g.box((x,0,.38),(.18,.65,.76),'metal')
for y in (-.22,0,.22):g.box((0,y,.75),(2.3,.18,.12),'woodlight')
for z in (1.05,1.30):g.box((0,.3,z),(2.3,.1,.18),'woodlight')
asset('SM_Banca',g)
g=Geo();g.box((0,0,.48),(.65,.65,.96),'metal');g.box((0,0,1.05),(.78,.78,.16),'steel');asset('SM_Caneca',g)
g=Geo();g.box((0,0,.5),(3,1.3,1),'sand');g.box((0,0,1.18),(2.7,1,1.1),'leafdark');g.box((0,0,1.8),(2.4,.9,.4),'leaf');asset('SM_Jardinera',g)
g=Geo();g.box((0,0,.45),(.25,.25,.9),'metal');g.box((0,0,.55),(.28,.28,.15),'yellow');asset('SM_Bolardo',g)
g=Geo();g.box((0,0,3.05),(6,2.5,.25),'metal')
for x in (-2.7,2.7):g.box((x,.9,1.5),(.2,.2,3),'metal')
g.box((0,1,1.7),(5.5,.08,2.2),'glasslit');g.box((0,.5,.5),(4,.5,.15),'wood');asset('SM_Paradero',g)
g=Geo();g.box((0,0,.5),(4,2.2,1),'busred');g.box((0,0,1.25),(2.3,2.05,.65),'glass');g.box((0,0,1.66),(2.5,2.1,.15),'busred')
for x in (-1.3,1.3):
 for y in (-1.13,1.13):g.box((x,y,.4),(.7,.25,.8),'black')
asset('SM_Carro_Rojo',g)
g=Geo();g.box((0,0,.6),(4.4,2.2,1.05),'yellow');g.box((0,0,1.33),(2.5,2.05,.65),'glass');g.box((0,0,1.69),(2.6,2.1,.15),'yellow');g.box((0,0,1.9),(.6,.4,.25),'white')
for x in (-1.4,1.4):
 for y in (-1.13,1.13):g.box((x,y,.42),(.8,.24,.85),'black')
asset('SM_Taxi',g)
g=Geo();g.box((0,0,1.6),(18,2.65,2.9),'busred');g.box((0,0,3.15),(18.2,2.8,.25),'busdark')
for x in [-7.5,-5.5,-3.5,-1.5,2,4,6,8]:
 for y in [-1.34,1.34]:g.box((x,y,2.15),(1.6,.05,1.2),'glass')
g.box((.25,0,1.65),(1.35,2.74,2.9),'metal')
for x in [-6.5,-1.5,6.5]:
 for y in [-1.4,1.4]:g.box((x,y,.62),(1.2,.3,1.25),'black')
g.box((9.03,0,2.1),(.1,2.3,1.15),'glass');letters(g,'TRANSMILENIO',-4,-1.40,2.97,.065,'amber');asset('SM_Bus_Articulado',g)

# Landmark cathedral built as a distinctive stepped silhouette, front is local -Y.
g=Geo();g.box((0,6,9),(25,30,18),'cream');g.box((0,-9.6,8),(25,1.4,16),'sand')
for x in [-12,-8,-4,4,8,12]:
 g.box((x,-10.7,8),(.85,1.2,16),'cream');g.box((x,-10.9,1.0),(1.4,1.7,2),'paver')
for x in [-7.5,0,7.5]:
 g.box((x,-10.5,3.4),(3.6,.28,6.8),'wood');g.box((x,-10.8,6.7),(4.3,.5,.5),'cream');g.box((x,-10.6,11.2),(2.5,.25,3),'glass')
for z,w in [(17,27),(17.6,25),(18.2,22),(18.8,18),(19.4,14),(20,10),(20.6,6)]:g.box((0,-9.5,z),(w,3,.65),'cream')
for x in [-10.8,10.8]:
 g.box((x,-4,20),(6.2,7,13),'cream');g.box((x,-7.6,22.5),(2.7,.15,4.5),'black')
 for z,w in [(25.8,7),(26.4,6.4),(27,5.5),(27.6,4.6),(28.2,3.6),(28.8,2.6),(29.4,1.6)]:g.box((x,-4,z),(w,w,.65),'sand' if z<27 else 'metal')
 g.box((x,-4,30.8),(.35,.35,2.1),'metal');g.box((x,-4,31.2),(1.5,.35,.3),'metal')
for s in range(6):g.box((0,9,18.4+s*.35),(24-s*3.2,22,.36),'terracotta')
asset('SM_Catedral_Primada',g,[{'center':[0,5,10],'size':[27,33,20]}])

def civic(n,w,d,h,arches=False):
 g=Geo();g.box((0,0,h/2),(w,d,h),'cream');g.box((0,0,1),(w+1,d+1,2),'sand')
 for x in range(-int(w/2)+2,int(w/2),3):
  g.box((x,-d/2-.8,h*.45),(.6,1.2,h*.85),'paver')
  if x<int(w/2)-3:window(g,x+1.5,-d/2-.12,h*.6,1.4,2.3,'sand')
 for z in [h*.42,h-.4,h]:g.box((0,0,z),(w+1.5,d+1,.35),'sand')
 g.box((0,-d/2-.1,1.8),(2.6,.25,3.6),'wood')
 asset(n,g,[{'center':[0,0,h/2],'size':[w,d,h]}]);return n
civic('SM_Capitolio',43,15,11);civic('SM_Lievano',39,12,13);civic('SM_Palacio_Justicia',34,13,12)
g=Geo()
for z,s in [(.18,5),(.5,4.3),(.95,3.6),(2.5,2.7)]:g.box((0,0,z),(s,s,.4 if z<1 else 3),'sand')
g.box((0,0,4.55),(.9,.65,1.4),'greenpaint');g.box((0,0,5.6),(.65,.6,.75),'greenpaint')
for x in [-.25,.25]:g.box((x,0,3.6),(.28,.4,1.1),'greenpaint')
g.bar((.5,0,4.9),(1.1,-.1,4.3),.24,'greenpaint');g.bar((-.5,0,4.9),(-.9,0,4.5),.24,'greenpaint');asset('SM_Estatua_Bolivar',g)
g=Geo();g.box((0,0,4),(10,16,8),'white');g.box((0,-8,6),(10.5,1,6),'cream')
for x in [-3.7,3.7]:
 g.box((x,-6,7),(2.3,3,10),'white');g.box((x,-6,12.3),(.3,.3,2.3),'metal');g.box((x,-6,12.6),(1.2,.3,.25),'metal')
for s in range(5):g.box((0,0,8.1+s*.4),(11-s*1.9,17,.42),'roof')
g.box((0,-8.6,2),(2,.15,4),'wood');asset('SM_Santuario_Monserrate',g)

# Plaza orientation: cathedral east, Capitol south, Lievano west and Justice north.
plaza=(105,-105);z=elev(*plaza)+.5;g=Geo();g.box((105,-105,z-.5),(51,51,1),'paver')
for x in range(80,131,5):g.box((x,-105,z+.015),(.09,51,.03),'paver2')
for y in range(-130,-79,5):g.box((105,y,z+.02),(51,.09,.03),'paver2')
unique('SM_Plaza_Bolivar',g,'03_Centro_historico');place('SM_Catedral_Primada',(159,-105,elev(159,-105)+.4),-90,col='03_Centro_historico')
place('SM_Capitolio',(105,-151,elev(105,-151)+.4),180,col='03_Centro_historico');place('SM_Lievano',(54,-105,elev(54,-105)+.4),90,col='03_Centro_historico');place('SM_Palacio_Justicia',(105,-55,elev(105,-55)+.4),0,col='03_Centro_historico');place('SM_Estatua_Bolivar',(105,-105,z),col='03_Centro_historico')
place('SM_Torre_Colpatria',(33,50,elev(33,50)+.4),col='03_Centro_historico')

reserved={(4,4),(5,4),(4,3),(3,4),(4,5),(3,6),(2,9),(2,10),(4,11),(5,1),(4,1),(0,1),(0,8)}
building_count=0
for ix,(xa,xb) in enumerate(zip(XS[:-1],XS[1:])):
 for iy,(ya,yb) in enumerate(zip(YS[:-1],YS[1:])):
  if (ix,iy) in reserved:continue
  style='sur' if yb<=-175 else 'norte' if ya>=140 else 'centro';col={'sur':'05_Sur_y_laderas','centro':'03_Centro_historico','norte':'04_Norte_residencial'}[style]
  # Two street-facing rows per block. Back courts and alleys remain open.
  for row in [-1,1]:
   for j in range(3):
    x=xa+17+j*18;y=(ya+yb)/2+row*20
    if abs(x+70)<18:x+=5
    a,w,d,h=housing[style][(ix*7+iy*3+j+(row==1)*4)%9]
    z=elev(x,y)+.45
    g=roadgeo(y);g.box((x,y,z-1.1),(w+1.4,d+1.4,2.2),'sand' if style!='sur' else 'brickdark')
    place(a,(x,y,z),0 if row==-1 else 180,col=col);building_count+=1
    if (ix+iy+j)%4==0:
     entry=(x,y+row*(d/2+2),elev(x,y+row*(d/2+2))+.5)
     drops.append({'id':'ENTREGA_%03d'%len(drops),'position_m':list(entry),'district':style,'kind':'vivienda_comercio','asset':a})
  if style=='norte' and (ix+iy)%3==0:
   x=(xa+xb)*.5;y=(ya+yb)*.5;place('SM_Oficinas_Calle100' if iy>9 else 'SM_Torre_Ladrillo',(x,y,elev(x,y)+.5),col=col);building_count+=1

# Parks with crossings, planted beds and delivery-accessible paths.
def park(name,cx,cy,sx,sy,court=False):
 g=Geo();z=elev(cx,cy)+.40;g.box((cx,cy,z-.5),(sx,sy,1),'grass')
 g.box((cx,cy,z+.04),(4,sy,.08),'paver');g.box((cx,cy,z+.05),(sx,4,.08),'paver')
 if court:
  g.box((cx+sx*.22,cy+sy*.17,z+.08),(20,11,.1),'cycle')
  for s in [-1,1]:g.box((cx+sx*.22+s*9.6,cy+sy*.17,z+.15),(.1,10,.03),'white')
  for s in [-1,1]:g.box((cx+sx*.22,cy+sy*.17+s*5,z+.15),(19.3,.1,.03),'white')
  g.box((cx+sx*.22,cy+sy*.17,z+.15),(.1,10,.03),'white')
 for dx in [-sx*.37,sx*.37]:
  for dy in [-sy*.35,sy*.35]:
   place('SM_Arbol_%02d'%(int(abs(dx+dy))%5),(cx+dx,cy+dy,z),col='06_Parques_y_arbolado')
   place('SM_Banca',(cx+dx*.7,cy+dy*.7,z),0 if dy>0 else 180,col='06_Parques_y_arbolado')
 for dx in [-sx*.2,sx*.2]:
  for dy in [-sy*.35,sy*.35]:place('SM_Arbol_%02d'%random.randrange(5),(cx+dx,cy+dy,z),col='06_Parques_y_arbolado')
 unique(name,g,'06_Parques_y_arbolado');drops.append({'id':name,'position_m':[cx,cy-sy/2-2,z],'district':'parque','kind':'plaza'})
park('SM_Parque_Virrey',-35,280,48,110)
park('SM_Plaza_Usaquen',105,385,48,48)
park('SM_Parque_Sur',105,-315,48,48,True)
park('SM_Parque_Barrio_Occidente',-175,175,48,48,True)

# Portal and a southern church around a market plaza.
g=Geo();g.box((0,0,.8),(44,24,1.6),'concrete')
for x in range(-20,21,8):g.box((x,0,3.7),(.5,.5,6),'metal')
g.box((0,0,6.8),(47,27,.6),'steel');g.box((0,-12,4.7),(43,.3,1.6),'busdark');letters(g,'PORTAL SUR',0,-12.25,4.18,.14,'white')
asset('SM_Portal_Sur',g,[{'center':[0,0,.8],'size':[44,24,1.6]}]);place('SM_Portal_Sur',(175,-315,elev(175,-315)+.4),col='05_Sur_y_laderas')
place('SM_Santuario_Monserrate',(175,-348,elev(175,-348)+.5),col='05_Sur_y_laderas')
mx,my=308,14;mz=terrain_h(mx,my)+1.8;g=Geo();g.box((mx,my,mz-3),(38,37,6),'rock');unique('SM_Terraza_Monserrate',g,'01_Terreno_y_cerros');place('SM_Santuario_Monserrate',(mx,my,mz),-90,col='03_Centro_historico')

# Eastern scenic access route with broad switchbacks, graded for a bicycle.
mountain_path=[]
for i in range(101):
 t=i/100;y=-130+t*150;x=218+90*t+24*math.sin(t*4*math.pi);z=elev(218,-130)+(mz-elev(218,-130))*t
 mountain_path.append((x,y,z+.2))
g=Geo();path_grade=0
for a,b in zip(mountain_path[:-1],mountain_path[1:]):
 a,b=Vector(a),Vector(b);side=(b-a).cross(Vector((0,0,1))).normalized()*2.3
 g.face([tuple(a-side),tuple(b-side),tuple(b+side),tuple(a+side)],'paver')
 path_grade=max(path_grade,abs(b.z-a.z)/max(.01,math.hypot(b.x-a.x,b.y-a.y)))
# Keep summit approach as a pedestrian scenic trail: street network remains separately traversable.
unique('SM_Sendero_Cerros_Peatonal',g,'01_Terreno_y_cerros')

# Signals, lamps, trees and vehicle staging. Traffic objects are static examples for engine logic.
for ix,x in enumerate(XS):
 for iy,y in enumerate(YS):
  if ix in (0,len(XS)-1) or iy in (0,len(YS)-1):continue
  w=10 if x==-70 else 6
  for s in [-1,1]:place('SM_Semaforo_Rojo' if ix%2 else 'SM_Semaforo_Verde',(x+s*(w+1),y+s*7.5,elev(x+s*(w+1),y+s*7.5)+.3),0 if s>0 else 180)
 for y in range(-393,420,35):
  w=10 if x==-70 else 6
  for s in [-1,1]:
   xx=x+s*(w+2.2);yy=y
   place('SM_Luz_Vial' if x==-70 else 'SM_Farola_Centro',(xx,yy,elev(xx,yy)+.3),90 if s>0 else -90)
   if y%70!=0 and x!=-70:
    xx=x+s*(w+5);yy=y+8
    place('SM_Arbol_%02d'%random.randrange(5),(xx,yy,elev(xx,yy)+.4),scale=(.75,.75,.75),col='06_Parques_y_arbolado')
for x in [84,126]:
 for y in [-126,-84]:place('SM_Farola_Centro',(x,y,z+.05));place('SM_Banca',(x,y+2,z+.05),180 if y<-100 else 0)
for i in range(90):
 y=random.choice(YS[:-1])+random.choice([22,45]);x=random.choice(XS)
 if -160<y<0 and x>100:continue
 xx=x+random.choice([-1,1])*(5.6 if x==-70 else 3)
 place('SM_Taxi' if i%3==0 else 'SM_Carro_Rojo',(xx,y,elev(xx,y)+.18),90 if i%2 else -90)
for i,y in enumerate([-365,-250,-100,40,200,345]):place('SM_Bus_Articulado',(-70+(-1 if i%2 else 1)*1.7,y,elev(-70,y)+.18),90 if i%2 else -90)
for y in [-270,-60,150,320]:
 xx=-85;place('SM_Paradero',(xx,y,elev(xx,y)+.3),90)
for i in range(110):
 x=random.uniform(250,420);y=random.uniform(-450,450);z=terrain_h(x,y)
 place('SM_Arbol_%02d'%random.randrange(5),(x,y,z),scale=(1.7,1.7,1.7),col='06_Parques_y_arbolado')

# Bike/foot spawn markers are empties, never rendered or exported as collision.
markers=[('INICIO_REPARTIDOR',(90,-120,elev(90,-120)+.5)),('BICICLETA_INICIAL',(87,-120,elev(87,-120)+.5))]
for name,p in markers+[(d['id'],d['position_m']) for d in drops]:
 o=bpy.data.objects.new(name,None);collection('08_Puntos_de_reparto').objects.link(o);o.location=p;o.empty_display_type='ARROWS';o.empty_display_size=1.2
 o['uso']='Marcador de logica; no geometria de juego'

def camera(n,loc,target,lens=45,ortho=None):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);collection('09_Camaras_e_iluminacion').objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=4000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
cam=camera('Vista_general_Bogota',(-780,-950,880),(40,-5,20),ortho=1190)
camera('Calle_Candelaria',(105,-137,elev(105,-137)+2.4),(155,-101,elev(155,-101)+12),lens=23)
camera('Norte_Parque_Virrey',(-92,234,elev(-92,234)+3),(-27,290,20),lens=24)
camera('Sur_Laderas',(-212,-390,elev(-212,-390)+3),(-130,-290,35),lens=23)
ld=bpy.data.lights.new('Sol_Bogota','SUN');lo=bpy.data.objects.new('Sol_Bogota',ld);collection('09_Camaras_e_iluminacion').objects.link(lo);lo.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-28));ld.energy=3.0;ld.angle=math.radians(9)
scene.camera=cam
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  a.spaces.active.region_3d.view_distance=1000;a.spaces.active.region_3d.view_location=Vector((30,0,25));a.spaces.active.clip_end=5000
  a.spaces.active.shading.type='MATERIAL'
scene['descripcion']='Bogota compacta voxel para juego de reparto. +Y norte, +X oriente; metros.'
scene['alcance']='Mapa artistico modular, no cartografia real. Calles conectadas, geometria de trafico sin simulacion.'
scene['pendiente_maxima_calles_porcentaje']=round(max_grade*100,2)
scene['ciclo_iluminacion']='Escena diurna de presentacion; ciclo dinamico debe implementarse en Unreal.'

# Save before exports/renders. The .blend contains packed textures and linked mesh instances.
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ciudad_bogota.blend'))
print('BOGOTA_BLEND_SAVED',flush=True)

manifest={'schema':1,'units':'metres','axes':{'north':'+Y','east':'+X','up':'+Z'},'seed':814,'bounds_m':[-252,-462,428,462],
 'road_max_grade_percent':round(max_grade*100,2),'buildings':building_count+9,'placements':placements,'assets':{},'routes':routes,'delivery_points':drops,
 'spawn_points':[{'id':n,'position_m':list(p)} for n,p in markers]}
library.hide_viewport=False
for idx,(name,info) in enumerate(assets.items()):
 bpy.ops.object.select_all(action='DESELECT');o=info['object'];o.select_set(True);bpy.context.view_layer.objects.active=o
 collision_objects=[]
 for j,box in enumerate(info['collision']):
  cg=Geo();cg.box(box['center'],box['size'],'white');co=bpy.data.objects.new('UCX_'+name+'_%02d'%j,cg.mesh('UCX'));scene.collection.objects.link(co);co.select_set(True);collision_objects.append(co)
 bpy.ops.export_scene.fbx(filepath=str(OUT/'Unreal'/'Mallas'/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,global_scale=1.0,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_custom_props=False,add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
 for co in collision_objects:bpy.data.objects.remove(co,do_unlink=True)
 manifest['assets'][name]={'file':'Mallas/'+name+'.fbx','triangles':info['tris'],'collision':'complex_static' if name.startswith(('SM_Terreno','SM_Vialidad','SM_Plaza','SM_Parque','SM_Sendero','SM_Terraza')) else 'UCX' if info['collision'] else 'none'}
 if idx%20==0:print('EXPORT',idx,len(assets),flush=True)
library.hide_viewport=True
(OUT/'Unreal'/'distribucion_ciudad.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
stats={'unique_meshes':len(assets),'mesh_instances':len(placements),'triangles_unique':sum(a['tris'] for a in assets.values()),'triangles_instanced':sum(assets[p['asset']]['tris'] for p in placements),'road_edges':len(routes),'delivery_points':len(drops),'max_road_grade_percent':round(max_grade*100,2),'bounds_m':manifest['bounds_m']}
(WORK/'estadisticas.json').write_text(json.dumps(stats,indent=2),encoding='utf8')
print('STATS',json.dumps(stats),flush=True)
# Overview and two inspection views stay in work, not amongst the game resources.
scene.camera=cam;scene.render.filepath=str(WORK/'vista_general.png');bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['Calle_Candelaria'];scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.filepath=str(WORK/'vista_centro.png');bpy.ops.render.render(write_still=True)
scene.camera=cam
print('BOGOTA_COMPLETE',flush=True)
