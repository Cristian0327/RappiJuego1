import bpy, bmesh, math, json, random
from pathlib import Path
from collections import defaultdict, deque
from mathutils import Vector, Quaternion
import numpy as np

BASE=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto')
# Reuse the approved silhouette and palette; replace the entire mesh/rig pipeline.
source=(BASE/'work/build_character.py').read_text(encoding='utf8')
exec(compile(source.split('# Remove overlaps')[0], 'approved_voxel_shapes', 'exec'))
OUT=BASE/'outputs/unreal_v2';OUT.mkdir(parents=True,exist_ok=True)
UNIT=2.25 # centimeters; transforms remain identity in both the mesh and skeleton.
scene.unit_settings.scale_length=.01
scene.unit_settings.length_unit='CENTIMETERS'
scene.render.fps=30
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4

vox={}
for p,vs in parts.items():
 for q,m in vs.items():vox[q]=(m,bone_for[p],p)

# Close the skull/temple gap: the old ear cut removed an entire band of hair,
# leaving no continuous scalp behind it. Fill only missing cells, preserving skin/hair.
def fill(m,b,x0,x1,y0,y1,z0,z1,replace=False):
 for x in range(x0,x1):
  for y in range(y0,y1):
   for z in range(z0,z1):
    if replace or (x,y,z) not in vox:vox[x,y,z]=(m,b,'repair')
fill('skin','head',-8,8,-6,7,60,70)
fill('skin','head',-8,8,-8,-6,65,69)
fill('skin','head',7,10,-4,2,61,65)
fill('skin','head',-10,-7,-4,2,61,65)
fill('hair','head',8,10,-6,-4,65,70)
fill('hair','head',-10,-8,-6,-4,65,70)
fill('hair_dark','head',-3,3,7,9,69,74)
# Emblem and nose are part of the same closed surface. Eyes are painted, not loose cubes.
fill('ice_light','head',-4,4,-9,-8,72,79,True)
fill('skin_light','head',-1,1,-9,-8,60,61,True)

# Keep clearance below the armpits: no accidental sleeve-to-harness weld along the arm.
for q,(_,b,p) in list(vox.items()):
 x,y,z=q
 if b=='chest' and 39<=z<49 and (x==9 or x==-10) and y<5:del vox[q]

dirs=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def neighbors(q):
 return [(q[0]+d[0],q[1]+d[1],q[2]+d[2]) for d in dirs]
def components(cells):
 rem=set(cells);cs=[]
 while rem:
  start=rem.pop();todo=[start];c={start}
  while todo:
   for nb in neighbors(todo.pop()):
    if nb in rem:rem.remove(nb);c.add(nb);todo.append(nb)
  cs.append(c)
 return sorted(cs,key=len,reverse=True)
cs=components(vox)
print('VOXEL_COMPONENTS_BEFORE',list(map(len,cs)),flush=True)
# Minor isolated original tufts can be joined by the shortest voxel bridge.
while len(cs)>1:
 small=cs[-1];large=set().union(*cs[:-1]);best=None
 for a in small:
  for d in range(1,5):
   for axis in range(3):
    for sign in [-1,1]:
     b=list(a);b[axis]+=d*sign;b=tuple(b)
     if b in large and (best is None or d<best[0]):best=(d,a,axis,sign)
 if best is None:raise RuntimeError('Disconnected silhouette requires review')
 d,a,axis,sign=best
 for i in range(1,d):
  q=list(a);q[axis]+=i*sign;vox[tuple(q)]=vox[a]
 cs=components(vox)

# Resolve voxel configurations touching only at an edge (nonmanifold cross sections).
repairs=0
for iteration in range(12):
 changes={}
 for x,y,z in list(vox):
  q=(x,y,z)
  for axis in range(3):
   a=(axis+1)%3;b=(axis+2)%3
   for da in [-1,1]:
    for db in [-1,1]:
     pa=list(q);pa[a]+=da;pb=list(q);pb[b]+=db
     pc=list(pa);pc[b]+=db
     pa,pb,pc=tuple(pa),tuple(pb),tuple(pc)
     if pc in vox and pa not in vox and pb not in vox:
      # Prefer the less exposed bridge to minimize silhouette changes.
      choose=max([pa,pb],key=lambda k:sum(n in vox for n in neighbors(k)))
      changes[choose]=vox[q]
 if not changes:break
 vox.update(changes);repairs+=len(changes)

