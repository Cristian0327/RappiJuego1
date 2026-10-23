exec((__import__('pathlib').Path(__file__).parent/'build_cohesive_shops.py').read_text().split("for kind,label in enumerate")[0])
for kind,label in enumerate(['Market','Restaurant','Tech','Pharmacy','Florist']):
 bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];M=[];library={};accent=['red','gold','blue','sage','sage'][kind]
 # Front at Y=0, room extends towards +Y. Blender import reflection handled by runtime.
 for x in [-3,3]:
  box((x,0,1.65),(4,.12,3.3),'oak')
  for row in range(14):
   for col in range(9):box((x-1.75+col*.43,-.075,.12+row*.23),(.40,.045,.20),'honey' if (row+col)%5 else 'oak')
  box((x,-.12,1.8),(2.8,.10,1.55),'ink');box((x,-.18,1.8),(2.58,.045,1.32),'blue')
  for dx in [-1.35,0,1.35]:box((x+dx,-.22,1.8),(.07,.06,1.55),'steel')
  box((x,-.3,.98),(2.9,.40,.11),'cream')
  for i in range(5):
   if kind==1:product('SM_Burger',(x-1+i*.5,-.3,1.05),.85)
   elif kind==4:product('SM_Bouquet',(x-1+i*.5,-.3,1.05),1)
   else:box((x-1+i*.5,-.31,1.22),(.20,.16,.32),'ivory')
 box((0,0,3.12),(10,.15,.60),accent)
 for x in [-1.02,1.02]:box((x,-.10,1.3),(.08,.15,2.6),'ink')
 for i in range(25):box((-4.8+i*.4,-.55,2.90),(.38,1.05,.10),accent if i%2 else 'cream')
 # Two usable-looking residential upper levels integrated with the ground floor footprint.
 for floor in range(2):
  z=3.6+floor*2.7
  for y in [0,8]:box((0,y,z+1.35),(10,.18,2.7),'oak')
  for x in [-5,5]:box((x,4,z+1.35),(.18,8,2.7),'oak')
  box((0,4,z),(10.2,8.2,.16),'cream')
  for x in [-3.7,-1.25,1.25,3.7]:
   box((x,-.13,z+1.45),(1.65,.11,1.6),'ink');box((x,-.2,z+1.45),(1.48,.035,1.43),'blue')
   box((x,-.235,z+1.45),(.055,.025,1.45),'cream');box((x,-.235,z+1.45),(1.50,.025,.055),'cream');box((x,-.28,z+.62),(1.85,.5,.13),'cream')
   for k in range(7):box((x-.7+k*.23,-.5,z+.85),(.025,.025,.43),'ink')
  for row in range(10):
   for col in range(22):
    x=-4.85+col*.45;zz=z+.12+row*.26
    if not any(abs(x-w)<.90 and z+.60<zz<z+2.3 for w in [-3.7,-1.25,1.25,3.7]):box((x,-.11,zz),(.42,.035,.23),'honey' if (row+col)%6==0 else 'oak')
 box((0,4,9.1),(10.3,8.3,.18),'ink');box((2,5,9.35),(1.6,2,.45),'steel')
 finalize('SM_'+label+'Front',False)
