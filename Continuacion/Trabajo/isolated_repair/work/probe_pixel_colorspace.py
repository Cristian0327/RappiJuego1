import bpy,json
from pathlib import Path
p=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs/DeliveryArt/Crowd/T_CrowdPixelAtlas.png');im=bpy.data.images.load(str(p));coords=[(0,0),(16,16),(100,100),(250,250)];d={'size':list(im.size),'colorspace':im.colorspace_settings.name,'samples':[(x,y,list(im.pixels[(y*im.size[0]+x)*4:(y*im.size[0]+x)*4+3])) for x,y in coords]};Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/work/pixel_colorspace_probe.json').write_text(json.dumps(d));print(d)
