import bpy,json
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');out=r/'outputs/DeliveryArt/TrafficDetailed/Accordion';out.mkdir(exist_ok=True)
for name in ['SK_TransMilenio','SK_TransMilenioG66']:
 bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/TrafficDetailed'/(name+'.blend')));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=bpy.data.objects.get(name);joint=rig.data.bones['articulation'].head_local.x;vg=mesh.vertex_groups;art=vg['articulation'];root=vg['root'];count=0
 for v in mesh.data.vertices:
  if not any(g.group==art.index and g.weight>.9 for g in v.groups):continue
  if not joint-.42<v.co.x<joint+.42:continue
  t=max(0,min(1,(joint+.42-v.co.x)/.84));art.add([v.index],t,'REPLACE');root.add([v.index],1-t,'REPLACE');count+=1
 assert count>100,(name,count);rig.animation_data_clear();bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=False,axis_forward='-Y',axis_up='Z');print('ACCORDION_WEIGHTS',name,count)
