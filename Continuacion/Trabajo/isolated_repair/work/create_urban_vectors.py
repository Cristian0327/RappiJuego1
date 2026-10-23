from pathlib import Path
import html
root=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Vectors'
root.mkdir(parents=True,exist_ok=True)
ink='#111b2a';edge='#304052';paper='#f3e6c8';orange='#ff6729';cyan='#26c8df';yellow='#f5cb42'
def svg(name,w,h,body):
 (root/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>',encoding='utf-8')
def rect(x,y,w,h,c):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>'
def poly(points,c):return f'<polygon points="{points}" fill="{c}"/>'
def cube(x,y,w,h,top,front,side):
 return poly(f'{x},{y} {x+w},{y-w/2} {x+w*2},{y} {x+w},{y+w/2}',top)+poly(f'{x},{y} {x+w},{y+w/2} {x+w},{y+w/2+h} {x},{y+h}',side)+poly(f'{x+w},{y+w/2} {x+w*2},{y} {x+w*2},{y+h} {x+w},{y+w/2+h}',front)
# Icons are vector paths, not font glyphs or downloaded stock artwork.
b=cube(18,37,31,48,'#ffb059',orange,'#bc3e24')
b+=rect(36,11,27,6,ink)+rect(31,15,6,14,ink)+rect(60,15,6,14,ink)+poly('19,44 49,59 79,44 79,52 49,67 19,52',ink)+rect(51,68,9,13,paper)+rect(23,61,8,19,'#f09344')
svg('T_AppOrders',100,110,b)
b=poly('12,24 37,14 62,25 87,14 87,81 62,93 37,82 12,93',paper)+poly('37,14 62,25 62,93 37,82','#c8c9aa')
b+=poly('14,52 35,41 50,57 67,42 85,43 85,53 66,52 51,69 33,52 14,63',cyan)+poly('28,19 35,17 35,46 45,57 45,85 38,82 38,61 28,50',ink)
b+=rect(65,22,15,20,orange)+rect(61,26,23,12,orange)+poly('65,40 80,40 73,52',orange)+rect(69,27,7,9,ink)
svg('T_AppMap',100,110,b)
b=''
for cx in [25,77]:
 b+=poly(f'{cx-12},62 {cx+12},62 {cx+18},69 {cx+18},85 {cx+12},92 {cx-12},92 {cx-18},85 {cx-18},69',edge)+rect(cx-10,70,20,14,ink)+rect(cx-3,62,6,30,cyan)
b+=poly('25,73 40,42 66,47 77,76 42,76 40,42 46,43 48,69 69,69 62,53 44,49 31,77',cyan)+rect(32,35,20,7,paper)+rect(65,35,17,7,paper)
b+=poly('70,8 79,8 79,18 88,18 88,8 95,8 95,27 89,33 89,56 78,56 78,33 70,27',orange)
svg('T_AppWorkshop',100,110,b)
# Distinct parcel illustrations on the route receipts.
for n,c in [('Coffee','#b97c43'),('Market','#75b768'),('Food',orange)]:
 b=cube(17,27,28,39,paper,c,'#704132')
 if n=='Coffee':b+=rect(35,44,20,23,paper)+rect(40,50,10,11,c)
 if n=='Market':
  for x,y in [(26,19),(42,12),(56,20)]:b+=rect(x,y,11,24,'#4b9959')+rect(x-4,y+7,20,7,'#74c269')
 if n=='Food':b+=rect(29,52,36,8,paper)+rect(36,42,22,7,yellow)
 svg('T_Parcel'+n,90,100,b)
# A stepped shell with an actual transparent screen cutout, exported by Illustrator.
b=f'<path fill="{ink}" fill-rule="evenodd" d="M24 0H396V12H408V24H420V656H408V668H396V680H24V668H12V656H0V24H12V12H24Z M24 48V644H396V48Z"/>'
b+=rect(12,30,6,620,edge)+rect(402,30,6,620,'#080f18')+rect(24,36,372,5,edge)+rect(24,644,372,6,edge)
b+=rect(2,122,9,53,cyan)+rect(409,212,11,67,orange)
for x in range(159,261,12):b+=rect(x,19,6,7,'#52616b')
b+=rect(177,659,66,6,orange)+rect(28,13,30,16,yellow)+rect(31,17,5,8,ink)+rect(40,17,5,8,ink)+rect(49,17,5,8,ink)
b+=rect(330,14,33,5,cyan)+rect(341,21,22,5,cyan)+rect(354,28,9,5,cyan)
svg('T_UrbanShell',420,680,b)
# A custom pixel logotype. Source stays editable in Illustrator.
glyphs={'R':['11110','10001','11110','10100','10010'],'U':['10001','10001','10001','10001','01110'],'T':['11111','00100','00100','00100','00100'],'A':['01110','10001','11111','10001','10001'],'B':['11110','10001','11110','10001','11110'],'O':['01110','10001','10001','10001','01110'],'G':['01111','10000','10111','10001','01111']}
b=''
for row,word,color in [(0,'RUTA',paper),(1,'BOG',orange)]:
 for i,ch in enumerate(word):
  for y,line in enumerate(glyphs[ch]):
   for x,cell in enumerate(line):
    if cell=='1':b+=rect(i*54+x*9,row*58+y*9,9,9,color)
svg('T_RutaBog',220,110,b)
# Screen-printed route insignia: local skyline + signal blocks.
b=''
for x,h in [(0,16),(10,26),(22,20),(35,38),(48,27),(61,46),(76,32),(88,23)]:b+=rect(x,50-h,9,h,cyan)
b+=poly('102,50 130,8 150,50',edge)+rect(128,7,6,15,paper)+rect(122,11,18,5,paper)
svg('T_CityStamp',155,55,b)
print('URBAN_VECTORS_READY',len(list(root.glob('*.svg'))))
