import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Traffic'
OUT.mkdir(parents=True,exist_ok=True)
COL={'Yellow':(1,.66,.015,1),'Red':(.72,.018,.026,1),'Blue':(.018,.23,.63,1),'White':(.8,.85,.83,1),'Rubber':(.018,.023,.03,1),'Glass':(.035,.13,.18,1),'Steel':(.28,.34,.38,1),'Lamp':(1,.9,.58,1),'Tail':(.9,.025,.015,1)}
manifest=json.loads((OUT/'manifest.json').read_text()) if '--repair' in sys.argv else []
for name,length,paint,bus in [('TaxiCompact',3.7,'Yellow',False),('TaxiSedan',4.25,'Yellow',False),('Private',4.1,'White',False),('SITP',9.8,'Blue',True),('TransMilenio',17,'Red',True)]:
 if '--repair' in sys.argv and name=='SITP':continue
 manifest=[m for m in manifest if m['name']!=name]
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 mats={}
 for k,c in COL.items():
  m=bpy.data.materials.new(k);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.35 if k=='Glass' else .72;mats[k]=m
 parts=[];bones={'root':((0,0,0),(0,0,.3),None)}
 def box(n,p,s,c,b='root'):
  bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[c]);parts.append((o,b));return o
 width=2.45 if bus else 1.78;r=.48 if bus else .33
 if name=='TransMilenio':bones['articulation']=((-1.8,0,1.2),(-1.8,0,1.8),'root')
 sections=[(3.4,10.2,'root'),(-5.4,6.2,'articulation')] if name=='TransMilenio' else [(0,length,'root')]
 for cx,l,b in sections:
  box('Chassis',(cx,0,.64 if bus else .49),(l,width,.34),'Rubber',b)
  if bus:
   box('LowerBody',(cx,0,1.15),(l,width,1.12),paint,b);box('Roof',(cx,0,3.02),(l,width,.17),'Steel',b)
   for y in [-1,1]:
    box('WindowBand',(cx,y*(width/2-.035),2.25),(l-.18,.085,1.35),'Glass',b)
    for j in range(int(l/.85)+1):box('WindowPillar',(cx-l/2+.12+j*.85,y*width/2,2.26),(.065,.07,1.5),paint,b)
    box('SafetyStripe',(cx,y*(width/2+.01),1.53),(l,.025,.065),'Yellow',b)
   for dx in [-l/2+.7,l/2-1.1]:
    for y in [-1,1]:
     box('DoubleDoor',(cx+dx,y*(width/2+.02),1.92),(.82,.035,1.96),'Rubber',b)
     for q in [-1,1]:box('DoorGlass',(cx+dx+q*.21,y*(width/2+.045),2.08),(.32,.025,1.36),'Glass',b)
   box('FrontGlass',(cx+l/2+.012,0,2.23),(.035,width-.15,1.23),'Glass',b)
   box('BlankDisplay',(cx+l/2+.032,0,2.83),(.018,1.55,.23),'Rubber',b)
   box('RoofAC',(cx-.6,0,3.18),(1.6,1.6,.22),'White',b)
  else:
   box('Body',(cx,0,.78),(l,width,.65),paint,b);box('Hood',(l*.31,0,1.13),(l*.32,width-.06,.12),paint,b)
   box('Cabin',(-.26,0,1.38),(l*.52,width-.15,.65),'Glass',b);box('Roof',(-.30,0,1.73),(l*.47,width-.10,.10),paint,b)
   for x in [-l*.29,-.08,l*.19]:
    for y in [-1,1]:box('Pillar',(x,y*(width/2-.045),1.40),(.085,.065,.66),paint,b)
   for x in [-.72,.35]:
    for y in [-1,1]:box('DoorHandle',(x,y*(width/2+.025),1.1),(.18,.045,.045),'Steel',b)
   for y in [-1,1]:box('Mirror',(.61,y*(width/2+.12),1.38),(.21,.20,.13),'Rubber',b)
   box('Grille',(l/2+.02,0,.73),(.04,.68,.19),'Rubber',b)
  for y in [-1,1]:
   box('Headlight',(cx+l/2+.03,y*(width*.32),.99 if bus else .94),(.06,.33,.20),'Lamp',b)
   box('Taillight',(cx-l/2-.03,y*(width*.34),1.1 if bus else .85),(.06,.20,.28),'Tail',b)
 if name=='TransMilenio':
  for j in range(12):box('AccordionFold',(-2.27+j*.052,0,1.82),(.036,2.40 if j%2 else 2.30,2.25),'Rubber','articulation')
 axles=[length*.31,-length*.31] if not bus else ([6.0,-.5,-6.7] if name=='TransMilenio' else [3.25,-3.15])
 for i,x in enumerate(axles):
  parent='articulation' if name=='TransMilenio' and i==2 else 'root'
  for side in [-1,1]:
   y=side*(width/2-.03);bone=f'wheel_{i}_{"L" if side<0 else "R"}';bones[bone]=((x,y,r),(x,y+.22,r),parent)
   bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=.24 if bus else .20,location=(x,y,r),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Tire';o.data.materials.append(mats['Rubber']);parts.append((o,bone))
   for j in range(6):
    a=j*math.tau/6;box('HubSpoke',(x+math.cos(a)*r*.35,y+side*.13,r+math.sin(a)*r*.35),(.09,.035,.09),'Steel',bone)
   box('Hub',(x,y+side*.14,r),(.12,.04,.12),'Steel',bone)
 bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='Rig_'+name;bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
 for n,(h,t,p) in bones.items():
  eb=rig.data.edit_bones.new(n);eb.head=h;eb.tail=t
  if p:eb.parent=rig.data.edit_bones[p]
 bpy.ops.object.mode_set(mode='OBJECT')
 for o,b in parts:
  group=o.vertex_groups.new(name=b);group.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('RigidSkin','ARMATURE');mod.object=rig
 bpy.ops.object.select_all(action='DESELECT')
 for o,b in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0][0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_'+name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');mesh.parent=rig
 assert len(mesh.vertex_groups)==len(bones)
 for frame,angle in [(1,0),(31,math.tau)]:
  for n in bones:
   if n.startswith('wheel_'):pb=rig.pose.bones[n];pb.rotation_mode='XYZ';pb.rotation_euler.y=angle;pb.keyframe_insert('rotation_euler',frame=frame)
 if name=='TransMilenio':
  for f,a in [(1,0),(16,.3),(31,0)]:pb=rig.pose.bones['articulation'];pb.rotation_mode='XYZ';pb.rotation_euler.z=a;pb.keyframe_insert('rotation_euler',frame=f)
 scene=bpy.context.scene;scene.frame_end=31;scene.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(OUT/('SK_'+name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 bpy.ops.object.camera_add(location=(length*.8,-length*.85,length*.55+2));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=length*1.32;scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(2,-4,10));bpy.context.object.data.energy=2000;bpy.context.object.data.size=10
 scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1100;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='Standard';scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('SK_'+name+'.blend')));bpy.ops.render.render(write_still=True)
 manifest.append({'name':name,'length_m':length,'width_m':width,'wheel_radius_m':r,'bones':list(bones),'vertices':len(mesh.data.vertices),'text_objects':0})
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('COLOMBIA_TRAFFIC_READY')
