import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'work'));from voxel_greedy import emit
out=root/'outputs/DeliveryArt/Services';out.mkdir(parents=True,exist_ok=True)
COL={'Green':(.045,.19,.11,1),'White':(.82,.87,.83,1),'Navy':(.025,.055,.06,1),'Rubber':(.016,.023,.029,1),'Steel':(.22,.30,.33,1),'Chrome':(.55,.66,.67,1),'Blue':(.02,.22,.86,.02),'Red':(.85,.025,.02,.02),'Lamp':(.92,.96,.80,.02),'Amber':(1,.38,.025,.02),'Gold':(.75,.65,.20,1),'Reflect':(.63,.77,.09,1),'CivilBlue':(.035,.35,.51,1),'CivilRed':(.59,.07,.045,1),'CivilYellow':(.87,.55,.035,1),'CivilPurple':(.35,.075,.49,1),'CivilWhite':(.76,.78,.72,1)}
FONT={'P':['110','101','110','100','100'],'O':['010','101','101','101','010'],'L':['100','100','100','100','111'],'I':['111','010','010','010','111'],'C':['011','100','100','100','011'],'A':['010','101','111','101','101'],'N':['101','111','111','101','101']}
report=[]
pixel_palette=[];pixel_lookup={}
def shader():
 m=bpy.data.materials.get('ServiceVoxel') or bpy.data.materials.new('ServiceVoxel');m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');v=n.new('ShaderNodeVertexColor');v.layer_name='ServiceColor';tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(out/'T_ServicePixelAtlas.png'),check_existing=True);tex.image.filepath='//T_ServicePixelAtlas.png';tex.interpolation='Closest';m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.78;m.node_tree.links.new(p.outputs['BSDF'],o.inputs['Surface']);return m

def mesh_vox(name,vox,q,rig=None,bones=None):
 V,F,M,B=emit(vox,q);data=bpy.data.meshes.new(name);data.from_pydata(V,[],F);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);a=data.color_attributes.new(name='ServiceColor',type='FLOAT_COLOR',domain='CORNER')
 for poly,mat in zip(data.polygons,M):
  for li in poly.loop_indices:a.data[li].color=COL[mat]
 data.materials.append(shader())
 if not rig:
  rd=bpy.data.armatures.new(name+'_Rig');rig=bpy.data.objects.new(name+'_Rig',rd);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
  for bone,(head,tail,parent) in bones.items():
   b=rd.edit_bones.new(bone);b.head=head;b.tail=tail
   if parent:b.parent=rd.edit_bones[parent]
  bpy.ops.object.mode_set(mode='OBJECT')
 for bone in set(B):
  g=obj.vertex_groups.new(name=bone);g.add([i for i,b in enumerate(B) if b==bone],1,'REPLACE')
 mod=obj.modifiers.new('RigidVoxelRig','ARMATURE');mod.object=rig;return obj,rig

def voxel_helpers(vox,q):
 def box(p,s,mat,b='root'):
  lo=[round((p[i]-s[i]/2)/q) for i in range(3)];hi=[max(lo[i]+1,round((p[i]+s[i]/2)/q)) for i in range(3)]
  for x in range(lo[0],hi[0]):
   for y in range(lo[1],hi[1]):
    for z in range(lo[2],hi[2]):vox[(x,y,z)]=(mat,b)
 def line(a,b,t,mat,bone='root'):
  a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/q))
  for i in range(n+1):box(a.lerp(b,i/n),(t,t,t),mat,bone)
 def word(text,center,y,z,mat,bone='root'):
  width=(len(text)*4-1)*q
  for j,ch in enumerate(text):
   for row,line_ in enumerate(FONT[ch]):
    for col,c in enumerate(line_):
     if c=='1':box((center-width/2+(j*4+col+.5)*q,y,z+(4-row)*q),(q,q,q),mat,bone)
 return box,line,word

def join_meshes(base,extra):
 bpy.ops.object.select_all(action='DESELECT');base.select_set(True);extra.select_set(True);bpy.context.view_layer.objects.active=base;bpy.ops.object.join();return base

