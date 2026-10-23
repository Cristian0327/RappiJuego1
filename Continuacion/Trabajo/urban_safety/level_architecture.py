import bpy,json,numpy as np,collections
from pathlib import Path
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');P=R/'urban_safety';root=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');m=json.loads((root/'outputs/BogotaUrban/manifest.json').read_text());levels={v['mesh']:v for v in json.loads((P/'base_levels.json').read_text())};out=P/'export_clean';out.mkdir(exist_ok=True);s=(R/'prepare_new_map_blender.py').read_text();s=s[s.index('def bake(mesh):'):s.index('cache={};exports=[]')];exec(compile(s,'PreservedVoxelColorBake','exec'),globals());meshes={};report=[]
for v in m['instances']:
 if v['mesh'] not in levels:continue
 ob=bpy.data.objects.get(v['source'])
 if not ob:continue
 name=v['mesh']
 if name not in meshes:
  row=levels[name];positive=[(h,a) for h,a in row['levels'] if h>.08];dominant=max(positive,key=lambda a:a[1])[0] if positive else 0;vertical=float(ob.matrix_world[2][2]);base=(dominant-float(ob.matrix_world.translation.z))/vertical;me=ob.data.copy();bake(me);co=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',co);co=co.reshape(-1,3);co[:,2]=co[:,2]-base;me.vertices.foreach_set('co',co.ravel());me.update();meshes[name]=me;temp=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(temp);bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp;bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR');bpy.data.objects.remove(temp,do_unlink=True);report.append(dict(mesh=name,old_floor_height_m=dominant,local_plinth_removed=base))
 ob.data=meshes[name]
 if abs(v['location'][2])<.01:ob.location.z=.20;v['location'][2]=.20
(P/'leveled_manifest.json').write_text(json.dumps(m));(P/'base_leveling_report.json').write_text(json.dumps(report,indent=2));bpy.context.scene['UrbanFloorDatumMeters']=.20;bpy.ops.wm.save_as_mainfile(filepath=str(P/'Mapa_Bogota_Nivelado.blend'));print('ARCHITECTURE_PLINTHS_LEVELED',len(report))

