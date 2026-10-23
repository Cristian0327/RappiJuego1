import numpy as np,json
from pathlib import Path
from scipy.ndimage import binary_closing,binary_fill_holes
h=np.load('compact_city/original_terrain_heights_2m.npy');mask=binary_fill_holes(binary_closing(np.isfinite(h)&(abs(h)<30),iterations=3));rows=[]
for y,line in enumerate(mask[:-1]):
 xs=np.where(line[:-1]&line[1:]&mask[y+1,:-1]&mask[y+1,1:])[0]
 if not len(xs):continue
 starts=np.r_[0,np.where(np.diff(xs)>1)[0]+1];ends=np.r_[starts[1:]-1,len(xs)-1]
 for a,b in zip(starts,ends):rows.append([int(xs[a]*200-40000),int(y*200-50000),int((xs[b]+1)*200-40000),int((y+1)*200-50000)])
Path('urban_safety/safety_floor_rects.json').write_text(json.dumps(rows));print(len(rows),'physical floor strips')
