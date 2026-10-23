import numpy as np
from PIL import Image,ImageDraw
from pathlib import Path
W=Path('new_map_audit');a=np.load(W/'wall_polygons.npy',allow_pickle=True);im=Image.new('L',(800,1000));d=ImageDraw.Draw(im)
for poly in a:
 pts=[tuple(v) for v in poly];d.polygon(pts,fill=255);d.line(pts+[pts[0]],fill=255,width=1)
im.save(W/'obstacles.png');print('RASTER_READY',len(a))
