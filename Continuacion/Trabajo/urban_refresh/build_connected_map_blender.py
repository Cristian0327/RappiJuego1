import bpy,json,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));inv=terrain.matrix_world.inverted();down=inv.to_3x3()@Vector((0,0,-1))
tree=BVHTree.FromPolygons([v.co for v in terrain.data.vertices],[list(p.vertices) for p in terrain.data.polygons])
def ground(x,y):
 co,n,j,dist=tree.ray_cast(inv@Vector((x/100,-y/100,200)),down);return (terrain.matrix_world@co).z*100 if co is not None else 99999
plan=json.loads((U/'secondary_road_plan.json').read_text());bad=[]
for s in plan['secondary_roads']:
 for q in s['samples'][::5]:
  z=ground(*q)
  if abs(z)>35:bad.append([*q,z])
if bad:raise RuntimeError('Roads leave flat urban terrain '+str(bad[:5]))
mat=bpy.data.materials.get('Bogota_Calles_Voxel') or bpy.data.materials.new('Bogota_Calles_Voxel');mat.use_nodes=True;vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Color';mat.node_tree.links.new(vc.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.88
for spec in json.loads((U/'secondary_geometry.json').read_text()):
 old=bpy.data.objects.get(spec['name'])
 if old:bpy.data.objects.remove(old,do_unlink=True)
 me=bpy.data.meshes.new(spec['name']);me.from_pydata(spec['verts'],[],[list(reversed(v)) if spec['name'].startswith('SM_Bogota') else v for v in spec['faces']]);me.update();me.materials.append(mat);a=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');colors=[]
 for poly,c in zip(me.polygons,spec['colors']):colors.extend([c]*len(poly.loop_indices))
 a.data.foreach_set('color',np.asarray(colors,np.float32).ravel());me.color_attributes.active_color=a;o=bpy.data.objects.new(spec['name'],me);bpy.context.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(U/'export'/(spec['name']+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR')
keep=[];reject=[]
for v in json.loads((U/'additional_infill_plan.json').read_text()):
 lo,hi=np.array(v['bounds'])*[100,-100,100];a=np.minimum(lo,hi);b=np.maximum(lo,hi);zs=[ground(x,y) for x in [a[0],(a[0]+b[0])/2,b[0]] for y in [a[1],(a[1]+b[1])/2,b[1]]]
 if any(abs(z)>35 for z in zs):reject.append(v['source']);continue
 name=v['source'].split(' | Relleno urbano ')[0];old=bpy.data.objects.get(name)
 if not old:raise RuntimeError(name)
 o=old.copy();o.data=old.data;bpy.context.collection.objects.link(o);o.name=v['source'];o.location=Vector(v['location']);keep.append(v)
(U/'accepted_infill.json').write_text(json.dumps(keep,indent=2));(U/'secondary_ground_report.json').write_text(json.dumps(dict(roads=14,road_ground_errors=bad,accepted_buildings=len(keep),rejected_buildings=reject),indent=2));
for mod in terrain.modifiers:mod.show_viewport=False;mod.show_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(U/'Mapa_Bogota_RedConectada.blend'));print('CONNECTED_MAP_BLEND_READY',len(keep),'infill')
