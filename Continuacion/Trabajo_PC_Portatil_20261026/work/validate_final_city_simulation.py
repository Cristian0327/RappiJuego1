from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
for name in ['validate_city_repairs.py','validate_colombia_traffic_detailed.py']:
 p=root/'work'/name
 exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
traffic=json.loads((root/'outputs/DeliveryArt/TrafficDetailed/traffic_validation.json').read_text())
if traffic['status']=='PASS':
 sim=traffic['simulation']
 if sim['moving_render_frames']<118 or sim['hitch_time_loss_cm']>30.1:traffic['status']='FAIL';traffic['error']='Traffic render cadence or lost time regression'
 (root/'outputs/DeliveryArt/TrafficDetailed/traffic_validation.json').write_text(json.dumps(traffic,indent=2))
