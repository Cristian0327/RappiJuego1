"""Original Bogotá-style pizza shop, Blender source and FBX; no lettering."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'work/build_commercial_district_blender.py').read_text().split('\nnew_products()')[0]
source=source.replace("['Restaurant','Cafe','Bakery','Florist']","['Restaurant','Cafe','Bakery','Florist','Pizza']")
source=source.replace(" counter(2.7,2.75,2.6,'oak' if food else a)"," counter(2.7,D-8 if L=='Pizza' else 2.75,4.8 if L=='Pizza' else 2.6,'oak' if food else a)")
source=source.replace("  kitchen(W,D,L=='Cafe',L=='Bakery')","  if L!='Pizza':kitchen(W,D,L=='Cafe',L=='Bakery')")
source=source.replace("for y in [7,13,19]:", "for y in ([7,13] if L=='Pizza' else [7,13,19]):")
source=source.replace("'Bread' if L=='Bakery' else 'Burger'", "'Bread' if L=='Bakery' else 'Pizza' if L=='Pizza' else 'Burger'")
source=source.replace(" finish('SM_'+label+'Front')",''' if label=='Pizza':
  for x in [-10,-6,6,10]:
   for z in range(19):box((x,-.24,.15+z*.29),(.48,.42,.27),'bricklight' if z%4 else 'brick')
  for x in range(-11,12):box((x,-.70,4.35),(.18,1.65,.20),'oak')
  # Pixel pizza silhouette over the entrance: food symbol, no lettering.
  for ix in range(-8,9):
   for iz in range(-5,6):
    if (ix/8)**2+(iz/5)**2<1:
     box((ix*.16,-.32,5.0+iz*.13),(.15,.10,.12),'honey' if (ix/8)**2+(iz/5)**2>.68 else 'cream')
  for x,z in [(-.6,4.85),(.3,5.2),(.7,4.95),(-.3,5.35)]:box((x,-.39,z),(.20,.06,.18),'red')
 finish('SM_'+label+'Front')''')
# Keep the existing human-scale restaurant fittings, add a dedicated visible pizza kitchen.
insertion='''
 if L=='Pizza':
  # Staggered glazed tiles and brick returns make the working kitchen legible.
  for ix in range(-39,40):
   for iz in range(10):
    xx=ix*.30+(iz%2)*.15
    box((xx,D-.20,.25+iz*.16),(.288,.035,.148),'cream' if (ix+iz)%11 else 'sage')
  for side in [-1,1]:
   for yy in range(17,28):
    for iz in range(11):
     box((side*(W/2-.21),yy+.25+(iz%2)*.25,.22+iz*.18),(.045,.48,.165),'bricklight' if (yy+iz)%4 else 'brick')
  # Ingredient silhouettes in a framed pixel mural, with no words or logos.
  box((4,D-.25,3.05),(8,.10,2.3),'ink');box((4,D-.32,3.05),(7.75,.06,2.05),'cream')
  for cx,cz,rad in [(1.5,3.0,.62),(4,3.15,.72),(6.5,3.0,.60)]:
   for ix in range(-7,8):
    for iz in range(-7,8):
     if (ix*.10)**2+(iz*.10)**2<rad*rad:box((cx+ix*.10,D-.37,cz+iz*.10),(.096,.04,.096),'red' if cx<3 else 'gold' if cx<5 else 'sage')
   box((cx,D-.39,cz+rad),(.30,.05,.15),'leaf')
  # Small service fixtures and preparation utensils at human scale.
  for x in [1.4,2.0,2.6]:
   box((x,D-5,1.18),(.17,.17,.24),'ivory');box((x,D-5,1.32),(.15,.15,.04),'red')
  box((6,D-5.1,1.14),(.65,.48,.045),'oak')
  for x in [5.7,5.9,6.1]:box((x,D-5.1,1.18),(.075,.38,.035),'steel')
  # Masonry oven with a stepped voxel dome, dark firebox and metal flue.
  for layer in range(13):
   z=1.15+layer*.14;radius=max(.40,1.55-layer*.085)
   for ix in range(-12,13):
    for iy in range(-12,13):
     xx=ix*.14;yy=iy*.14
     if radius-.19<(xx*xx+yy*yy)**.5<radius and not (yy<0 and abs(xx)<.56 and z<2.02):
      box((-5+xx,D-4+yy,z),(.135,.135,.135),'bricklight' if (ix+iy+layer)%5 else 'brick')
  box((-5,D-4,.55),(3.5,3.3,1.1),'brick')
  box((-5,D-5.6,1.14),(3.6,.55,.16),'tile')
  box((-5,D-4,3.7),(.5,.5,2.65),'steel')
  for xx in [-.32,0,.32]:box((-5+xx,D-4.8,1.38),(.22,.5,.32),'warm')
  # Prep counter with ingredient wells, refrigerator doors and pizza peels.
  box((4,D-5,.50),(5,1.35,1),'steel');box((4,D-5,1.05),(5.1,1.45,.12),'ivory')
  for i in range(8):
   box((1.9+i*.58,D-4.63,1.15),(.50,.48,.14),'ink')
   box((1.9+i*.58,D-4.63,1.23),(.42,.39,.03),['red','leaf','cream','honey'][i%4])
  for x in [2.3,3.9,5.5]:
   box((x,D-5.70,.55),(1.4,.035,.78),'graphite');box((x+.5,D-5.74,.7),(.06,.05,.34),'steel')
  for x in [-7.2,-6.8]:
   box((x,D-1.0,1.25),(.07,.07,2.5),'honey');box((x,D-1.0,2.65),(.45,.08,.48),'steel')
  for x in [-9,9]:
   for z in [.6,1.2,1.8]:
    box((x,D-1,z),(2.4,.7,.08),'oak')
    for dx in [-.8,0,.8]:
     for k in range(4):box((x+dx,D-1,z+.10+k*.055),(.66,.60,.05),'cream')
'''
source=source.replace(" finish('SM_'+L+'Interior',shift=-D/2)",insertion+"\n finish('SM_'+L+'Interior',shift=-D/2)")
exec(compile(source,str(ROOT/'work/build_commercial_district_blender.py'),'exec'))
row={'label':'Pizza','width':24,'depth':28,'category':1,'accent':'red'}
exterior(row);interior(row)
(ROOT/'work/pizzeria_blender_manifest.json').write_text(json.dumps(REPORT,indent=2))
