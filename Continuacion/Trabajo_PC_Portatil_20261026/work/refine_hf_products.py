exec((__import__('pathlib').Path(__file__).parent/'refine_hf_interiors.py').read_text().split("names=['SM_MarketInterior'")[0])
# Stepped silhouettes rather than smooth low-poly cylinders.
def disk(p,r,h,c):
 pitch=.012
 for j in range(-math.ceil(r/pitch),math.ceil(r/pitch)+1):
  y=j*pitch
  if abs(y)>=r:continue
  width=2*math.floor(math.sqrt(r*r-y*y)/pitch)*pitch
  if width>0:box((p[0],p[1]+y,p[2]),(width,pitch,h),c)
names=['SM_Milk','SM_Rice','SM_Apples','SM_Burger','SM_Headphones','SM_Keyboard','SM_PhoneBox','SM_FirstAid','SM_Medicine','SM_Bouquet']
for name in names:
 bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];M=[]
 if name=='SM_Milk':
  box((0,0,.17),(.16,.16,.34),'ivory');box((0,-.083,.16),(.145,.01,.15),'blue')
  for i in range(5):box((0,0,.35+i*.012),(.16-i*.027,.16,.012),'ivory')
  box((0,0,.42),(.025,.17,.025),'blue');box((.04,-.07,.33),(.035,.04,.025),'ivory')
 elif name=='SM_Rice':
  for i in range(12):
   z=.025+i*.025;w=.23*(.8+.2*math.sin(i*math.pi/11));box((0,0,z),(w,.13,.025),'cream')
  box((0,-.071,.17),(.19,.02,.10),'red')
  for i in range(7):box((-.085+i*.028,0,.325),(.012,.14,.035),'ivory')
  for i in range(12):box((random.uniform(-.075,.075),-.086,random.uniform(.13,.21)),(.015,.008,.006),'gold')
 elif name=='SM_Apples':
  box((0,0,.03),(.36,.32,.06),'oak')
  for x in [-.09,.09]:
   for y in [-.08,.08]:
    for k,r in enumerate([.045,.065,.073,.07,.055]):disk((x,y,.06+k*.025),r,.025,'red')
    box((x,y,.20),(.018,.018,.035),'oak');box((x+.03,y,.195),(.06,.03,.015),'leaf')
 elif name=='SM_Burger':
  box((0,0,.02),(.46,.40,.025),'ivory');box((0,0,.039),(.38,.34,.009),'cream')
  for z,r,h,c in [(.05,.12,.025,'honey'),(.075,.15,.035,'gold'),(.11,.155,.02,'leaf'),(.135,.14,.035,'oak'),(.175,.15,.02,'red'),(.205,.15,.035,'honey'),(.24,.135,.025,'gold'),(.265,.105,.02,'gold'),(.285,.07,.015,'gold')]:disk((0,0,z),r,h,c)
  box((0,0,.174),(.27,.27,.012),'gold')
  for i in range(17):
   x=random.uniform(-.08,.08);y=random.uniform(-.08,.08);box((x,y,.30 if x*x+y*y<.005 else .284),(.009,.022,.007),'cream')
 elif name=='SM_Headphones':
  for x in [-.14,.14]:
   box((x,0,.16),(.07,.12,.14),'ink');box((x,-.068,.16),(.075,.02,.11),'blue');box((x,0,.28),(.023,.055,.15),'steel')
  for i in range(-6,7):
   x=i*.022;z=.36+.035*(1-(i/6)**2);box((x,0,z),(.023,.065,.03),'ink')
 elif name=='SM_Keyboard':
  box((0,0,.028),(.49,.19,.055),'ink');box((0,0,.058),(.47,.175,.008),'steel')
  for i in range(12):
   for j in range(3):box((-.216+i*.039,-.058+j*.043,.071),(.031,.034,.02),'ivory' if i<10 else 'blue')
  box((-.02,.067,.071),(.18,.032,.02),'ivory')
  for x in [-.20,-.16,.14,.18,.22]:box((x,.067,.071),(.028,.032,.02),'blue')
 elif name=='SM_PhoneBox':
  box((0,0,.035),(.20,.36,.07),'cream');box((0,0,.078),(.205,.365,.025),'ivory');box((0,0,.105),(.15,.29,.03),'ink');box((0,0,.123),(.13,.26,.006),'blue')
  for x in [-.04,0,.04]:
   for y in [-.05,0,.05]:box((x,y,.129),(.024,.025,.003),['gold','sage','pink'][int((y+.051)*20)%3])
  box((0,.11,.13),(.04,.008,.005),'ink')
 elif name=='SM_FirstAid':
  box((0,0,.16),(.36,.20,.28),'ivory');box((0,0,.018),(.33,.19,.035),'steel')
  for x in [-.17,.17]:box((x,-.10,.16),(.025,.025,.25),'blue')
  for x in [-.08,.08]:box((x,0,.32),(.025,.035,.055),'blue')
  box((0,0,.345),(.18,.035,.025),'blue');box((0,-.109,.16),(.15,.015,.045),'red');box((0,-.109,.20875),(.045,.015,.0525),'red');box((0,-.109,.11125),(.045,.015,.0525),'red')
 elif name=='SM_Medicine':
  box((0,0,.12),(.27,.11,.24),'ivory');box((0,-.061,.09),(.255,.009,.07),'blue');box((0,.058,.12),(.25,.008,.21),'cream');box((0,0,.244),(.275,.115,.012),'ivory')
  for x in [-.08,-.04,0,.04,.08]:box((x,-.067,.19),(.014,.006,.014),'sage')
 elif name=='SM_Bouquet':
  for k in range(9):disk((0,0,.03+k*.027),.045+k*.011,.027,'cream')
  disk((0,0,.14),.1,.022,'pink')
  for i in range(9):
   a=i*2.4;r=.12*math.sqrt(i/9);bloom(math.cos(a)*r,math.sin(a)*r,.10+random.uniform(0,.07),['pink','red','ivory'][i%3])
 # Small authored details that remain legible at the close pickup camera.
 if name=='SM_Milk':
  for x in [-.069,.069]:box((x,-.091,.17),(.009,.012,.30),'blue')
  box((0,-.095,.27),(.10,.01,.018),'cream')
 elif name=='SM_Rice':
  for x in [-.103,.103]:box((x,-.075,.16),(.012,.009,.22),'ivory')
  for i in range(6):box((-.07+i*.027,-.075,.29),(.008,.008,.027),'honey')
 elif name=='SM_Apples':
  for y in [-.17,.17]:
   for z in [.04,.085]:box((0,y,z),(.40,.025,.025),'honey')
  for x in [-.19,.19]:box((x,0,.06),(.025,.35,.10),'oak')
 elif name=='SM_Burger':
  box((.17,.09,.105),(.095,.085,.16),'red')
  for i in range(9):box((.135+(i%3)*.023,.06+(i//3)*.025,.23-(i%2)*.025),(.016,.016,.19),'gold')
  for i in range(8):
   a=i*math.pi/4;box((math.cos(a)*.14,math.sin(a)*.14,.116),(.055,.055,.012),'sage')
 elif name=='SM_Headphones':
  for x in [-.145,.145]:
   box((x,0,.16),(.084,.132,.156),'steel');box((x,-.074,.16),(.075,.025,.145),'ink');box((x,-.09,.16),(.047,.012,.105),'blue')
  for x in [-.06,0,.06]:box((x,0,.376),(.055,.071,.012),'blue')
 elif name=='SM_Keyboard':
  for x in [-.20,.20]:box((x,.055,.004),(.04,.035,.012),'steel')
  for i in range(12):
   for j in range(3):box((-.216+i*.039,-.063+j*.043,.082),(.009,.006,.002),'ink')
 elif name=='SM_PhoneBox':
  box((.04,-.08,.132),(.026,.026,.008),'sage');box((0,-.13,.132),(.03,.01,.005),'ivory')
  for y in [-.06,-.02]:box((-.087,y,.105),(.008,.025,.009),'steel')
 elif name=='SM_FirstAid':
  for x in [-.12,.12]:box((x,-.115,.27),(.033,.015,.035),'steel')
  for x in [-.09,.09]:box((x,.109,.26),(.045,.018,.018),'steel')
 elif name=='SM_Medicine':
  box((.18,0,.012),(.105,.19,.015),'steel')
  for x in [.15,.19]:
   for y in [-.06,0,.06]:box((x,y,.031),(.022,.044,.018),'ivory')
 elif name=='SM_Bouquet':
  for i in range(7):
   a=i*2.4;box((math.cos(a)*.08,math.sin(a)*.08,.16),(.025,.025,.23),'leaf')
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 for key,c in COL.items():
  mat=bpy.data.materials.new('ENV_'+key);mat.diffuse_color=c;mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mesh.materials.append(mat)
 for p,i in zip(mesh.polygons,M):p.material_index=i
 obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
print('TEN_HF_PRODUCTS_EXPORTED')
