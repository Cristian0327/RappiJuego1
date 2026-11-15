import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent
reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True)
sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);sk=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
report={'static':[],'skeletal':[],'textures':[],'blueprints':{},'api':{}}
for folder in ['/Game/World','/Game/Delivery/Stores','/Game/Crowd','/Game/Traffic']:
 for data in reg.get_assets_by_path(folder,recursive=True):
  typ=str(data.asset_class_path.asset_name);path=str(data.package_name)
  if typ not in ['StaticMesh','SkeletalMesh','Texture2D']:continue
  obj=data.get_asset()
  if typ=='StaticMesh':
   row=dict(path=path,lods=sm.get_lod_count(obj),triangles=obj.get_num_triangles(0),vertices=obj.get_num_vertices(0))
   report['static'].append(row)
  elif typ=='SkeletalMesh':report['skeletal'].append(dict(path=path,lods=sk.get_lod_count(obj)))
  else:report['textures'].append(dict(path=path,never_stream=obj.get_editor_property('never_stream')))
for p in ['/Game/World/BlueprintWorld/Optimization/BP_ServiceDistanceBudget','/Game/World/BlueprintWorld/Optimization/BP_StoreDistanceBudget','/Game/World/BlueprintWorld/Crowd/BP_StreetCitizen','/Game/World/BlueprintWorld/BP_BlueprintPlayer','/Game/Delivery/BlueprintGameplay/UI/BP_BlueprintHUD']:
 b=unreal.load_asset(p)
 if b:report['blueprints'][p]=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(b))
for cls,methods in [(unreal.StaticMeshEditorSubsystem,['set_lods','get_lod_screen_sizes']),(unreal.EditorLevelUtils,['create_new_streaming_level','move_actors_to_level'])]:
 for name in methods:
  try:report['api'][name]=getattr(cls,name).__doc__
  except Exception:pass
(R/'optimization_audit.json').write_text(json.dumps(report,indent=2))
unreal.log('OPTIMIZATION_AUDIT_READY')
