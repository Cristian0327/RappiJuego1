import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
base=unreal.load_class(None,'/Game/World/BlueprintWorld/Crowd/BP_CrosswalkCitizen.BP_CrosswalkCitizen_C')
models=[m for m in json.loads((r/'work/pure_crowd_models.json').read_text()) if not m['cane']]
classes=[]
for i in range(12):
 model=models[(i*7)%len(models)];path='/Game/World/BlueprintWorld/Crowd/CrosswalkCitizens/BP_CrosswalkCitizen'+str(i).zfill(2);b=unreal.load_asset(path)
 if not b:
  f=unreal.BlueprintFactory();f.set_editor_property('parent_class',base);b=T.create_asset(path.rsplit('/',1)[1],path.rsplit('/',1)[0],unreal.Blueprint,f)
 assert E.compile_blueprint(b)
 c=unreal.get_default_object(b.generated_class());m=c.get_editor_property('mesh');src=unreal.get_default_object(unreal.load_asset(model['asset']).generated_class()).get_editor_property('mesh')
 m.set_skeletal_mesh_asset(src.get_skeletal_mesh_asset());m.set_material(0,src.get_material(0))
 for prop in ['relative_location','relative_rotation','relative_scale3d']:m.set_editor_property(prop,src.get_editor_property(prop))
 assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False);classes.append(b.generated_class())
points=[(x,y) for y in [-22000,-11000,11000] for x in [-24000,-12000,0,12000]]
for path in ['/Game/Maps/Bogota_Blueprint_Integration','/Game/QA/PureIntegratedWorld']:
 assert unreal.EditorLoadingAndSavingUtils.load_map(path)
 for a in actors.get_all_level_actors():
  if a.get_class().get_path_name().startswith('/Game/World/BlueprintWorld/Crowd/CrosswalkCitizens/'):actors.destroy_actor(a)
 for i,(x,y) in enumerate(points):
  y0=y+1250;y1=y+11000-(1530 if y==-11000 else 1250);route=[(x-1130,y0),(x+1130,y0),(x+10800,y0),(x+10800,y1),(x+1130,y1),(x-1130,y1),(x-10800,y1),(x-10800,y0)]
  p=actors.spawn_actor_from_class(classes[i],unreal.Vector(route[0][0],route[0][1],114));p.set_editor_property('Route',[unreal.Vector(a,b,26) for a,b in route]);p.set_editor_property('RouteIndex',1);p.set_actor_label('CrosswalkCitizen_'+str(i).zfill(2))
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,path)
(r/'work/pure_crosswalk_placement.json').write_text(json.dumps({'status':'STAGING_NOT_MAIN','passengers_per_map':12,'models':12,'maps':2}))
unreal.log('PURE_CROSSWALK_CITIZENS_PLACED')

exec((r/'work/plan_native_asset_retirement.py').read_text(encoding='utf-8-sig'))
exec((r/'work/convert_legacy_profile_to_blueprint.py').read_text(encoding='utf-8-sig'))
