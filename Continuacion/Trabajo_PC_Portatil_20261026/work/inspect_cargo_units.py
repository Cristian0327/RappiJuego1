import bpy
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Cargo/VoxelExplorer_CargoLoadout.blend';bpy.ops.wm.open_mainfile(filepath=str(p));print('UNIT',bpy.context.scene.unit_settings.scale_length)
for o in bpy.context.scene.objects:
 if o.type in ['MESH','ARMATURE']:print('ASSET',o.name,'DIMS',tuple(o.dimensions),'SCALE',tuple(o.scale))
