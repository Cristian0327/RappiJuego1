import bpy,json,statistics
from pathlib import Path
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");out=r/'outputs/DeliveryArt/AnimationRebuild';report=[]
for path in list(out.glob('AN_*Run_Rebuilt.blend'))+list(out.glob('AN_*Cane_Rebuilt.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(path));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');sc=bpy.context.scene;feet=[b for b in rig.pose.bones if b.name.startswith('foot')];tracks={b.name:[] for b in feet};unit=sc.unit_settings.scale_length*100
 for f in range(sc.frame_start,sc.frame_end+1):
  sc.frame_set(f);bpy.context.view_layer.update()
  for b in feet:tracks[b.name].append(tuple((rig.matrix_world@b.head)*unit))
 velocities=[]
 for track in tracks.values():
  floor=min(v[2] for v in track)
  for a,b in zip(track,track[1:]):
   speed=(b[1]-a[1])*sc.render.fps
   if max(a[2],b[2])<floor+4 and speed>10:velocities.append(speed)
 report.append({'clip':path.stem,'stance_speed_cm_s':statistics.median(velocities) if velocities else None,'samples':len(velocities),'unit_cm':unit})
(out/'run_cane_stance_speeds.json').write_text(json.dumps(report,indent=2));print('STANCE_SPEED_ANALYSIS_PASS',report,flush=True)