# Remove all enclosed air pockets before surface extraction.
mins=[min(q[i] for q in vox)-1 for i in range(3)]
maxs=[max(q[i] for q in vox)+1 for i in range(3)]
ext={tuple(mins)};queue=deque(ext)
while queue:
 q=queue.popleft()
 for n in neighbors(q):
  if n in vox or n in ext or any(n[i]<mins[i] or n[i]>maxs[i] for i in range(3)):continue
  ext.add(n);queue.append(n)
cavities=0
for x in range(mins[0]+1,maxs[0]):
 for y in range(mins[1]+1,maxs[1]):
  for z in range(mins[2]+1,maxs[2]):
   q=x,y,z
   if q not in vox and q not in ext:
    vox[q]=('hair' if z>56 else 'cloth','head' if z>56 else 'chest','interior');cavities+=1
print('REPAIRED_EDGES',repairs,'FILLED_CAVITIES',cavities,flush=True)

# Greedy meshing on the UNION, rather than closing every former component separately.
# Keep extra surface loops where elbows, knees, wrists, shoulders and spine must bend.
zcuts={7,9,11,16,18,20,28,30,32,36,38,40,42,44,46,49,51,53,55,57,59}
buckets=defaultdict(dict)
for q,(m,b,p) in vox.items():
 for axis in range(3):
  a=(axis+1)%3;c=(axis+2)%3
  for sign in [-1,1]:
   n=list(q);n[axis]+=sign
   if tuple(n) in vox:continue
   buckets[axis,sign,q[axis]+(sign==1)][q[a],q[c]]=m
surfaces=[]
for (axis,sign,plane),mask in buckets.items():
 a=(axis+1)%3;b=(axis+2)%3
 while mask:
  u,v=min(mask,key=lambda q:(q[1],q[0]));m=mask[u,v];w=h=1
  while mask.get((u+w,v))==m and not (a==2 and u+w in zcuts):w+=1
  while all(mask.get((u+i,v+h))==m for i in range(w)) and not (b==2 and v+h in zcuts):h+=1
  for i in range(w):
   for j in range(h):del mask[u+i,v+j]
  surfaces.append(dict(axis=axis,sign=sign,plane=plane,u=u,v=v,w=w,h=h,m=m))

# One UV atlas. Facial features and badge graphics are rasterized onto connected surfaces.
TEXELS=4;PAD=3;size=1024
def pack(size):
 x=y=PAD;row=0
 for f in sorted(surfaces,key=lambda f:f['h'],reverse=True):
  w=f['w']*TEXELS+2*PAD;h=f['h']*TEXELS+2*PAD
  if x+w>size:x=PAD;y+=row;row=0
  if y+h>size:return False
  f['tx']=x+PAD;f['ty']=y+PAD;x+=w;row=max(row,h)
 return True
while not pack(size):size*=2
pixels=np.ones((size,size,4),dtype=np.float32);pixels[:,:,:3]=.15
paint=[d for d in details if any(s in d[0] for s in ['eyebrow','eye /','mouth','badge / dark','badge / orange'])]
for f in surfaces:
 a=(f['axis']+1)%3;b=(f['axis']+2)%3
 for j in range(-PAD,f['h']*TEXELS+PAD):
  for i in range(-PAD,f['w']*TEXELS+PAD):
   ii=max(0,min(f['w']*TEXELS-1,i));jj=max(0,min(f['h']*TEXELS-1,j))
   pos=[0.,0.,0.];pos[f['axis']]=f['plane'];pos[a]=f['u']+(ii+.5)/TEXELS;pos[b]=f['v']+(jj+.5)/TEXELS
   m=f['m'];factor=1.
   if f['axis']==1 and f['sign']==-1:
    for name,col,(x0,x1,y0,y1,z0,z1),bone in paint:
     # Half texel coverage preserves a fine pixel mouth.
     if x0<=pos[0]<x1 and z0-.125<=pos[2]<z1+.125:
      if ('badge' in name and f['plane']==-9) or ('badge' not in name and f['plane']==-8):m=col
   uu=math.floor(pos[a]/2);vv=math.floor(pos[b]/2)
   noise=((uu*73856093 ^ vv*19349663 ^ f['plane']*83492791)&255)/255
   factor=.988+noise*.024
   if (ii+f['u']*TEXELS)%8==0 or (jj+f['v']*TEXELS)%8==0:factor*=.978
   pixels[f['ty']+j,f['tx']+i,:3]=np.clip(np.array(rgb[m])*factor,0,1)
