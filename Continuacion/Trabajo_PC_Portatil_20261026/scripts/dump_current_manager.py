import unreal,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficManager')
(root/'current_manager_audit.json').write_text(unreal.DeliveryEditorLibrary.audit_blueprint(bp))
cdo=unreal.get_default_object(bp.generated_class())
(root/'current_junction_centers.json').write_text(json.dumps([list(v.to_tuple()) for v in cdo.get_editor_property('JunctionCentres')]))
