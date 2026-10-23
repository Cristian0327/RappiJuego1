from PIL import Image
import json
from pathlib import Path
root=Path.cwd(); out=root/'outputs/Illustrator/Telefono_Pixel'; out.mkdir(parents=True,exist_ok=True)
im=Image.open('C:/Users/CRISTIAN/AppData/Local/Temp/codex-clipboard-0b762a34-adba-4611-b94b-a705d05d7be0.png').convert('RGBA').resize((256,384),Image.Resampling.NEAREST)
names=['01 Botones laterales','02 Carcasa y biseles','03 Altavoz y camara','04 Cielo','05 Paisaje','06 Estado','07 Buscador','08 Aplicaciones y textos','09 Indicadores','10 Dock','11 Navegacion']
cells=[]
for y in range(384):
 for x in range(256):
  r,g,b,a=im.getpixel((x,y)); X=x*4;Y=y*4
  if a<128:continue
  layer=1
  if X>=864:layer=0
  elif Y<224:layer=2 if 408<=X<=704 and Y>=152 else 1
  elif Y>=1336:layer=10 if 312<=X<=712 and Y<1408 else 1
  elif 208<=X<816:
   layer=3 if Y<688 else 4
   if Y<296:layer=5
   elif 232<=X<792 and 320<=Y<416:layer=6
   elif 984<=Y<1136:layer=7
   elif 1152<=Y<1184:layer=8
   elif 1200<=Y<1312:layer=9
  cells.append([x,y,r,g,b,layer])
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1536" viewBox="0 0 1024 1536" shape-rendering="crispEdges">']
for n,name in enumerate(names):
 svg.append('<g id="'+name.replace(' ','_')+'">')
 for x,y,r,g,b,l in cells:
  if l==n:svg.append(f'<rect x="{x*4}" y="{y*4}" width="4" height="4" fill="#{r:02x}{g:02x}{b:02x}"/>')
 svg.append('</g>')
svg.append('</svg>');(out/'Telefono_Pixel_Final.svg').write_text('\n'.join(svg),encoding='utf-8')
script='''var prev=app.userInteractionLevel;
try {
app.userInteractionLevel=UserInteractionLevel.DONTDISPLAYALERTS;
var doc=app.documents.add(DocumentColorSpace.RGB,1024,1536);
var original=doc.layers[0]; var names=NAMES;var cells=CELLS;var layers=[];
for(var i=0;i<names.length;i++){layers.push(doc.layers.add());layers[i].name=names[i];}
original.remove();var top=doc.artboards[0].artboardRect[1];
for(var i=0;i<cells.length;i++){var p=cells[i];var q=layers[p[5]].pathItems.rectangle(top-p[1]*4,p[0]*4,4,4);q.stroked=false;q.filled=true;var c=new RGBColor();c.red=p[2];c.green=p[3];c.blue=p[4];q.fillColor=c;}
var bad=0;for(var i=0;i<doc.pathItems.length;i++){var p=doc.pathItems[i];if(Math.abs(p.width-4)>0.001||Math.abs(p.height-4)>0.001)bad++;}
var opts=new IllustratorSaveOptions();opts.pdfCompatible=true;opts.compressed=true;doc.saveAs(new File(OUT+'/Telefono_Pixel_Final.ai'),opts);
var png=new ExportOptionsPNG24();png.transparency=true;png.artBoardClipping=true;png.antiAliasing=false;png.horizontalScale=100;png.verticalScale=100;doc.exportFile(new File(OUT+'/Telefono_Pixel_Final.png'),ExportType.PNG24,png);
var f=new File(OUT+'/verificacion_reticula.txt');f.open('w');f.writeln('Cuadricula: 4 x 4 px');f.writeln('Cuadrados vectoriales: '+doc.pathItems.length);f.writeln('Pixeles de dimensiones incorrectas: '+bad);f.writeln('Imagenes raster: '+doc.rasterItems.length);f.writeln('Imagenes enlazadas: '+doc.placedItems.length);f.writeln('Capas: '+doc.layers.length);f.close();doc.selection=null;doc.save();doc.activate();
}finally{app.userInteractionLevel=prev;}
'''.replace('NAMES',json.dumps(names)).replace('CELLS',json.dumps(cells,separators=(',',':'))).replace('OUT',json.dumps(str(out).replace('\\','/')))
(root/'work/create_grid_phone.jsx').write_text(script,encoding='utf-8')
print('Prepared',len(cells),'uniform vector squares')