tex=bpy.data.images.new('T_VoxelExplorer_BaseColor',width=size,height=size,alpha=False)
tex.pixels.foreach_set(pixels.ravel());tex.filepath_raw=str(OUT/'T_VoxelExplorer_BaseColor.png');tex.file_format='PNG';tex.save();tex.pack()
mat=bpy.data.materials.new('M_VoxelExplorer');mat.use_nodes=True
bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.87;bs.inputs['Specular IOR Level'].default_value=.18
im=mat.node_tree.nodes.new('ShaderNodeTexImage');im.image=tex;im.interpolation='Closest';mat.node_tree.links.new(im.outputs['Color'],bs.inputs['Base Color'])

# Resolve every T-junction geometrically before triangulation, so adjacent faces share edges.
verts=[];vid={};quads=[]
for f in surfaces:
 rect=[(0,0),(f['w'],0),(f['w'],f['h']),(0,f['h'])]
 if f['sign']<0:rect.reverse()
 ids=[]
 for du,dv in rect:
  q=[0,0,0];q[f['axis']]=f['plane'];q[(f['axis']+1)%3]=f['u']+du;q[(f['axis']+2)%3]=f['v']+dv;q=tuple(q)
  if q not in vid:vid[q]=len(verts);verts.append(q)
  ids.append(vid[q])
 quads.append(ids)
lines=defaultdict(list)
for idx,q in enumerate(verts):
 for axis in range(3):lines[axis,q[(axis+1)%3],q[(axis+2)%3]].append((q[axis],idx))
for line in lines.values():line.sort()
faces=[];uvs=[]
for ids,f in zip(quads,surfaces):
 face=[];uv=[]
 for i,idx in enumerate(ids):
  q=verts[idx];r=verts[ids[(i+1)%4]];axis=next(a for a in range(3) if q[a]!=r[a])
  points=[(q[axis],idx)]+[(t,k) for t,k in lines[axis,q[(axis+1)%3],q[(axis+2)%3]] if min(q[axis],r[axis])<t<max(q[axis],r[axis])]
  points.sort(reverse=r[axis]<q[axis])
  for t,k in points:
   face.append(k);qq=verts[k];du=qq[(f['axis']+1)%3]-f['u'];dv=qq[(f['axis']+2)%3]-f['v']
   uv.append(((f['tx']+du*TEXELS)/size,(f['ty']+dv*TEXELS)/size))
 faces.append(face);uvs.append(uv)
collection=bpy.data.collections.new('UNREAL | one mesh + skeleton');scene.collection.children.link(collection)
mesh=bpy.data.meshes.new('VoxelExplorer_ContinuousSurface');mesh.from_pydata([tuple(c*UNIT for c in q) for q in verts],[],faces);mesh.update()
uv=mesh.uv_layers.new(name='UVMap')
for p,coords in zip(mesh.polygons,uvs):
 for li,co in zip(p.loop_indices,coords):uv.data[li].uv=co
ob=bpy.data.objects.new('SK_VoxelExplorer',mesh);collection.objects.link(ob);mesh.materials.append(mat)
bm=bmesh.new();bm.from_mesh(mesh)
bad=[e for e in bm.edges if not e.is_manifold]
print('SURFACE_BEFORE_TRIANGULATION',len(verts),len(faces),'NONMANIFOLD_EDGES',len(bad),flush=True)
if bad:
 print('BAD_EDGES',[(tuple(e.verts[0].co/UNIT),tuple(e.verts[1].co/UNIT),len(e.link_faces)) for e in bad][:30],flush=True)
 raise RuntimeError('Surface is not watertight')
bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()

# One rooted biped hierarchy, with physically connected elbow/wrist/knee/ankle chains.
arm=bpy.data.armatures.new('SKEL_VoxelExplorer');rig=bpy.data.objects.new('Armature',arm);collection.objects.link(rig)
rig.show_in_front=True;arm.display_type='OCTAHEDRAL'
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
bones={}
def addbone(name,head,tail,parent=None,connected=False):
 eb=arm.edit_bones.new(name);eb.head=Vector(head)*UNIT;eb.tail=Vector(tail)*UNIT
 if parent:eb.parent=bones[parent];eb.use_connect=connected
 eb.use_deform=True;bones[name]=eb
