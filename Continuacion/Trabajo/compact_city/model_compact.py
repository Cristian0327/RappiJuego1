import bpy,json,math
from pathlib import Path
from mathutils import Vector,Euler,Matrix
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');C=R/'compact_city';O=R/'urban_refresh';m=json.loads((R/'new_map_audit/manifest.json').read_text())
for row in m['instances']:
 obj=bpy.data.objects.get(row['source'])
 if not obj or row['source'].startswith('SM_Mapa_Road_'):continue
 rot=Euler([math.radians(v) for v in row['rotation']],'XYZ');obj.matrix_world=Matrix.LocRotScale(Vector(row['location']),rot.to_quaternion(),Vector(row['scale']))
# Preserve the warm urban ground and green mountains at their original proportions.
s=(R/'pave_city_blender.py').read_text();s=s[:s.index('bpy.ops.wm.save_as_mainfile')];exec(compile(s,'OriginalSizedUrbanPaving','exec'),globals())
for mod in next(o for o in bpy.data.objects if o.name.startswith('Relieve')).modifiers:mod.show_viewport=False;mod.show_render=False
s=(O/'build_connected_map_blender.py').read_text();s=s[:s.index('keep=[]')];exec(compile(s,'CompactConnectedRoadMeshes','exec'),globals())
exec(compile((O/'assemble_blender_map.py').read_text(),'CompactVoxelFurniture','exec'),globals())
exec(compile((R/'urban_corrections/model_access_and_markings.py').read_text(),'CompactStationsAndSignals','exec'),globals())
bpy.context.scene['CitySpacingExpansion']=1.;bpy.context.scene['OriginalBuildingCount']=909;bpy.context.scene['LocalBuildingAdjustments']=len(json.loads((C/'local_building_adjustments.json').read_text()));bpy.ops.wm.save_as_mainfile(filepath=str(O/'Mapa_Bogota_Ambientado.blend'));print('ORIGINAL_PROPORTIONS_BLEND_READY')
