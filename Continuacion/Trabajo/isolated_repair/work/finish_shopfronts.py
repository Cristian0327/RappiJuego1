exec((__import__('pathlib').Path(__file__).parent/'build_cohesive_shops.py').read_text().split("for kind,label in enumerate")[0])
for kind,label in enumerate(['Market','Restaurant','Tech','Pharmacy','Florist']):
 bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];M=[];library={};accent=['red','gold','blue','sage','sage'][kind]
 box((1.4,0,-.04),(3.0,5.3,.08),'steel')
 for y in [-2.55,2.55]:box((2.1,y,1.7),(2.2,.15,3.4),'oak');box((2.1,y,3.44),(2.4,.23,.15),'ink')
 box((2.15,0,3.5),(2.5,5.3,.10),'ink')
 for side in [-1,1]:
  box((1.1,side*1.8,.4),(.25,1.25,.8),accent)
  for y in [side*1.13,side*2.46]:
   box((1.08,y,1.65),(.32,.20,3.3),'ink')
   for row in range(14):box((.885,y,.12+row*.23),(.05,.18,.21),accent)
  # Recessed shop window leaves the central doorway fully open.
  box((1.5,side*1.80,1.70),(.05,1.15,1.70),'blue' if kind!=4 else 'sage')
  for z in [.83,1.58,2.48]:box((1.18,side*1.80,z),(.12,1.18,.065),'steel')
  for y in [side*1.35,side*2.20]:
   for z in [.91,1.67]:
    if kind==1:product('SM_Burger',(1.12,y,z),.65)
    elif kind==4:product('SM_Bouquet',(1.12,y,z),1)
    else:box((1.11,y,z+.15),(.16,.22,.3),'ivory');box((1.02,y,z+.15),(.025,.19,.10),accent)
  box((1.025,side*1.79,1.70),(.06,.045,1.6),'ink')
  planter(.10,side*2.4,0)
  for i in range(16):
   a=i*2.4;r=.17*math.sqrt(i/16);box((.1+math.cos(a)*r,side*2.4+math.sin(a)*r,.55+(i%4)*.07),(.09,.09,.12),'leaf' if i%2 else 'sage')
  box((.74,side*1.14,2.22),(.18,.25,.38),'ink');box((.635,side*1.14,2.22),(.045,.16,.24),'ivory')
 box((1.06,0,2.74),(.28,5.0,.30),accent);box((1.06,0,3.17),(.28,5.0,.42),accent);box((.90,0,2.96),(.07,5.0,.10),'ivory')
 for i in range(16):
  y=-2.4+i*.32
  for step in range(4):box((.85-step*.27,y,2.84-step*.065),(.29,.31,.09),accent if kind!=1 or i%2 else 'cream')
 box((-.09,0,2.59),(.07,5.15,.16),accent)
 # Central portal has no door-sized display or obstruction.
 for side in [-1,1]:box((1.12,side*.90,1.3),(.06,.055,2.6),'steel')
 box((1.12,0,2.61),(.06,1.85,.065),'steel')
 finalize('SM_'+label+'Front',False)
