import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;E=unreal.BlueprintEditorLibrary;reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True)
roots=['/Game/Maps/MapaCompleto_Integration','/Game/QA/GraphicsSettingsQA','/Game/QA/OptimizationBenchmark'];paths=['/Game/World/BlueprintWorld/Optimization/'+n for n in ['WBP_GraphicsSettings','WBP_ShaderWarmup','BP_GraphicsSettings','BP_ServiceDistanceBudget','BP_StoreDistanceBudget']]+['/Game/World/BlueprintWorld/Crowd/BP_CrowdVisibility','/Game/QA/BP_GraphicsSettingsQA','/Game/QA/BP_OptimizationFrameProbe']
report={'blueprints':[],'native_project_dependencies':[],'dependency_count':0}
for path in paths:
 b=unreal.load_asset(path);assert b and E.compile_blueprint(b),path
 audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(b));assert audit['compiled'],path
 assert not any(g['native_calls'] for g in audit['graphs']),(path,'project C++ calls')
 report['blueprints'].append(dict(path=path,nodes=audit['logic_nodes'],compiled=True))
 if path.endswith('BP_CrowdVisibility'):assert len(unreal.get_default_object(b.generated_class()).get_editor_property('Batch'))==32
 if path.endswith('/BP_GraphicsSettings'):
  c=unreal.get_default_object(b.generated_class());assert c.get_editor_property('auto_receive_input')==unreal.AutoReceiveInput.PLAYER0
  assert c.get_editor_property('primary_actor_tick').get_editor_property('tick_interval')==.25
 options=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)
seen=set();pending=roots+paths
while pending:
 package=pending.pop()
 if package in seen:continue
 seen.add(package)
 for dep in reg.get_dependencies(package,options) or []:
  dep=str(dep)
  if dep.startswith('/Script/BogotaVoxel'):report['native_project_dependencies'].append(dep)
  elif dep.startswith('/Game/') and dep not in seen:pending.append(dep)
report['dependency_count']=len(seen);assert not report['native_project_dependencies'],report['native_project_dependencies']
(R/'optimization_asset_validation.json').write_text(json.dumps(report,indent=2));unreal.log('OPTIMIZATION_ASSET_VALIDATION_PASS')
