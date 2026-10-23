import bpy,json,numpy as np
from pathlib import Path
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit')
o=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Relieve'));m=o.data
# Preserve the original mountain palette, baking it exactly as the existing imported assets.
vertexmat=bpy.data.materials.get('Mapa_ColorVoxel')
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/prepare_new_map_blender.py').read_text();exec(s[s.index('def bake(mesh):'):s.index('vertexmat=bpy.data.materials.new')]);bake(m)
n=len(m.vertices);v=np.empty(n*3,np.float32);m.vertices.foreach_get('co',v);v=v.reshape(-1,3);mat=np.asarray(o.matrix_world,dtype=np.float32);world=v@mat[:3,:3].T+mat[:3,3];li=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',li);p=world[li];cols=np.empty(len(li)*4,np.float32);m.color_attributes['Color'].data.foreach_get('color',cols);cols=cols.reshape(-1,4);flat=(p[:,2]>=-.4)&(p[:,2]<=.35);cols[flat,:3]=(.38,.39,.40);m.color_attributes['Color'].data.foreach_set('color',cols.ravel())
# Blender source uses the same world-space brick/concrete motif as Unreal.
matp=bpy.data.materials.new('Andenes_Concreto_Adoquin_Bogota');matp.use_nodes=True;nt=matp.node_tree;bs=nt.nodes.get('Principled BSDF');vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name='Color';nt.links.new(vc.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.93
# Bake fine patterns into source face corners for Blender's material preview.
row=np.floor(p[:,1]/.2);u=np.mod(p[:,0]/.4+np.mod(row,2)*.5,1);vv=np.mod(p[:,1]/.2,1);zone=np.mod(np.floor(p[:,0]/36)+np.floor(p[:,1]/36),3);brick=flat&(zone==0);grout=brick&((u<.05)|(vv<.09));cols[brick,:3]=(.34,.27,.22);cols[grout,:3]=(.24,.25,.26);m.color_attributes['Color'].data.foreach_set('color',cols.ravel());m.materials.clear();m.materials.append(matp)
bpy.ops.wm.save_as_mainfile(filepath=str(W/'Mapa_Completo_Andenes_Ampliado.blend'))
# FBX geometry stays local, matching existing terrain instance transform.
temp=bpy.data.objects.new('SM_Mapa_081',m.copy());bpy.context.scene.collection.objects.link(temp);bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp
bpy.ops.export_scene.fbx(filepath=str(W/'export/SM_Mapa_081.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR')
(W/'paving_report.json').write_text(json.dumps({'flat_urban_corners':int(flat.sum()),'mountain_corners_preserved':int((~flat).sum()),'same_terrain_geometry':True,'concrete_and_ochre_brick':True},indent=2));print('URBAN_PAVING_READY',int(flat.sum()),int((~flat).sum()))
