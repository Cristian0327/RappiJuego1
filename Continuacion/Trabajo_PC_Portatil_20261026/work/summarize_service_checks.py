import json,re
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');j=json.loads((r/'work/ServicesRegressionQA/Saved/npc_developer_validation.json').read_text());checks=[(x['id'],x['passed']) for x in j['checks']]
for group in ['vehicle_dynamics','dynamic_weather']:checks.extend((group+'/'+k,v) for k,v in j[group]['checks'].items())
print(json.dumps({'checks':len(checks),'failures':[n for n,v in checks if not v],'pedestrians':j['pedestrians']},indent=2))
log=(r/'work/PureNpcAnimationQA.log').read_text(errors='replace');samples=re.findall(r'PURE_NPC_RUNTIME (\w+) (walking|idle)=(true|false)',log);print('NPC samples',len(samples),'failures',[x for x in samples if x[2]!='true']);print(re.findall(r'POLICE_BLUEPRINT_QA[^\n]+',log))
