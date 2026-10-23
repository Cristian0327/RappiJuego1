import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Traffic'
for f in OUT.glob('SK_*.blend'):
 bpy.ops.wm.open_mainfile(filepath=str(f));scene=bpy.context.scene
 bus='SITP' in f.stem or 'TransMilenio' in f.stem
 scene.camera.rotation_euler=(Vector((0,0,1.5 if bus else .85))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale*=1.10
 scene.render.filepath=str(OUT/(f.stem[3:]+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(f));bpy.ops.render.render(write_still=True)
