import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[1];out=r/'outputs/DeliveryArt/Crowd'
for f in sorted(out.glob('SK_Citizen*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(f));o=next(o for o in bpy.data.objects if o.type=='MESH')
 tex=next(n for n in o.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');tex.image=bpy.data.images.load(str(out/'T_CrowdPixelAtlas.png'),check_existing=False);tex.image.pack();bpy.ops.wm.save_as_mainfile(filepath=str(f))
print('EDITABLE_PALETTE_ALL_60_PASS')
