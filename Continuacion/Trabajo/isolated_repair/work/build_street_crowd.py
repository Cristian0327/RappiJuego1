import bpy,math,json,sys,copy
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'work'));from voxel_greedy import emit
out=root/'outputs/DeliveryArt/Crowd';out.mkdir(parents=True,exist_ok=True)
source=(root/'work/build_character.py').read_text();env={};exec(compile(source[:source.index('# Remove overlaps')],'<hero-style>','exec'),env)
baseparts=copy.deepcopy(env['parts']);basebones=env['bone_for'];details=env['details'];basecolors=env['rgb'];U=2.25
rows=[
('Estudiante_Chaqueta',21,'sur','informal','cap','backpack',1.74,'305CA8','253653'),('Joven_Rizos',24,'norte','casual','curls','bag',1.67,'BA5969','24354A'),('Tecnico_Reflectivo',38,'centro','trabajo','helmet','vest',1.78,'D6AE34','3A4350'),('Joven_Parka',19,'sureste','casual','hood','backpack',1.72,'4B7860','27334C'),('Profesional_Blazer',32,'noroccidente','formal','bun','blazer',1.66,'766C91','2E3046'),('Artista_Gorro',26,'oriente','casual','beanie','scarf',1.79,'B76639','35334C'),
('Mayor_Boina',71,'sur','cotidiano','flatcap','cardigan',1.65,'756754','333948'),('Mayor_Canosa',68,'norte','cotidiano','silverbun','bag',1.58,'A17785','3E4159'),('Mayor_Abrigo',75,'centro','formal','silver','coat',1.67,'4C556B','34333E'),('Adulta_Cardigan',58,'sureste','cotidiano','long','cardigan',1.61,'9C6154','263B56'),('Mayor_Sueter',64,'noroccidente','cotidiano','bald','glasses',1.69,'596F86','343A48'),('Mayor_Caminante',62,'oriente','deportivo','silver','jacket',1.70,'467C73','33494D'),
('Joven_Deportivo',23,'sur','deportivo','short','jacket',1.83,'AD494E','252C3D'),('Profesional_Abrigo',42,'norte','formal','short','coat',1.82,'58546B','323442'),('Trabajadora_Urbana',35,'centro','trabajo','bun','vest',1.65,'399092','324453'),('Estudiante_Larga',20,'sureste','informal','long','backpack',1.63,'815A92','2C3B58'),('Adulto_Camisa',47,'noroccidente','formal','short','blazer',1.76,'748EAF','36384B'),('Joven_Bandana',22,'oriente','casual','curls','scarf',1.69,'BE7743','314552'),
('Adulta_Chaqueta',45,'sur','cotidiano','long','jacket',1.70,'63816B','3C3D54'),('Joven_Formal',27,'norte','formal','bun','blazer',1.72,'B58D66','383A48'),('Adulto_Bolso',54,'centro','cotidiano','beard','bag',1.77,'6F637A','303E4C'),('Joven_Buzo',18,'sureste','informal','beanie','hoodie',1.74,'477DA3','373B52'),('Adulta_Rizos',34,'noroccidente','casual','curls','bag',1.68,'AE6379','3B435A'),('Trabajador_Gorra',40,'oriente','trabajo','cap','vest',1.80,'7F9862','33434C')]
rows.extend([
('Empresario_Traje',46,'norte','empresarial','short','suit',1.94,'293449','202633'),
('Empresaria_Sastre',39,'centro','empresarial','bun','suit',1.57,'505968','282B37'),
('Joven_Urbano_Gorra',20,'sur','urbano','cap','urban',1.69,'A1323A','355A83'),
('Joven_Urbana_Conjunto',22,'sureste','urbano','bun','tracksuit',1.53,'865AAF','322742'),
('Joven_Urbano_Deportivo',25,'noroccidente','urbano','short','tracksuit',1.88,'356B58','242936'),
('Empresario_Senior',63,'oriente','empresarial','silver','suit',1.73,'665C50','343439')])
rows.extend([
('Mujer_Vestido_Floral',29,'sur','vestido','long','dress',1.60,'67927B','384353'),
('Mujer_Vestido_Formal',45,'norte','vestido','bun','dress',1.81,'485589','343845'),
('Mayor_Vestido',69,'centro','vestido','silverbun','dress',1.55,'A3637E','3E4355'),
('Joven_Falda_Chaqueta',19,'sureste','falda','long','skirt',1.66,'8F668F','36455B'),
('Empresaria_Traje',48,'noroccidente','empresarial','short','suit',1.86,'596B7D','252B38'),
('Empresaria_Cabello_Largo',35,'oriente','empresarial','long','suit',1.71,'657493','292E3E'),
('Mujer_Vestido_Casual',24,'sur','vestido','curls','dress',1.73,'BC995D','344654'),
('Hombre_Camisa_Remangada',32,'centro','casual','short','shirt',1.62,'A6B5A4','314258'),
('Joven_Urbana_Gorra',23,'noroccidente','urbano','cap','urban',1.78,'B78355','3F577E'),
('Mayor_Sueter_Baston',78,'sureste','cotidiano','flatcap','cardigan',1.59,'758872','35434E')])
rows.extend([('Universitario_Morral', 20, 'centro', 'universitario', 'short', 'student', 1.77, '536E9D', '354358'), ('Universitaria_Morral', 21, 'norte', 'universitario', 'long', 'student', 1.64, 'B2756A', '293C54'), ('Universitario_Buzo', 19, 'sur', 'universitario', 'beanie', 'student', 1.82, '65816B', '303849'), ('Universitaria_Rizos', 23, 'oriente', 'universitario', 'curls', 'student', 1.71, '98769C', '3F465A'), ('Estudiante_Ingenieria', 22, 'noroccidente', 'universitario', 'short', 'student', 1.68, '667B8D', '283748'), ('Estudiante_Arte', 24, 'sureste', 'universitario', 'bun', 'student', 1.59, 'B39358', '3D4E60'), ('Ejecutivo_Corbata', 37, 'centro', 'empresarial', 'short', 'suit', 1.79, '343D50', '262B38'), ('Ejecutiva_Sastre_Moreno', 43, 'norte', 'empresarial', 'bun', 'suit', 1.69, '846D7C', '37303D'), ('Ejecutivo_Canoso', 57, 'oriente', 'empresarial', 'silver', 'suit', 1.84, '696E72', '383D43'), ('Ejecutiva_Traje_Claro', 31, 'noroccidente', 'empresarial', 'long', 'suit', 1.76, 'A69B84', '635E57'), ('Docente_Lentes', 52, 'centro', 'docente', 'short', 'teacher', 1.72, '65778D', '383C4A'), ('Docente_Cardigan', 48, 'sur', 'docente', 'bun', 'teacher', 1.62, 'AA7668', '3A4350'), ('Trabajador_Obra', 36, 'sureste', 'trabajo', 'helmet', 'vest', 1.81, 'CE9E43', '3B4A61'), ('Trabajadora_Salud', 29, 'centro', 'salud', 'bun', 'scrubs', 1.65, '648C92', '507E84'), ('Cocinero', 41, 'sur', 'cocina', 'short', 'apron', 1.74, 'DDDDD0', '3E4653'), ('Cocinera', 34, 'norte', 'cocina', 'bun', 'apron', 1.6, 'DAD5C7', '394453'), ('Comerciante_Bolso', 55, 'oriente', 'comercio', 'beard', 'bag', 1.78, '9D805D', '405167'), ('Deportista_Morral', 26, 'noroccidente', 'deportivo', 'cap', 'student', 1.87, '426A82', '293A51'), ('Joven_Urbana_Chaqueta', 20, 'sur', 'urbano', 'curls', 'urban', 1.67, '815B80', '3D5876'), ('Trabajador_Camisa', 46, 'sureste', 'trabajo', 'short', 'shirt', 1.7, 'A7AFA1', '3D4A61')])
catalog=[];globalcolors={}
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
skins=[(.91,.64,.44),(.61,.36,.22),(.39,.23,.15),(.78,.48,.30)]
for i,row in enumerate(rows):
 label,age,region,style,hair,extra,height,shirt,pants=row;c=dict(basecolors);skin=skins[i%4];shirt=rgb(shirt);pants=rgb(pants)
 for key,mul in [('skin',1),('skin_light',1.10),('skin_dark',.78)]:c[key]=tuple(min(1,v*mul) for v in skin)
 for key,mul in [('teal',1),('teal_light',1.10),('teal_dark',.79),('orange',.94),('orange_light',1.06),('orange_dark',.80),('ice',1.08),('ice_light',1.16),('ice_shadow',.86)]:c[key]=tuple(min(1,v*mul) for v in shirt)
 for key,mul in [('cloth',1),('cloth_light',1.12),('stitch',.88)]:c[key]=tuple(min(1,v*mul) for v in pants)
 hc=(.57,.59,.59) if age>60 else [(.16,.105,.065),(.12,.12,.15),(.24,.14,.08)][i%3]
 for key,mul in [('hair',1),('hair_light',1.35),('hair_dark',.75)]:c[key]=tuple(min(1,v*mul) for v in hc)
 c['black']=(.06,.065,.075);c['sole']=(.10,.105,.11);c['white']=(.88,.89,.85);c['metal']=(.39,.41,.43);c['scarf']=(.68,.36,.17) if i%2==0 else (.24,.46,.52)
 c['cane']=(.30,.18,.10)
 if extra in ['dress','skirt']:
  for key,mul in [('cloth',1),('cloth_light',1.08),('stitch',.9)]:c[key]=tuple(min(1,v*mul) for v in skin)
 for key,value in c.items():globalcolors[f'{i}:{key}']=value
 catalog.append({'name':f'Citizen{i:02d}','label':label,'age':age,'region':region,'outfit':style,'height_m':height,'hair':hair,'extra':extra,'width':.95+(i%5)*.035,'colors':c})
