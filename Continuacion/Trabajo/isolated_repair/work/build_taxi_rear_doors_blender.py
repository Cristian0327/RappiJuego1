import bpy,bmesh,json,shutil
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];out=r/'outputs/DeliveryArt/TrafficDetailed';backup=r/'Recuperacion_Migracion_Blueprints/2026-10-18_taxi_rear_doors';backup.mkdir(exist_ok=True,parents=True);report=[]
for name in ['SK_TaxiSedan','SK_TaxiCompact']:
 f=out/(name+'.blend');saved=backup/f.name
 if not saved.exists():shutil.copy2(f,saved)
 bpy.ops.wm.open_mainfile(filepath=str(saved));obj=bpy.data.objects[name];rig=obj.find_armature();bpy.context.scene.frame_set(1);half=max(abs(v.co.y) for v in obj.data.vertices);top=min(1.65,max(v.co.z for v in obj.data.vertices)-.12);xmin=-1.65;xmax=-.65;zmin=.36;inner=half*.58
 bm=bmesh.new();bm.from_mesh(obj.data)
 for axis,value in [(0,xmin),(0,xmax),(2,zmin),(2,top),(1,-inner),(1,inner)]:
  co=[0.,0.,0.];co[axis]=value;normal=[0.,0.,0.];normal[axis]=1;bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=co,plane_no=normal,clear_inner=False,clear_outer=False)
 bm.to_mesh(obj.data);bm.free();obj.data.update();old=obj.data;colors=old.color_attributes['TrafficColor'];group_names=[g.name for g in obj.vertex_groups];verts=[];faces=[];cols=[];weights=[];counts={}
 for poly in old.polygons:
  c=poly.center;door=('door_rear_L' if c.y<0 else 'door_rear_R') if xmin+.0001<c.x<xmax-.0001 and zmin+.0001<c.z<top-.0001 and abs(c.y)>inner else None;ids=[]
  for li in poly.loop_indices:
   v=old.vertices[old.loops[li].vertex_index];ids.append(len(verts));verts.append(tuple(v.co));cols.append(tuple(colors.data[li].color));existing=max(v.groups,key=lambda g:g.weight,default=None);bone=group_names[existing.group] if existing else 'root';weights.append(door if door and bone=='root' else bone)
  faces.append(ids)
  if door:counts[door]=counts.get(door,0)+1
 data=bpy.data.meshes.new(name+'_RearDoors');data.from_pydata(verts,[],faces);data.update();attribute=data.color_attributes.new(name='TrafficColor',type='BYTE_COLOR',domain='CORNER')
 for li,c in enumerate(cols):attribute.data[li].color=c
 for material in old.materials:data.materials.append(material)
 obj.data=data;bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT');definitions={'door_rear_L':(xmax,-half*.8,.7),'door_rear_R':(xmax,half*.8,.7)}
 for bone_name,co in definitions.items():
  bone=rig.data.edit_bones.new(bone_name);bone.head=co;bone.tail=Vector(co)+Vector((0,0,.25));bone.parent=rig.data.edit_bones['root']
 bpy.ops.object.mode_set(mode='OBJECT');obj.vertex_groups.clear();groups={n:obj.vertex_groups.new(name=n) for n in group_names+list(definitions)};indices={n:[] for n in groups}
 for i,n in enumerate(weights):indices[n].append(i)
 for n,ii in indices.items():
  if ii:groups[n].add(ii,1,'REPLACE')
 assert all(counts.get(n,0)>0 for n in definitions),(name,counts)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE');bpy.context.scene['separate_rear_taxi_doors']=True;bpy.ops.wm.save_as_mainfile(filepath=str(f));report.append({'mesh':name,'rear_door_faces':counts});print('TAXI_REAR_DOORS_READY',name,counts,flush=True)
(r/'work/taxi_rear_door_geometry.json').write_text(json.dumps(report,indent=2))
