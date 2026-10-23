import bpy,json,math
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_safety');moved=0
for row in json.loads((P/'furniture_relocations.json').read_text()):
 mesh=row['mesh'].split('/')[-1].split('.')[0];targets=[mesh]+(['SM_Bogota_FarolaLuz'] if mesh=='SM_Bogota_Farola' else [])
 for name in targets:
  for ob in bpy.data.objects:
   if not ob.name.startswith(name) or math.hypot(ob.location.x*100-row['old'][0],-ob.location.y*100-row['old'][1])>20:continue
   ob.location=(row['new'][0]/100,-row['new'][1]/100,row['new'][2]/100);moved+=1
bpy.context.scene['UrbanFurnitureRoadClearance']='Actual footprint outside carriageway';bpy.ops.wm.save_as_mainfile(filepath=str(P/'Mapa_Bogota_Nivelado.blend'));print('FURNITURE_SOURCE_SYNCHRONIZED',moved)
