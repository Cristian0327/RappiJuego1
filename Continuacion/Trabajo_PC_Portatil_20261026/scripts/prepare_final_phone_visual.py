import unreal,json,sys
from pathlib import Path
R=Path(__file__).resolve().parent.parent
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for command in ['Editor.AsyncAssetCompilationMaxConcurrency 2','Editor.AsyncAssetCompilationMaxMemoryUsage 2']:
 unreal.SystemLibrary.execute_console_command(world,command)
p=R/'scripts/cache_phone_layout.py';exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
b=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone');tree=unreal.find_object(b,'WidgetTree');hints=unreal.find_object(tree,'PhoneHints');assert hints
font=hints.get_editor_property('font');font.set_editor_property('size',16);hints.set_editor_property('font',font);assert unreal.BlueprintEditorLibrary.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
source=(R/'work/build_pure_phone_runtime_test.py').read_text(encoding='utf-8-sig')
source=source.replace("{'name':'Age','default':'0'}","{'name':'Age','default':'-15'}")
source=source.replace("1.8+i*.75","4+i*6").replace("2.+i*.75","8+i*6")
source=source.replace("phase('Close',7.3)","phase('Close',46.)").replace("phase('ClosedState',7.5)","phase('ClosedState',47.)").replace("phase('PersistentHUD',7.6)","phase('PersistentHUD',47.5)").replace("phase('Finish',8.)","phase('Finish',49.)")
source=source.replace("r/('work/PurePhoneVisualQA/'+name+'.png')","r/('AdversarialQA_20261026/screens_after/phone_'+name+'.png')")
source=source.replace("g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='true')","g.call('Quit','ExecuteConsoleCommand',K,Command='open /Game/QA/CPUIsolation')")
# Verify geometry, not merely the page number, after its first paint/layout pass.
old="g.exec(p0,'Shot'+name);advance('Shot'+name)"
new="""g.exec(p0,'Shot'+name)
 if name=='MAP':
  g.call('MapPanel','GetActiveMapPanel',PHONE);g.link('Phone',p,'MapPanel','self');g.call('MapGeometry','GetCachedGeometry','/Script/UMG.Widget');g.link('MapPanel','ReturnValue','MapGeometry','self');g.call('MapSize','GetLocalSize','/Script/UMG.SlateBlueprintLibrary');g.link('MapGeometry','ReturnValue','MapSize','Geometry');g.call('SizeAxes','BreakVector2D',M);g.link('MapSize','ReturnValue','SizeAxes','InVec')
  for axis in ['X','Y']:g.call('SizeValid'+axis,'Greater_DoubleDouble',M,B='1');g.link('SizeAxes',axis,'SizeValid'+axis,'A')
  g.call('SizeValid','BooleanAND',M);g.link('SizeValidX','ReturnValue','SizeValid','A');g.link('SizeValidY','ReturnValue','SizeValid','B');report('MAP_PANEL_HAS_SIZE','Shot'+name,'SizeValid')
 else:advance('Shot'+name)"""
assert old in source;source=source.replace(old,new)
(R/'AdversarialQA_20261026/screens_after').mkdir(exist_ok=True)
exec(compile(source,'FinalPhoneVisualRegression','exec'),{'__file__':str(R/'work/build_pure_phone_runtime_test.py'),'__name__':'__main__'})
assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PurePhoneRuntime')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not any(a.get_class().get_name()=='BP_MapNavigation_C' for a in actors.get_all_level_actors()):actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BogotaUrban/BP_MapNavigation.BP_MapNavigation_C'),unreal.Vector())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/PurePhoneRuntime')
unreal.log('FINAL_PHONE_VISUAL_READY')
