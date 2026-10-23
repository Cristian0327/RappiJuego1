import bpy,json,numpy as np,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');C=R/'compact_city';sys.path.insert(0,str(R/'urban_refresh/python_deps'))
from mathutils.kdtree import KDTree
hill=json.loads((C/'monserrate_path.json').read_text());q=np.array(hill['points'],float);out=C/'hill_export';out.mkdir(exist_ok=True)
# Model a tangible, continuous mountain path with a solid base and guard posts.
mat=bpy.data.materials.get('Bogota_Calles_Voxel') or bpy.data.materials.new('Bogota_Calles_Voxel');mat.use_nodes=True;nt=mat.node_tree;vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name='Color';nt.links.new(vc.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);nt.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
verts=[];faces=[];cols=[]
def face(points,color):
 i=len(verts);verts.extend([(float(x/100),float(-y/100),float(z/100)) for x,y,z in points]);faces.append(list(reversed(range(i,i+len(points)))));cols.append(color)
def box(center,size,color):
 x,y,z=center;a,b,c=np.array(size)/2;p=np.array([[x+sx*a,y+sy*b,z+sz*c] for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
 for ids in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:face(p[ids],color)
t=np.gradient(q[:,:2],axis=0);t/=np.linalg.norm(t,axis=1)[:,None];right=np.stack([-t[:,1],t[:,0]],1);left=q.copy();rr=q.copy();left[:,:2]+=right*150;rr[:,:2]-=right*150
for i in range(len(q)-1):
 a,b,c,d=left[i],rr[i],rr[i+1],left[i+1];tone=[.51,.37,.23,1] if (i//4)%2 else [.58,.43,.28,1];face([a,b,c,d]+np.array([0,0,8]),tone)
 for aa,bb in [(a,d),(c,b)]:face([aa+np.array([0,0,-25]),bb+np.array([0,0,-25]),bb+np.array([0,0,8]),aa+np.array([0,0,8])],[.35,.27,.18,1])
 face([a,b,c,d]+np.array([0,0,-25]),[.32,.26,.18,1])
 # Low curb/edge rails leave the full 3m path clear.
 for sign in [-1,1]:
  x=q[i].copy();y=q[i+1].copy();x[:2]+=right[i]*sign*166;y[:2]+=right[i+1]*sign*166
  face([x+np.array([0,0,5]),y+np.array([0,0,5]),y+np.array([0,0,23]),x+np.array([0,0,23])],[.63,.54,.38,1])
# Separate posts, with a connected guard along elevated portions.
arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q[:,:2],axis=0),axis=1))]
for i in range(len(q)-1):
 if q[i,2]<250:continue
 for sign in [-1,1]:
  a=q[i].copy();b=q[i+1].copy();a[:2]+=right[i]*sign*173;b[:2]+=right[i+1]*sign*173
  face([a+[0,0,85],b+[0,0,85],b+[0,0,100],a+[0,0,100]],[.24,.20,.14,1])
for s in np.arange(500,arc[-1],450):
 i=np.searchsorted(arc,s)
 if q[i,2]<250:continue
 for sign in [-1,1]:
  a=q[i].copy();a[:2]+=right[i]*sign*173;a[2]+=55;box(a,[16,16,110],[.28,.22,.15,1])
# Vehicle filtering entrance: three 16cm bollards leave two 126cm gaps; bicycles/motos fit.
for lateral in [-142,0,142]:
 p=q[12].copy();p[:2]+=right[12]*lateral;p[2]+=50;box(p,[16,16,100],[.8,.61,.14,1]);box(p+[0,0,28],[18,18,14],[.92,.89,.72,1])
# Small summit viewing landing.
box(q[-1]+[0,0,-14],[620,620,36],[.56,.43,.29,1])
# Sign beside entry, not in the travel corridor.
p=q[14].copy();p[:2]+=right[14]*260;box(p+[0,0,105],[18,18,210],[.22,.19,.13,1]);box(p+[0,0,180],[210,16,78],[.13,.29,.22,1])
name='SM_Bogota_CaminoMonserrate';old=bpy.data.objects.get(name)
if old:bpy.data.objects.remove(old,do_unlink=True)
me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mat);a=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');a.data.foreach_set('color',np.array([col for p,col in zip(me.polygons,cols) for _ in p.loop_indices],np.float32).ravel());me.color_attributes.active_color=a;ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
def export(ob,name):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR')
export(ob,name)
terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'))
for mod in terrain.modifiers:mod.show_viewport=False;mod.show_render=False
terrain.data=terrain.data.copy();data=terrain.data;co=np.empty(len(data.vertices)*3,np.float32);data.vertices.foreach_get('co',co);co=co.reshape(-1,3);mw=np.array(terrain.matrix_world);world=co@mw[:3,:3].T+mw[:3,3];ue=world*[100,-100,100];tree=KDTree(len(q));
for i,p in enumerate(q):tree.insert((p[0],p[1],0),i)
tree.balance();nearest=[tree.find((p[0],p[1],0)) for p in ue];dist=np.array([v[2] for v in nearest]);ids=np.array([v[1] for v in nearest]);mask=dist<500;target=q[ids,2]-12;blend=np.clip((500-dist)/280,0,1);new=ue[:,2]+(target-ue[:,2])*blend;ue[mask,2]=new[mask];world=ue/[100,-100,100];inv=np.linalg.inv(mw);co=world@inv[:3,:3].T+inv[:3,3];data.vertices.foreach_set('co',co.astype(np.float32).ravel());data.update();clone=bpy.data.objects.new('SM_Mapa_081_Graded',data);bpy.context.collection.objects.link(clone);export(clone,'SM_Mapa_081');bpy.data.objects.remove(clone,do_unlink=True)
bpy.context.scene['MonserrateAccess']='Player only: walking, bicycle or motorcycle; no cars or NPC traffic';bpy.context.scene['MonserrateLengthMeters']=hill['length_m'];bpy.ops.wm.save_as_mainfile(filepath=str(C/'Mapa_Bogota_Monserrate.blend'));(C/'hill_model_report.json').write_text(json.dumps(dict(vertices=len(verts),faces=len(faces),graded_terrain_vertices=int(mask.sum()),hill=hill),indent=2));print('MONSERRATE_BLENDER_MODEL_READY',len(faces),'faces',int(mask.sum()),'graded terrain vertices')