addbone('root',(0,0,0),(0,0,3))
addbone('pelvis',(0,0,30),(0,0,37),'root')
addbone('spine_01',(0,0,37),(0,0,43),'pelvis',True)
addbone('spine_02',(0,0,43),(0,0,49),'spine_01',True)
addbone('spine_03',(0,0,49),(0,0,53),'spine_02',True)
addbone('neck_01',(0,0,53),(0,0,58),'spine_03',True)
addbone('head',(0,0,58),(0,0,74),'neck_01',True)
for s,suf in [(1,'l'),(-1,'r')]:
 addbone('clavicle_'+suf,(0,0,53),(s*10,0,51),'spine_03',True)
 addbone('upperarm_'+suf,(s*10,0,51),(s*12,-.4,44),'clavicle_'+suf,True)
 addbone('lowerarm_'+suf,(s*12,-.4,44),(s*13,0,31),'upperarm_'+suf,True)
 addbone('hand_'+suf,(s*13,0,31),(s*13,-.3,27),'lowerarm_'+suf,True)
 addbone('thigh_'+suf,(s*5,0,30),(s*5,-.5,18),'pelvis')
 addbone('calf_'+suf,(s*5,-.5,18),(s*5,0,9),'thigh_'+suf,True)
 addbone('foot_'+suf,(s*5,0,9),(s*5,-5,3),'calf_'+suf,True)
 addbone('ball_'+suf,(s*5,-5,3),(s*5,-8,3),'foot_'+suf,True)
bpy.ops.object.mode_set(mode='OBJECT')
def blend(a,b,t):
 t=max(0.,min(1.,t));return {a:1-t,b:t}
def chain(z,entries):
 # Entries are bone names at their fully weighted height; interpolate only near joints.
 for low,high,ba,bb in entries:
  if z<low:return {ba:1.}
  if z<=high:return blend(ba,bb,(z-low)/(high-low))
 return {entries[-1][3]:1.}
def weights_for_region(q,region,p):
 x,y,z=q;suf='l' if x>=0 else 'r'
 if region=='head':return blend('neck_01','head',(z-56)/3)
 if region=='chest':
  if 'Backpack' in p:return {'spine_03':1.}
  wt=chain(z,[(36,40,'pelvis','spine_01'),(42,46,'spine_01','spine_02'),(48,51,'spine_02','spine_03')])
  if abs(x)>6 and z>=49 and y<5:
   t=min(1,(abs(x)-6)/4)*min(1,(z-48)/3)
   wt={b:w*(1-t) for b,w in wt.items()};wt['clavicle_'+suf]=t
  return wt
 if region=='pelvis':return {'pelvis':1.}
 if region.startswith(('upper_arm','forearm','hand')):
  wt=chain(z,[(30,32,'hand_'+suf,'lowerarm_'+suf),(42,46,'lowerarm_'+suf,'upperarm_'+suf),(50,53,'upperarm_'+suf,'clavicle_'+suf)])
  return wt
 if region.startswith(('thigh','shin','foot')):
  wt=chain(z,[(7,11,'foot_'+suf,'calf_'+suf),(16,20,'calf_'+suf,'thigh_'+suf),(28,32,'thigh_'+suf,'pelvis')])
  if z<5 and y<-4:wt=blend('foot_'+suf,'ball_'+suf,(-y-4)/3)
  return wt
 raise ValueError(region)
groups={b.name:ob.vertex_groups.new(name=b.name) for b in arm.bones}
for v in mesh.vertices:
 q=tuple(round(c/UNIT) for c in v.co);regions=[]
 for dx in [-1,0]:
  for dy in [-1,0]:
   for dz in [-1,0]:
    n=q[0]+dx,q[1]+dy,q[2]+dz
    if n in vox:regions.append(vox[n][1:])
 totals=defaultdict(float)
 for region,p in regions:
  for b,w in weights_for_region(q,region,p).items():totals[b]+=w/len(regions)
 ordered=sorted(totals.items(),key=lambda t:t[1],reverse=True)[:4];total=sum(w for _,w in ordered)
 for b,w in ordered:
  if w>1e-7:groups[b].add([v.index],w/total,'REPLACE')
