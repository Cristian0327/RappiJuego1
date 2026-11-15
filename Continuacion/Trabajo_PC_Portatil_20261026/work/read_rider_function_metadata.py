import json
from pathlib import Path
j=json.loads(Path('work/pure_rider_foundation.json').read_text());g=next(g for g in j['audit']['graphs'] if g['name']=='AdvanceDriveSpeed');print(json.dumps({k:v for k,v in g.items() if k!='pins'},indent=2));print('\n'.join(g.get('pins',[])[:7]))
