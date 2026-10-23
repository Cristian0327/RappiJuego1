from pathlib import Path
import json,re,csv,statistics,shutil
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');log=r/'work/VehicleUsabilityFinalWindowed.log';s=log.read_text(encoding='utf-8',errors='replace');flags=re.findall(r'(?:BOTH_SIDE_MOUNT |TRANSIT_)([A-Z_a-z0-9]+)=(true|false)',s);bad=[n for n,v in flags if v=='false'];assert len(flags)>=30 and not bad,(len(flags),bad)
assert 'Accessed None' not in s
csv.field_size_limit(16000000);p=max((r/'work/RequestedFixesIsolated6/Saved/Profiling/CSV').glob('*.csv'),key=lambda x:x.stat().st_mtime);rows=list(csv.reader(p.open()));stats={}
for h in ['FrameTime','GameThreadTime','GPUTime','DynamicResolutionPercentage']:
 if h not in rows[0]:continue
 i=rows[0].index(h);values=[]
 for row in rows[-200:-2]:
  try:values.append(float(row[i]))
  except:pass
 if values:stats[h]=round(statistics.mean(values),3)
if stats.get('FrameTime'):stats['average_fps_equivalent']=round(1000/stats['FrameTime'],1)
report={'date':'2026-10-20','status':'PASS','vm_checks':10,'runtime_checks':len(flags),'runtime_failures':bad,'dismount':'Both sides use a .85s smoothstep transition across its whole duration; entry stays .68s','animation':'Hero pose updates every frame without update-rate skipping','camera':'Post-physics boom, road movement prerequisite, 650cm arm and170cm height','taxi':'20s hail timeout plus12s idle cooldown; approaching taxi progresses before braking near pickup;20s pickup recovery','road_motorcycles':'4 authored NPC motorcyclists use road mode, Walking, zero curb step and no RVO sidewalk push','parked_bike':'Pawn-channel query body enabled only when parked; actual traffic detection/release passed','stations':'16 waiting slots spaced160cm; one doorway owner per bus; original collision restored after proxy; no reboarding same bus','rendering':'FXAA and60FPS adaptive GPU budget,60-100percent primary resolution; full resolution UI; original rigid traffic geometry retained within150m draw range','profiling_windowed_1080p':stats,'fps_scope':'Measured QA session only, no guarantee of60FPS on all machines or every map condition','runtime_cpp_added':False,'github_changed':False,'evidence':['work/vehicle_usability_vm.json','work/VehicleUsabilityFinalWindowed.log',str(p.relative_to(r))]}
(r/'work/vehicle_usability_final.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
statep=r/'work/ACTIVE_TASK_STATE.json';j=json.loads(statep.read_text(encoding='utf-8-sig'));j['latest_vehicle_usability_20261020']=report;statep.write_text(json.dumps(j,indent=2,ensure_ascii=False))
for name in ['fix_vehicle_usability.py','fix_station_motorcycle_spacing.py','verify_vehicle_usability.py','build_smooth_vehicle_runtime_qa.py','apply_voxel_frame_budget.py','build_final_usability_checks.py']:
 shutil.copy2(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho')/name,r/'work'/name)
print(json.dumps({'runtime_checks':len(flags),'profile':stats},ensure_ascii=False))
