import bpy
from pathlib import Path
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh')
for o in bpy.data.objects:
 if o.type=='CURVE':o.hide_set(True);o.hide_render=True
bpy.context.scene['SecondaryStreetNetwork']='14 calles conectadas; 28 extremos sobre las vías principales'
bpy.context.scene['TransitStations']=7
bpy.context.scene['AdditionalNeighborhoodBuildings']=24
bpy.ops.wm.save_as_mainfile(filepath=str(U/'Mapa_Bogota_Ambientado.blend'));print('FINAL_BLENDER_SOURCE_READY')
