import bpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto")
for name,y in [('HeroBikePedal',15),('HeroMotoRide',15),('CrowdMotoRide',31)]:
 bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/AnimationRebuild'/('AN_'+name+'_Rebuilt.blend')));m=next(o for o in bpy.data.objects if o.type=='MESH');bpy.context.scene.frame_set(1);bpy.context.view_layer.update();tree=BVHTree.FromObject(m,bpy.context.evaluated_depsgraph_get());print(name,[('y',p,tree.ray_cast(Vector((0,p,60)),Vector((0,0,1)),60)[0]) for p in [y-3,y,y+3]],flush=True)
