"""Model from the approved project-style turnaround sheets, then rigid-skin for Unreal."""
import bpy,math,json,sys,time,hashlib,struct
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from voxel_greedy import emit
from fleet20_catalog import FLEET20,EXTRA_COLORS
OUT=ROOT/'outputs/DeliveryArt/TrafficDetailed';OUT.mkdir(parents=True,exist_ok=True)
COL={'PaintYellow':(1,.61,.014,1),'PaintRed':(.66,.022,.028,1),'PaintBlue':(.018,.15,.55,1),'PaintWhite':(.77,.80,.81,1),'PaintGray':(.32,.35,.39,1),'Black':(.009,.014,.021,1),'Rubber':(.022,.029,.036,1),'Tread':(.035,.044,.052,1),'Glass':(.045,.085,.12,1),'GlassLight':(.095,.15,.19,1),'GlassDark':(.019,.03,.044,1),'Seal':(.031,.036,.04,1),'Chrome':(.52,.61,.66,1),'Rim':(.24,.31,.36,1),'Steel':(.11,.15,.18,1),'Roof':(.48,.51,.54,1),'Lamp':(.92,.95,1,1),'Amber':(1,.39,.012,1),'Tail':(.66,.01,.022,1),'TailLight':(.94,.02,.015,1),'Plate':(.95,.62,.014,1),'Seam':(.29,.20,.014,1),'Seat':(.075,.11,.16,1)}
COL.update(EXTRA_COLORS)
for base in [k for k in COL if k.startswith('Paint')]+['Roof','Rubber']:
 for i,f in enumerate([.94,.98,1.02,1.055]):COL[base+str(i)]=tuple(min(1,c*f) for c in COL[base][:3])+(1,)
(OUT/'materials.json').write_text(json.dumps(COL,indent=2))
manifest=json.loads((OUT/'manifest.json').read_text()) if (OUT/'manifest.json').exists() else []
def interp(x,points):
 for i in range(len(points)-1):
  a,va=points[i];b,vb=points[i+1]
  if x<=b:return va+(vb-va)*max(0,min(1,(x-a)/(b-a)))
 return points[-1][1]

