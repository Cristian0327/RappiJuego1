from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto')
s=(r/'work/build_mount_animations.py').read_text(encoding='utf-8-sig')
s=s.replace("exec(compile((r/'work/rebuild_crowd_bike_pedal.py').read_text(),str(r/'work/rebuild_crowd_bike_pedal.py'),'exec'))",'')
s=s.replace("origin=Vector((0 if who=='Hero' else -55,0,0))", "origin=Vector((-55,0,0))")
s=s.replace("'mount_animation_validation.json'","'mount_animation_corrected_validation.json'")
exec(compile(s,'AlignedVehicleMounts','exec'))
