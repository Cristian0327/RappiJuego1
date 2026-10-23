import unreal,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');assert 'isolated_repair' in Path(unreal.Paths.project_dir()).parts
S=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem) or unreal.new_object(unreal.StaticMeshEditorSubsystem);m=json.loads((P/'manifest.json').read_text());by_source={r['source']:r for r in m['instances']};rows=[]
for v in json.loads((P/'frontage_variants.json').read_text()):
 source=by_source[v['source']];old=unreal.load_asset('/Game/Maps/MapaCompleto/Geometry/'+source['mesh']);mesh=unreal.load_asset('/Game/World/BogotaUrban/StreetFrontages/'+v['name']);a=old.get_bounds();b=mesh.get_bounds();original_top=a.origin.z+a.box_extent.z;new_top=b.origin.z+b.box_extent.z;ratio=original_top/new_top if new_top>0 else 1;unreal.log('V2_UNIT_MEASURE '+v['name']+' old='+str(original_top)+' new='+str(new_top)+' ratio='+str(ratio));settings=S.get_lod_build_settings(mesh,0);before=settings.build_scale3d
 if ratio>50:
  settings.set_editor_property('build_scale3d',unreal.Vector(before.x*100,before.y*100,before.z*100));S.set_lod_build_settings(mesh,0,settings);unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);b=mesh.get_bounds();new_top=b.origin.z+b.box_extent.z
 rows.append(dict(asset=v['name'],source=source['mesh'],original_top=original_top,top=new_top,old_scale=list(before.to_tuple()),ratio_before=ratio));unreal.log('V2_FRONTAGE_SCALE '+v['name']+' ratio='+str(ratio)+' top='+str(new_top))
(P/'frontage_unit_audit.json').write_text(json.dumps(rows,indent=2));unreal.log('V2_FRONTAGE_UNITS_VERIFIED '+str(len(rows)))
