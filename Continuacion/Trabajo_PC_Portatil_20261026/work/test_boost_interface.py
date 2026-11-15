import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';I='/Game/Delivery/Interfaces/BPI_DeliveryRiderInput.BPI_DeliveryRiderInput_C';path='/Game/QA/BP_BoostInputFixture';f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(path) or T.create_asset('BP_BoostInputFixture','/Game/QA',unreal.Blueprint,f);known=[str(x) for x in E.list_member_variable_names(bp)]
for n in ['FixtureMounted','FixtureWants','FixtureThrottle']:
 if n not in known:assert E.add_member_variable(bp,n,E.get_basic_type_by_name('bool'))
assert E.compile_blueprint(bp);nodes=[];links=[['entry','then','result','execute']]
for var,out in [('FixtureMounted','Mounted'),('FixtureWants','WantsBoost'),('FixtureThrottle','HasThrottle')]:nodes.append({'id':var,'kind':'get','var':var});links.append([var,var,'result',out])
assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'QueryDeliveryInputState',json.dumps({'interface_owner':I,'nodes':nodes,'links':links}));params=[{'name':n,'category':'bool'} for n in ['Mounted','Wants','Throttle']];nodes=[];links=[];last='entry'
for var,param in [('FixtureMounted','Mounted'),('FixtureWants','Wants'),('FixtureThrottle','Throttle')]:
 nodes.append({'id':var,'kind':'set','var':var});links += [['entry',param,var,var],[last,'then',var,'execute']];last=var
links.append([last,'then','result','execute']);assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'SetInputCase',json.dumps({'parameters':params,'nodes':nodes,'links':links}));params=[{'name':'Delivery','category':'object','object':CORE}]+[{'name':n,'category':t} for n,t in [('Energy','real'),('Vehicle','byte'),('PhoneOpen','bool'),('InfiniteBoost','bool'),('bExhausted','bool'),('bHadBoost','bool'),('RegenDelayRemaining','real')]]+[{'name':'Purchased','category':'name','array':True}];nodes=[];links=[];last='entry'
for var in ['Energy','Vehicle','PhoneOpen','InfiniteBoost','bExhausted','bHadBoost','RegenDelayRemaining','Purchased']:
 nodes.append({'id':'Set'+var,'kind':'setfield','owner':CORE,'var':var});links += [['entry','Delivery','Set'+var,'self'],['entry',var,'Set'+var,var],[last,'then','Set'+var,'execute']];last='Set'+var
for var,value in [('Capacity','100'),('Drain','20'),('Regen','15'),('BoostActive','false'),('BoostUsedFrame','false'),('BikeEnergy','100'),('MotoEnergy','100')]:
 nodes.append({'id':'Set'+var,'kind':'setfield','owner':CORE,'var':var,'defaults':{var:value}});links += [['entry','Delivery','Set'+var,'self'],[last,'then','Set'+var,'execute']];last='Set'+var
links.append([last,'then','result','execute']);assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'ConfigureBoostCase',json.dumps({'parameters':params,'nodes':nodes,'links':links}));assert E.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.EditorLoadingAndSavingUtils.new_blank_map(False);owner=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(bp.generated_class(),unreal.Vector());core=owner.call_method('AddComponentByClass',args=(unreal.load_class(None,CORE),False,unreal.Transform(),False));checks=[]
def ck(n,a,b=True):
 assert a==b,(n,a,b);checks.append(n)
def val(n):return core.get_editor_property(n)
def near(n,expected):ck(n,math.isclose(val(n),expected,abs_tol=.001))
def setup(energy=100,vehicle=0,phone=False,infinite=False,exhausted=False,had=False,cooldown=0,purchased=[]):owner.call_method('ConfigureBoostCase',args=(core,float(energy),vehicle,phone,infinite,exhausted,had,float(cooldown),[unreal.Name(x) for x in purchased]))
def inputs(mounted=True,wants=True,throttle=True):owner.call_method('SetInputCase',args=(mounted,wants,throttle))
def step(t):core.call_method('UpdateBoost',args=(float(t),))
setup();inputs();step(1);near('Energy',80);ck('BikeBoostActive',val('BoostActive'));near('BikeEnergy',80);inputs(wants=False);step(.5);near('Energy',80);near('RegenDelayRemaining',1);step(1);near('Energy',95);ck('ReleaseStopsBoost',val('BoostActive'),False)
setup(energy=10);inputs();step(1);near('Energy',0);ck('Exhausted',val('bExhausted'));ck('ExhaustedBoostOff',val('BoostActive'),False);near('RegenDelayRemaining',1.5);step(.5);near('Energy',0);step(.5);near('Energy',0);step(.5);near('Energy',7.5);ck('StillExhaustedBelowThreshold',val('bExhausted'));step(1);near('Energy',22.5);ck('RecoveredAfterThreshold',val('bExhausted'),False);step(1);near('Energy',2.5);ck('CanBoostAgain',val('BoostActive'))
setup(energy=50,infinite=True);inputs();step(10);near('Energy',50);ck('InfiniteBoostActive',val('BoostActive'))
for name,mounted,wants,throttle,phone in [('Walking',False,True,True,False),('NoThrottle',True,True,False,False),('Phone',True,True,True,True)]:
 setup(energy=50,phone=phone);inputs(mounted,wants,throttle);step(1);ck(name+'NoBoost',val('BoostActive'),False);near('Energy',65)
setup(energy=50,vehicle=1);inputs();step(1);ck('LockedMotoTurbo',val('BoostActive'),False);near('Energy',65);setup(energy=50,vehicle=1,purchased=['MotoTurbo']);inputs();step(1);ck('UnlockedMotoTurbo',val('BoostActive'));near('Energy',30);near('MotoEnergy',30)
for delta in [0,-1,-100]:
 setup(energy=50);inputs();step(delta);near('Energy',50)
setup(energy=50,exhausted=True,cooldown=1);inputs(wants=False);step(-1);near('Energy',50);near('RegenDelayRemaining',1)
(r/'work/boost_interface_vm_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'count':len(checks),'profile_saved':False},indent=2));unreal.log('BOOST_INTERFACE_VM_VALIDATION_PASS checks='+str(len(checks)))
