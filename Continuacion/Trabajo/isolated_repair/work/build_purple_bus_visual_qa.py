import unreal,sys,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/build_pure_morado_qa.py').read_text(encoding='utf-8-sig')
# Delay quit to allow one frame for the screenshot.
s=s.replace("g.exec('Print','Quit')", "g.exec('Print','result');g.call('QuitAge','Greater_DoubleDouble',M,B='4');g.link('Age','Age','QuitAge','A');g.branch('QuitNow','QuitAge');g.exec('Assess','QuitNow','else');g.exec('QuitNow','Quit');g.exec('QuitNow','result','else')") if False else s
# Retain the established spawn/overlap test. Screenshot at 2sec; quit at 3sec.
s=s.replace("B='2');g.link('Age','Age','AfterTwo'","B='3');g.link('Age','Age','AfterTwo'")
s=s.replace("g.exec('Assess','result','else')", "g.call('CameraActor','GetActorOfClass',G,ActorClass='/Script/Engine.CameraActor');g.call('Controller','GetPlayerController',G,PlayerIndex='0');g.call('LookAtBus','SetViewTargetWithBlend','/Script/Engine.PlayerController',BlendTime='0');g.link('Controller','ReturnValue','LookAtBus','self');g.link('CameraActor','ReturnValue','LookAtBus','NewViewTarget');g.exec('Assess','CameraActor','else');g.exec('CameraActor','LookAtBus');g.call('Shot','ExecuteConsoleCommand',K,Command='Shot filename=\"'+str(r/'work/PureIntegratedVisualQA/PURPLE_BUS.png').replace('\\\\','/')+'\"');g.exec('LookAtBus','Shot');g.exec('Shot','result')")
exec(compile(s,'PurpleBusVisualFixture','exec'))
# Add light and a view of the bus body to the flat fixture.
cam=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(800,-1800,850));cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),unreal.Vector(2400,0,170)),False);cam.camera_component.set_editor_property('field_of_view',60)
light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1500));light.set_actor_rotation(unreal.Rotator(-45,-30,0),False);light.light_component.set_editor_property('intensity',5)
actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,1000))
assert unreal.EditorLoadingAndSavingUtils.save_map(world,path)
unreal.log('PURPLE_BUS_VISUAL_QA_READY')

