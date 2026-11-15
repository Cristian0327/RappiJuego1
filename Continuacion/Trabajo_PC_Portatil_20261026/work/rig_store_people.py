import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/People';OUT.mkdir(exist_ok=True)
names=['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']
spec=[(.68,1.15,.40),(.72,1.24,.52),(.77,1.26,.36),(.75,1.23,.36),(.73,1.20,.38),(.77,1.26,.39),(.75,1.23,.39),(.72,1.24,.39)]
report=[]
for role,name in enumerate(names):
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'outputs/DeliveryArt/HighFidelity'/('SM_'+name+'.blend')))
 obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');obj.name='SK_'+name
 # Split greedy rectangles on the original voxel lattice before skinning.
 # This removes T-junction cracks while retaining the authored silhouette and colors.
 verts=[];faces=[];mats=[];old=obj.data
 for poly in old.polygons:
  corners=[old.vertices[i].co.copy() for i in poly.vertices]
  if len(corners)!=4:
   start=len(verts);verts.extend(corners);faces.append(tuple(range(start,len(verts))));mats.append(poly.material_index);continue
  a,b,c,d=corners;nu=max(1,round((b-a).length/.0225));nv=max(1,round((d-a).length/.0225))
  start=len(verts)
  for j in range(nv+1):
   for i in range(nu+1):verts.append(a+(b-a)*(i/nu)+(d-a)*(j/nv))
  for j in range(nv):
   for i in range(nu):
    k=start+j*(nu+1)+i;faces.append((k,k+1,k+nu+2,k+nu+1));mats.append(poly.material_index)
 mesh=bpy.data.meshes.new('SkinTopology');mesh.from_pydata(verts,[],faces)
 for m in old.materials:mesh.materials.append(m)
 for p,mi in zip(mesh.polygons,mats):p.material_index=mi
 obj.data=mesh
 # One palette atlas/material per character instead of a section per voxel color.
 image=bpy.data.images.new('NPCPalette',width=64,height=64,alpha=True);pixels=[0.0]*(64*64*4)
 for i,mat in enumerate(obj.data.materials):
  c=mat.diffuse_color
  for y in range((i//8)*8,(i//8)*8+8):
   for x in range((i%8)*8,(i%8)*8+8):pixels[(y*64+x)*4:(y*64+x)*4+4]=list(c)
 image.pixels=pixels;image.filepath_raw=str(OUT/'NPCPalette.png');image.file_format='PNG';image.save();image.pack()
 uv=obj.data.uv_layers.new(name='Palette')
 for p in obj.data.polygons:
  i=p.material_index
  for li in p.loop_indices:uv.data[li].uv=((i%8+.5)/8,(i//8+.5)/8)
  p.material_index=0
 obj.data.materials.clear();atlas=bpy.data.materials.new('NPC_Atlas');atlas.use_nodes=True;tex=atlas.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest';atlas.node_tree.links.new(tex.outputs['Color'],atlas.node_tree.nodes['Principled BSDF'].inputs['Base Color']);obj.data.materials.append(atlas)
 leg,shoulder,w=spec[role]
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='Rig_'+name
 bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
 def bone(n,a,b,parent=None):
  e=rig.data.edit_bones.new(n);e.head=a;e.tail=b
  if parent:e.parent=rig.data.edit_bones[parent]
 bone('root',(0,0,0),(0,0,.15));bone('pelvis',(0,0,leg),(0,0,leg+.12),'root');bone('spine',(0,0,leg+.12),(0,0,shoulder-.10),'pelvis');bone('head',(0,0,shoulder+.08),(0,0,shoulder+.40),'spine')
 for s,side in [(-1,'L'),(1,'R')]:
  x=s*(.145 if role==1 else .105)
  bone('thigh_'+side,(x,0,leg),(x,0,.43),'pelvis');bone('shin_'+side,(x,0,.43),(x,0,.17),'thigh_'+side);bone('foot_'+side,(x,0,.17),(x,-.17,.10),'shin_'+side)
  bone('upperarm_'+side,(s*w*.47,0,shoulder-.06),(s*w*.68,-.012,shoulder-.27),'spine');bone('forearm_'+side,(s*w*.68,-.012,shoulder-.27),(s*w*.71,-.025,shoulder-.48),'upperarm_'+side);bone('hand_'+side,(s*w*.71,-.025,shoulder-.48),(s*w*.71,-.05,shoulder-.62),'forearm_'+side)
 bpy.ops.object.mode_set(mode='OBJECT')
 groups={b.name:obj.vertex_groups.new(name=b.name) for b in rig.data.bones}
 # Coincident vertices share weights: greedy voxel faces must not split at joints.
 for v in obj.data.vertices:
  x,y,z=v.co;side='L' if x<0 else 'R'
  def blend(a,b,t):
   t=max(0.,min(1.,t))
   if t<1:groups[a].add([v.index],1-t,'REPLACE')
   if t>0:groups[b].add([v.index],t,'REPLACE')
  if z>shoulder+.02:blend('spine','head',(z-shoulder-.02)/.10)
  elif abs(x)>w*.51 and z>leg-.02:
   if z>shoulder-.32:blend('forearm_'+side,'upperarm_'+side,(z-(shoulder-.32))/.12)
   else:blend('hand_'+side,'forearm_'+side,(z-(shoulder-.54))/.12)
  elif z<leg+.05:
   if z<.30:blend('foot_'+side,'shin_'+side,(z-.18)/.12)
   elif z<.52:blend('shin_'+side,'thigh_'+side,(z-.40)/.12)
   else:blend('thigh_'+side,'pelvis',(z-leg+.06)/.11)
  else:blend('pelvis','spine',(z-leg-.02)/.20)
 mod=obj.modifiers.new('Voxel rigid skin','ARMATURE');mod.object=rig;obj.parent=rig
 sc=bpy.context.scene;sc.render.fps=24;sc.frame_start=1;sc.frame_end=97
 for frame in range(1,98,4):
  phase=(frame-1)/96*math.tau
  for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0)
  rig.pose.bones['spine'].rotation_euler[1]=math.sin(phase)*.018
  rig.pose.bones['head'].rotation_euler[1]=math.sin(phase)*.025;rig.pose.bones['head'].rotation_euler[2]=math.sin(phase*.0+phase)*.065
  for side,offset in [('L',0),('R',1.1)]:
   rig.pose.bones['upperarm_'+side].rotation_euler[0]=-.12-.08*math.sin(phase+offset)
   rig.pose.bones['forearm_'+side].rotation_euler[0]=-.18-.12*math.sin(phase+offset)
  for b in rig.pose.bones:b.keyframe_insert('rotation_euler',frame=frame,group=b.name)
 rig.animation_data.action.name='A_'+name+'_Work';sc.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);obj.select_set(True);bpy.context.view_layer.objects.active=rig
 sc['style_reference']='outputs/view_hero.png';sc['voxel_size']=.0225
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('SK_'+name+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(OUT/('SK_'+name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=.5,axis_forward='-Y',axis_up='Z')
 report.append({'asset':'SK_'+name,'bones':len(rig.data.bones),'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons),'animation':'A_'+name+'_Work','duration_seconds':4,'rigid_weights':True})
(OUT/'rig_manifest.json').write_text(json.dumps(report,indent=2));print('FIVE_RIGGED_PEOPLE_EXPORTED')
