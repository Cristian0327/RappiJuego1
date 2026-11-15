import json
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');j=json.loads((r/'work/ServicesFinalRegressionQA/Saved/npc_developer_validation.json').read_text());checks=[(x['id'],x['passed']) for x in j['checks']]
for group in ['vehicle_dynamics','dynamic_weather']:checks.extend((group+'/'+k,v) for k,v in j[group]['checks'].items())
assert len(checks)==65 and all(v for _,v in checks),checks
log=(r/'work/ServicesFinalRegressionQA.log').read_text(errors='replace');assert 'Failed to compile Material' not in log and 'LogBlueprint: Error' not in log
p=r/'RappiJuego1/Docs/validacion_servicios_y_animaciones_blueprints.json';a=json.loads(p.read_text());a['final_regression']={'profile':'ServicesFinalRegressionQA','checks_passed':65,'temporary_test_assets_removed':True,'material_compile_errors':0};p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8');print('FINAL_SERVICES_REGRESSION_PASS 65/65')
