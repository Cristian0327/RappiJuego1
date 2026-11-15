from pathlib import Path
from collections import Counter
import sys,json,re,math
p=Path(sys.argv[1]);rows=[]
for line in p.read_text(errors='replace').splitlines():
 if 'V2MOTIONSTATE|' not in line:continue
 x=line.split('V2MOTIONSTATE|')[1].split('|')
 if len(x)<17:continue
 v=[float(q) for q in re.findall(r'[XYZ]=([-+\d.]+)',x[15])]
 rows.append(dict(time=float(x[0]),name=x[1],mode=x[2],default_mode=x[3],maximum=float(x[4]),step=float(x[10]),class_name=x[13],components=int(x[14]),speed=math.hypot(*v[:2])))
counts=Counter(r['mode'] for r in rows);result=dict(samples=len(rows),last_time=max([r['time'] for r in rows],default=0),modes=dict(counts),grounded_fraction=counts['1']/max(len(rows),1),unsafe_overspeed=[r for r in rows if r['speed']>r['maximum']*1.35+20][-10:],falling_examples=[r for r in rows if r['mode']=='3'][-8:])
p.with_name(p.stem+'_motion_state.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
