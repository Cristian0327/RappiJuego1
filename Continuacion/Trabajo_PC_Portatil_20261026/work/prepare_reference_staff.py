from pathlib import Path
p=Path('work/build_distinct_staff.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('U=.025','U=.025\n# Modeling target: References/Encargados_Detallados.png, generated before this revision.')
start=s.index(' mats=[];keys=list(palette)')
detail=''' # Sculpt against the concept: cheek/jaw steps, ears, brows and layered garments.
 # Erase the old flat helmet hair; rebuild in offset locks at varied heights.
 for q in list(v):
  if q[2]>=head+13:del v[q]
 for z,rx,ry in [(head-1,5,5),(head,6,6),(head+1,7,6),(head+12,7,6),(head+13,6,6)]:oval(skin,z,z+1,rx,ry)
 for side in [-1,1]:
  oval(skin,head+5,head+10,2,2,side*(10 if role==1 else 8),0)
  box('hair',side*4-2,side*4+2,-8,-7,head+12,head+13)
  x=side*(width+2)
  # Individual fingertips, cuff seam, elbow pad, shoulder layering.
  for j in range(3):box(skin,x-2+j,x-1+j,-5,-3,shoulder-22,shoulder-19)
  box('white' if role in [1,3] else shirt,x-3,x+3,-4,5,shoulder-14,shoulder-12)
  for dz in range(3):box(shirt,x-3+dz,x+3-dz,-3,4,shoulder-2+dz,shoulder-1+dz)
  # Feet have toe, heel, sole, tongue and laces rather than a single block.
  x=side*5
  box('white' if role in [2,3] else 'hair',x-4,x+4,-8,5,1,3)
  box('white' if role==3 else 'blue' if role==2 else 'hair',x-3,x+3,-8,3,3,6)
  box('ink',x-2,x+2,-6,-1,5,7)
  for yy in [-5,-3,-1]:box('gold' if role==4 else 'white',x-2,x+2,yy,yy+1,7,8)
  box('denim',x-4,x+4,-4,5,8,10)
 if role==0:
  # Swept locks and low bun, cardigan lapels, brass buttons, floral blouse.
  for x in range(-9,9,3):oval('gray',head+13,head+17+(9-abs(x))//3,3,7,x,1)
  for z in range(head+3,head+14,3):oval('gray',z,z+3,4,4,-7,5)
  oval('gray',head+5,head+13,5,4,-5,8)
  box('white',-5,5,-8,-6,38,shoulder)
  for x,z in [(-3,40),(2,44),(-1,47),(3,39)]:box('green',x,x+1,-9,-8,z,z+3);box('red',x-1,x+2,-10,-9,z+2,z+4)
  for x in [-8,6]:box('purple',x,x+2,-9,-7,36,shoulder)
  for z in [38,42,46]:box('gold',-8,-6,-10,-9,z,z+2)
  for x in [-6,3]:box('white',x,x+4,-10,-8,24,31);box('gold',x,x+4,-11,-10,29,30)
  for x in [-5,4]:box('blue',x,x+1,-10,-9,30,34)
  box('white',width+1,width+7,-7,-5,shoulder-22,shoulder-9)
  for z in range(shoulder-21,shoulder-10,3):box('gray',width+2,width+5,-8,-7,z,z+1)
 elif role==1:
  # Bald crown is rounded in steps, side hair asymmetric; collar and apron ties.
  oval(skin,head+13,head+15,8,6);oval(skin,head+15,head+16,6,5)
  for side in [-1,1]:
   oval('hair',head+10,head+15,3,5,side*8,2)
   for j in range(4):box('white',side*j-2,side*j+2,-8,-6,shoulder+1-j,shoulder+3-j)
  for x in [-5,4]:box('ink',x,x+2,-9,-8,shoulder-4,shoulder-2)
  box('red',-14,14,5,7,waist+5,waist+7)
  for x,z in [(-7,30),(3,42),(-4,46),(6,24)]:box('gold',x,x+3,-9,-8,z,z+2)
  box('white',5,10,-10,-8,25,40)
  for z in [27,29]:box('red',5,10,-11,-10,z,z+1)
  box('ink',-10,-3,-10,-8,29,38)
  for x in [-9,-7,-5]:box('gold',x,x+1,-10,-9,36,44)
 elif role==2:
  # Dense independent curls with deliberate uneven hairline.
  for x in range(-9,10,3):
   for y in range(-6,8,3):oval('hair',head+12+(abs(x+y)%3),head+18+(x*y%4),2,2,x,y)
  # Headphones rest on shoulders, open head silhouette.
  for q in list(v):
   if abs(q[0])>=10 and q[2]>head:del v[q]
  for side in [-1,1]:
   box('ink',side*6-2,side*6+2,-7,-3,shoulder-2,shoulder+5);box('blue',side*6-1,side*6+1,-8,-7,shoulder-1,shoulder+4)
   box('blue',side*6-1,side*6+1,-8,-7,waist+1,shoulder-6)
   box('denim',side*6-3,side*6+3,-6,-3,waist-11,waist-3)
  for z in range(shoulder-10,shoulder-2):
   a=(z-(shoulder-10))//2+1;box('blue',-a,-a+1,-9,-8,z,z+1);box('blue',a,a+1,-9,-8,z,z+1)
  box('white',-2,3,-10,-8,shoulder-15,shoulder-10);box('gray',-1,2,-11,-10,shoulder-14,shoulder-12)
  box('ink',width,width+5,-8,-3,shoulder-23,shoulder-12);box('ink',width-1,width+6,-12,-4,shoulder-13,shoulder-9);box('red',width,width+4,-13,-12,shoulder-12,shoulder-10)
 elif role==3:
  # Bob with cheek framing tips, coat collar, folded lapels and pocket contents.
  for x in range(-9,9,3):oval('hair',head+12,head+17+(8-abs(x))//3,3,7,x,1)
  for side in [-1,1]:
   for z in range(head-1,head+13,3):oval('hair',z,z+3,2,5,side*8,2)
   for j in range(5):box('white',side*(j+2)-1,side*(j+2)+2,-9,-7,shoulder-5+j,shoulder-3+j)
   box('white',side*6-3,side*6+3,-9,-7,waist-5,waist+1)
  box('white',4,9,-10,-8,shoulder-11,shoulder-4)
  box('green',6,7,-11,-10,shoulder-10,shoulder-5);box('green',4,9,-11,-10,shoulder-8,shoulder-7)
  for x in [5,7]:box('red' if x==5 else 'blue',x,x+1,-10,-9,shoulder-4,shoulder)
 else:
  for x in range(-9,10,3):
   for y in range(-6,8,3):oval('red',head+11,head+17+(x*y%3),2,2,x,y)
  for z in range(head-2,head+10,3):oval('red',z,z+3,3,3,7,6)
  for z in range(head+7,head+20):box('white',4,7,2,7,z,z+1)
  for z in range(head+8,head+20,4):box('green',4,7,1,2,z,z+2)
  for side in [-1,1]:
   box('green',side*7-1,side*7+1,-8,-6,shoulder-3,shoulder+2)
   box('gold',side*5-4,side*5+4,-5,5,9,13)
  box('gold',-7,0,-10,-8,25,32);box('white',-6,-4,-11,-10,30,35)
  for x in [4,7]:box('red',x,x+2,-11,-9,24,32);box('gray',x,x+1,-11,-10,32,37)
 # Small color variation makes voxel planes legible without coarse giant surfaces.
 import random
 rng=random.Random(410+role)
 for key,c in list(v.items()):
  if key[0]%2==0 and key[2]%2==0 and rng.random()<.25 and c not in ['ink','skin','skinDark','skinLight']:
   variant=c+'_shade'
   if variant not in palette:palette[variant]=tuple(t*.91 for t in palette[c][:3])+(1,)
   v[key]=variant
'''
s=s[:start]+detail+s[start:];s=s.replace("bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))","bpy.context.scene['modeling_reference']='../References/Encargados_Detallados.png';bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))")
Path('work/build_reference_staff.py').write_text(s,encoding='utf-8')
