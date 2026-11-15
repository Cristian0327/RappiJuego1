from pathlib import Path
path=Path(__file__).with_name('build_bicycle.py')
code=path.read_text(encoding='utf-8')
code=code[:code.index("rig.animation_data.action=None")]
code=code.replace("OUT=BASE/'outputs/unreal_v2'","OUT=BASE/'outputs/DeliveryArt/Progression'")
code=code.replace("OUT/'VoxelExplorer_Unreal.blend'","BASE/'outputs/unreal_v2/VoxelExplorer_Unreal.blend'")
code=code.replace("'BikePedal'","'MotoRide'").replace("'AN_BikePedal.fbx'","'AN_MotoRide.fbx'")
code=code.replace('(sign*11,-8-11*math.cos(phase),49+11*math.sin(phase)),(sign*15,-70,60)','(sign*24,10,49),(sign*45,-45,65)')
exec(code)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'MotoRide.blend'))
print('MOTO_RIDE_POSE_READY',flush=True)
