from pathlib import Path
import json,re
r=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto')
log=(r/'work/PurePhoneIntegratedQA.log').read_text(encoding='utf-8',errors='replace')
checks=dict(re.findall(r'PURE_PHONE_RUNTIME (\w+)=(true|false)',log))
assert len(checks)==12 and all(v=='true' for v in checks.values()),checks
warnings=[x for x in log.splitlines() if 'LogScript: Warning:' in x or 'LogBlueprint: Error:' in x]
assert not warnings,warnings[:5]
(r/'work/pure_phone_integrated_runtime_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'script_warnings':warnings,'visual_review':['Phone proportions maintained','Upgrade labels now fit','Map background overlay issue found; source correction pending rebuild','Garage live preview integration in progress'],'main_project_promoted':False},indent=2))
p=r/'work/ACTIVE_TASK_STATE.json';j=json.loads(p.read_text(encoding='utf-8-sig'));j['phone_continuation_2026_10_17']={'map_compiled':True,'map_visual_issue':'Oversized thick-line background removed in source; rebuild and visual retest pending','rider_phone_input_edges':12,'rider_HUD_bootstrap_saved':True,'combined_authoring_process':'Crashed during redundant animation guard recompile after frame save; run fresh processes','runtime_report':'work/pure_phone_integrated_runtime_validation.json','runtime_checks_passed':12,'garage_geometry_components':116,'garage_render_functions_compiled':True,'garage_phone_integration':'In progress','main_promoted':False};p.write_text(json.dumps(j,indent=2))
print('PHONE_RUNTIME_REPORT_SAVED checks=12')
