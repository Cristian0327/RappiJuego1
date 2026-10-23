import sys
from pathlib import Path
sys.path.insert(0,'urban_refresh/python_deps')
from shapely import wkt
from shapely.ops import unary_union
from PIL import Image,ImageDraw
area=unary_union([wkt.loads(Path('urban_corrections/unified_asphalt.wkt').read_text()),wkt.loads(Path('urban_corrections/unified_sidewalks.wkt').read_text())]).buffer(-25);im=Image.new('L',(4096,5120));dr=ImageDraw.Draw(im)
def coords(r):return [((x+40000)/80000*4096,(y+50000)/100000*5120) for x,y in r.coords]
for p in ([area] if area.geom_type=='Polygon' else area.geoms):
 dr.polygon(coords(p.exterior),fill=255)
 for r in p.interiors:dr.polygon(coords(r),fill=0)
im.save('texture_cycle/T_UrbanGroundPriority.png');print('GROUND_LAYER_MASK_READY')
