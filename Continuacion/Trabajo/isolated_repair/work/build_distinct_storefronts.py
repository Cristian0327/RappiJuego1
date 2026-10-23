exec((__import__('pathlib').Path(__file__).parent/'build_cohesive_shops.py').read_text().split("for kind,label in enumerate")[0])
for kind,label in enumerate(['Market','Restaurant','Tech','Pharmacy','Florist']):
 bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];M=[];library={}
 base=['cream','oak','ink','ivory','sage'][kind];accent=['red','red','blue','blue','leaf'][kind]
 # Single commercial volume; central opening matches the existing walkable interior.
 for x in [-3,3]:
  box((x,0,1.8),(4,.15,3.6),base)
  box((x,-.11,1.85),(3.5,.07,2.1),'ink')
  box((x,-.16,1.85),(3.25,.035,1.86),'blue')
  for dx in [-1.65,0,1.65]:box((x+dx,-.20,1.85),(.07,.045,2.15),'steel')
  box((x,-.24,.72),(3.65,.34,.10),base)
  if kind==1:
   for row in range(3):
    for col in range(9):box((x-1.8+col*.43,-.1,.12+row*.22),(.4,.03,.2),'honey' if (row+col)%4 else 'oak')
  if kind==2:
   for col in range(14):box((x-1.85+col*.28,-.12,3.15),(.12,.07,.64),'steel')
 for x in [-1.05,1.05]:box((x,-.1,1.35),(.10,.18,2.7),accent)
 box((0,0,3.25),(10,.22,.7),accent)
 box((0,-.5,3.02),(10.3,1.15,.15),accent)
 box((0,-1.05,2.95),(10.3,.09,.16),'gold' if kind==1 else 'ivory')
 for x in [-5,5]:box((x,4,1.8),(.16,8,3.6),base)
 box((0,8,1.8),(10,.16,3.6),base);box((0,4,3.72),(10.4,8.4,.18),'ink')
 if kind==3:
  box((-3,-.22,3.28),(.55,.05,.14),'ivory');box((-3,-.22,3.28),(.14,.05,.55),'ivory')
 if kind==4:
  for x in [-4,-2,2,4]:planter(x,-.5,0)
 if kind==0:
  for x in [-4,-2,2,4]:
   box((x,-.5,.35),(.9,.7,.7),'oak')
   for i in range(5):box((x-.3+i*.15,-.5,.77),(.13,.35,.13),'leaf' if i%2 else 'red')
 finalize('SM_'+label+'Front',False)
