from pathlib import Path
import re,json,math,sys
p=Path(sys.argv[1]);records=[]
def vec(s):return [float(v) for v in re.findall(r'[XYZ]=([-+\d.]+)',s)]
for line in p.read_text(errors='replace').splitlines():
 if 'V2INPUT|' not in line:continue
 x=line.split('V2INPUT|')[1].split('|')
 if len(x)<11:continue
 t,name=x[:2];last,accel,command,goal,pos=map(vec,[x[2],x[3],x[5],x[6],x[7]])
 if any(len(v)<2 for v in [last,accel,command,goal,pos]):continue
 delta=[goal[i]-pos[i] for i in range(2)];length=math.hypot(*delta)
 dot=lambda v:sum(v[i]*delta[i]/max(length,.001) for i in range(2))
 records.append(dict(t=float(t),name=name,dt=float(x[4]),command_dot_goal=dot(command),last_dot_goal=dot(last),accel_dot_goal=dot(accel),command=command,last=last,accel=accel,goal=goal,pos=pos,limit=float(x[8]),scale=float(x[9]),index=x[10]))
report=dict(samples=len(records),last_time=max([r['t'] for r in records],default=0),max_delta_seconds=max([r['dt'] for r in records],default=0),bad_command=[r for r in records if r['scale']>.1 and r['command_dot_goal']<.9][-12:],bad_consumed_input=[r for r in records if r['scale']>.1 and r['last_dot_goal']<.9][-12:],latest=records[-24:])
p.with_name(p.stem+'_input.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