specs={s['name']:s for s in FLEET20}
items=[(s['name'],s['length'],s['width'],s['paint'],False) for s in FLEET20]+[('TaxiCompact',3.7,1.70,'PaintYellow',False),('TaxiSedan',4.28,1.73,'PaintYellow',False),('TransMilenio',18.0,2.48,'PaintRed',True)]
for name,L,W,paint,bus in items:
 if name=='PrivateBeetle':continue # Its accurate classic shape is built by build_beetle_reference.py.
 if '--only' in sys.argv and name!=sys.argv[sys.argv.index('--only')+1]:continue
 if '--cars-only' in sys.argv and bus:continue
 if '--new-only' in sys.argv and name in ['Private','PrivateHatch','PrivateSUV','PrivatePickup','TaxiCompact','TaxiSedan','TransMilenio']:continue
 manifest=[item for item in manifest if item['name']!=name]
 started=time.time();bpy.ops.wm.read_factory_settings(use_empty=True)
 q=.04 if not bus else .06;vox={};panes=[];bones={'root':((0,0,0),(0,0,.3),None)}
 S=specs.get(name,{});extras=S.get('extras',[]);kind=S.get('kind','');beetle=kind=='beetle';van=kind=='van'
 compact=name in ['TaxiCompact','PrivateHatch'] or kind=='compact';suv=name=='PrivateSUV' or kind=='suv';pickup=name=='PrivatePickup' or kind=='pickup'
 def put(ix,iy,iz,mat,b='root'):vox[(ix,iy,iz)]=(mat,b)
 def box(p,s,mat,b='root'):
  ranges=[range(math.floor((p[i]-s[i]/2)/q),math.ceil((p[i]+s[i]/2)/q)) for i in range(3)]
  for ix in ranges[0]:
   for iy in ranges[1]:
    for iz in ranges[2]:put(ix,iy,iz,mat,b)
 def line(a,b,t,mat,bone='root'):
  a=Vector(a);b=Vector(b);n=max(1,int((b-a).length/q*1.6))
  for i in range(n+1):box(a.lerp(b,i/n),(t,t,t),mat,bone)
 def shade(base,ix,iy,iz):
  return base
 radius=.37 if suv else .38 if pickup else .32 if not bus else .49
 axles=[1.13,-1.10] if compact else [1.39,-1.39] if suv else [1.62,-1.55] if pickup else [1.36,-1.31] if not bus else [3.37,-3.13] if name=='SITP' else [6.7,-.4,-6.8]
 if S.get('profile'):radius=S['radius'];axles=S['axles']
 if name=='TransMilenio':bones['articulation']=((-1.82,0,1.4),(-1.82,0,2),'root')
 if not bus:
  if compact:profile=[(-L/2,.89),(-1.60,1.02),(-1.27,1.42),(-1.04,1.50),(.02,1.52),(.36,1.43),(.85,1.00),(1.42,.96),(L/2,.84)];glassrear=(-1.59,-1.19);glassfront=(.36,.85)
  elif suv:profile=[(-L/2,1.04),(-1.95,1.14),(-1.68,1.64),(-1.40,1.70),(.17,1.72),(.43,1.64),(.99,1.19),(1.80,1.12),(L/2,.96)];glassrear=(-1.93,-1.68);glassfront=(.43,.99)
  elif pickup:profile=[(-L/2,1.23),(-1.22,1.23),(-1.02,1.31),(-.92,1.77),(-.70,1.82),(.34,1.82),(.73,1.71),(1.25,1.20),(2.1,1.12),(L/2,1.02)];glassrear=(-1.03,-.93);glassfront=(.73,1.25)
  else:profile=[(-L/2,.87),(-1.54,.98),(-1.17,1.04),(-.83,1.43),(-.51,1.49),(.17,1.50),(.43,1.42),(.94,1.01),(1.70,.94),(L/2,.80)];glassrear=(-1.15,-.76);glassfront=(.41,.95)
  if S.get('profile'):profile=S['profile'];glassfront=S['glassfront'];glassrear=S['glassrear']
  roofround=.16 if beetle else .025 if kind.startswith('retro') or van else .055
  bedend=-.25 if 'singlecab' in extras else -1.10
  def side_y(z):
   return W/2-.075-max(0,z-.83)*.22+.02 if beetle else W/2-max(0,z-1.76)*.15+.02 if van else W/2-max(0,z-1.02)*.26+.02
  for ix in range(math.floor(-L/2/q),math.ceil(L/2/q)):
   x=(ix+.5)*q;zroof=interp(x,profile);bodytop=interp(x,[(-L/2,.89),(-L/2+.27,1.01),(L/2-.28,.98),(L/2,.83)])
   for iz in range(math.ceil((.34 if suv or pickup else .23)/q),math.ceil(zroof/q)):
    z=(iz+.5)*q
    endtaper=max(0,abs(x)-(L/2-.34))*.29
    half=W/2-endtaper-(max(0,z-1.02)*.26 if z>1.02 else max(0,.55-z)*.15)
    if beetle:half=W/2-.075-endtaper*.5-max(0,z-.83)*.22
    if van:half=W/2-endtaper*.35-max(0,z-1.76)*.15
    for iy in range(math.floor(-half/q),math.ceil(half/q)):
     y=(iy+.5)*q
     if abs(y)>half:continue
     if z>zroof-roofround*(abs(y)/half)**3:continue
     # Real open wheel wells cut into the body silhouette.
     if any((x-a)**2+(z-radius)**2<(radius+.075)**2 for a in axles) and z<radius*2+.10:continue
     if pickup and x<bedend and z>.77 and abs(y)<half-.10:continue
     mat=shade(paint,ix,iy,iz)
     side=abs(y)>half-q*1.5;top=z>zroof-roofround*(abs(y)/half)**3-q*1.5
     if z<.31:mat='Black'
     glassfloor=S.get('window_low',1.22 if suv or pickup else 1.045)-.055
     if z>glassfloor:
      if side and z<zroof-.10:
       mat='Seal'
       if z>glassfloor+.07 and z<zroof-.155 and abs(x+.35)>.045 and abs(x-.64)>.03:mat='GlassLight' if z>glassfloor+.23 and (ix//12)%5==0 else 'Glass'
      if top and ((glassfront[0]<x<glassfront[1])or(glassrear[0]<x<glassrear[1])):
       if abs(y)<half-.13 and z>zroof-(.23 if beetle else .10):continue
       mat='Seal'
     if side and .38<z<1.015:
      seams=[-.57,glassfront[1]-.05] if S.get('doors')==2 else [-.35,glassfront[1]-.05,glassrear[0]+.12]
      if any(abs(x-seam)<q*.50 for seam in seams):mat='Seam' if paint=='PaintYellow' else 'Steel'
      if .42<z<.46:mat=paint+'0'
     if side and (suv or pickup) and any(radius+.075<math.hypot(x-a,z-radius)<radius+.15 for a in axles) and z<radius*2+.16:mat='Rubber'
     if van and side and z>1.18 and x<.45:mat=shade(paint,ix,iy,iz)
     put(ix,iy,iz,mat)
  # Recessed front face, stepped lamps and separate grille slats.
  fx=L/2+.01
  if not beetle:
   box((fx,0,.55),(.035,.91,.26),'Black')
   for z in [.44,.51,.58,.65]:box((fx+.022,0,z),(.025,.86,.025),'Steel')
   box((fx-.015,0,.77),(.07,.80,.10),'Black')
   for z in [.745,.79]:box((fx+.025,0,z),(.025,.76,.014),'Chrome')
  box((fx+.053,0,.57),(.03,.42,.16),'Plate')
  for side in [-1,1]:
   for j in range(0 if 'roundlights' in extras or 'rectlights' in extras else 4):
    y=side*(.45+j*.07);z=interp(L/2-.12-j*.02,profile)-.08
    box((fx-.025-j*.02,y,z),(.15,.09,.10),'Seal');box((fx+.06-j*.02,y,z+.006),(.045,.07,.070),'Amber' if j==3 else 'Lamp')
   box((fx+.025,side*.65,.46),(.08,.18,.17),'Black');box((fx+.075,side*.65,.46),(.035,.085,.075),'Lamp')
   # Handles, mirrors, fuel flap and narrow door trim.
   lift=.20 if suv or pickup else 0
   for x in ([.33] if S.get('doors')==2 else [.33,-.84]):box((x,side*(W/2+.015),1.005+lift),(.14,.035,.045),'Chrome' if 'chrome' in extras else 'Seal')
   line((.68,side*.76,1.15+lift),(.59,side*(W/2+.17),1.17+lift),.035,'Black')
   box((.61,side*(W/2+.18),1.205+lift),(.18,.15,.10),paint);box((.51,side*(W/2+.18),1.205+lift),(.035,.10,.065),'GlassLight')
   if S.get('profile'):
    bz=(S['window_low']+S['window_high'])/2;box((-.57 if S.get('doors')==2 else -.35,side*side_y(bz),bz),(.04,.035,S['window_high']-S['window_low']+.04),paint)
   else:box((-.35,side*(W/2-.065),1.50 if suv or pickup else 1.31),(.045,.035,.30),paint)
   za=interp(glassfront[0],profile)-roofround*.5;zb=interp(glassfront[1],profile)-roofround*.5
   line((glassfront[0],side*side_y(za),za),(glassfront[1],side*side_y(zb),zb),.035,paint)
   za=interp(glassrear[1],profile)-roofround*.5;zb=interp(glassrear[0],profile)-roofround*.5
   line((glassrear[1],side*side_y(za),za),(glassrear[0],side*side_y(zb),zb),.035,paint)
   tailz=interp(-L/2,profile)-.17
   box((-L/2-.012,side*.65,tailz),(.045,.22,.24),'Tail')
   box((-L/2-.04,side*.65,tailz),(.028,.17,.035),'Lamp')
   if compact:box((-1.50,side*.79,1.03),(.08,.09,.19),'Tail')
   for z in [tailz-.08,tailz+.01,tailz+.09]:box((-L/2-.04,side*.63,z),(.035,.17,.03),'TailLight')
  box((-L/2-.04,0,.69),(.035,.47,.19),'Seal');box((-L/2-.07,0,.70),(.025,.40,.14),'Plate')
  box((-L/2+.05,0,.41),(.12,1.15,.11),'Black')
  # No windshield wipers.
  antennaz=interp(-.65,profile)+.025;line((-.65,.20,antennaz),(-.73,.20,antennaz+.17),.016,'Black')
  for xa,xb in [glassfront,glassrear]:
   za=interp(xa,profile)+.025;zb=interp(xb,profile)+.025
   ya=W/2-.12-max(0,za-1.02)*.26;yb=W/2-.12-max(0,zb-1.02)*.26
   if beetle:
    za=interp(xa,profile)-.095;zb=interp(xb,profile)-.075;ya=.50;yb=.56
   panes.append(([(xa,-ya,za),(xb,-yb,zb),(xb,yb,zb),(xa,ya,za)],'GlassDark','root'))
  # Clear planar glazing bounded by small voxel seals, like the shop windows.
  low=S.get('window_low',1.27 if suv or pickup else 1.11);high=S.get('window_high',1.64 if suv else 1.73 if pickup else 1.405)
  split=.48 if van else -.1 if 'singlecab' in extras else -.57 if S.get('doors')==2 else -.35
  frontcoords=[(split+.06,low),(glassfront[1]-.10,low),(glassfront[0]-.05,high),(split+.06,high)]
  rearcoords=[(glassrear[0]+.16,low),(split-.06,low),(split-.06,high),(glassrear[1]+.16,high)]
  for side in [-1,1]:
   for coords in ([frontcoords] if van or 'singlecab' in extras else [frontcoords,rearcoords]):
    points=[(x,side*side_y(z),z) for x,z in coords]
    if side>0:points.reverse()
    panes.append((points,'GlassDark','root'))
  for side in [-1,1]:
   xx=glassfront[1]-.15;zz=interp(xx,profile)+.055
   pass # No wipers.
  if suv:
   for side in [-1,1]:
    railz=interp(-.4,profile)+.07
    line((-L*.29,side*.65,railz),(L*.06,side*.65,railz),.055,'Black');box((-.2,side*.65,railz-.025),(L*.30,.035,.035),'Chrome')
    box((0,side*(W/2+.015),.47),(2.20,.055,.13),'Rubber')
   box((L/2+.06,0,.48),(.075,1.02,.12),'Chrome');box((-L/2-.035,0,.52),(.065,1.07,.12),'Chrome')
  if pickup:
   for side in [-1,1]:
    bedcx=(-L/2+bedend)/2;bedlength=bedend+L/2
    box((bedcx,side*(W/2-.07),interp(bedcx,profile)+.02),(bedlength,.12,.05),'Black');box((.25 if 'singlecab' in extras else -.15,side*(W/2+.06),.42),(1.40 if 'singlecab' in extras else 2.24,.15,.07),'Chrome')
   for y in [-.56,-.28,0,.28,.56]:box((bedcx,y,.79),(bedlength-.16,.026,.025),'Steel')
   box((-L/2-.027,0,1.06),(.045,.20,.07),'Black')
  # Gas cap rendered as a recessed square, no emblem.
  for z in [.90,1.0]:box((-1.31,W/2+.015,z),(.13,.025,.025),'Seam' if paint=='PaintYellow' else 'Steel')
  if beetle:
   # Separate bulbous fenders make the air-cooled silhouette unmistakable.
   for axle in axles:
    for ix in range(math.floor((axle-.66)/q),math.ceil((axle+.66)/q)):
     x=(ix+.5)*q
     for iz in range(math.floor(radius/q),math.ceil((radius+.49)/q)):
      z=(iz+.5)*q
      if ((x-axle)/.66)**2+((z-radius)/.49)**2>1:continue
      if (x-axle)**2+(z-radius)**2<(radius+.075)**2:continue
      for side in [-1,1]:
       for iy in range(math.floor((W/2-.26)/q),math.ceil((W/2+.035)/q)):
        put(ix,iy if side>0 else -iy-1,iz,shade(paint,ix,iy,iz))
   box((L/2+.035,0,.41),(.08,1.59,.055),'Chrome')
   for side in [-1,1]:box((L/2+.075,side*.50,.47),(.06,.055,.24),'Chrome')
   for j in range(7):
    vx=-L*.40+j*.030;box((vx,0,interp(vx,profile)+.018),(.016,.54,.018),'Black')
  if 'roundlights' in extras:
   lampx=L/2-.12 if beetle else L/2+.05;lampz=.84 if beetle else interp(L/2,profile)-.15;lr=.145 if beetle else .115
   for side in [-1,1]:
    cy=side*(.62 if beetle else .47)
    if beetle:
     for ix in range(math.floor((lampx-.25)/q),math.ceil(lampx/q)):
      hx=(ix+.5)*q
      for iy in range(math.floor((cy-.18)/q),math.ceil((cy+.18)/q)):
       hy=(iy+.5)*q
       for iz in range(math.floor((lampz-.18)/q),math.ceil((lampz+.18)/q)):
        hz=(iz+.5)*q
        if ((hx-(lampx-.10))/.18)**2+((hy-cy)/.18)**2+((hz-lampz)/.18)**2<1:put(ix,iy,iz,paint)
    for iy in range(math.floor((cy-lr-.035)/q),math.ceil((cy+lr+.035)/q)):
     y=(iy+.5)*q
     for iz in range(math.floor((lampz-lr-.035)/q),math.ceil((lampz+lr+.035)/q)):
      z=(iz+.5)*q;rr=math.hypot(y-cy,z-lampz)
      if rr>lr+.025:continue
      box((lampx,y,z),(.055,q,q),'Chrome' if rr>lr else 'Lamp')
  if 'rectlights' in extras:
   lampz=interp(L/2,profile)-.12
   for side in [-1,1]:
    box((L/2+.05,side*.52,lampz),(.07,.37,.18),'Seal');box((L/2+.09,side*.52,lampz),(.035,.29,.115),'Lamp');box((L/2+.09,side*.72,lampz),(.035,.075,.115),'Amber')
  if 'chrome' in extras:
   for x in [-L/2-.06,L/2+.09]:box((x,0,.40),(.055,W-.08,.07),'Chrome')
   for side in [-1,1]:box((-.15,side*(W/2+.015),.91),(L*.58,.023,.022),'Chrome')
  if 'rubbertrim' in extras:
   for side in [-1,1]:box((-.05,side*(W/2+.02),.69),(L*.73,.045,.055),'Black')
  if 'roofrails' in extras and not suv:
   rz=max(z for _,z in profile)+.055
   for side in [-1,1]:line((-L*.28,side*.61,rz),(L*.04,side*.61,rz),.045,'Black')
  if 'spare' in extras:
   cx=-L/2-.16;cz=1.10
   for iy in range(math.floor(-radius/q),math.ceil(radius/q)):
    y=(iy+.5)*q
    for iz in range(math.floor((cz-radius)/q),math.ceil((cz+radius)/q)):
     z=(iz+.5)*q;rr=math.hypot(y,z-cz)
     if rr>radius:continue
     mat='Rubber' if rr>radius*.68 else 'Chrome' if rr>radius*.52 else 'Steel'
     box((cx,y,z),(.22,q,q),mat)
  if van:
   for side in [-1,1]:
    points=[(-.85,side*(W/2+.022),1.19),(.15,side*(W/2+.022),1.19),(.15,side*(W/2+.022),1.73),(-.85,side*(W/2+.022),1.73)]
    if side>0:points.reverse()
    panes.append((points,'GlassDark','root'))
    for x in [-1.2,.25]:box((x,side*(W/2+.03),1.10),(.022,.023,1.48),'Steel')
    box((-.1,side*(W/2+.035),.94),(.15,.035,.045),'Black')
  if 'cargoglass' in extras:
   for side in [-1,1]:
    x=-1.20;box((x,side*side_y(1.30),1.30),(.045,.035,.39),paint)
 else:
  sections=[(-L/2,L/2,'root')] if name=='SITP' else [(-1.45,9.0,'root'),(-9.0,-2.20,'articulation')]
  for x0,x1,b in sections:
   roofmat='PaintBlue' if name=='SITP' else 'Roof'
   doors=[x1-.78,(x0+x1)/2-1.0] if name=='SITP' else ([x1-.78,3.8,-.55] if b=='root' else [-3.1])
   for ix in range(math.floor(x0/q),math.ceil(x1/q)):
    x=(ix+.5)*q
    for iz in range(math.ceil(.32/q),math.ceil(3.2/q)):
     z=(iz+.5)*q
     end=max(0,.22-min(x-x0,x1-x))
     half=W/2-end*.7-max(0,z-2.92)*.55
     maxz=3.20-.09*(abs(x-(x0+x1)/2)/((x1-x0)/2))**8
     for iy in range(math.floor(-half/q),math.ceil(half/q)):
      y=(iy+.5)*q
      if abs(y)>half or z>maxz-.06*(abs(y)/half)**6:continue
      if any((x-a)**2+(z-radius)**2<.555**2 for a in axles) and z<1.07:continue
      shell=abs(y)>half-q*1.5 or x<x0+q*1.5 or x>x1-q*1.5 or z<.42 or z>maxz-.12
      if not shell:continue
      mat=shade(paint,ix,iy,iz);side=abs(y)>half-q*1.6
      if z<.43:mat='Black'
      if z>3.03:mat=shade(roofmat,ix,iy,iz)
      if side:
       if 1.38<z<2.99:
        mat='Seal';pillar=(x-x0-.12)%1.05
        if .09<pillar<.98 and 1.51<z<2.85 and abs(z-2.54)>.04:mat='GlassLight' if z>2.58 and int(x/q)%17<3 else 'Glass'
       if 1.21<z<1.30:mat='PaintYellow'
       if .90<z<.94:mat=paint+'0'
       if .5<z<1.18 and abs((x-x0)%1.05-.52)<.022:mat='Steel'
       if y<0:
        for dx in doors:
         if abs(x-dx)<.48 and .38<z<2.9:
          mat='Seal'
          if abs(x-dx)>.045 and abs(x-dx)<.395 and .72<z<2.76:mat='GlassDark' if z<1.22 else 'Glass'
          if .42<z<.48:mat='PaintYellow'
      if x>x1-q*1.5:
       if 1.28<z<2.83:mat='Glass' if abs(y)<1.03 and 1.4<z<2.71 else 'Seal'
       if 2.84<z<3.0 and abs(y)<.97:mat='Black'
      if x<x0+q*1.5 and 2.1<z<2.8:mat='GlassDark' if abs(y)<1.0 else 'Seal'
      put(ix,iy,iz,mat,b)
   # Passenger-window mullions, pane highlights and recessed roof equipment.
   for side in [-1,1]:
    for x in [x0+.48+i*1.05 for i in range(int((x1-x0-.8)/1.05))]:
     box((x,side*(W/2+.01),2.91),(.85,.025,.026),'Seal',b)
     box((x+.23,side*(W/2+.02),2.65),(.09,.02,.22),'GlassLight',b)
    for k in range(9):box((x0+.62,side*(W/2+.025),.63+k*.06),(.64,.04,.028),'Black',b)
    for x in [x0+.32,x1-.28]:box((x,side*(W/2+.02),1.1),(.10,.035,.08),'Amber',b)
   cx=(x0+x1)/2
   box((cx,0,3.29),(1.65,1.66,.23),roofmat,b)
   for side in [-1,1]:
    for k in range(7):box((cx-.65+k*.20,side*.85,3.28),(.10,.055,.15),'Black',b)
   for k in range(5):box((cx,0,3.40-k*.016),(1.52-k*.07,1.55-k*.07,.025),roofmat,b)
   for x in [cx-2,cx+2]:box((x,0,3.20),(.62,.9,.065),roofmat,b)
   # Interior seats and rails show through gaps and give the bus a believable structure.
   for x in [x0+.6+i*.68 for i in range(int((x1-x0-1)/.68))]:
    for side in [-1,1]:box((x,side*.86,1.30),(.43,.43,.12),'Seat',b);box((x-.19,side*.87,1.58),(.10,.43,.50),'Seat',b)
   for x in [x0+1,x1-1]:line((x,-.63,1.1),(x,-.63,2.9),.035,'PaintYellow',b)
  front=L/2
  box((front+.035,0,.77),(.045,1.42,.39),'Black')
  for z in [.60,.70,.80,.90]:box((front+.07,0,z),(.03,1.36,.023),'Steel')
  box((front+.10,0,.56),(.03,.47,.19),'Plate')
  box((front+.07,0,1.12),(.045,1.28,.055),'Steel')
  for side in [-1,1]:
   for k in range(4):box((front+.035-k*.015,side*(.82+k*.07),1.02+k*.025),(.055,.075,.115),'Amber' if k==3 else 'Lamp')
   box((front+.06,side*.96,.53),(.04,.15,.13),'Black');box((front+.09,side*.96,.53),(.03,.075,.07),'Lamp')
   line((front-.1,side*1.17,2.63),(front+.22,side*1.51,2.67),.065,'Black')
   box((front+.20,side*1.54,2.40),(.18,.13,.48),'Black');box((front+.11,side*1.54,2.41),(.03,.09,.36),'GlassLight')
   for z,mat in [(1.49,'Tail'),(1.36,'Amber'),(1.23,'Lamp'),(1.10,'TailLight')]:box((-L/2-.035,side*1.07,z),(.04,.19,.095),mat,'articulation' if name=='TransMilenio' else 'root')
  # No bus windshield wipers.
  rearbone='articulation' if name=='TransMilenio' else 'root'
  box((-L/2-.05,0,.57),(.035,.48,.19),'Plate',rearbone)
  for z in [.86,1.0,1.14,1.28]:box((-L/2-.05,0,z),(.035,1.62,.045),'Black',rearbone)
  if name=='TransMilenio':
   for k in range(16):
    x=-2.19+k*.048;wide=2.38 if k%2 else 2.24
    box((x,0,2.99),(.03,wide,.12),'Rubber' if k%2 else 'Tread','articulation')
    for side in [-1,1]:box((x,side*wide/2,1.74),(.032,.07,2.5),'Rubber' if k%2 else 'Tread','articulation')
    box((x,0,.49),(.032,wide,.12),'Rubber','articulation')
 # Voxel tires, real recessed rims, tread and hub detail. Front axle is +X.
 for i,x in enumerate(axles):
  for side in [-1,1]:
   y=side*(W/2-.01);b=f'wheel_{i}_{"L" if side<0 else "R"}';parent='articulation' if name=='TransMilenio' and i==2 else 'root';bones[b]=((x,y,radius),(x,y+.2,radius),parent)
   tirewidth=.26 if bus else .21
   for ix in range(math.floor((x-radius)/q),math.ceil((x+radius)/q)):
    xx=(ix+.5)*q-x
    for iz in range(math.floor(0/q),math.ceil(radius*2/q)):
     zz=(iz+.5)*q-radius;rr=math.hypot(xx,zz);angle=math.atan2(zz,xx)
     for iy in range(math.floor((y-tirewidth/2)/q),math.ceil((y+tirewidth/2)/q)):
      yy=(iy+.5)*q-y
      if rr>radius-max(0,abs(yy)-tirewidth*.32)*.40:continue
      mat='Tread' if rr>radius-.075 and ((int(angle*18/math.pi)+iy)%3==0) else shade('Rubber',ix,iy,iz)
      outward=side*yy>tirewidth*.24
      if outward and rr<radius*.67:
       mat='Chrome' if rr>radius*.55 else 'Black'
       if rr<radius*.52 and abs(math.sin(angle*(8 if bus else 5)))<.30:mat='Rim' if rr<radius*.40 else 'Chrome'
       if rr<radius*.16:mat='Steel'
      put(ix,iy,iz,mat,b)
   # The axle's hub nuts remain visibly raised on the outside face.
   for j in range(6 if bus else 5):
    a=j*math.tau/(6 if bus else 5);box((x+math.cos(a)*radius*.25,y+side*(tirewidth/2+.005),radius+math.sin(a)*radius*.25),(.035,.035,.035),'Chrome',b)
 # Emit only exposed voxel faces, preserving color blocks and rigid bone boundaries.
 verts=[];faces=[];mi=[];vb=[];keys=list(COL);matindex={k:i for i,k in enumerate(keys)}
 directions=[((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),((-1,0,0),[(0,1,0),(0,0,0),(0,0,1),(0,1,1)]),((0,1,0),[(1,1,0),(0,1,0),(0,1,1),(1,1,1)]),((0,-1,0),[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)]),((0,0,-1),[(0,1,0),(1,1,0),(1,0,0),(0,0,0)])]
 verts,faces,facekeys,vb=emit(vox,q);mi=[matindex[k] for k in facekeys]
 for points,mat,b in panes:
  first=len(verts);verts.extend(points);faces.append((first,first+1,first+2,first+3));mi.append(matindex[mat]);vb.extend([b]*4)
 data=bpy.data.meshes.new('SK_'+name);data.from_pydata(verts,[],faces);data.update();obj=bpy.data.objects.new('SK_'+name,data);bpy.context.collection.objects.link(obj)
 for k in keys:
  mat=bpy.data.materials.new('TV_'+k);mat.diffuse_color=COL[k];mat.use_nodes=True;bsdf=mat.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=COL[k];bsdf.inputs['Roughness'].default_value=.27 if k.startswith('Glass') else .35 if k in ['Chrome','Rim'] else .66
  if k in ['Lamp','TailLight']:bsdf.inputs['Emission Color'].default_value=COL[k];bsdf.inputs['Emission Strength'].default_value=.15
  data.materials.append(mat)
 for p,m in zip(data.polygons,mi):p.material_index=m
 # Bake the palette into vertex colors: one draw section per vehicle in Unreal.
 colors=data.color_attributes.new(name='TrafficColor',type='BYTE_COLOR',domain='CORNER')
 for poly,idx in zip(data.polygons,mi):
  key=keys[idx];rough=.035 if key in ['Lamp','TailLight'] else .35 if key.startswith('Glass') else .55 if key in ['Chrome','Rim'] else .85
  for li in poly.loop_indices:colors.data[li].color=tuple(COL[key][:3])+(rough,)
 vertexmat=bpy.data.materials.new('TV_VoxelVertex');vertexmat.use_nodes=True
 vc=vertexmat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='TrafficColor';bsdf=vertexmat.node_tree.nodes['Principled BSDF'];vertexmat.node_tree.links.new(vc.outputs['Color'],bsdf.inputs['Base Color']);vertexmat.node_tree.links.new(vc.outputs['Alpha'],bsdf.inputs['Roughness'])
 data.materials.clear();data.materials.append(vertexmat)
 for poly in data.polygons:poly.material_index=0
 bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='Rig_'+name;bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
 for b,(h,t,parent) in bones.items():
  eb=rig.data.edit_bones.new(b);eb.head=h;eb.tail=t
  if parent:eb.parent=rig.data.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');groups={b:obj.vertex_groups.new(name=b) for b in bones};indices={b:[] for b in bones}
 for i,b in enumerate(vb):indices[b].append(i)
 for b,ii in indices.items():groups[b].add(ii,1,'REPLACE')
 mod=obj.modifiers.new('RigidVoxelSkin','ARMATURE');mod.object=rig;obj.parent=rig
 for frame,angle in [(1,0),(31,math.tau)]:
  for b in bones:
   if b.startswith('wheel_'):pb=rig.pose.bones[b];pb.rotation_mode='XYZ';pb.rotation_euler.y=angle;pb.keyframe_insert('rotation_euler',frame=frame)
 if name=='TransMilenio':
  for f,a in [(1,0),(16,.25),(31,0)]:pb=rig.pose.bones['articulation'];pb.rotation_mode='XYZ';pb.rotation_euler.y=a;pb.keyframe_insert('rotation_euler',frame=f)
 referencefiles={'classic':'Flota20_Clasicos_SinTexto.png','modern':'Flota20_Modernos_SinTexto.png','utility':'Flota20_Utilitarios_SinTexto.png','family':'Flota20_Familiares_SinTexto.png'}
 scene=bpy.context.scene;scene.frame_end=31;scene.frame_set(1);scene['reference_sheet']=str(ROOT/'outputs/DeliveryArt/References'/('TransMilenio_Rojo_Detallado_SinTexto.png' if bus else referencefiles[S['reference']] if S else 'Vehiculos_Colombia_Detallados_SinTexto.png'));scene['art_direction']='Fine voxel contours and details matched to NPC/store references; no text or logos.'
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(OUT/('SK_'+name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard';scene.view_settings.exposure=-.5
 scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.59,.64,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
 floor=bpy.data.materials.new('StudioFloor');floor.diffuse_color=(.25,.24,.22,1);floor.use_nodes=True;floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.24,.22,1)
 bpy.ops.mesh.primitive_plane_add(size=200);plane=bpy.context.object;plane.name='ReviewFloor';plane.data.materials.append(floor);plane.location.z=-.03
 aim=Vector((0,0,1.45 if bus else .78));bpy.ops.object.camera_add(location=(L*.83,-L*.95,L*.27+.8));cam=bpy.context.object;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=L*1.35;scene.camera=cam
 for pos,energy,size in [((L*.3,-L*.5,L*.6+3),450,5),((-L*.4,-1,5),200,5),((0,L*.5,7),350,5)]:
  bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=energy*(2 if bus else 1);light.data.size=size;light.rotation_euler=(aim-light.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(OUT/(name+'_Review.png'));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('SK_'+name+'.blend')))
 if '--no-render' not in sys.argv:bpy.ops.render.render(write_still=True)
 geometry_hash=hashlib.sha256(b''.join(struct.pack('<fff',*v) for v in verts)).hexdigest()
 manifest.append({'name':name,'label':S.get('label',name),'length_m':L,'width_m':W,'wheel_radius_m':radius,'voxel_m':q,'voxel_count':len(vox),'vertices':len(verts),'faces':len(faces),'bones':list(bones),'reference':scene['reference_sheet'],'geometry_hash':geometry_hash,'no_text':True,'build_seconds':round(time.time()-started,1)})
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('DETAILED_VEHICLE_READY',name,len(vox),len(faces),flush=True)
