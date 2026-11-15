import unreal,json
from pathlib import Path
b=unreal.load_asset('/Game/World/BogotaUrban/BP_BogotaServiceSignals');data=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(b));g=next(g for g in data['graphs'] if g['name']=='EnsureServiceProxies')
Path(unreal.Paths.project_dir()).resolve().parent.joinpath('ground_cast_pins.json').write_text(json.dumps([p for p in g['pins'] if 'DynamicCast' in p],indent=2))
