import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/TrafficDetailed';report={}
for name in ['TransMilenio','TransMilenioG66']:
 f=out/('SK_'+name+'.blend');bpy.ops.wm.open_mainfile(filepath=str(f));o=bpy.data.objects['SK_'+name];rig=o.find_armature();bpy.context.scene.frame_set(1)
 xs=[v.co.x for v in o.data.vertices];zs=[v.co.z for v in o.data.vertices]
 # Body width excludes the wing mirrors; the painted side panels define it.
 a=o.data.color_attributes['TrafficColor'];ys=[]
 for p in o.data.polygons:
  r,g,b,rough=a.data[p.loop_start].color
  if rough>.8 and ((r>.35 and g<.09 and b<.1) or (b>.30 and r>.1 and g<.1)):
   ys.extend(o.data.vertices[i].co.y for i in p.vertices)
 sx=18/(max(xs)-min(xs));sy=2.6/(max(ys)-min(ys));sz=3.4/(max(zs)-min(zs));originx=(max(xs)+min(xs))/2;floor=min(zs)
 for v in o.data.vertices:v.co.x=(v.co.x-originx)*sx;v.co.y=max(-1.55,min(1.55,v.co.y*sy));v.co.z=(v.co.z-floor)*sz
 bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 for bone in rig.data.edit_bones:
  for pt in [bone.head,bone.tail]:pt.x=(pt.x-originx)*sx;pt.y*=sy;pt.z=(pt.z-floor)*sz
 bpy.ops.object.mode_set(mode='OBJECT');bpy.ops.object.select_all(action='DESELECT');o.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(out/('SK_'+name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE')
 bpy.context.scene['physical_dimensions_m']='18.0 length, 2.6 body width, 3.4 height; 3.1 width including mirrors.'
 bpy.ops.wm.save_as_mainfile(filepath=str(f));report[name]={'length_m':18,'body_width_m':2.6,'height_m':3.4,'mirror_width_m':3.1,'unit_scale':1}
(out/'physical_bus_dimensions.json').write_text(json.dumps(report,indent=2));print('REAL_BUS_DIMENSIONS_READY',flush=True)
