import bpy,json,numpy as np,math
from pathlib import Path
from mathutils import Vector
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');s=json.loads((P/'station_move.json').read_text());origin=np.array(s['old']);delta=np.array(s['delta']);ang=math.radians(s['yaw']);t=np.array([math.cos(ang),math.sin(ang)]);n=np.array([-t[1],t[0]]);out=P/'station_access_export';out.mkdir(exist_ok=True)
for name in ['SM_Bogota_AccesosEstaciones','SM_Bogota_MarcasInterseccion']:
 ob=bpy.data.objects.get(name)
 if not ob:
  before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(P.parent/'urban_refresh/export'/(name+'.fbx')));ob=next(o for o in bpy.data.objects if o not in before and o.type=='MESH')
 me=ob.data.copy();ob.data=me;mw=ob.matrix_world;inv=mw.inverted();changed=0
 for v in me.vertices:
  world=np.array(mw@v.co)*[100,-100,100];d=world[:2]-origin[:2];u=float(np.dot(d,t));side=float(np.dot(d,n))
  if abs(u)<4000 and abs(side)<2800:
   world+=delta;v.co=inv@Vector(world/[100,-100,100]);changed+=1
 me.update();bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR');print('STATION_ACCESS_MOVED',name,changed,flush=True)
