import bpy,bmesh,json,numpy as np,math
from pathlib import Path
from mathutils import Matrix,Vector,Euler
from mathutils.kdtree import KDTree
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');P=R/'map_adaptation_v2';out=P/'export';out.mkdir(exist_ok=True);m=json.loads((P/'manifest.json').read_text());mask=np.load(P/'clip_mask.npy');variants=[]
def export(ob,name):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR')
for item in m['instances']:
 if 'Relieve' in item['source'] or item['mesh'].startswith('SM_Mapa_Road'):continue
 ob=bpy.data.objects.get(item['source'])
 if not ob or ob.type!='MESH':continue
 ob.location=Vector(item['location']);bpy.context.view_layer.update();me=ob.data;co=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',co);co=co.reshape(-1,3);mat=np.array(ob.matrix_world);v=(co@mat[:3,:3].T+mat[:3,3])*[100,-100,100];start=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_start',start);li=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',li);lo=np.minimum.reduceat(v[li,2],start);hi=np.maximum.reduceat(v[li,2],start);candidates=np.where((hi<240)&(lo>-120))[0];delete=[]
 for i in candidates:
  q=v[list(me.polygons[int(i)].vertices),:2];a=np.floor((q.min(0)+[40000,50000])/20).astype(int);b=np.ceil((q.max(0)+[40000,50000])/20).astype(int);a=np.maximum(a,0);b=np.minimum(b,[3999,4999])
  if np.any(b<a):continue
  yy,xx=np.where(mask[a[1]:b[1]+1,a[0]:b[0]+1])
  if not len(xx):continue
  # Convex voxel faces: sample the road cells inside their true face projection.
  pts=np.column_stack([xx+a[0],yy+a[1]])*20+[-39990,-49990];edges=np.roll(q,-1,axis=0)-q;cross=edges[None,:,0]*(pts[:,None,1]-q[None,:,1])-edges[None,:,1]*(pts[:,None,0]-q[None,:,0]);inside=np.all(cross>=-200,axis=1)|np.all(cross<=200,axis=1)
  if np.any(inside):delete.append(int(i))
 if not delete:continue
 clone=me.copy();bm=bmesh.new();bm.from_mesh(clone);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in delete],context='FACES');bm.to_mesh(clone);bm.free();clone.update();name='SM_StreetFrontage_%03d'%len(variants);temp=bpy.data.objects.new(name,clone);bpy.context.collection.objects.link(temp);export(temp,name);bpy.data.objects.remove(temp,do_unlink=True);ob.data=clone;variants.append(dict(source=item['source'],name=name,removed_low_faces=len(delete),remaining_faces=len(clone.polygons)));print('FRONTAGE_CLEARED',len(variants),item['source'],len(delete),flush=True)
(P/'frontage_variants.json').write_text(json.dumps(variants,indent=2))
mat=bpy.data.materials.get('Bogota_Calles_Voxel') or bpy.data.materials.new('Bogota_Calles_Voxel');mat.use_nodes=True
for spec in json.loads((P/'road_meshes.json').read_text()):
 old=bpy.data.objects.get(spec['name'])
 if old:bpy.data.objects.remove(old,do_unlink=True)
 me=bpy.data.meshes.new(spec['name']);me.from_pydata(spec['verts'],[],spec['faces']);me.update();me.materials.append(mat);a=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');a.data.foreach_set('color',np.array([c for poly,c in zip(me.polygons,spec['colors']) for _ in poly.loop_indices],np.float32).ravel());me.color_attributes.active_color=a;ob=bpy.data.objects.new(spec['name'],me);bpy.context.collection.objects.link(ob);export(ob,spec['name'])
# Grade only the new street corridors. The existing Monserrate path stays intact.
terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));data=terrain.data.copy();terrain.data=data;co=np.empty(len(data.vertices)*3,np.float32);data.vertices.foreach_get('co',co);co=co.reshape(-1,3);mw=np.array(terrain.matrix_world);world=co@mw[:3,:3].T+mw[:3,3];ue=world*[100,-100,100];xyz=np.load(P/'road_grade_samples.npy');tree=KDTree(len(xyz))
for i,q in enumerate(xyz):tree.insert((q[0],q[1],0),i)
tree.balance();near=[tree.find((p[0],p[1],0)) for p in ue];dist=np.array([n[2] for n in near]);ids=np.array([n[1] for n in near]);blend=np.clip((1100-dist)/600,0,1);target=xyz[ids,2]-2;new=ue[:,2]+(target-ue[:,2])*blend;ue[dist<1100,2]=new[dist<1100];inv=np.linalg.inv(mw);local=(ue/[100,-100,100])@inv[:3,:3].T+inv[:3,3];data.vertices.foreach_set('co',local.astype(np.float32).ravel());data.update();temp=bpy.data.objects.new('TerrainExport',data);bpy.context.collection.objects.link(temp);export(temp,'SM_Mapa_081');bpy.data.objects.remove(temp,do_unlink=True)
bpy.context.scene['AuthoredSecondaryStreetCount']=14;bpy.context.scene['StreetSource']='Downloads/Mapa_Completo.blend; exact Bezier paths at original 3x scale';bpy.ops.wm.save_as_mainfile(filepath=str(P/'Mapa_Bogota_Calles_Completas.blend'));(P/'model_report.json').write_text(json.dumps(dict(streets=14,frontage_variants=len(variants),graded_vertices=int((dist<1100).sum())),indent=2));print('V2_MODEL_EXPORT_READY',len(variants),flush=True)
