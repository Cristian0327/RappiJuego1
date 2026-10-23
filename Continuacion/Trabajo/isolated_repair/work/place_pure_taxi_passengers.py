import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
base=unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_TaxiPassenger.BP_TaxiPassenger_C')
models=[m for m in json.loads((r/'work/pure_crowd_models.json').read_text()) if not m['cane']]
classes=[]
for i in range(12):
 model=models[(i*7)%len(models)];path='/Game/World/BlueprintWorld/Traffic/TaxiPassengers/BP_TaxiPassenger'+str(i).zfill(2);b=unreal.load_asset(path)
 if not b:
  f=unreal.BlueprintFactory();f.set_editor_property('parent_class',base);b=T.create_asset(path.rsplit('/',1)[1],path.rsplit('/',1)[0],unreal.Blueprint,f)
 assert E.compile_blueprint(b)
 c=unreal.get_default_object(b.generated_class());m=c.get_editor_property('mesh');src=unreal.get_default_object(unreal.load_asset(model['asset']).generated_class()).get_editor_property('mesh')
 m.set_skeletal_mesh_asset(src.get_skeletal_mesh_asset());m.set_material(0,src.get_material(0))
 for prop in ['relative_location','relative_rotation','relative_scale3d']:m.set_editor_property(prop,src.get_editor_property(prop))
 c.set_editor_property('CitizenId',i);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False);classes.append(b.generated_class())
points=[(-6000,12130),(6000,12130),(18000,12130),(-18000,12130),(-30000,-9870),(30000,-9870),(-6000,1730),(6000,1730),(18000,-1730),(-18000,-1730),(-30000,-12130),(30000,9870)]
for path in ['/Game/Maps/Bogota_Blueprint_Integration','/Game/QA/PureIntegratedWorld']:
 assert unreal.EditorLoadingAndSavingUtils.load_map(path)
 for a in actors.get_all_level_actors():
  if a.get_class().get_path_name().startswith('/Game/World/BlueprintWorld/Traffic/TaxiPassengers/'):actors.destroy_actor(a)
 for i,(x,y) in enumerate(points):
  p=actors.spawn_actor_from_class(classes[i],unreal.Vector(x,y,90));p.set_actor_label('TaxiPassenger_'+str(i).zfill(2))
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,path)
(r/'work/pure_taxi_placement.json').write_text(json.dumps({'status':'STAGING_NOT_MAIN','passengers_per_map':12,'models':12,'maps':2}))
unreal.log('PURE_TAXI_PASSENGERS_PLACED')
