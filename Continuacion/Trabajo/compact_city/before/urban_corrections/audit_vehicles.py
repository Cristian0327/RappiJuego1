import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;out={'models':[],'base_graph':{}};E=unreal.EditorAssetLibrary;ME=unreal.MaterialEditingLibrary;ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for row in json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']:
 bp=unreal.load_asset(row['asset']);c=unreal.get_default_object(bp.generated_class());rec=dict(asset=row['asset'],palette=[[v.r,v.g,v.b,v.a] for v in c.get_editor_property('PaintPalette')],components=[])
 for h in ss.k2_gather_subobject_data_for_blueprint(bp):
  o=lib.get_object_for_blueprint(lib.get_data(h),bp)
  if isinstance(o,unreal.StaticMeshComponent):
   mesh=o.get_editor_property('static_mesh')
   if mesh:rec['components'].append(dict(name=str(lib.get_variable_name(lib.get_data(h))),mesh=mesh.get_path_name(),slots=[str(v.material_interface.get_path_name()) if v.material_interface else None for v in mesh.static_materials],overrides=[m.get_path_name() if m else None for m in o.get_materials()],lod=mesh.get_num_lods()))
 out['models'].append(rec)
for name in ['M_TrafficVoxelVertex','M_TrafficVoxel']:
 m=unreal.load_asset('/Game/Traffic/Detailed/'+name);expr=[]
 for q in unreal.ObjectIterator(unreal.MaterialExpression):
  if q.get_outer()!=m:continue
  rec=dict(type=q.get_class().get_name())
  for field in ['code','parameter_name','default_value','texture']:
   try:rec[field]=str(q.get_editor_property(field))
   except:pass
  expr.append(rec)
 out[name]=expr
out['base_graph']=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle')))
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_corrections/vehicle_audit.json').write_text(json.dumps(out,indent=2));unreal.log('VEHICLE_CURRENT_AUDIT_READY')

