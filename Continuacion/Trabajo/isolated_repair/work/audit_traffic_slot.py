import unreal,json
from pathlib import Path
r={}
for n in ['Private','PrivateBeetle','TaxiCompact','TransMilenio']:
 m=unreal.load_asset('/Game/Traffic/Detailed/SK_'+n)
 r[n]=[{'slot':str(s.material_slot_name),'material':str(s.material_interface)} for s in m.get_editor_property('materials')]
Path(__file__).resolve().parent.joinpath('traffic_slot_audit.json').write_text(json.dumps(r))
