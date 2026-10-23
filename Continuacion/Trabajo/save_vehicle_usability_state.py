from pathlib import Path
import json,shutil
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');w=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho')
for name in ['guard_motorcycles_road.py','restore_uncontended_visual_quality.py','fix_vehicle_usability.py','fix_station_motorcycle_spacing.py','build_smooth_vehicle_runtime_qa.py']:
 shutil.copy2(w/name,r/'work'/name)
p=r/'work/vehicle_usability_final.json';j=json.loads(p.read_text());j['evidence'].append('work/motorcycle_road_guard_validation.json');p.write_text(json.dumps(j,ensure_ascii=False,indent=2));statep=r/'work/ACTIVE_TASK_STATE.json';st=json.loads(statep.read_text(encoding='utf-8-sig'));st['latest_vehicle_usability_20261020']=j;statep.write_text(json.dumps(st,ensure_ascii=False,indent=2));print('FUNCTIONAL_FIXES_SAVED_43_CHECKS')
