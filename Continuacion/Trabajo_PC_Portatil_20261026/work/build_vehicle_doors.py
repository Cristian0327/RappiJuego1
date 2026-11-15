import bpy,bmesh,json,shutil
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/TrafficDetailed';base=root/'outputs/VehicleDoorBases';base.mkdir(exist_ok=True)
report=[]
files=sorted(out.glob('SK_Private*.blend'))+sorted(out.glob('SK_Taxi*.blend'))+[out/'SK_TransMilenio.blend',out/'SK_TransMilenioG66.blend']
for f in files:
 backup=base/f.name
 if not backup.exists():shutil.copy2(f,backup)
 bpy.ops.wm.open_mainfile(filepath=str(backup));obj=bpy.data.objects[f.stem];rig=obj.find_armature();bpy.context.scene.frame_set(1);bus='TransMilenio' in f.stem
 # Cut existing planar faces at the door boundaries before assigning rigid weights.
 half=max(abs(v.co.y) for v in obj.data.vertices);top=min(1.65,max(v.co.z for v in obj.data.vertices)-.12)
 xmin,xmax,zmin,zmax,inner=(3.3,4.3,.4,2.9,1.05) if bus else (-.65,.45,.36,top,half*.58)
 bm=bmesh.new();bm.from_mesh(obj.data)
 cuts=[(0,xmin),(0,xmax),(2,zmin),(2,zmax),(1,-inner),(1,inner)]
 if bus:cuts.append((0,3.8))
 for axis,value in cuts:
  co=[0.,0.,0.];co[axis]=value;normal=[0.,0.,0.];normal[axis]=1
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=co,plane_no=normal,clear_inner=False,clear_outer=False)
 bm.to_mesh(obj.data);bm.free();obj.data.update()
 group_names=[g.name for g in obj.vertex_groups];old=obj.data;colors=old.color_attributes['TrafficColor'];verts=[];faces=[];cols=[];weights=[];counts={}
 for poly in old.polygons:
  center=poly.center;door=None
  if xmin+.0001<center.x<xmax-.0001 and zmin+.0001<center.z<zmax-.0001:
   if bus and center.y<-inner:door='bus_door_a' if center.x<3.8 else 'bus_door_b'
   if not bus and abs(center.y)>inner and (f.stem!='SK_PrivateBeetle' or abs(center.y)<.75):door='door_L' if center.y<0 else 'door_R'
  ids=[]
  for li in poly.loop_indices:
   v=old.vertices[old.loops[li].vertex_index];ids.append(len(verts));verts.append(tuple(v.co));cols.append(tuple(colors.data[li].color))
   existing=max(v.groups,key=lambda g:g.weight,default=None);bone=group_names[existing.group] if existing else 'root'
   weights.append(door if door and bone=='root' else bone)
  faces.append(ids)
  if door:counts[door]=counts.get(door,0)+1
 data=bpy.data.meshes.new(f.stem+'_Doors');data.from_pydata(verts,[],faces);data.update();attribute=data.color_attributes.new(name='TrafficColor',type='BYTE_COLOR',domain='CORNER')
 for li,c in enumerate(cols):attribute.data[li].color=c
 for material in old.materials:data.materials.append(material)
 obj.data=data
 bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 definitions={'bus_door_a':(3.55,-1.3,.4),'bus_door_b':(4.05,-1.3,.4)} if bus else {'door_L':(.45,-half*.8,.7),'door_R':(.45,half*.8,.7)}
 for name,co in definitions.items():
  bone=rig.data.edit_bones.new(name);bone.head=co;bone.tail=Vector(co)+Vector((0,0,.25));bone.parent=rig.data.edit_bones['root']
 bpy.ops.object.mode_set(mode='OBJECT');obj.vertex_groups.clear();groups={name:obj.vertex_groups.new(name=name) for name in list(group_names)+list(definitions)};indices={name:[] for name in groups}
 for i,name in enumerate(weights):indices[name].append(i)
 for name,ii in indices.items():
  if ii:groups[name].add(ii,1,'REPLACE')
 assert all(counts.get(n,0)>0 for n in definitions),(f.name,counts)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(out/(f.stem+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE')
 bpy.context.scene['working_doors']=True;bpy.ops.wm.save_as_mainfile(filepath=str(f));report.append({'mesh':f.stem,'door_faces':counts,'bones':list(definitions)})
 print('DOORS_READY',f.stem,counts,flush=True)
(root/'work/vehicle_door_geometry.json').write_text(json.dumps(report,indent=2))
