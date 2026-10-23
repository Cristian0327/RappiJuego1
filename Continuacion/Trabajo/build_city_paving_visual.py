import unreal,json,sys,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset('/Game/QA/BP_CityPavingVisual') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_CityPavingVisual','/Game/QA',unreal.Blueprint,f);d.bp=bp
for n in ['Cam1','Cam2']:
 if n not in [str(v) for v in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,n,E.get_object_reference_type(unreal.Actor))
E.set_blueprint_variable_instance_editable(bp,'Cam1',True);E.set_blueprint_variable_instance_editable(bp,'Cam2',True);E.compile_blueprint(bp);g=d.Graph();g.variables=[{'name':'Age','default':'0'},{'name':'Stage','default':'0'}];g.get('Age');g.get('Stage');g.get('Cam1');g.get('Cam2');g.call('PC','GetPlayerController','/Script/Engine.GameplayStatics',PlayerIndex='0');g.call('Clock','Add_DoubleDouble',d.M);g.link('Age','Age','Clock','A');g.link('entry','DeltaSeconds','Clock','B');g.setter('Now','Age','Clock');g.exec('entry','Now');last='Now';edge='then'
for i,(t,action) in enumerate([(1,'Cam1'),(3,'urban_pavement'),(5,'Cam2'),(7,'urban_adoquin'),(9,'quit')]):
 tag='S'+str(i);g.call(tag+'Time','Greater_DoubleDouble',d.M,B=str(t));g.link('Age','Age',tag+'Time','A');g.call(tag+'Index','NearlyEqual_FloatFloat',d.M,B=str(i),ErrorTolerance='.01');g.link('Stage','Stage',tag+'Index','A');g.call(tag+'Due','BooleanAND',d.M);g.link(tag+'Time','ReturnValue',tag+'Due','A');g.link(tag+'Index','ReturnValue',tag+'Due','B');g.branch(tag,tag+'Due');g.exec(last,tag,edge)
 if action.startswith('Cam'):
  g.call(tag+'Act','SetViewTargetWithBlend','/Script/Engine.PlayerController',BlendTime='0');g.link('PC','ReturnValue',tag+'Act','self');g.link(action,action,tag+'Act','NewViewTarget')
 else:g.call(tag+'Act','ExecuteConsoleCommand','/Script/Engine.KismetSystemLibrary',Command='quit' if action=='quit' else 'HighResShot 1920x1080 filename="'+str(r/'outputs/MapRebuild'/(action+'.png')).replace('\\','/')+'"')
 g.exec(tag,tag+'Act');g.setter(tag+'Next','Stage',value=str(i+1));g.exec(tag+'Act',tag+'Next');g.exec(tag+'Next','result');last=tag;edge='else'
g.exec(last,'result',edge);g.build('ReceiveTick');assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/CityPavingVisual');unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/CityPavingVisual');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.GameModeBase);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);qa=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());infill=json.loads((W/'urban_infill_report.json').read_text());x,y,z=infill[0]['position']
for name,pos,target in [('Cam1',(x-2000,y-2600,1800),(x,y,150)),('Cam2',(x+800,y-1000,450),(x+1500,y+300,0))]:
 v=unreal.Vector(*pos);aim=unreal.MathLibrary.find_look_at_rotation(v,unreal.Vector(*target));cam=actors.spawn_actor_from_class(unreal.CameraActor,v,aim);qa.set_editor_property(name,cam)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('CITY_PAVING_VISUAL_READY')

