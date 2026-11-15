import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];folder=r/'outputs/DeliveryArt/TrafficDetailed'
colors=json.loads((folder/'materials.json').read_text())
paint_colors=[c[:3] for k,c in colors.items() if k.startswith('Paint')]
all_colors=[(k,c[:3]) for k,c in colors.items()]
report=[];bpy.context.preferences.filepaths.save_version=0
for f in sorted(folder.glob('SK_Private*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(f));m=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SK_'));rig=m.find_armature();bpy.context.scene.frame_set(1)
 a=m.data.color_attributes['TrafficColor'];uv=m.data.uv_layers.get('TrafficPaintMask') or m.data.uv_layers.new(name='TrafficPaintMask')
 assert list(m.data.uv_layers).index(uv)==1
 painted=0;details=0
 for poly in m.data.polygons:
  c=a.data[poly.loop_start].color
  key,nearest=min(all_colors,key=lambda item:sum((c[i]-item[1][i])**2 for i in range(3)))
  ispaint=key.startswith('Paint')
  # UV1.x is the explicit body mask; y preserves the authored panel shade.
  shade=max(c[:3])/max(nearest) if max(nearest)>0 else 1
  if ispaint:painted+=1
  else:details+=1
  for li in poly.loop_indices:uv.data[li].uv=(1 if ispaint else 0,shade)
 assert painted and details,(f.name,painted,details)
 m.data.uv_layers.active_index=0
 bpy.ops.object.select_all(action='DESELECT');m.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=m
 bpy.ops.export_scene.fbx(filepath=str(folder/(f.stem+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE')
 bpy.ops.wm.save_as_mainfile(filepath=str(f));report.append({'model':f.stem,'paint_faces':painted,'preserved_detail_faces':details})
 print('MASK_PASS',f.stem,painted,details,flush=True)
(folder/'paint_mask_validation.json').write_text(json.dumps(report,indent=2));assert len(report)==20
