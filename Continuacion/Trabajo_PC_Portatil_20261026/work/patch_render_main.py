from pathlib import Path
s=Path('work/render_rigged_cast.py').read_text();s=s.replace("folder=root/'outputs/DeliveryArt/People'", "folder=root/'outputs/DeliveryArt/Animation'").replace("folder.glob('SK_*.blend')", "folder.glob('AN_Mixamo*.blend')");s=s.replace('sc.frame_set(25)','sc.frame_set(25)\n for o in list(sc.objects):\n  if o.type in {\'MESH\',\'ARMATURE\'}:o.scale*=.01\n bpy.context.view_layer.update()')
Path('work/render_main_motion.py').write_text(s)
