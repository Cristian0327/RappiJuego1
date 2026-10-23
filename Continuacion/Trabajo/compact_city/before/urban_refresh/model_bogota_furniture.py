import bpy,math,json,numpy as np
from pathlib import Path
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');W.mkdir(exist_ok=True);(W/'export').mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
P={'metal':(.065,.09,.085,1),'concrete':(.44,.39,.29,1),'wood':(.31,.12,.045,1),'edge':(.65,.48,.25,1),'black':(.012,.018,.02,1),'white':(.82,.78,.64,1),'red':(.64,.025,.014,1),'yellow':(.95,.55,.035,1),'green':(.06,.65,.22,1),'blue':(.035,.22,.26,1),'glass':(.055,.19,.22,1),'roof':(.52,.09,.045,1),'glow':(1,.72,.32,1)}
mat=bpy.data.materials.new('Bogota_Voxel_Palette');mat.use_nodes=True;vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Color';mat.node_tree.links.new(vc.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.82
assets=[]
def start():return [[],[],[]]
def box(g,p,s,c):
 v,f,co=g;x,y,z=p;a,b,d=[q/2 for q in s];i=len(v);v.extend([(x+xx*a,y+yy*b,z+zz*d) for xx,yy,zz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]);f.extend([tuple(i+j for j in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);co.extend([P.get(c,c)]*6)
def finish(name,g):
 v,f,cols=g
 if name in ['SM_Bogota_EstacionTransmi','SM_Bogota_PuertaEstacion']:v=[(x,-y,z) for x,y,z in v];f=[tuple(reversed(q)) for q in f]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();me.materials.append(mat);a=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');a.data.foreach_set('color',np.repeat(np.array(cols,np.float32),4,axis=0).ravel());me.color_attributes.active_color=a;o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(W/'export'/(name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR');assets.append({'name':name,'polygons':len(f)});o.hide_set(True);return o
g=start()
for x in [-.70,.70]:box(g,(x,0,.20),(.24,.58,.40),'concrete');box(g,(x,.22,.67),(.10,.10,.58),'metal')
for y in [-.23,-.12,-.01,.10,.21]:box(g,(0,y,.44),(2,.08,.10),'wood')
for z in [.61,.75,.89]:box(g,(0,.26,z),(2,.10,.10),'wood')
for x in [-.85,.85]:box(g,(x,0,.65),(.08,.55,.08),'metal')
finish('SM_Bogota_Banca',g)
g=start();box(g,(0,0,.08),(.50,.50,.16),'metal');box(g,(0,0,.44),(.44,.44,.62),'black')
for x in [-.25,.25]:
 for y in [-.18,-.06,.06,.18]:box(g,(x,y,.48),(.06,.075,.72),'metal')
for y in [-.25,.25]:
 for x in [-.18,-.06,.06,.18]:box(g,(x,y,.48),(.075,.06,.72),'metal')
box(g,(0,.0,.95),(.60,.60,.10),'metal');box(g,(0,.0,.78),(.56,.56,.05),'edge');box(g,(0,.26,.53),(.25,.03,.23),'white');finish('SM_Bogota_Caneca',g)
g=start();box(g,(0,0,.35),(.20,.20,.70),'concrete');box(g,(0,0,.65),(.22,.22,.08),'yellow');box(g,(0,0,.76),(.20,.20,.12),'metal');finish('SM_Bogota_Bolardo',g)
g=start();box(g,(0,0,.15),(.45,.45,.30),'concrete');box(g,(0,0,2.6),(.15,.15,5.2),'metal');box(g,(0,-.65,5.05),(.15,1.30,.15),'metal');box(g,(0,-1.15,4.95),(.70,1.20,.16),'metal');finish('SM_Bogota_Farola',g)
g=start();box(g,(0,-1.15,4.85),(.55,1.05,.04),'glow');finish('SM_Bogota_FarolaLuz',g)
g=start();box(g,(0,0,.10),(.40,.40,.20),'concrete');box(g,(0,0,2.1),(.14,.14,4.2),'metal');box(g,(0,-.40,4.05),(.14,.80,.14),'metal');box(g,(0,-.70,3.78),(.35,.50,1.30),'black');box(g,(0,-.70,2.70),(.30,.45,.65),'black')
for z in [4.15,3.80,3.45]:box(g,(-.20,-.70,z),(.08,.42,.30),'black')
finish('SM_Bogota_SemaforoPoste',g)
for name,z,c in [('Rojo',4.15,'red'),('Amarillo',3.80,'yellow'),('Verde',3.45,'green'),('Peaton',2.70,'green'),('PeatonRojo',2.70,'red')]:
 g=start()
 if 'Peaton' in name:
  for yy,zz,sy,sz in [(-.70,2.88,.10,.10),(-.70,2.74,.12,.16),(-.81,2.73,.07,.09),(-.59,2.73,.07,.09),(-.75,2.57,.065,.16),(-.65,2.57,.065,.16)]:box(g,(-.25,yy,zz),(.035,sy,sz),c)
 else:box(g,(-.25,-.70,z),(.035,.28,.22),c)
 finish('SM_Bogota_Semaforo'+name,g)
g=start();hw=15.28
for yy in np.arange(-hw+2.6,hw-2.4,.85):
 for xx in [-2.5,2.5]:box(g,(xx,float(yy),.055),(2.10,.45,.02),'white')
for x,y in [(-7.7,7.35),(7.7,-7.35)]:box(g,(x,y,.055),(.35,14.7,.02),'white')
# Wide curb ramps with eight-percent approach slope.
for sign in [-1,1]:
 y0=sign*(hw-2.4);y1=sign*hw;i=len(g[0]);g[0].extend([(-5,y0,.04),(5,y0,.04),(5,y1,.20),(-5,y1,.20),(-5,y0,0),(5,y0,0),(5,y1,0),(-5,y1,0)]);g[1].extend([tuple(i+j for j in q) for q in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]]);g[2].extend([P['edge']]*6)
