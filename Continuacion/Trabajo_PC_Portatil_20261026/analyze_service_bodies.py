"""Conservative sampled body envelopes, including real service characters."""
import json, math, re, sys
from pathlib import Path

root = Path(__file__).resolve().parent
source = root.parent / 'BogotaVoxel/Continuacion/Trabajo'
defaults = json.loads((source / 'map_adaptation_v2/defaults.json').read_text())['/Game/World/BlueprintWorld/Traffic/BP_TrafficManager']
models = json.loads((root / 'work/pure_traffic_vehicle_foundation.json').read_text())['models']
selection = [int(i * 140 / 80) for i in range(80)] + list(range(140, 150))
indices = [defaults['ModelIndices'][i] for i in selection]
path = Path(sys.argv[1]); frames = {}; states = {}; reverse = []; count = 0
def vec(value):
    return [float(x) for x in re.findall(r'[XYZ]=([-+\d.]+)', value)]
def dot(a, b): return a[0]*b[0] + a[1]*b[1]
for line in path.read_text(errors='replace').splitlines():
    if 'V2CAR|' in line:
        t, index, _, _, position, yaw = line.split('V2CAR|')[1].split('|')[:6]
        index = int(index)
        if index >= 90: continue
        model = models[indices[index]]; angle = math.radians(float(yaw))
        frames.setdefault(float(t), {})['car:'+str(index)] = (vec(position), [math.cos(angle), math.sin(angle)], model['half_length'], model['half_width'])
    if 'V2SERVICE|' in line:
        t, name, position, velocity, forward = line.split('V2SERVICE|')[1].split('|')[:5]
        if not any(kind in name for kind in ['PoliceRoadPatrol', 'CivilMotorcycle', 'PoliceMotorcycle', 'TwoWheelerCitizen']): continue
        p, v, f = vec(position), vec(velocity), vec(forward); count += 1
        if dot(v, f) < -5: reverse.append({'time': float(t), 'name': name, 'speed': dot(v, f)})
        police = 'PoliceRoadPatrol' in name
        frames.setdefault(float(t), {})[name] = (p, f, 300 if police else 160, 135 if police else 70)
    if 'V2CYCLEDETAIL|' in line:
        x = line.split('V2CYCLEDETAIL|')[1].split('|')
        states[(float(x[0]), x[1])] = float(x[2])
bad = []
for t, frame in sorted(frames.items()):
    names = list(frame)
    for i, name in enumerate(names):
        if states.get((t, name), 0) >= 2: continue
        p, f, hl, hw = frame[name]; r = [-f[1], f[0]]
        for other in names[i+1:]:
            if name.startswith('car:') and other.startswith('car:'): continue
            if states.get((t, other), 0) >= 2: continue
            q, g, ql, qw = frame[other]; delta = [q[0]-p[0], q[1]-p[1]]
            if math.hypot(*delta) > hl+ql+hw+qw: continue
            s = [-g[1], g[0]]
            if all(abs(dot(delta, a)) < hl*abs(dot(f,a))+hw*abs(dot(r,a))+ql*abs(dot(g,a))+qw*abs(dot(s,a))-25 for a in [f,r,g,s]):
                bad.append({'time':t, 'a':name, 'b':other})
result = dict(service_samples=count, reverse_samples=len(reverse), reverse_examples=reverse[:10], estimated_body_overlap_samples=len(bad), overlap_examples=bad[:40], note='Sampled conservative envelopes; parked/walking cyclists excluded. Not continuous collision certification.')
path.with_name(path.stem+'_service_bodies.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
