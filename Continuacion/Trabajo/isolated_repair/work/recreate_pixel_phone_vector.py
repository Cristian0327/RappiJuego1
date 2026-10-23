from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import random,html,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/Illustrator/Telefono_Pixel';OUT.mkdir(parents=True,exist_ok=True)
parts=[];groups=[]
def group(name):parts.append(f'<g id="{html.escape(name)}">');groups.append(name)
def end():parts.append('</g>')
def rect(x,y,w,h,c,opacity=1):parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" opacity="{opacity}"/>')
def poly(points,c,opacity=1):parts.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{c}" opacity="{opacity}"/>')
def path(d,c):parts.append(f'<path d="{d}" fill="{c}"/>')
def outline(x,y,w,h,s=14):
 return [(x+2*s,y),(x+w-2*s,y),(x+w-2*s,y+s),(x+w-s,y+s),(x+w-s,y+2*s),(x+w,y+2*s),(x+w,y+h-2*s),(x+w-s,y+h-2*s),(x+w-s,y+h-s),(x+w-2*s,y+h-s),(x+w-2*s,y+h),(x+2*s,y+h),(x+2*s,y+h-s),(x+s,y+h-s),(x+s,y+h-2*s),(x,y+h-2*s),(x,y+2*s),(x+s,y+2*s),(x+s,y+s),(x+2*s,y+s)]
def pixelplate(x,y,w,h,c,s=7):poly(outline(x,y,w,h,s),c)
fonts={k:TTFont(ROOT/f'outputs/DeliveryArt/UI/Fonts/RutaPixel-{k}.ttf') for k in ['Regular','Bold']}
def text(label,x,y,size=26,center=False,bold=False):
 f=fonts['Bold' if bold else 'Regular'];gs=f.getGlyphSet();cmap=f.getBestCmap();scale=size/f['head'].unitsPerEm
 width=sum(f['hmtx'][cmap[ord(ch)]][0] for ch in label)*scale
 if center:x-=width/2
 parts.append(f'<g id="Texto_{html.escape(label.replace(" ","_"))}" fill="#f8fcfa" transform="translate({x},{y}) scale({scale},{-scale})">')
 offset=0
 for ch in label:
  name=cmap[ord(ch)];pen=SVGPathPen(gs);gs[name].draw(pen);d=pen.getCommands()
  if d:parts.append(f'<path transform="translate({offset},0)" d="{d}"/>')
  offset+=f['hmtx'][name][0]
 parts.append('</g>')
defs='''<defs>
<linearGradient id="body" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#292c2d"/><stop offset=".48" stop-color="#191c1d"/><stop offset="1" stop-color="#202123"/></linearGradient>
<linearGradient id="bezel" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#292c2e"/><stop offset=".55" stop-color="#1c1f20"/><stop offset="1" stop-color="#191a1c"/></linearGradient>
<linearGradient id="rim" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#55575b"/><stop offset=".5" stop-color="#393b3e"/><stop offset="1" stop-color="#292b2d"/></linearGradient>
<linearGradient id="sky" x1="0" y1="0" x2=".24" y2="1"><stop stop-color="#1289ed"/><stop offset=".45" stop-color="#20a2e5"/><stop offset="1" stop-color="#50b4e2"/></linearGradient>
<linearGradient id="paper" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#f2f0ec"/><stop offset="1" stop-color="#e5e5df"/></linearGradient>
<linearGradient id="green" x1="0" y1="0" x2=".3" y2="1"><stop stop-color="#398b46"/><stop offset=".5" stop-color="#246b45"/><stop offset="1" stop-color="#174e3d"/></linearGradient>
<linearGradient id="hill" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#73a93b"/><stop offset="1" stop-color="#4e9138"/></linearGradient>
<linearGradient id="teal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#23928d"/><stop offset="1" stop-color="#176b7d"/></linearGradient>
<linearGradient id="phonegreen" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#25d645"/><stop offset="1" stop-color="#1dca42"/></linearGradient>
<linearGradient id="blue" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#087efa"/><stop offset="1" stop-color="#138ef4"/></linearGradient>
<clipPath id="screenclip"><polygon points="219,225 805,225 805,237 815,237 815,1325 804,1325 804,1334 219,1334 219,1325 208,1325 208,237 219,237"/></clipPath>
<clipPath id="chromeclip"><polygon points="403,993 474,993 474,1000 480,1000 480,1007 487,1007 487,1076 480,1076 480,1083 474,1083 474,1090 403,1090 403,1083 396,1083 396,1076 389,1076 389,1007 396,1007 396,1000 403,1000"/></clipPath>
</defs>'''
group('01_Botones_laterales')
for y,h in [(330,144),(531,124)]:
 pixelplate(858,y,36,h,'#2c2f31',5);rect(867,y+8,17,h-17,'#41454a');rect(870,y+8,11,8,'#73777b');rect(883,y+16,9,h-30,'#26292c');rect(868,y+20,5,h-31,'#4d5055')
