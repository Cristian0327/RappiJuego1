import json,math
from pathlib import Path
P=Path(__file__).resolve().parent;a=json.loads((P/'actors.json').read_text());s=next(x for x in a if x['name']=='BP_BogotaTransmiStation_C_4');angle=math.radians(s['rotation'][1]);delta=[-4500*math.cos(angle),-4500*math.sin(angle),0];old=s['position'][:];s['position']=[v+d for v,d in zip(old,delta)];(P/'station_move.json').write_text(json.dumps(dict(actor=s['name'],old=old,new=s['position'],yaw=s['rotation'][1],delta=delta,id=4),indent=2));(P/'actors_final.json').write_text(json.dumps(a));print('STATION_CLEAR_OF_NEW_STREET_AND_BUS_SWEEP',delta)
