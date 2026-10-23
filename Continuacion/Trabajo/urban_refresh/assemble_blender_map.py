import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector,Euler
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');p=json.loads((U/'placement_plan.json').read_text());city=json.loads((U.parent/'new_map_audit/integration_plan.json').read_text());names=[v['name'] for v in json.loads((U/'assets.json').read_text())]
with bpy.data.libraries.load(str(U/'Mobiliario_Bogota_Voxel.blend'),link=False) as (src,dst):dst.objects=names
protos={o.name:o for o in dst.objects};col=bpy.data.collections.new('Mobiliario Bogotá - estaciones y cruces');bpy.context.scene.collection.children.link(col)
def put(name,pos,yaw=0):
 o=bpy.data.objects.new(name,protos[name].data);col.objects.link(o);o.location=(pos[0]/100,-pos[1]/100,pos[2]/100);o.rotation_euler=(0,0,-math.radians(yaw));return o
for item in p['furniture']:
 name='SM_Bogota_'+item['type'];yaw=item['yaw']+180 if item['type'] in ['Farola','Banca'] else item['yaw'];put(name,item['position'],yaw)
 if item['type']=='Farola':put('SM_Bogota_FarolaLuz',item['position'],yaw)
for s in p['crossings']:
 put('SM_Bogota_CruceAccesible',s['position'],s['yaw']);ang=math.radians(s['yaw']);t=(math.cos(ang),math.sin(ang));rr=(-t[1],t[0])
 for sign in [-1,1]:
  q=[s['position'][0]-t[0]*sign*800+rr[0]*sign*(s['halfwidth']-35),s['position'][1]-t[1]*sign*800+rr[1]*sign*(s['halfwidth']-35),20];yaw=s['yaw']+(180 if sign<0 else 0);put('SM_Bogota_SemaforoPoste',q,yaw);put('SM_Bogota_SemaforoVerde',q,yaw);put('SM_Bogota_SemaforoPeatonRojo',q,yaw)
for st in city['stations']:
 pos=[st['position'][0],st['position'][1],0];put('SM_Bogota_EstacionTransmi',pos,st['yaw']);ang=math.radians(st['yaw'])
 for x in [320,440]:put('SM_Bogota_PuertaEstacion',[pos[0]+math.cos(ang)*x-math.sin(ang)*140,pos[1]+math.sin(ang)*x+math.cos(ang)*140,0],st['yaw'])
 for x in [-900,-500]:put('SM_Bogota_Banca',[pos[0]+math.cos(ang)*x,pos[1]+math.sin(ang)*x,90],st['yaw'])
# Match the warm terracotta and sand palette used by the game material.
for mat in bpy.data.materials:
 if mat.name.startswith('Andenes_Concreto') and mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type=='TEX_BRICK':node.inputs['Color1'].default_value=(.42,.16,.075,1);node.inputs['Color2'].default_value=(.46,.20,.095,1);node.inputs['Mortar'].default_value=(.25,.13,.075,1)
   if node.type=='MIX_RGB' and not node.inputs[1].is_linked:node.inputs[1].default_value=(.55,.36,.18,1)
import numpy as np
o=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));me=o.data;v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);world=np.array(o.matrix_world);z=v@world[2,:3]+world[2,3];vi=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',vi);a=me.color_attributes['Color'];colors=np.empty(len(a.data)*4,np.float32);a.data.foreach_get('color',colors);colors=colors.reshape(-1,4);mask=z[vi]>.35;shade=np.clip(colors[mask,:3]@np.array([.21,.72,.07])*3,0,1);colors[mask,:3]=np.array([.035,.09,.025])*(1-shade[:,None])+np.array([.16,.29,.055])*shade[:,None];a.data.foreach_set('color',colors.ravel())
bpy.context.scene['RuntimeLogic']='Unreal Engine Blueprints';bpy.context.scene['BogotaUrbanDesign']='Terracota, arena, mobiliario voxel, cruces accesibles y estaciones TransMilenio';bpy.ops.wm.save_as_mainfile(filepath=str(U/'Mapa_Bogota_Ambientado.blend'));print('BOGOTA_FURNISHED_BLEND_READY',len(col.objects))