end()
group('02_Carcasa_y_biseles')
poly(outline(147,94,728,1368,20),'url(#body)')
poly(outline(168,114,686,1328,20),'url(#rim)')
poly(outline(190,134,644,1288,19),'url(#bezel)')
rect(208,94,607,20,'#25282a');rect(228,114,567,20,'#585b60')
rect(168,171,22,1213,'#56595e');rect(148,155,20,1247,'#25282b')
rect(834,171,20,1213,'#34373b');rect(855,155,20,1247,'#24272a')
rect(208,1422,607,19,'#44474b');rect(228,1442,567,19,'#242628')
for x,y,c in [(188,134,'#74777b'),(169,154,'#696c70'),(208,114,'#62656a'),(795,134,'#46494d'),(815,154,'#424549'),(188,1384,'#3b3e42'),(208,1403,'#3d4044'),(795,1403,'#404347'),(815,1384,'#34383c')]:rect(x,y,20,20,c)
end()
group('03_Altavoz_y_camara')
poly([(427,164),(595,164),(595,176),(607,176),(607,191),(595,191),(595,203),(427,203),(427,191),(415,191),(415,176),(427,176)],'#090b0d')
rect(428,177,167,13,'#2c2e30');rect(428,190,167,12,'#080a0c')
pixelplate(655,158,47,47,'#080a0b',8);rect(672,174,13,15,'#788590');rect(674,175,10,11,'#8c98a0')
end()
parts.append('<g clip-path="url(#screenclip)">')
group('04_Pantalla_cielo')
rect(208,225,607,1109,'url(#sky)')
for x,y,w,h,c,o in [(208,470,310,35,'#55b7ee',.11),(518,494,214,38,'#087ed8',.1),(732,470,83,69,'#63caf3',.17),(208,505,42,35,'#83d2ef',.3),(440,565,199,61,'#64c3ed',.12),(208,610,201,48,'#4bbfe9',.16),(409,626,221,30,'#83d7ee',.15),(208,658,201,70,'#70c6eb',.15),(436,702,85,32,'#8fd4ee',.17),(569,740,211,52,'#78d0ef',.13),(748,539,67,51,'#82d3ec',.15)]:rect(x,y,w,h,c,o)
poly([(208,576),(233,576),(233,548),(272,548),(272,529),(332,529),(332,565),(406,565),(406,579),(476,579),(476,594),(297,594),(297,610),(208,610)],'#c9e2eb')
poly([(208,541),(230,541),(230,511),(249,511),(249,494),(265,494),(265,478),(346,478),(346,494),(362,494),(362,532),(424,532),(424,548),(441,548),(441,567),(476,567),(476,578),(407,578),(407,564),(332,564),(332,528),(272,528),(272,548),(233,548),(233,577),(208,577)],'url(#paper)')
poly([(570,672),(611,672),(611,656),(639,656),(639,641),(661,641),(661,624),(678,624),(678,606),(707,606),(707,591),(776,591),(776,606),(796,606),(796,624),(815,624),(815,716),(707,716),(707,700),(570,700)],'url(#paper)')
poly([(570,686),(647,686),(647,672),(677,672),(677,641),(707,641),(707,625),(770,625),(770,656),(790,656),(790,673),(815,673),(815,716),(707,716),(707,701),(570,701)],'#c6dfea')
end()
group('05_Montanas_y_valle')
poly([(208,720),(228,720),(228,702),(254,702),(254,686),(303,686),(303,702),(332,702),(332,729),(373,729),(373,754),(395,754),(395,780),(421,780),(421,805),(445,805),(445,830),(472,830),(472,856),(499,856),(499,883),(529,883),(529,910),(571,910),(571,967),(208,967)],'url(#teal)')
poly([(208,720),(228,720),(228,702),(254,702),(254,686),(276,686),(276,767),(312,767),(312,814),(337,814),(337,839),(371,839),(371,864),(408,864),(408,888),(436,888),(436,913),(478,913),(478,964),(208,964)],'#18778a')
poly([(408,754),(497,754),(497,779),(521,779),(521,801),(545,801),(545,821),(587,821),(587,843),(628,843),(628,866),(662,866),(662,884),(690,884),(690,917),(606,917),(606,941),(538,941),(538,966),(478,966),(478,926),(444,926),(444,901),(419,901),(419,878),(395,878),(395,770),(408,770)],'url(#teal)')
poly([(408,754),(452,754),(452,780),(477,780),(477,821),(488,821),(488,835),(511,835),(511,857),(546,857),(546,880),(608,880),(608,902),(570,902),(570,928),(537,928),(537,949),(506,949),(506,965),(476,965),(476,927),(440,927),(440,903),(419,903),(419,879),(395,879),(395,830),(408,830)],'#16788c')
poly([(815,792),(780,792),(780,804),(754,804),(754,820),(721,820),(721,836),(694,836),(694,851),(666,851),(666,868),(641,868),(641,883),(613,883),(613,899),(585,899),(585,918),(559,918),(559,933),(533,933),(533,949),(506,949),(506,965),(815,965)],'#176d7b')
poly([(208,856),(226,856),(226,839),(302,839),(302,856),(324,856),(324,885),(379,885),(379,919),(405,919),(405,934),(442,934),(442,950),(476,950),(476,965),(606,965),(606,941),(658,941),(658,921),(696,921),(696,936),(719,936),(719,906),(747,906),(747,886),(815,886),(815,1334),(208,1334)],'url(#green)')
poly([(208,856),(226,856),(226,839),(302,839),(302,855),(324,855),(324,885),(379,885),(379,918),(405,918),(405,934),(443,934),(443,950),(476,950),(476,969),(406,969),(406,954),(372,954),(372,938),(332,938),(332,918),(304,918),(304,899),(254,899),(254,871),(208,871)],'url(#hill)')
poly([(208,927),(250,927),(250,950),(292,950),(292,975),(329,975),(329,993),(348,993),(348,1008),(394,1008),(394,1031),(447,1031),(447,1060),(499,1060),(499,1088),(545,1088),(545,1120),(581,1120),(581,1158),(627,1158),(627,1191),(659,1191),(659,1220),(720,1220),(720,1267),(772,1267),(772,1334),(208,1334)],'#22694a',.65)
poly([(815,900),(796,900),(796,950),(782,950),(782,920),(743,920),(743,935),(720,935),(720,950),(687,950),(687,969),(652,969),(652,987),(631,987),(631,976),(605,976),(605,1016),(651,1016),(651,1059),(683,1059),(683,1113),(707,1113),(707,1140),(749,1140),(749,1170),(790,1170),(790,1138),(815,1138)],'#2e7548',.8)
random.seed(1024)
for y in range(981,1325,24):
 for x in range(208,815,24):
  if random.random()<.37:rect(x,y,min(random.choice([24,24,48]),815-x),24,random.choice(['#123d36','#347c4d','#104d42','#558f42']),random.uniform(.12,.28))
