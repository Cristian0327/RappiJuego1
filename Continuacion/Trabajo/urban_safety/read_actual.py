import json,collections
from pathlib import Path
rows=json.loads(Path('urban_safety/actual_instances.json').read_text())
for r in rows:
 if r['actor']=='BP_BogotaUrbanDressing_C':print(r['component'],r['mesh'].split('/')[-1],len(r['transforms']))
