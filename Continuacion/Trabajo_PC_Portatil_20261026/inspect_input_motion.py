import json,re,math,sys
from pathlib import Path
r=Path(__file__).parent;p=Path(sys.argv[1]) if len(sys.argv)>1 else r/'traffic_input_v17.log'
rows={};inputs={}
def vec(s):return [float(v) for v in re.findall(r'[XYZ]=([-+\d.]+)',s)]
for line in p.read_text(errors='replace').splitlines():
 if 'V2ROADDETAIL|' in line:
  x=line.split('V2ROADDETAIL|')[1].split('|');rows[(x[0],x[1])]=dict(t=float(x[0]),name=x[1],goal=vec(x[3]),pos=vec(x[5]),vel=vec(x[6]),index=x[2],actual_limit=float(x[4]))
 if 'V2INPUT|' in line:
  x=line.split('V2INPUT|')[1].split('|');inputs[(x[0],x[1])]=dict(dt=float(x[4]),command=vec(x[5]),before=vec(x[7]),limit=float(x[8]),scale=float(x[9]))
cases=[]
for key,row in rows.items():
 if key not in inputs:continue
 row.update(inputs[key]);delta=[row['pos'][i]-row['before'][i] for i in range(2)]
 expected=row['limit']*row['dt'];travel=math.hypot(*delta)
 cross=abs(delta[0]*row['command'][1]-delta[1]*row['command'][0]);speed=math.hypot(*row['vel'][:2])
 if cross>25 or travel>expected+30:
  row.update(travel=travel,expected=expected,cross=cross,speed=speed);cases.append(row)
cases.sort(key=lambda x:x['cross'],reverse=True)
p.with_name(p.stem+'_motion_cases.json').write_text(json.dumps(cases,indent=2));print(json.dumps(cases[:6],indent=2))
