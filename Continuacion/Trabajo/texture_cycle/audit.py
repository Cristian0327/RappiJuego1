import unreal,json,sys
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/texture_cycle');root=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');AS=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in AS.get_all_level_actors():
 if a.get_class().get_name() not in ['BP_MapaCompletoGeometry_C','BP_CallesSecundarias_C','BP_BogotaUrbanDressing_C']:continue
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  mesh=c.get_editor_property('static_mesh')
  if mesh:rows.append(dict(actor=a.get_class().get_name(),component=c.get_name(),mesh=mesh.get_path_name(),materials=[m.get_path_name() if m else None for m in c.get_materials()]))
(P/'used_map_materials.json').write_text(json.dumps(rows,indent=2));data=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/World',recursive=True):
 if 'BP_Traffic_' not in path and not any(s in path for s in ['BP_Police','BP_CivilMotorcycle']):continue
 bp=unreal.load_asset(path)
 if not isinstance(bp,unreal.Blueprint):continue
 cdo=unreal.get_default_object(bp.generated_class());rec=dict(asset=path,components=[])
 for c in cdo.get_components_by_class(unreal.MeshComponent):rec['components'].append(dict(name=c.get_name(),materials=[m.get_path_name() if m else None for m in c.get_materials()]))
 data.append(rec)
(P/'vehicle_material_templates.json').write_text(json.dumps(data,indent=2));unreal.log('TEXTURE_DEPENDENCIES_AUDITED')
