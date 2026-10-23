import unreal,json
from pathlib import Path
out={};m=unreal.load_asset('/Game/Maps/MapaCompleto/Geometry/SM_Mapa_067');desc=m.get_static_mesh_description(0);out['description_api']=[x for x in dir(desc) if 'color' in x.lower() or 'vertex_instance' in x.lower()]
for name,path in [('citizen','/Game/World/BlueprintWorld/Crowd/BP_StreetCitizen'),('crowd','/Game/World/BlueprintWorld/Crowd/BP_CrowdManager'),('phone','/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone')]:out[name]=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(unreal.load_asset(path)))
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/deep_runtime_audit.json').write_text(json.dumps(out,indent=2));unreal.log('DEEP_AUDIT_READY')