finish('SM_Bogota_CruceAccesible',g)
g=start();box(g,(0,0,.43),(28,2.8,.86),'concrete');box(g,(0,0,.88),(28,2.8,.04),'edge');box(g,(0,1.20,.92),(27,.20,.04),'yellow');box(g,(0,-1.20,.92),(27,.15,.04),'yellow')
for x in [-13,-9,-5,-1,3,7,11,13]:box(g,(x,-1.40,2.40),(.15,.15,3),'metal')
for x in [-13,-9,-5,-1,1.5,6,10,13]:box(g,(x,1.40,2.40),(.15,.15,3),'metal')
for y in [-1.4,1.4]:
 for a,b in ([(-14,2.5),(5.1,14)] if y>0 else [(-14,14)]):
  box(g,((a+b)/2,y,1.10),(b-a,.12,.40),'metal');box(g,((a+b)/2,y,2.25),(b-a,.08,1.85),'glass')
  for x in np.arange(a+.4,b,.7):box(g,(float(x),y-.01,2.25),(.04,.11,1.8),'edge')
box(g,(0,0,4.05),(28.8,3.50,.30),'roof');box(g,(0,0,3.85),(28.4,3.30,.10),'white');box(g,(0,1.73,3.68),(28,.10,.50),'roof');box(g,(0,-1.73,3.68),(28,.10,.50),'roof')
for sign in [-1,1]:
 # Stepped voxel ramp, ~8 percent, 10 m long.
 for k in range(20):
  height=.90*(20-k)/20;xx=sign*(14+.25+k*.5);box(g,(xx,0,height/2),(.50,2.8,height),'concrete')
 for y in [-1.35,1.35]:
  for k in range(21):
   xx=sign*(14+k*.5);zz=.9*(20-k)/20;box(g,(xx,y,zz+.55),(.07,.07,1.1),'metal');box(g,(xx,y,zz+1.1),(.50,.08,.08),'metal')
# Pixel lettering is geometry, so signage shares the voxel grid.
letters={'T':['11111','00100','00100','00100','00100','00100','00100'],'R':['11110','10001','10001','11110','10100','10010','10001'],'A':['01110','10001','10001','11111','10001','10001','10001'],'N':['10001','11001','11001','10101','10011','10011','10001'],'S':['01111','10000','10000','01110','00001','00001','11110'],'M':['10001','11011','10101','10101','10001','10001','10001'],'I':['11111','00100','00100','00100','00100','00100','11111'],'L':['10000','10000','10000','10000','10000','10000','11111'],'E':['11111','10000','10000','11110','10000','10000','11111'],'O':['01110','10001','10001','10001','10001','10001','01110']}
text='TRANSMILENIO';pix=.045
for ci,ch in enumerate(text):
 for rr,line in enumerate(letters[ch]):
  for cc,s in enumerate(line):
   if s=='1':
    for sign in [-1,1]:box(g,((ci*6+cc-len(text)*3)*pix,sign*1.795,3.70+(.5-rr/7)*.34),(pix,.025,pix),'white')
finish('SM_Bogota_EstacionTransmi',g)
g=start();box(g,(0,0,2.0),(1.15,.10,2.20),'glass');box(g,(0,0,3.1),(1.20,.16,.10),'metal');box(g,(0,0,.92),(1.20,.16,.10),'metal')
for x in [-.57,.57]:box(g,(x,0,2.0),(.06,.16,2.20),'metal')
box(g,(0,-.065,1.35),(.7,.03,.08),'yellow');finish('SM_Bogota_PuertaEstacion',g)
# Asset source scene is laid out as a catalog; exported geometry retains local pivots.
for i,o in enumerate([bpy.data.objects[v['name']] for v in assets]):o.hide_set(False);o.location=(i%5*8,i//5*12,0)
bpy.ops.wm.save_as_mainfile(filepath=str(W/'Mobiliario_Bogota_Voxel.blend'));(W/'assets.json').write_text(json.dumps(assets,indent=2));print('BOGOTA_BLENDER_ASSETS_READY',len(assets))


