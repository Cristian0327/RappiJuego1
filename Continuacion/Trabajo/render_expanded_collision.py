import numpy as np,json,math
from PIL import Image,ImageDraw
from pathlib import Path
W=Path('new_map_audit');f=json.loads((W/'manifest.json').read_text())['spacing_expansion'];a=np.load(W/'expanded_wall_quads.npy',mmap_mode='r');im=Image.new('L',(math.ceil(800*f),math.ceil(1000*f)));d=ImageDraw.Draw(im)
for poly in a:
 pts=[tuple(v) for v in poly];d.polygon(pts,fill=255);d.line(pts+[pts[0]],fill=255,width=1)
im.save(W/'obstacles.png');print('EXPANDED_PHYSICAL_RASTER',len(a))