def save_export(obj,rig,name,unit):
 global pixel_palette,pixel_lookup
 for layer in list(obj.data.uv_layers):obj.data.uv_layers.remove(layer)
 uv=obj.data.uv_layers.new(name='ServicePixelUV');colors=obj.data.color_attributes['ServiceColor']
 for face in obj.data.polygons:
  color=colors.data[face.loop_start].color;key=tuple(round(max(0,min(1,c))*255) for c in color[:3])
  if key not in pixel_lookup:pixel_lookup[key]=len(pixel_palette);pixel_palette.append(key)
  index=pixel_lookup[key];x=index%64;y=index//64
  for li,xy in zip(face.loop_indices,[(.12,.12),(.88,.12),(.88,.88),(.12,.88)]):uv.data[li].uv=((x+xy[0])/64,(y+xy[1])/64)
 if name=='SK_PolicePatrol':
  window=bpy.data.materials.get('ServiceWindow') or bpy.data.materials.new('ServiceWindow');window.use_nodes=True;window.diffuse_color=(.04,.10,.14,.18);window.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.04,.10,.14,1);window.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=.18;window.surface_render_method='DITHERED';obj.data.materials.append(window);wi=len(obj.data.materials)-1;traffic=obj.data.color_attributes['TrafficColor']
  for face in obj.data.polygons:
   if .33<traffic.data[face.loop_start].color[3]<.37:face.material_index=wi
 if name.startswith('SK_PoliceOfficer'):
  hi=obj.vertex_groups['head'].index;assert min(v.co.z for v in obj.data.vertices if any(g.group==hi for g in v.groups))>60,'Head geometry below neck'
 obj.name=name;rig.name='Armature' if unit==.01 else name+'_Rig';bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=unit
 if rig.animation_data:rig.animation_data.action=None
 for p in rig.pose.bones:p.rotation_mode='QUATERNION';p.rotation_quaternion=(1,0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
 bpy.context.scene.frame_set(1);bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=obj
 for attribute in list(obj.data.color_attributes):
  if attribute.name!='ServiceColor':obj.data.color_attributes.remove(attribute)
 obj.data.color_attributes.active_color=obj.data.color_attributes['ServiceColor'];obj.data.color_attributes.render_color_index=list(obj.data.color_attributes).index(obj.data.color_attributes['ServiceColor'])
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_armature_deform_only=True,mesh_smooth_type='FACE')
 bpy.context.view_layer.update();dims=[round(d*unit,3) for d in obj.dimensions];report.append({'name':name,'dimensions_m':dims,'bones':[b.name for b in rig.data.bones],'vertices':len(obj.data.vertices),'source_blend':str(out/(name+'.blend'))})
 # Review images use meters, while the saved character sources retain centimeters.
 for other in list(bpy.context.scene.objects):
  if other not in (obj,rig):bpy.data.objects.remove(other,do_unlink=True)
 if unit!=1:
  for o in [obj,rig]:
   if o.parent not in (obj,rig):o.scale*=unit
 target=Vector((0,0,dims[2]*.45));radius=max(dims[0],dims[1],dims[2]);bpy.ops.object.camera_add(location=target+Vector((radius*1.2,-radius*1.6,radius*.95)));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=radius*1.35;scene=bpy.context.scene;scene.camera=cam;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=768;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.view_settings.view_transform='Standard';scene.world=scene.world or bpy.data.worlds.new('ServiceStudio');scene.world.color=(.35,.35,.35)
 for loc,power,size in [((3,-4,6),1000,5),((-3,-1,3),650,4),((1,4,5),900,4)]:
  bpy.ops.object.light_add(type='AREA',location=Vector(loc)*max(1,radius*.5));lamp=bpy.context.object;lamp.data.energy=power*max(1,radius*.5)**2;lamp.data.shape='DISK';lamp.data.size=size*max(1,radius*.5);lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('SERVICE_MODEL_READY',name,dims,flush=True)

# Patrol shares the exact SUV silhouette, wheels and working front-door rig.
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/DeliveryArt/Services/PatrolCabinSource/SK_PrivateSUV.blend'));obj=bpy.data.objects['SK_PrivateSUV'];rig=obj.find_armature();a=obj.data.color_attributes['TrafficColor'];service=obj.data.color_attributes.new(name='ServiceColor',type='FLOAT_COLOR',domain='CORNER')
for poly in obj.data.polygons:
 c=a.data[poly.loop_start].color;paint=c[0]>.4 and .018<c[1]<.04 and .024<c[2]<.05
 for li in poly.loop_indices:service.data[li].color=COL['Green' if poly.center.z<1.06 else 'White'] if paint else tuple(a.data[li].color[:3])+((.02 if a.data[li].color[3]<.08 else 1),)
