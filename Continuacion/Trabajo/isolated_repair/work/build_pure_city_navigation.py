import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/BlueprintWorld/Navigation'
def asset(name,parent):
 b=unreal.load_asset(folder+'/'+name)
 if not b:
  f=unreal.BlueprintFactory();f.set_editor_property('parent_class',parent);b=T.create_asset(name,folder,unreal.Blueprint,f)
 assert E.compile_blueprint(b);return b
road=asset('BP_NavArea_Road',unreal.NavArea);unreal.get_default_object(road.generated_class()).set_editor_property('default_cost',4.);assert unreal.EditorAssetLibrary.save_loaded_asset(road,only_if_is_dirty=False)
fil=asset('BP_NavFilter_Sidewalk',unreal.NavigationQueryFilter);area=unreal.NavigationFilterArea();area.set_editor_property('area_class',road.generated_class());area.set_editor_property('is_excluded',True);unreal.get_default_object(fil.generated_class()).set_editor_property('areas',[area]);assert unreal.EditorAssetLibrary.save_loaded_asset(fil,only_if_is_dirty=False)
# Only the staging map is changed. Modifier volumes exclude houses and roofs, road filter prevents pavement shortcuts.
assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PureCityRoutes');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if a.get_class().get_name().startswith('BP_TestPureCityRoutes') or isinstance(a,(unreal.NavMeshBoundsVolume,unreal.NavModifierVolume)):actors.destroy_actor(a)
def volume(cls,name,x,y,hx,hy,area_class=None):
 a=actors.spawn_actor_from_class(cls,unreal.Vector(x,y,80));a.set_actor_label(name);b=a.get_editor_property('brush_builder');assert b
 for key,value in [('x',hx*2),('y',hy*2),('z',400.)]:b.set_editor_property(key,float(value))
 if area_class:a.set_editor_property('area_class',area_class)
 return a
bounds=volume(unreal.NavMeshBoundsVolume,'CitySidewalkNavigation',0,0,39000,25000)
foot=json.loads((r/'work/city_building_footprints.json').read_text());unique={}
for x,y,hx,hy in foot:
 key=(x,y);old=unique.get(key,(0,0));unique[key]=(max(hx,old[0]),max(hy,old[1]))
for i,((x,y),(hx,hy)) in enumerate(unique.items()):volume(unreal.NavModifierVolume,'NoNavigationInsideBuilding_'+str(i),x,y,hx+10,hy+10,unreal.NavArea_Null)
for i,x in enumerate([-36000,-24000,-12000,0,12000,24000,36000]):volume(unreal.NavModifierVolume,'RoadNS_'+str(i),x,0,1000,25000,road.generated_class())
for i,y in enumerate([-22000,-11000,0,11000,22000]):volume(unreal.NavModifierVolume,'RoadEW_'+str(i),0,y,39000,1400 if y==0 else 1000,road.generated_class())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.NavigationSystemV1.get_navigation_system(world).on_navigation_bounds_updated(bounds);assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/PureCityCrowd');(r/'work/pure_city_navigation.json').write_text(json.dumps({'map':'/Game/QA/PureCityCrowd','building_exclusions':len(unique),'road_areas':12,'status':'AUTHORED_PENDING_RUNTIME'},indent=2));unreal.log('PURE_CITY_NAVIGATION_AUTHORED')