mod=ob.modifiers.new('Skin | shared joint weights','ARMATURE');mod.object=rig;ob.parent=rig
rig['Design']='Connected biped chains. Pelvis/root and thighs use normal parent offsets. Custom skeleton, not drop-in Manny.'
rig['Units']='centimeters, identity object scales, one root at ground origin'
ob['Topology']='One connected watertight triangle surface; no interior faces or detached pixel cubes.'

def worldrot(name,axis,degrees):
 pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION'
 local=pb.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
 pb.rotation_quaternion=Quaternion(local,math.radians(degrees))
def reset_pose():
 for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
def select_export():
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);ob.select_set(True);bpy.context.view_layer.objects.active=rig

# Bind with arms opened 35 degrees to give animation and retargeting useful clearance.
for s,suf in [(1,'l'),(-1,'r')]:worldrot('upperarm_'+suf,(0,1,0),-35*s)
bpy.context.view_layer.update();bpy.context.view_layer.objects.active=ob
bpy.ops.object.modifier_apply(modifier=mod.name)
mesh=ob.data
bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='POSE');bpy.ops.pose.armature_apply(selected=False);bpy.ops.object.mode_set(mode='OBJECT')
mod=ob.modifiers.new('Skin | shared joint weights','ARMATURE');mod.object=rig

# Native file has two objects only. Preview setup is added later to a separate scene.
scene.name='GAME_ASSET'
reset_pose();select_export()
scene.frame_start=1;scene.frame_end=61
fbx_common=dict(use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,use_armature_deform_only=True,armature_nodetype='NULL',path_mode='COPY',embed_textures=True,bake_anim_use_all_bones=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0)
bpy.ops.export_scene.fbx(filepath=str(OUT/'SK_VoxelExplorer.fbx'),bake_anim=False,**fbx_common)

def add_action(name,end,pose_fn):
 rig.animation_data_create();rig.animation_data.action=None
 action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
 for frame in range(1,end+1):
  reset_pose();pose_fn((frame-1)/(end-1))
  for pb in rig.pose.bones:
   pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
   if pb.name in ['root','pelvis']:pb.keyframe_insert('location',frame=frame,group=pb.name)
 action['Description']='Authored test/demo motion. Custom voxel skeleton.'
 return action
def lowered_arms():
 for s,suf in [(1,'l'),(-1,'r')]:worldrot('upperarm_'+suf,(0,1,0),35*s)
def idle(t):
 lowered_arms();w=math.sin(2*math.pi*t)
 worldrot('spine_02',(1,0,0),w*.5);worldrot('head',(0,0,1),w*1.4)
 rig.pose.bones['pelvis'].location.z=w*.18
def walk(t):
 lowered_arms();w=math.sin(2*math.pi*t)
 rig.pose.bones['pelvis'].location.z=.7*math.sin(4*math.pi*t)
 worldrot('spine_02',(0,0,1),-w*2)
 for s,suf in [(1,'l'),(-1,'r')]:
  ph=2*math.pi*t+(0 if s==1 else math.pi)
  worldrot('thigh_'+suf,(1,0,0),24*math.sin(ph))
  worldrot('calf_'+suf,(1,0,0),-max(0,math.sin(ph))*32)
  worldrot('foot_'+suf,(1,0,0),max(0,math.sin(ph))*8)
  # Composite arm swing in the local space of the already-lowered arm.
  pb=rig.pose.bones['upperarm_'+suf]
  axis=pb.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0))
  pb.rotation_quaternion=Quaternion(axis,-.2*math.sin(ph))@pb.rotation_quaternion
  worldrot('lowerarm_'+suf,(1,0,0),8+5*math.sin(ph))