obj.data.materials.clear();obj.data.materials.append(shader());vox={};q=.04;box,line,word=voxel_helpers(vox,q);top=1.72

for side in [-1,1]:box((0,side*.4,top+.02),(.24,.16,.08),'Rubber')
box((0,0,top+.06),(.32,1.36,.08),'Rubber');box((0,-.40,top+.14),(.24,.48,.12),'Red');box((0,.40,top+.14),(.24,.48,.12),'Blue');box((0,0,top+.14),(.24,.24,.12),'White')
for side in [-1,1]:word('POLICIA',-.1,side*.975,.76,'White','door_L' if side<0 else 'door_R')
extra,_=mesh_vox('PatrolDetails',vox,q,rig);obj=join_meshes(obj,extra)
# More cabin room without changing the character or breaking the four-centimeter grid.
for v in obj.data.vertices:v.co=Vector(round(c*1.08/.04)*.04 for c in v.co)
obj.data.update();bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for b in rig.data.edit_bones:b.head=Vector(round(c*1.08/.04)*.04 for c in b.head);b.tail=Vector(round(c*1.08/.04)*.04 for c in b.tail)
bpy.ops.object.mode_set(mode='OBJECT');save_export(obj,rig,'SK_PolicePatrol',1)

# Four full-size motorcycle variants, with independently rigged wheels and steering.
for name,paint,police,cargo in [('SK_MotoCivilBlue','CivilBlue',False,False),('SK_MotoCivilRed','CivilRed',False,False),('SK_MotoCourier','CivilBlue',False,True),('SK_MotoPolice','White',True,False),('SK_MotoCivilYellow','CivilYellow',False,False),('SK_MotoCivilPurple','CivilPurple',False,False),('SK_MotoCivilWhite','CivilWhite',False,True),('SK_MotoPoliceGreen','Green',True,False)]:
 bpy.ops.wm.read_factory_settings(use_empty=True);vox={};q=.04;box,line,word=voxel_helpers(vox,q)
 box((0,0,.52),(.56,.40,.32),'Steel');box((.26,0,.86),(.48,.40,.28),paint);box((-.28,0,.84),(.64,.36,.12),'Rubber');box((-.62,0,.78),(.24,.40,.24),paint);box((-.76,0,.84),(.04,.24,.08),'Red');line((-.68,0,.36),(.16,0,.68),.08,'Navy')
 for side in [-1,1]:
  line((.44,side*.12,1.08),(.72,side*.12,.36),.08,'Chrome','steer');box((.36,side*.28,1.16),(.16,.16,.08),'Rubber','steer');line((.36,side*.20,1.16),(.44,side*.40,1.40),.04,'Navy','steer');box((.44,side*.40,1.40),(.16,.08,.12),'Chrome','steer');box((-.12,side*.24,.36),(.28,.12,.08),'Steel');box((-.44,side*.27,.44),(.72,.12,.12),'Navy')
 box((.36,0,1.16),(.08,.64,.08),'Chrome','steer');box((.52,0,1.06),(.24,.40,.28),paint,'steer');box((.66,0,1.08),(.04,.24,.16),'Lamp','steer')
 for axle in [-.72,.72]:
  bone='wheel_front' if axle>0 else 'wheel_rear'
  for x in range(round((axle-.36)/q),round((axle+.36)/q)+1):
   for z in range(0,19):
    r=math.hypot((x+.5)*q-axle,(z+.5)*q-.36)
    if .265<r<.36:box(((x+.5)*q,0,(z+.5)*q),(q,.20,q),'Rubber',bone)
    elif .20<r<.265:box(((x+.5)*q,0,(z+.5)*q),(q,.12,q),'Chrome',bone)
    elif r<.20 and (abs((x+.5)*q-axle)<.045 or abs((z+.5)*q-.36)<.045):box(((x+.5)*q,0,(z+.5)*q),(q,.08,q),'Steel',bone)
  box((axle,0,.36),(.12,.24,.12),'Chrome',bone)
 if police:
  for side in [-1,1]:box((-.52,side*.32,.73),(.48,.24,.44),'White');box((-.52,side*.45,.75),(.40,.04,.12),'Green');box((.52,side*.24,1.12),(.12,.12,.12),'Blue' if side>0 else 'Red','steer')
  box((.24,-.22,.88),(.40,.04,.08),'Green');box((.24,.22,.88),(.40,.04,.08),'Green')
 if cargo:box((-.60,0,1.12),(.48,.52,.48),'CivilRed');box((-.60,0,1.38),(.52,.56,.04),'Rubber')
 bones={'root':((0,0,0),(0,0,.3),None),'steer':((.72,0,.36),(.72,0,.66),'root'),'wheel_front':((.72,0,.36),(.72,.16,.36),'steer'),'wheel_rear':((-.72,0,.36),(-.72,.16,.36),'root')};obj,rig=mesh_vox(name,vox,q,bones=bones);save_export(obj,rig,name,1)