end()
group('06_Barra_de_estado')
text('10:00',228,275,36,bold=True)
poly([(688,269),(696,269),(696,262),(704,262),(704,254),(711,254),(711,247),(718,247),(718,276),(688,276)],'#f5fcff')
poly([(735,253),(742,253),(742,247),(749,247),(749,241),(757,241),(757,276),(735,276)],'#f5fcff')
poly([(771,247),(778,247),(778,241),(785,241),(785,247),(792,247),(792,276),(771,276)],'#f5fcff')
end()
group('07_Buscador_Google')
pixelplate(235,322,555,93,'url(#paper)',7)
rect(272,342,31,13,'#ff1514');rect(264,355,13,24,'#ffbf00');rect(264,355,13,10,'#ff9b0b');rect(264,379,13,7,'#21b855');rect(272,386,31,11,'#00b842');rect(279,377,24,10,'#08be50');rect(288,364,24,13,'#137ff1');rect(301,375,11,12,'#1979e1')
rect(734,347,14,30,'url(#blue)');rect(720,369,8,11,'#ffb400');rect(727,378,8,9,'#ffb000');rect(734,386,15,10,'#ffb000');rect(748,370,13,9,'#f12822');rect(741,379,13,8,'#f12822');rect(732,348,2,27,'#77bdff')
end()
group('08_Aplicaciones')
group('Play_Store')
pixelplate(240,993,97,97,'url(#paper)',7)
matrix=['BG......','BBGG....','BBBGGY..','BBBBGYY.','BBBBYYYY','BBBBRRR.','BBBRRR..','BBRR....','BR......'];colors={'B':'#08a7f1','G':'#06bd53','Y':'#ffd13b','R':'#f3292e'}
for j,row in enumerate(matrix):
 for i,c in enumerate(row):
  if c!='.':rect(264+i*7,1009+j*7,7,7,colors[c])