def testpose(t):
 a=math.sin(math.pi*t)
 worldrot('head',(0,0,1),30*a);worldrot('neck_01',(1,0,0),5*a)
 worldrot('spine_01',(0,0,1),-6*a);worldrot('spine_02',(1,0,0),6*a);worldrot('spine_03',(0,0,1),5*a)
 for s,suf in [(1,'l'),(-1,'r')]:
  worldrot('clavicle_'+suf,(0,1,0),-s*4*a)
  worldrot('upperarm_'+suf,(1,0,0),s*25*a)
  worldrot('lowerarm_'+suf,(1,0,0),70*a)
  worldrot('hand_'+suf,(0,0,1),s*18*a)
  worldrot('thigh_'+suf,(1,0,0),s*20*a)
  worldrot('calf_'+suf,(1,0,0),-45*a)
  worldrot('foot_'+suf,(1,0,0),15*a)
  worldrot('ball_'+suf,(1,0,0),10*a)
actions={}
for name,end,fn in [('Idle',61,idle),('Walk_InPlace',31,walk),('Rig_Test',61,testpose)]:
 actions[name]=add_action(name,end,fn);scene.frame_end=end;scene.frame_set(1);select_export()
 animation_options=dict(fbx_common,object_types={'ARMATURE'},embed_textures=False,path_mode='AUTO')
 bpy.ops.export_scene.fbx(filepath=str(OUT/('AN_'+name+'.fbx')),bake_anim=True,**animation_options)

rig.animation_data.action=actions['Idle'];scene.frame_end=61;scene.frame_set(1)
select_export()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   s=area.spaces.active;s.shading.type='MATERIAL';s.overlay.show_floor=False
   s.clip_end=10000;s.region_3d.view_distance=290;s.region_3d.view_location=(0,0,95)
   s.region_3d.view_rotation=(Vector((300,-600,230))-Vector((0,0,95))).to_track_quat('Z','Y')
   s.region_3d.view_perspective='ORTHO'
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='DESELECT')
arm.bones.active=arm.bones['pelvis']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'VoxelExplorer_Unreal.blend'),compress=True)

# Automated topology/weights audit in the final bind mesh.
bm=bmesh.new();bm.from_mesh(mesh)
remaining=set(bm.verts);nc=0
while remaining:
 nc+=1;todo=[remaining.pop()]
 while todo:
  v=todo.pop()
  for e in v.link_edges:
   n=e.other_vert(v)
   if n in remaining:remaining.remove(n);todo.append(n)
audit={'mesh_objects':1,'connected_components':nc,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'triangles':len(mesh.polygons),'vertices':len(mesh.vertices),'bones':len(arm.bones),'connected_bones':sum(b.use_connect for b in arm.bones),'root_bones':[b.name for b in arm.bones if not b.parent],'max_weights':max(len(v.groups) for v in mesh.vertices),'weights_normalized':all(abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in mesh.vertices),'materials':1,'texture_size':size,'bind_pose':'A-pose','units':'cm','clips':list(actions),'unreal_editor_tested':False}
bm.free();assert nc==1 and audit['boundary_edges']==0 and audit['nonmanifold_edges']==0
assert audit['weights_normalized'] and audit['max_weights']<=4
(OUT/'validation.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
print('ASSET_AUDIT',audit,flush=True)

# Render in this background session only; do not pollute the game-asset file with a stage.
bpy.ops.object.mode_set(mode='OBJECT');rig.hide_set(True)
bpy.ops.mesh.primitive_plane_add(size=20000,location=(0,0,-.8));floor=bpy.context.object
fm=bpy.data.materials.new('Preview floor');fm.diffuse_color=(.025,.025,.025,1);floor.data.materials.append(fm)
for name,loc,power,size in [('Key',(-300,-400,500),4500000,400),('Fill',(300,-200,250),2700000,300),('Rim',(100,300,400),5500000,300)]:
 d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;o.rotation_euler=(Vector((0,0,95))-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('Preview');cam=bpy.data.objects.new('Preview',camd);scene.collection.objects.link(cam);camd.type='ORTHO';camd.ortho_scale=215;camd.clip_end=10000;scene.camera=cam
scene.render.resolution_x=720;scene.render.resolution_y=1080;scene.cycles.samples=32
for name,loc,act,frame in [('hero',(300,-600,235),'Idle',1),('side',(700,0,93),'Idle',1),('back',(0,700,93),'Idle',1),('articulations',(300,-600,235),'Rig_Test',31)]:
 rig.animation_data.action=actions[act];scene.frame_set(frame);cam.location=loc;cam.rotation_euler=(Vector((0,0,95))-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDER',name,flush=True)
print('UNREAL_BUILD_COMPLETE',flush=True)
