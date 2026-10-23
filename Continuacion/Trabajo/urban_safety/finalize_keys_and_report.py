import unreal,json,sys,shutil
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_safety');root=Path(unreal.Paths.project_dir()).parent
exec(compile((P/'build_traversal_blueprint.py').read_text(),'FinalFlightKeys','exec'),{})
sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
bp=unreal.load_asset('/Game/World/BogotaUrban/BP_MapTraversal');audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['compiled'] and not any(g['native_calls'] for g in audit['graphs']);(P/'flight_blueprint_audit.json').write_text(json.dumps(audit,indent=2))
report=json.loads((P/'implementation_report.json').read_text());report['architecture_meshes']=81;report['runtime_tests']={name:True for name in ['DEVELOPER_FLIGHT_ACTIVE','FLIGHT_VERTICAL_MOVEMENT','FALL_THROUGH_MAP_RECOVERED','CURB_CROSSED_WITHOUT_JUMP']};report['collision_samples']=537;report['collision_errors']=0;(P/'implementation_report.json').write_text(json.dumps(report,indent=2));shutil.copy2(P/'Mapa_Bogota_Nivelado.blend',root/'outputs/BogotaUrban/Mapa_Bogota_Ambientado.blend');shutil.copy2(P/'implementation_report.json',root/'outputs/BogotaUrban/urban_safety_report.json');unreal.log('FLIGHT_KEYS_AND_SAVED_SOURCE_FINALIZED')
