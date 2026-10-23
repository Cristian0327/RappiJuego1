from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'RepairHelpers','exec'))
# Rebuild only the clearance wrapper: preserve station crossings when no junction is ahead.
b=use(TM);g=d.Graph();field(g,'Pos','NextPosition',('entry','Visitor'),V);field(g,'Yaw','NextYaw',('entry','Visitor'),V);field(g,'Length','HalfLength',('entry','Visitor'),V);g.call('Rot','MakeRotator',M);g.link('Yaw','NextYaw','Rot','Yaw');g.call('Dir','GetForwardVector',M);g.link('Rot','ReturnValue','Dir','InRot');g.call('Find','FindUpcomingJunction',TM);g.link('entry','Visitor','Find','Visitor');g.exec('entry','Find');g.call('Valid','IsValid',K);g.link('Find','ReturnValue','Valid','Object');g.branch('Have','Valid');g.exec('Find','Have');g.call('StationGap','CrossingClearanceAt',TM);g.link('Pos','NextPosition','StationGap','Position');g.link('Dir','ReturnValue','StationGap','Direction');g.link('Length','HalfLength','StationGap','VehicleHalfLength');g.exec('Have','StationGap','else');g.node('StationResult','return');g.link('StationGap','ReturnValue','StationResult','ReturnValue');g.exec('StationGap','StationResult');g.call('Center','K2_GetActorLocation',A);g.link('Find','ReturnValue','Center','self');g.call('Green','UrbanJunctionGreen',TM);g.link('Center','ReturnValue','Green','Center');g.link('Dir','ReturnValue','Green','Direction');g.exec('Have','Green');g.call('Exit','ExitLaneClear',V,Band='2300');g.link('entry','Visitor','Exit','self');g.link('Center','ReturnValue','Exit','Centre');g.call('Pass','RequestUrbanPass',J);g.link('Find','ReturnValue','Pass','self');g.link('entry','Visitor','Pass','Visitor');g.link('Green','ReturnValue','Pass','Green');g.link('Exit','ReturnValue','Pass','ExitClear');g.exec('Green','Pass');g.link('Pass','ReturnValue','result','ReturnValue');g.exec('Pass','result');build(b,g,'JunctionClearance',[dict(name='Visitor',category='object',object=V),dict(name='ReturnValue',category='real',out=True)]);save(b)
# Validate the actual Blueprint reservation VM with perpendicular cars.
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);spawned=[]
def spawn(cls,pos=unreal.Vector()):
 a=aa.spawn_actor_from_class(unreal.load_class(None,cls),pos);spawned.append(a);return a
for path,names in [(V,['NextPosition','NextYaw','HalfLength','Lane']), (J,['Owners'])]:
 bb=unreal.load_asset(path.split('.')[0])
 for n in names:E.set_blueprint_variable_instance_editable(bb,n,True)
 E.compile_blueprint(bb);save(bb)
j=spawn(J);j.call_method('ConfigureJunction');a=spawn(V);other=spawn(V)
for v,at,yaw in [(a,unreal.Vector(-2560,0,14),0.),(other,unreal.Vector(0,-2560,14),90.)]:v.set_editor_property('NextPosition',at);v.set_editor_property('NextYaw',yaw);v.set_editor_property('HalfLength',260.)
checks={}
checks['red_denies_entry']=j.call_method('RequestUrbanPass',(a,False,True))<1
checks['green_admits_clear_exit']=j.call_method('RequestUrbanPass',(a,True,True))>1e7
checks['cross_traffic_waits']=j.call_method('RequestUrbanPass',(other,True,True))<1
checks['admitted_car_keeps_priority']=j.call_method('RequestUrbanPass',(a,False,True))>1e7
a.set_editor_property('NextPosition',unreal.Vector(3000,0,14));j.call_method('ReleaseClearedOwners');checks['released_after_rear_clears']=len(j.get_editor_property('Owners'))==0
checks['waiting_cross_traffic_then_admitted']=j.call_method('RequestUrbanPass',(other,True,True))>1e7
j.set_editor_property('Owners',[]);checks['blocked_exit_denies_entry']=j.call_method('RequestUrbanPass',(other,True,False))<1
(P/'junction_vm_checks.json').write_text(json.dumps(checks,indent=2));assert all(checks.values()),checks
for a in spawned:aa.destroy_actor(a)
unreal.log('JUNCTION_VM_CHECKS '+json.dumps(checks))
