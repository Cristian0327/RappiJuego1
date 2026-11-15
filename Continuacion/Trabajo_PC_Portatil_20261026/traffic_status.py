import json
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
cars, causes, roads, cycles = {}, {}, {}, {}
for line in path.read_text(errors='replace').splitlines():
    for tag, rows in [('V2CAR', cars), ('V2CAUSE', causes), ('V2ROADDETAIL', roads), ('V2CYCLEDETAIL', cycles)]:
        if tag + '|' in line:
            fields = line.split(tag + '|', 1)[1].split('|')
            rows.setdefault(float(fields[0]), {})[fields[1]] = fields[2:]
if not cars:
    print('No traffic samples yet')
    sys.exit()
now = max(cars)
latest = cars[now]
stationary = []
for index, fields in latest.items():
    if float(fields[1]) > 20:
        continue
    history = [(time, row[index]) for time, row in sorted(cars.items()) if index in row]
    start = now
    for time, row in reversed(history):
        if float(row[1]) > 20:
            break
        start = time
    stationary.append(dict(id=int(index), stopped_seconds=round(now-start, 1), cause=causes.get(now, {}).get(index)))
stationary.sort(key=lambda row: -row['stopped_seconds'])
print(json.dumps(dict(time=now, moving=sum(float(row[1]) > 20 for row in latest.values()), total=len(latest), stopped=stationary[:12], roads=roads.get(max(roads), {}) if roads else {}), indent=2))
