exec((__import__('pathlib').Path(__file__).parent/'refine_hf_interiors.py').read_text().split("names=['SM_MarketInterior'")[0])
OUT=ROOT/'outputs/DeliveryArt/HighFidelity'
def disk(p,r,h,c):
 pitch=.012
 for j in range(-math.ceil(r/pitch),math.ceil(r/pitch)+1):
  y=j*pitch
  if abs(y)>=r:continue
  w=2*math.floor(math.sqrt(r*r-y*y)/pitch)*pitch
  if w>0:box((p[0],p[1]+y,p[2]),(w,pitch,h),c)
names=['GPU','RAM','CircuitBoard','ToolKit','Coffee','Salad','Bread','Carrots','Bananas','Nuggets','Pizza']
for name in names:
 bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];M=[]
 if name=='GPU':
  box((0,0,.055),(.36,.15,.055),'sage');box((0,0,.092),(.38,.17,.04),'ink')
  for x in [-.105,.105]:
   for z,r,h,c in [(.119,.065,.013,'steel'),(.128,.056,.01,'ink'),(.134,.015,.008,'blue')]:disk((x,0,z),r,h,c)
   for i in range(8):
    a=i*math.pi/4;box((x+math.cos(a)*.037,math.sin(a)*.037,.138),(.028,.016,.009),'steel')
  for i in range(22):box((-.154+i*.014,-.088,.055),(.009,.035,.025),'gold')
  for i in range(12):box((-.16+i*.029,.083,.065),(.012,.025,.08),'steel')
  for x in [-.195,.195]:box((x,0,.072),(.015,.19,.09),'steel')
 elif name=='RAM':
  box((0,0,.04),(.28,.06,.022),'sage')
  for x in [-.10,-.05,0,.05,.10]:box((x,0,.061),(.039,.035,.02),'ink')
  for i in range(23):box((-.126+i*.011,-.041,.037),(.007,.019,.014),'gold')
  for x in [-.143,.143]:box((x,0,.046),(.018,.070,.033),'steel')
 elif name=='CircuitBoard':
  box((0,0,.03),(.24,.19,.025),'sage');box((-.015,0,.053),(.068,.068,.025),'ink')
  for x in [-.1,.1]:
   for i in range(12):box((x,-.077+i*.014,.061),(.023,.009,.036),'ink');box((x,-.077+i*.014,.085),(.005,.005,.012),'gold')
  for i in range(9):box((-.056+i*.014,-.040,.055),(.005,.013,.012),'steel')
  for i in range(7):box((-.056+i*.018,.057,.06),(.012,.025,.02),'cream')
  box((-.062,.096,.049),(.06,.025,.048),'steel');box((.055,.089,.051),(.063,.045,.038),'steel')
  for x in [-.07,0,.07]:box((x,-.081,.047),(.048,.009,.004),'gold')
 elif name=='ToolKit':
  box((0,0,.035),(.34,.24,.04),'ink');box((0,.09,.075),(.34,.06,.04),'blue')
  for x in [-.13,-.065,0,.065,.13]:
   box((x,-.015,.069),(.033,.15,.035),'red' if x<0 else 'blue');box((x,.075,.063),(.013,.065,.022),'steel')
  for x in [-.155,.155]:box((x,-.07,.087),(.012,.28,.03),'steel')
 elif name=='Coffee':
  for i in range(12):disk((0,0,.022+i*.018),.052+i*.002,.018,'cream')
  disk((0,0,.14),.068,.03,'oak');disk((0,0,.253),.082,.015,'ink');disk((0,0,.264),.055,.008,'steel')
  box((.037,0,.272),(.027,.012,.008),'ink')
 elif name=='Salad':
  for i in range(7):disk((0,0,.014+i*.018),.09+i*.012,.018,'cream')
  for i in range(15):
   a=i*2.4;r=.105*math.sqrt(i/15);x=math.cos(a)*r;y=math.sin(a)*r
   box((x,y,.158+(i%3)*.012),(.063,.048,.018),'leaf' if i%3 else 'sage')
   if i%3==0:disk((x,y,.190),.025,.012,'red')
  for i in range(5):box((-.07+i*.034,.02,.203),(.025,.024,.018),'ivory')
 elif name=='Bread':
  box((0,0,.018),(.35,.22,.025),'cream')
  for i in range(7):box((0,0,.052+i*.023),(.31-i*.019,.18-i*.014,.023),'honey' if i<3 else 'gold')
  for x in [-.08,0,.08]:box((x,0,.213),(.015,.096,.008),'cream')
 elif name=='Carrots':
  for x in [-.07,0,.07]:
   for i in range(7):box((x,0,.020+i*.025),(.035+i*.004,.035+i*.004,.025),'gold')
   for j in range(3):box((x+(j-1)*.016,0,.25),(.013,.012,.14),'leaf')
 elif name=='Bananas':
  for j in range(4):
   for i in range(9):box((-.10+i*.025,j*.022-.04,.04+.06*math.sin(i*math.pi/8)),(.026,.022,.025),'gold')
   box((-.117,j*.022-.04,.039),(.018,.022,.018),'oak')
 elif name=='Nuggets':
  box((0,0,.018),(.32,.24,.03),'cream')
  for i in range(8):
   x=-.102+(i%4)*.067;y=-.054+(i//4)*.103
   for z,w,h in [(.051,.050,.03),(.075,.043,.018)]:box((x,y,z),(w,.067,h),'honey' if i%2 else 'gold')
  box((.115,.090,.040),(.06,.04,.025),'red')
 elif name=='Pizza':
  box((0,0,.013),(.44,.44,.02),'cream');disk((0,0,.035),.19,.022,'honey');disk((0,0,.05),.165,.015,'red');disk((0,0,.061),.159,.012,'gold')
  for i in range(11):
   a=i*2.4;r=.126*math.sqrt(i/11);disk((math.cos(a)*r,math.sin(a)*r,.073),.021,.008,'red')
  for i in range(8):box((math.cos(i*2.2)*.12,math.sin(i*2.2)*.12,.079),(.018,.025,.008),'leaf')
 mesh=bpy.data.meshes.new('SM_'+name);mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new('SM_'+name,mesh);bpy.context.collection.objects.link(obj)
 for key,c in COL.items():
  mat=bpy.data.materials.new('ENV_'+key);mat.diffuse_color=c;mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mesh.materials.append(mat)
 for face,index in zip(mesh.polygons,M):face.material_index=index
 obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('SM_'+name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(OUT/('SM_'+name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 print('DELIVERY_GOOD_DONE',name,flush=True)
