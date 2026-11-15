import json,math
from pathlib import Path
p=Path(__file__).parent/'live_snapshot.json'
if not p.exists():
    print('Awaiting PIE snapshot');raise SystemExit()
data=json.loads(p.read_text());rows=[]
for r in data['services']:
    if 'goal' not in r:continue
    d=[r['goal'][i]-r['position'][i] for i in range(2)]
    norm=math.hypot(*d);direction=[v/max(norm,.001) for v in d]
    speed=math.hypot(*r['velocity'][:2]);inp=r['last_input'][:2]
    align=sum(direction[i]*inp[i] for i in range(2))
    along=sum(direction[i]*r['velocity'][i] for i in range(2))
    rows.append(dict(name=r['name'],speed=round(speed,1),goal_distance=round(norm,1),input_dot_goal=round(align,3),velocity_toward_goal=round(along,1),input=inp,accel=r['acceleration'],rvo=r['use_rvo_avoidance'],friction=r['ground_friction'],limit=r['max_walk_speed'],tick_before_owner=r['tick_before_owner']))
print(json.dumps(dict(world=data['world'],wall_time=data['wall_time'],services=rows),indent=2))
