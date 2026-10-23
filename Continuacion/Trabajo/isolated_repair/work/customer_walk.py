import bpy,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/People'
for name in ['CustomerStudent','CustomerOffice','CustomerNeighbor']:
 bpy.ops.wm.open_mainfile(filepath=str(out/('SK_'+name+'.blend')));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();sc=bpy.context.scene;sc.frame_start=1;sc.frame_end=25;sc.render.fps=24
 for f in range(1,26):
  t=(f-1)/24*math.tau
  for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0)
  for side,sign in [('L',1),('R',-1)]:
   rig.pose.bones['thigh_'+side].rotation_euler.x=math.sin(t)*.32*sign
   rig.pose.bones['shin_'+side].rotation_euler.x=max(0,-math.sin(t)*sign)*.40
   rig.pose.bones['upperarm_'+side].rotation_euler.x=-math.sin(t)*.18*sign
   rig.pose.bones['forearm_'+side].rotation_euler.x=-.12
  for b in rig.pose.bones:b.keyframe_insert('rotation_euler',frame=f,group=b.name)
 rig.animation_data.action.name='Walk';bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.wm.save_as_mainfile(filepath=str(out/('A_'+name+'_Walk.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/('A_'+name+'_Walk.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
