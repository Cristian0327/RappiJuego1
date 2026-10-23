import unreal,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');report=[]
for i in range(7):
 b=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i));c=unreal.get_default_object(b.generated_class());report.append(dict(lane=i,group=c.get_editor_property('RouteGroup'),events=len(c.get_editor_property('ArcEntries'))))
models=json.loads((P.parent/'isolated_repair/work/pure_traffic_vehicle_foundation.json').read_text())['models'];sizes=[]
for row in models:
 path=row.get('asset') or row.get('blueprint')
 if not path:continue
 b=unreal.load_asset(path);c=unreal.get_default_object(b.generated_class());sizes.append(dict(path=path,halfLength=c.get_editor_property('HalfLength'),halfWidth=c.get_editor_property('HalfWidth'),expected=row['half_length']))
(P/'traffic_defaults_now.json').write_text(json.dumps(dict(lanes=report,models=sizes),indent=2));unreal.log('V2_ACTUAL_LANE_GROUPS '+str(report))
