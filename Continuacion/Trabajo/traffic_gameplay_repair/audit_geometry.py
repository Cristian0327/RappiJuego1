exec(compile(__import__('pathlib').Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();out={}
for path in ['/Game/World/BlueprintWorld/Traffic/BP_TrafficLane','/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintMap','/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore']:
 b=unreal.load_asset(path)
 if b:(P/(b.get_name()+'_current.json')).write_text(unreal.DeliveryEditorLibrary.audit_blueprint(b))
start=next(a for a in aa.get_all_level_actors() if isinstance(a,unreal.PlayerStart))
for path in [R,V,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_TaxiSedan.BP_Traffic_TaxiSedan_C','/Game/Traffic/Services/BP_PoliceRoadPatrol.BP_PoliceRoadPatrol_C']:
 cl=unreal.load_class(None,path)
 if not cl:continue
 a=aa.spawn_actor_from_class(cl,start.get_actor_location()+unreal.Vector(0,0,400));row={'components':[]}
 for c in a.get_components_by_class(unreal.SceneComponent):
  v={'name':c.get_name(),'at':str(c.get_relative_location()) if hasattr(c,'get_relative_location') else str(c.get_editor_property('relative_location')),'rot':str(c.get_editor_property('relative_rotation'))}
  if isinstance(c,unreal.PrimitiveComponent):
   try:v['bounds']=str(unreal.SystemLibrary.get_component_bounds(c))
   except:pass
  for n in ['static_mesh','skeletal_mesh','max_step_height','capsule_half_height']:
   try:v[n]=str(c.get_editor_property(n))
   except:pass
  row['components'].append(v)
 for n in ['GroundOffset','DriveModel','RoadSpeed']:
  try:row[n]=str(a.get_editor_property(n))
  except:pass
 out[path]=row;aa.destroy_actor(a)
out['methods']=[n for n in dir(unreal.DeliveryEditorLibrary) if any(t in n for t in ['graph','widget','bone','mesh'])]
(P/'geometry_current.json').write_text(json.dumps(out,indent=2));unreal.log('GEOMETRY_AUDIT_DONE')
