import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');O=W/'export';O.mkdir(exist_ok=True)
S=3.;CX=121.6244;CY=55.6001
source=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_get() and not o.name.startswith('Plane')]
manifest={'scale':S,'center':[CX,CY],'instances':[],'meshes':[],'roads':[]}
def mapped(v):return ((v.x-CX)*S,(v.y-CY)*S,v.z*S)
# Bake original flat/atlas colors to loop colors, one opaque shader in Unreal.
def bake(mesh):
 n=len(mesh.loops);cols=np.ones((n,4),dtype=np.float32);mi=np.empty(len(mesh.polygons),np.int32);tot=np.empty(len(mesh.polygons),np.int32);mesh.polygons.foreach_get('material_index',mi);mesh.polygons.foreach_get('loop_total',tot);idx=np.repeat(mi,tot)
 uv=None
 if mesh.uv_layers.active:
  uv=np.empty(n*2,np.float32);mesh.uv_layers.active.data.foreach_get('uv',uv);uv=uv.reshape(-1,2)
 for k,m in enumerate(mesh.materials):
  if not m:continue
  col=list(m.diffuse_color);tex=None
  if m.use_nodes:
   bs=next((v for v in m.node_tree.nodes if v.type=='BSDF_PRINCIPLED'),None)
   if bs:
    col=list(bs.inputs['Base Color'].default_value)
    if bs.inputs['Base Color'].is_linked:
     tex=next((v for v in m.node_tree.nodes if v.type=='TEX_IMAGE' and v.image and v.image.size[0]>0),None)
  mask=idx==k;cols[mask]=col
  if tex and uv is not None:
   im=tex.image;pixels=np.array(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4);u=uv[mask];xx=np.clip((u[:,0]*im.size[0]).astype(int),0,im.size[0]-1);yy=np.clip((u[:,1]*im.size[1]).astype(int),0,im.size[1]-1);cols[mask]=pixels[yy,xx]
 cols[:,3]=1
 for a in list(mesh.color_attributes):mesh.color_attributes.remove(a)
 a=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');a.data.foreach_set('color',cols.ravel());mesh.color_attributes.active_color=a
 mesh.materials.clear();mesh.materials.append(vertexmat)
 for p in mesh.polygons:p.material_index=0
vertexmat=bpy.data.materials.new('Mapa_ColorVoxel');vertexmat.use_nodes=True;nt=vertexmat.node_tree;vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name='Color';bs=nt.nodes.get('Principled BSDF');nt.links.new(vc.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.9
cache={};exports=[]
for o in source:
 key=o.data.as_pointer()
 if key not in cache:
  name='SM_Mapa_%03d'%len(cache);mesh=o.data.copy();mesh.name=name;bake(mesh);temp=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(temp);cache[key]=name;exports.append(temp);manifest['meshes'].append({'name':name,'source':o.name,'polygons':len(mesh.polygons)})
 mat=o.matrix_world;loc,rot,sc=mat.decompose();e=rot.to_euler('XYZ');bounds=[Vector(mapped(mat@Vector(p))) for p in o.bound_box]
 manifest['instances'].append({'mesh':cache[key],'source':o.name,'location':mapped(loc),'rotation':[math.degrees(x) for x in e],'scale':[x*S for x in sc],'bounds':[[min(v[i] for v in bounds) for i in range(3)],[max(v[i] for v in bounds) for i in range(3)]]})
# Reconstruct the actual road ribbons with sidewalk reserves inside their original footprints.
rows=json.loads((W/'road_rows.json').read_text());newobs=[]
def make(name,verts,faces,colors):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(vertexmat);a=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');data=[]
 for p,c in zip(mesh.polygons,colors):data.extend(list(c)+[1.] for _ in p.loop_indices)
 a.data.foreach_set('color',np.asarray(data,dtype=np.float32).ravel());ob=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(ob);newobs.append(ob);manifest['meshes'].append({'name':name,'source':'generated road and sidewalks','polygons':len(faces)});manifest['instances'].append({'mesh':name,'source':name,'location':[0,0,0],'rotation':[0,0,0],'scale':[1,1,1]});return ob
for ri,r in enumerate(rows):
 rr=[]
 for row in r['rows']:
  l=Vector(mapped(Vector(row['left'])));rt=Vector(mapped(Vector(row['right'])));c=(l+rt)*.5;half=(l-rt).length*.5;side=(l-rt).normalized();reserve=2.4 if ri==0 else .85;inner=max(half-reserve,1.35);rr.append((c,side,half,inner))
 verts=[];faces=[];colors=[]
 for i,(c,side,half,inner) in enumerate(rr):
  for w,z in [(-half,0),(-half,.20),(-inner,.20),(-inner,.04),(inner,.04),(inner,.20),(half,.20),(half,0)]:
   v=c+side*w;v.z=z;verts.append(tuple(v))
  if i:
   for j in range(7):faces.append(((i-1)*8+j,(i-1)*8+j+1,i*8+j+1,i*8+j));colors.append((.12,.15,.17) if j==3 else (.55,.57,.58) if j in [1,5] else (.68,.69,.66))
 make('SM_Mapa_Road_%d'%ri,verts,faces,colors)
 manifest['roads'].append({'name':r['name'],'center':[list(v[0]) for v in rr],'side':[list(v[1]) for v in rr],'halfwidth':[v[2] for v in rr],'innerwidth':[v[3] for v in rr]})
# Export reusable unique meshes; scene placements remain in metadata.
for ob in exports+newobs:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(O/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR')
print('EXPORTED',len(exports)+len(newobs))
# Save the modified Blender project: uniformly expanded layout, original road helpers hidden.
for ob in exports:bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(bpy.data.objects):
 if ob in newobs:continue
 if ob.type=='CAMERA' or ob.type=='LIGHT':continue
 if ob.name.startswith('Plane'):ob.hide_set(True);ob.hide_render=True;continue
 mat=ob.matrix_world.copy();mat.translation=Vector(mapped(mat.translation));mat=mat@Matrix.Diagonal((S,S,S,1));ob.matrix_world=mat
for ob in newobs:ob.hide_set(False);ob.hide_render=False
(W/'manifest.json').write_text(json.dumps(manifest))
bpy.ops.wm.save_as_mainfile(filepath=str(W/'Mapa_Completo_Andenes.blend'))
print('MAP_PREPARED',len(manifest['instances']))