end()
group('Chrome')
parts.append('<g clip-path="url(#chromeclip)">');rect(389,993,98,98,'#02bb60')
poly([(389,993),(487,993),(487,1022),(422,1022),(414,1036),(402,1036),(402,1029),(395,1029),(395,1022),(389,1022)],'#ff483b')
poly([(439,1022),(487,1022),(487,1091),(437,1091),(437,1062),(450,1062),(450,1036)],'#ffcf3b')
rect(415,1022,44,43,'#fffdf2');rect(423,1029,29,29,'url(#blue)');rect(423,1029,7,29,'#2496f7');parts.append('</g>')
end()
group('Ajustes')
pixelplate(537,993,97,97,'url(#blue)',7)
poly([(575,1009),(596,1009),(596,1019),(605,1019),(605,1027),(615,1027),(615,1048),(607,1048),(607,1058),(596,1058),(596,1074),(575,1074),(575,1064),(565,1064),(565,1054),(556,1054),(556,1027),(565,1027),(565,1019),(575,1019)],'#f9fcf6')
rect(575,1030,21,23,'#1389f4');rect(579,1026,13,7,'#1389f4');rect(579,1051,13,7,'#1389f4')
end()
group('YouTube')
pixelplate(688,993,97,97,'url(#paper)',7)
pixelplate(703,1016,67,52,'#ff3038',6)
poly([(725,1030),(733,1030),(733,1037),(741,1037),(741,1047),(733,1047),(733,1054),(725,1054)],'#fffdf4')
end()
text('Play Store',288,1123,26,center=True);text('Chrome',438,1123,26,center=True);text('Ajustes',586,1123,26,center=True);text('YouTube',737,1123,26,center=True)
end()
group('09_Indicadores_de_pagina')
rect(471,1162,15,15,'#f0faf6');rect(504,1162,15,15,'#91b7aa');rect(537,1162,15,15,'#91b7aa')
end()
group('10_Dock_inferior')
group('Telefono')
pixelplate(233,1207,93,96,'url(#phonegreen)',7)
for j,row in enumerate(['WW.....','WW.....','WW.....','WW.....','WWW....','.WWW...','..WWWW.','...WWWW','....WWW']):
 for i,c in enumerate(row):
  if c=='W':rect(254+i*7,1224+j*7,7,7,'#f5fff4')
end()
group('Mensajes')
pixelplate(349,1207,94,96,'url(#blue)',7);rect(370,1231,50,43,'#f6fcfc');rect(388,1274,7,13,'#f6fcfc');rect(379,1242,32,19,'#a9cbd8');rect(382,1245,26,9,'#91b4c4');end()
group('Cajon_de_aplicaciones')
pixelplate(469,1214,87,84,'url(#paper)',6)
for j in range(2):
 for i in range(3):rect(487+i*20,1236+j*26,11,12,'#24574b')
end()
group('Camara')
pixelplate(584,1207,93,96,'url(#paper)',7)
poly([(615,1227),(646,1227),(646,1237),(656,1237),(656,1273),(646,1273),(646,1283),(615,1283),(615,1273),(604,1273),(604,1237),(615,1237)],'#111418');rect(623,1248,14,15,'#0b87e4');rect(623,1248,7,7,'#2b9aef');end()
group('Fotos')
pixelplate(700,1207,92,96,'url(#paper)',7);rect(742,1221,19,40,'#ff160d');rect(712,1245,40,17,'#ffc400');rect(731,1261,18,31,'#04c454');rect(749,1254,30,19,'#057bf1');rect(732,1244,10,10,'#ff9b00');rect(742,1262,9,9,'#2da54a');end()
end()
parts.append('</g>')
group('11_Navegacion_Android')
poly([(342,1360),(350,1360),(350,1398),(342,1398),(342,1391),(334,1391),(334,1386),(328,1386),(328,1381),(321,1381),(321,1375),(328,1375),(328,1370),(335,1370),(335,1365),(342,1365)],'#d2d3d5')
rect(500,1360,25,7,'#c5c7c8');rect(493,1367,7,24,'#c5c7c8');rect(525,1367,7,24,'#c5c7c8');rect(500,1391,25,7,'#c5c7c8');rect(674,1364,30,30,'#c8c9ca')
end()
svg='<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="1024" height="1536" viewBox="0 0 1024 1536">'+defs+'\n'.join(parts)+'</svg>'
(OUT/'Telefono_Pixel_Recreado.svg').write_text(svg,encoding='utf-8')
(OUT/'capas.json').write_text(json.dumps({'canvas':[1024,1536],'groups':groups,'vector_shapes':svg.count('<rect')+svg.count('<polygon')+svg.count('<path'),'embedded_images':0},indent=2),encoding='utf-8')
print(OUT/'Telefono_Pixel_Recreado.svg')