for i,c in enumerate(catalog):c.update(gender='mujer' if i in {1,3,4,7,9,11,14,15,17,18,19,22,25,27,30,31,32,33,34,35,36,38,41,43,45,47,49,51,53,55,58} else 'hombre',age_group='joven' if c['age']<30 else 'mayor' if c['age']>=60 else 'adulto',cane=c['age']>=60)
# Shared small atlas, with the same restrained voxel shading as the protagonist.
N=64;tile=8;size=512;pixels=[.15,.15,.15,1]*(size*size);indices={k:j for j,k in enumerate(globalcolors)}
for key,j in indices.items():
 col=globalcolors[key];tx=j%N;ty=j//N
 for y in range(tile):
  for x in range(tile):
   factor=.94+(((x//4)*31+(y//4)*19+j*7)%41)/40*.14
   if x%8==0 or y%8==0:factor*=.972
   # Greedy head quads have different sizes. A mottled tile stretched over
   # each quad looked like disconnected horizontal slices on cheeks in motion.
   if key.split(':')[1] in ['skin','skin_light','skin_dark','white','eye']:factor=1.0
   at=((ty*tile+y)*size+tx*tile+x)*4;pixels[at:at+4]=[min(1,v*factor) for v in col]+[1]
img=bpy.data.images.new('CrowdPixelAtlas',width=size,height=size,alpha=True);img.pixels=pixels;img.filepath_raw=str(out/'T_CrowdPixelAtlas.png');img.file_format='PNG';img.save()
weightcode=(root/'work/rebuild_unreal.py').read_text();wenv={};exec(weightcode[weightcode.index('def blend(a,b,t):'):weightcode.index('groups={b.name:ob.vertex_groups.new')],wenv)
for i,s in enumerate(catalog):
 parts=copy.deepcopy(baseparts);bones=dict(basebones)
 for key in list(parts):
  if key.startswith(('03 |','06 |','14 |')):del parts[key]
 def box(part,mat,x0,x1,y0,y1,z0,z1,region='head'):
  parts.setdefault(part,{});bones[part]=region
  for x in range(math.floor(x0),math.ceil(x1)):
   for y in range(math.floor(y0),math.ceil(y1)):
    for z in range(math.floor(z0),math.ceil(z1)):parts[part][x,y,z]=mat
 def oval(part,mat,z0,z1,rx,ry,cx=0,cy=0,region='head'):
  for x in range(math.floor(cx-rx),math.ceil(cx+rx)):
   for y in range(math.floor(cy-ry),math.ceil(cy+ry)):
    if ((x+.5-cx)/rx)**2+((y+.5-cy)/ry)**2<=1:box(part,mat,x,x+1,y,y+1,z0,z1,region)
 # Close the skull beneath the hair and connect the ears to the cheek. The
 # hero's ear cut removed an entire horizontal band when reused without a cap.
 oval('Solid skull','skin',58,69,9,8,cy=0)
 box('Face plane','skin_light',-8,8,-8,3,60,66)
 for a,b in [(-10,-7),(7,10)]:box('Ear roots','skin',a,b,-3,1,61,65)
 # Keep sub-voxel graphic details out of the integer voxel conversion: the
 # iris and upper lid otherwise overwrite most of the white eye cells.
 for name,mat,bb,bone in details:
  if bone=='head':continue
  box('Face details',mat,*bb,bone)
 # Leave a full clear row above the eyes; all hair still follows the head bone.
 for key in list(parts):
  if bones.get(key)=='head':
   parts[key]={q:m for q,m in parts[key].items() if not (m.startswith('hair') and abs(q[0]+.5)<8 and q[1]<-5 and q[2]<67 and key!='Brows')}
 hair=s['hair'];extra=s['extra']
 # Close the crown and temple band before adding the individual hairstyles.
 oval('Continuous scalp','skin' if hair=='bald' else 'hair',66,70,9,8,cy=1)
 for side in [-1,1]:
  box('Temple hair','hair',-10,-8,-4,1,65,69) if side<0 else box('Temple hair','hair',8,10,-4,1,65,69)
 if hair == 'bald':
  parts['02 | Sculpted voxel hair']={q:m for q,m in parts['02 | Sculpted voxel hair'].items() if q[0]<-5 or q[0]>5 or q[1]>2}
 if hair in ['long','bun','silverbun']:
  box('Long Hair','hair',-9,9,4,10,50,69)
  if hair!='long':oval('Hair bun','hair_light',67,76,5,5,cy=7)
 if hair=='curls':
  for x in [-8,-4,0,4,8]:
   for y in [-4,0,4]:oval('Curly Hair','hair_light' if (x+y)%3==0 else 'hair',68,74+(x%3),3,3,x,y)
 if hair in ['cap','flatcap','beanie','hood','helmet']:
  top=77 if hair in ['cap','helmet'] else 73 if hair=='flatcap' else 76
  oval('Hat','orange' if hair=='cap' else 'scarf' if hair=='beanie' else 'teal',68,top,10,9,cy=1)
  if hair in ['cap','flatcap']:box('Hat brim','orange' if hair=='cap' else 'teal',-9,9,-13,-6,69,70)
  if hair=='helmet':box('Helmet band','white',-10,10,-8,-7,69,71);box('Helmet ridge','orange_light',-2,2,-8,9,73,78)
  if hair=='hood':box('Hood sides','teal',-11,-8,-7,8,58,73);box('Hood sides','teal',8,11,-7,8,58,73)
 # A stepped crown replaces the flat cylindrical hair silhouette.
 if hair not in ['cap','flatcap','beanie','hood','helmet','bald']:
  crown=74+(i%3) if hair!='curls' else 77+(i%2)
  for z in range(69,crown):
   t=(z-69)/max(1,crown-69)
   rx=9*math.sqrt(max(.05,1-t*t));ry=8*math.sqrt(max(.05,1-t*t))
   oval('Volumetric crown','hair_light' if z>=crown-2 else 'hair',z,z+1,rx,ry,cx=(i%3-1)*.6,cy=1)
  # A small offset lock gives each silhouette a visible part and asymmetry.
  oval('Crown lock','hair_light',crown-2,crown+1,2.5,3,cx=2 if i%2 else -2,cy=0)
 elif hair=='bald':
  for z,rx,ry in [(69,7,6),(70,5,4),(71,3,2)]:oval('Rounded scalp','skin',z,z+1,rx,ry,cy=1)
 if hair in ['cap','flatcap','beanie','hood','helmet']:
  hatpart=parts['Hat']
  for q in list(hatpart):
   x,y,z=q
   if z>=top-4:
    t=(z-(top-4))/4;rx=10*math.sqrt(max(.10,1-t*t));ry=9*math.sqrt(max(.10,1-t*t))
    if ((x+.5)/rx)**2+((y+.5-1)/ry)**2>1:del hatpart[q]
 if hair=='beard' or s['age']>65:
  if hair=='beard':box('Beard','hair',-6,6,-9,-8,57,60)
  for x in [-7,6]:box('Age face pixels','skin_dark',x,x+1,-9,-8,59,62)
 if extra=='glasses' or s['age']>64:
  for x in [-7,2]:
   for z in [60,64]:box('Spectacles','metal',x,x+5,-10,-9,z,z+1)
   for xx in [x,x+4]:box('Spectacles','metal',xx,xx+1,-10,-9,60,65)
  box('Spectacles','metal',-2,3,-10,-9,62,63)
 if extra in ['backpack','student']:parts['14 | Backpack / removable']=copy.deepcopy(baseparts['14 | Backpack / removable']);bones['14 | Backpack / removable']='chest'
 if extra=='student':
  box('Morral pocket','teal_dark',-6,6,13,16,35,43,'chest')
  box('Morral zipper','metal',-5,5,16,17,42,43,'chest')
  for side in [-1,1]:box('Morral shoulder straps','black',side*6-1,side*6+1,-7,-6,42,54,'chest')
 if extra=='teacher':
  box('Teacher cardigan seam','teal_dark',-1,1,-7,-6,36,52,'chest')
  box('Teacher shirt collar','white',-4,4,-8,-6,49,53,'chest')
  box('Document bag','cloth',-20,-11,-4,3,18,29,'prop_r')
 if extra=='scrubs':
  box('Scrubs collar','teal_dark',-4,4,-7,-6,49,53,'chest')
  box('Scrubs pocket','white',4,7,-7,-6,43,47,'chest')
 if extra=='apron':
  box('Apron bib','white',-6,6,-8,-6,36,49,'chest')
  box('Apron skirt','white',-8,8,-7,-5,25,36,'pelvis')
  box('Apron pocket','teal_dark',-4,4,-9,-8,35,40,'chest')
 if extra=='bag':box('Shoulder bag','cloth',9,14,3,9,29,43,'pelvis');box('Bag strap','black',8,10,2,4,42,54,'chest')
 if extra in ['coat','cardigan','blazer']:
  box('Outer coat','teal',-8,8,-5,5,34 if extra=='blazer' else 28,50,'chest')
  box('Coat seam','teal_dark',-1,1,-6,-5,34,51,'chest')
  for z in [37,42,47]:box('Buttons','metal',1,2,-7,-6,z,z+1,'chest')
  if extra=='blazer':box('Blazer shirt','white',-3,3,-7,-6,46,53,'chest')
 if extra=='vest':
  box('Work vest','teal',-8,8,-6,-5,38,50,'chest')
  for z in [40,47]:box('Reflective strip','white',-8,8,-7,-6,z,z+1,'chest')
 if extra=='scarf':box('Scarf','scarf',-5,5,-7,5,52,56,'chest');box('Scarf end','scarf',-4,-1,-8,-6,43,54,'chest')
 if extra=='hoodie':box('Hoodie pocket','teal_dark',-5,5,-6,-5,39,43,'chest')
 if extra=='suit':
  for key in list(parts):
   if key.startswith('11 |'):parts[key]={q:m for q,m in parts[key].items() if abs(q[0])<9}
   if key.startswith('13 |'):parts[key]={q:'black' for q in parts[key]}
  box('Tailored jacket','teal',-8,8,-5,5,33,51,'chest')
  box('White formal shirt','white',-3,3,-7,-5,39,53,'chest')
  for z in range(41,53):
   width=1 if z>47 else 2;box('Tie','scarf',-width,width,-8,-7,z,z+1,'chest')
  for side in [-1,1]:
   for z in range(44,52):
    x=side*(2+(51-z)//3);box('Suit lapel','teal_light',x-1,x+1,-8,-6,z,z+1,'chest')
  box('Briefcase','black',-20,-11,-4,4,17,28,'prop_r')
  box('Briefcase seam','metal',-21,-20,-3,3,19,26,'prop_r')
  box('Briefcase handle sides','black',-18,-17,-1,1,28,32,'prop_r')
  box('Briefcase handle sides','black',-14,-13,-1,1,28,32,'prop_r')
  box('Briefcase handle top','black',-18,-13,-1,1,32,33,'prop_r')
  box('Formal belt','black',-8,8,-6,-5,33,34,'pelvis')
  box('Belt buckle','metal',-1,1,-7,-6,33,34,'pelvis')
  for side in [-1,1]:box('Formal white cuffs','white',side*12-2,side*12+2,-4,4,33,35,'forearm.L' if side==1 else 'forearm.R')
  box('Formal shirt collar','white',-4,4,-8,-6,51,54,'chest')
 if extra in ['urban','tracksuit']:
  box('Crossbody pouch','black',-7,-1,-9,-6,36,42,'chest')
  for z in range(40,54):
   x=-6+(z-40)//2;box('Crossbody strap','black',x,x+1,-7,-6,z,z+1,'chest')
  if extra=='urban':
   for z in [39,43,47,51]:box('Puffer bands','teal_dark',-8,8,-6,-5,z,z+1,'chest')
  else:
   for side in [-1,1]:
    box('Tracksuit sleeve stripe','white',side*12-1,side*12+1,-3,-2,33,50,'forearm.L' if side==1 else 'forearm.R')
    box('Tracksuit leg stripe','white',side*7,side*7+1,-3,-2,12,29,'thigh.L' if side==1 else 'thigh.R')
 if s['cane']:
  box('Cane shaft','cane',14,15,-9,-8,1,35,'cane')
  box('Cane grip','cane',11,17,-10,-8,35,37,'cane')
  box('Cane rubber tip','black',13,16,-10,-7,0,2,'cane')
 if extra in ['dress','skirt']:
  for key in list(parts):
   if key.startswith('11 |'):parts[key]={q:m for q,m in parts[key].items() if abs(q[0])<8}
   if key.startswith('13 |'):parts[key]={q:'black' for q in parts[key]}
  if extra=='dress':box('Dress bodice','teal',-8,8,-6,5,34,52,'chest')
  for z in range(21,35):
   width=9+(34-z)//5;box('Dress skirt','teal',-width,width,-6,6,z,z+1,'dress')
   for x in range(-width,width,4):box('Pleat shading','teal_dark',x,x+1,-7,-6,z,z+1,'dress')
  box('Dress waist belt','scarf',-9,9,-7,6,34,35,'pelvis')
  if i==30:
   for x,z in [(-5,40),(4,46),(-2,49),(6,27),(-6,30)]:box('Dress floral pixels','white',x,x+2,-8,-7,z,z+2,'chest' if z>35 else 'dress')
 if extra=='shirt':
  box('Shirt collar','white',-4,4,-7,-5,49,53,'chest')
  box('Rolled cuffs','white',-15,-10,-4,4,41,43,'forearm.R');box('Rolled cuffs','white',10,15,-4,4,41,43,'forearm.L')
 vox={}
 for p,vs in parts.items():
  for q,m in vs.items():vox[q]=(m,(bones[p],'Unified head' if bones[p]=='head' else p))
 V,F,M,tags=emit(vox,U)
 # Preserve the courier's actual sub-voxel eye geometry and pupil/white ratio.
 # Quantizing these thin layers into voxels made pupils bulge over the whites.
 for name,mat,bb,bone in details:
  if bone!='head' or name.startswith('Cap'):continue
  x0,x1,y0,y1,z0,z1=[a*U for a in bb];first=len(V)
  V.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
  for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)]:
   F.append(tuple(first+j for j in face));M.append(mat)
  tags.extend([('head','Courier facial details')]*8)
 # Keep enough vertices at joint transitions for skinning. Greedy rectangles
 # spanning a whole leg cannot follow a bending knee.
 nv=[];nf=[];nm=[];nt=[]
 for face,key in zip(F,M):
  p0,p1,p2,p3=[Vector(V[j]) for j in face];tag=tags[face[0]]
  deform=tag[0]!='head'
  nx=max(1,math.ceil((p1-p0).length/(U*2))) if deform else 1
  ny=max(1,math.ceil((p3-p0).length/(U*2))) if deform else 1
  for ax in range(nx):
   for ay in range(ny):
    first=len(nv)
    for x,y in [(ax/nx,ay/ny),((ax+1)/nx,ay/ny),((ax+1)/nx,(ay+1)/ny),(ax/nx,(ay+1)/ny)]:nv.append(tuple(p0+(p1-p0)*x+(p3-p0)*y));nt.append(tag)
    nf.append(tuple(range(first,first+4)));nm.append(key)
 V,F,M,tags=nv,nf,nm,nt
 bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/unreal_v2/VoxelExplorer_GameRig.blend'))
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.animation_data_clear()
 for o in list(bpy.data.objects):
  if o!=rig:bpy.data.objects.remove(o,do_unlink=True)
 for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 cane=rig.data.edit_bones.new('cane');cane.head=(32,-19,0);cane.tail=(32,-19,80);cane.parent=rig.data.edit_bones['root'];bpy.ops.object.mode_set(mode='OBJECT')
 weights=[];vertices=[]
 for p,(region,part) in zip(V,tags):
  q=tuple(v/U for v in p)
  if region=='dress':
   pelvis=max(0,min(1,(q[2]-21)/13));left=max(0,min(1,(q[0]+3)/6));wt={'pelvis':pelvis,'thigh_l':(1-pelvis)*left,'thigh_r':(1-pelvis)*(1-left)}
  else:wt={'cane':1} if region=='cane' else {'hand_r':1} if region=='prop_r' else wenv['weights_for_region'](q,region,part)
  if region=='head':wt={'head':1}
  if region.startswith('foot'):wt={'foot_l' if q[0]>=0 else 'foot_r':1}
  pos=Vector(p);new=Vector((0,0,0))
  for bone,w in wt.items():
   if bone.startswith(('upperarm','lowerarm','hand')):
    sign=1 if bone.endswith('_l') else -1;pivot=Vector((sign*22.5,0,114.75));new+=(pivot+Quaternion((0,1,0),math.radians(-35*sign))@(pos-pivot))*w
   else:new+=pos*w
  new.x*=s['width'];vertices.append(tuple(new));weights.append(wt)
 data=bpy.data.meshes.new('SK_'+s['name']);data.from_pydata(vertices,[],F);data.update();obj=bpy.data.objects.new('SK_'+s['name'],data);bpy.context.collection.objects.link(obj)
 uv=data.uv_layers.new(name='UVMap')
 for poly,key in zip(data.polygons,M):
  j=indices[f'{i}:{key}'];tx=j%N;ty=j//N
  for li,xy in zip(poly.loop_indices,[(.12,.12),(.88,.12),(.88,.88),(.12,.88)]):uv.data[li].uv=((tx+xy[0])/N,(ty+xy[1])/N)
 img=bpy.data.images.load(str(out/'T_CrowdPixelAtlas.png'));img.pack();mat=bpy.data.materials.new('CrowdPixel');mat.use_nodes=True;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Closest';bsdf=mat.node_tree.nodes['Principled BSDF'];mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.82;data.materials.append(mat)
 groups={b.name:obj.vertex_groups.new(name=b.name) for b in rig.data.bones}
 for v,wt in enumerate(weights):
  for b,w in wt.items():
   if w>1e-7:groups[b].add([v],w,'REPLACE')
 mod=obj.modifiers.new('Shared protagonist skin','ARMATURE');mod.object=rig;obj.parent=rig
 h=max(v.co.z for v in data.vertices)-min(v.co.z for v in data.vertices);s['scale']=s['height_m']*100/h;s['vertices']=len(vertices);s['triangles']=len(F)*2;s['bones']=len(rig.data.bones)
 clip='AN_CrowdCane' if s['cane'] else 'AN_CrowdWalk'
 with bpy.data.libraries.load(str(out/(clip+'.blend')),link=False) as (a,b):b.actions=[n for n in a.actions if n==clip]
 action=b.actions[0];rig.animation_data_create();rig.animation_data.action=action;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=int(action.frame_range[1]);bpy.context.scene.frame_set(1)
 bpy.context.scene['art_reference']='Protagonist: identical authored facial language, voxel size, skin hierarchy and palette shading.'
 # Export bind pose; retain the shared grounded walk in the editable file.
 rig.animation_data.action=None
 for pb in rig.pose.bones:pb.rotation_quaternion=(1,0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
 bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(out/('SK_'+s['name']+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_armature_deform_only=True,mesh_smooth_type='FACE')
 rig.animation_data.action=action;bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/('SK_'+s['name']+'.blend')))
 print('CITIZEN_READY',s['name'],s['triangles'],flush=True)
(out/'catalog.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False))
lines=['struct FCrowdSpec {const TCHAR* Name;float Scale,Speed;int32 Region;};','static const FCrowdSpec CrowdModels[]={']
for i,s in enumerate(catalog):lines.append(f' {{TEXT("{s["name"]}"),{s["scale"]:.6f}f,{38*s["scale"] if s["cane"] else 112+(i%3)*8:.3f}f,{i%6},{str(s["cane"]).lower()}}},')
lines[0]='struct FCrowdSpec {const TCHAR* Name;float Scale,Speed;int32 Region;bool Cane;};'
lines+=['};','static_assert(UE_ARRAY_COUNT(CrowdModels)==60);'];(root/'outputs/BogotaVoxel/Source/BogotaVoxel/CrowdCatalog.inl').write_text('\n'.join(lines))
print('ALL_60_CITIZENS_READY',flush=True)

