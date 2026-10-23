import bpy,math,json
from pathlib import Path
from mathutils import Vector
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");out=r/'outputs/DeliveryArt/Services';palette=json.loads((out/'pixel_palette.json').read_text());reports=[]
for name,paint in [('SK_BicycleCivilBlue',(.035,.35,.51)),('SK_BicycleCivilRed',(.59,.07,.045)),('SK_BicycleCivilYellow',(.87,.55,.035))]:
 bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/Progression/SM_BikeStage0.blend'));body=next(o for o in bpy.data.objects if o.type=='MESH');body.name=name
 for o in list(bpy.data.objects):
  if o!=body:bpy.data.objects.remove(o,do_unlink=True)
 def box(p,s,material):
  bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o
 mats={m.name:m for m in body.data.materials};rubber=mats['Voxel_Rubber'];steel=mats['Voxel_Steel'];parts=[body];groups={}
 for suffix,x in [('front',.62),('rear',-.62)]:
  pieces=[]
  for i in range(24):
   a=math.tau*i/24;pieces.append(box((x+.30*math.sin(a),0,.33+.30*math.cos(a)),(.10,.14,.10),rubber))
  for vertical in [False,True]:
   for i in range(15):
    v=-.28+i*.04;pieces.append(box((x if vertical else x+v,0,.33+v if vertical else .33),(.04,.04,.04),steel))
  for o in pieces:
   g=o.vertex_groups.new(name='wheel_'+suffix);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
  parts+=pieces
 g=body.vertex_groups.new(name='root');g.add(list(range(len(body.data.vertices))),1,'REPLACE')
 # Pedal platforms share a crank pivot so the pose can be synchronized with distance.
 for sign in [-1,1]:
  p=box((.08+sign*.11,sign*.13,.33),(.22,.16,.06),steel);g=p.vertex_groups.new(name='crank');g.add(list(range(len(p.data.vertices))),1,'REPLACE');parts.append(p)
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=body;bpy.ops.object.join();body=bpy.context.object
 for v in body.data.vertices:v.co=Vector(tuple(round(c/.02)*.02 for c in v.co))
 color=body.data.color_attributes.new(name='ServiceColor',type='FLOAT_COLOR',domain='CORNER');uv=body.data.uv_layers.active or body.data.uv_layers.new()
 for poly in body.data.polygons:
  mat=body.data.materials[poly.material_index].name;c=paint if 'Paint' in mat else (.016,.023,.029) if 'Rubber' in mat else (.22,.30,.33);rgb=tuple(round(v*255) for v in c);index=min(range(len(palette)),key=lambda i:sum((palette[i][j]-rgb[j])**2 for j in range(3)));u=((index%64)*8+4)/512;v=((index//64)*8+4)/512
  for li in poly.loop_indices:color.data[li].color=tuple(c)+(1,);uv.data[li].uv=(u,v)
 m=bpy.data.materials.new('ServiceVoxel');m.use_nodes=True;n=m.node_tree.nodes;tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(out/'T_ServicePixelAtlas.png'),check_existing=True);tex.image.filepath='//T_ServicePixelAtlas.png';tex.interpolation='Closest';m.node_tree.links.new(tex.outputs['Color'],n['Principled BSDF'].inputs['Base Color']);n['Principled BSDF'].inputs['Roughness'].default_value=.82;body.data.materials.clear();body.data.materials.append(m)
 for p in body.data.polygons:p.material_index=0
 rigdata=bpy.data.armatures.new(name+'_Rig');rig=bpy.data.objects.new('Armature',rigdata);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for bone,head,tail in [('root',(0,0,0),(0,0,.2)),('wheel_front',(.62,0,.33),(.62,.2,.33)),('wheel_rear',(-.62,0,.33),(-.62,.2,.33)),('crank',(.08,0,.33),(.08,.2,.33))]:
  b=rigdata.edit_bones.new(bone);b.head=head;b.tail=tail
  if bone!='root':b.parent=rigdata.edit_bones['root']
 bpy.ops.object.mode_set(mode='OBJECT');mod=body.modifiers.new('BicycleRig','ARMATURE');mod.object=rig;bpy.ops.object.select_all(action='DESELECT');body.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z');reports.append({'name':name,'grid_cm':2,'wheel_bones':['wheel_front','wheel_rear'],'pedal_bone':'crank'})
(out/'civil_bicycles.json').write_text(json.dumps(reports,indent=2));print('THREE_VOXEL_CIVIL_BICYCLES_READY',flush=True)
