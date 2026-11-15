from pathlib import Path
from collections import Counter
import sys,json
p=Path(sys.argv[1]);hits=[];states=[];guards=[]
for line in p.read_text(errors='replace').splitlines():
 if 'V2CONTACT|' in line:
  x=line.split('V2CONTACT|')[1].split('|');hits.append(dict(time=float(x[0]),actor=x[1],other=x[2],component=x[3],position=x[4],normal=x[5]))
 if 'V2INPUT|' in line:
  x=line.split('V2INPUT|')[1].split('|')
  if len(x)>=16:states.append(dict(time=float(x[0]),actor=x[1],rvo=x[11],friction=x[12],controller=x[13],ai_status=x[14],root_motion=x[15]))
 if 'V2GUARD|' in line:
  x=line.split('V2GUARD|')[1].split('|');guards.append(dict(time=float(x[0]),actor=x[1],other=x[2],component=x[3],position=x[4]))
report=dict(contact_count=len(hits),obstacles=Counter(h['other']+' / '+h['component'] for h in hits).most_common(20),examples=hits[:15],guard_stops=len(guards),guard_obstacles=Counter(h['other']+' / '+h['component'] for h in guards).most_common(20),guard_examples=guards[:15],runtime_settings=states[-24:])
p.with_name(p.stem+'_contacts.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