# Police character retains the established citizen's silhouette, eyes, hair and skinning.
for officer_name,citizen in [('SK_PoliceOfficer',12),('SK_PoliceOfficerMale02',20),('SK_PoliceOfficerFemale01',1),('SK_PoliceOfficerFemale02',38)]:
 bpy.ops.wm.open_mainfile(filepath=str(root/f'outputs/DeliveryArt/Crowd/SK_Citizen{citizen:02d}.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');obj=next(o for o in bpy.data.objects if o.type=='MESH');uv=obj.data.uv_layers.active;image=next(m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links[0].from_node.image for m in obj.data.materials if m and m.use_nodes);pixels=list(image.pixels);width,height=image.size;groups=[g.name for g in obj.vertex_groups];a=obj.data.color_attributes.new(name='ServiceColor',type='FLOAT_COLOR',domain='CORNER')
 for poly in obj.data.polygons:
  v=obj.data.vertices[poly.vertices[0]];bone=groups[max(v.groups,key=lambda g:g.weight).group] if v.groups else 'root';cloth=any(s in bone for s in ['spine','pelvis','thigh','calf','upperarm','lowerarm','clavicle']);boot='foot' in bone or 'ball' in bone
  if poly.center.z>130 and abs(poly.center.x)<28:cloth=False;boot=False
  for li in poly.loop_indices:
   xy=sum((uv.data[j].uv for j in poly.loop_indices),Vector((0,0)))/len(poly.loop_indices);x=min(width-1,max(0,int(xy.x*width)));y=min(height-1,max(0,int(xy.y*height)));i=(y*width+x)*4;c=tuple(pixels[i:i+3])+ (1,)
   if cloth:
    base=COL['Navy' if any(s in bone for s in ['pelvis','thigh','calf']) else 'Green'];shade=max(.72,min(1.12,.80+sum(c[:3])*.18));c=tuple(v*shade for v in base[:3])+(1,)
   if boot:c=COL['Rubber']
   a.data[li].color=c
 obj.data.materials.clear();obj.data.materials.append(shader());vox={};q=2.25;box,line,word=voxel_helpers(vox,q);head_top=max(v.co.z for v in obj.data.vertices)-4.5;box((0,0,head_top+2.25),(36,31.5,4.5),'Green','head');box((0,0,head_top+6.75),(31.5,27,4.5),'Green','head');box((0,-18,head_top),(36,9,2.25),'Navy','head');box((0,-15.75,head_top+4.5),(4.5,2.25,4.5),'Gold','head');box((0,-15.75,112.5),(27,2.25,4.5),'Reflect','spine_03');extra,_=mesh_vox('PoliceUniformDetails',vox,q,rig);obj=join_meshes(obj,extra);save_export(obj,rig,officer_name,.01)
(out/'pixel_palette.json').write_text(json.dumps(pixel_palette));assert len(pixel_palette)<=4096
(out/'manifest.json').write_text(json.dumps({'style':'Existing voxel SUV and citizen sources; stepped four-centimeter vehicle grid; shared citizen skinning; no smooth geometry','models':report},ensure_ascii=False,indent=2));print('SERVICE_FLEET_BLENDER_PASS',flush=True)


