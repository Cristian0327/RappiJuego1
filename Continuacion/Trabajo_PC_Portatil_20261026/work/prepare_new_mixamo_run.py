from pathlib import Path
import shutil
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');shutil.copy2(Path('C:/Users/CRISTIAN/Downloads/Unarmed Run Forward.fbx'),r/'outputs/DeliveryArt/Mixamo/Run.fbx');p=r/'work/rebuild_anatomical_mixamo.py';s=p.read_text(encoding='utf-8-sig').replace("for clip in ['Walk','Idle','Jump']:","for clip in ['Run']:").replace("if clip=='Walk':","if clip=='Run':").replace("'retarget_report.json'","'run_retarget_report.json'").replace("'_Walk_Review.png'","'_Run_Review.png'")
s=s.replace("action=target.animation_data.action;", """# Preserve the run's flight phase, calibrated once across the cycle.
  heights=[];floors=[];ratio=(target.data.bones['thigh_l'].length+target.data.bones['calf_l'].length)/((source.matrix_world.to_3x3()@(src['LeftLeg'].bone.head_local-src['LeftUpLeg'].bone.head_local)).length+(source.matrix_world.to_3x3()@(src['LeftFoot'].bone.head_local-src['LeftLeg'].bone.head_local)).length)
  for frame in range(1,end+1):
   sc.frame_set(frame);root=target.pose.bones['root'];root.location=(0,0,0);bpy.context.view_layer.update();height=((align@(source.matrix_world@src['Hips'].head)).z-(align@resthead('Hips')).z)*ratio;ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());floors.append(min(v.co.z for v in ev.data.vertices)+height);heights.append(height)
  baseline=-min(floors)
  for frame,height in enumerate(heights,1):
   sc.frame_set(frame);root=target.pose.bones['root'];root.location=root.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,baseline+height));root.keyframe_insert('location',frame=frame,group='root')
  action=target.animation_data.action;""")
p.with_name('rebuild_mixamo_run.py').write_text(s,encoding='utf-8')
