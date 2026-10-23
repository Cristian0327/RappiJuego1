import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;A='/Script/Engine.Actor';G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';SC='/Script/Engine.SceneComponent';SK='/Script/Engine.SkeletalMeshComponent';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C'
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-19_controls_camera_mount'
for rel in ['Delivery/BlueprintGameplay/Player','Delivery/BlueprintGameplay/Developer','Delivery/Animation','VoxelExplorer/AN_HeroMountBike.uasset','VoxelExplorer/AN_HeroMountMoto.uasset','Crowd/AN_CrowdMountBike.uasset','Crowd/AN_CrowdMountMoto.uasset','Traffic/Services/BP_TwoWheelerCitizen.uasset']:
 src=r/'RappiJuego1/Content'/rel;dst=backup/rel
 if not dst.exists():
  dst.parent.mkdir(parents=True,exist_ok=True)
  if src.is_dir():shutil.copytree(src,dst)
  elif src.exists():shutil.copy2(src,dst)
def save(bp):
 assert E.compile_blueprint(bp),bp.get_name()
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
def build(g,n,params=None,pure=False):
 spec={'nodes':g.nodes,'links':g.links}
 if params is not None:spec['parameters']=params
 if pure:spec.update(pure=True,const=True)
 assert unreal.DeliveryEditorLibrary.build_logic_graph(d.bp,n,json.dumps(spec)),n
# Keep road transition, following and caches intact: rebuild ONLY its request and Tick.
s=(r/'work/build_pure_road_interaction.py').read_text(encoding='utf-8-sig');prefix=s[:s.index("for fn in ['EnterRoad'")];ns={};exec(compile(prefix,'RoadExistingSetup','exec'),ns)
body=s[s.index('# Request is called'):s.index('# Add a road interaction check')]
body=body.replace("out('CarsUnlocked'),out('PhoneClosed')","out('DevWalking'),out('PhoneClosed')").replace("out('AbsSpeed'),B='80'","out('AbsSpeed'),B='1800'")
body=body.replace("g.link('Steer','ReturnValue','Motion','Steer')","g.link('Keyboard','SideInput','Motion','Steer')")
exec(compile(body,'RoadDeveloperKeyboardFix','exec'),ns)
bp=ns['bp'];unreal.get_default_object(bp.generated_class()).set_editor_property('CarsEnabled',True);save(bp)
# Two-wheel steering is exclusively A/D.
bp=unreal.load_asset(R.rsplit('.',1)[0]);d.bp=bp;g=d.Graph();g.get('SideInput');g.call('Steer','FClamp',M,Min='-1',Max='1');g.link('SideInput','SideInput','Steer','Value')
s=(r/'work/build_combined_vehicle_controls.py').read_text(encoding='utf-8-sig');body=s[s.index("g.get('BikeSpeed');"):s.index("g.build('SteeringAngle')")];exec(compile(body,'KeyboardSteering','exec'));build(g,'SteeringAngle',[{'name':'Dt','category':'real'},{'name':'ReturnValue','category':'real','out':True}],True)
# On foot, latch the view basis at movement start; orbiting while holding W never turns movement.
known=[str(x) for x in E.list_member_variable_names(bp)]
for n,t in [('InputBasisYaw',E.get_basic_type_by_name('real')),('InputBasisValid',E.get_basic_type_by_name('bool'))]:
 if n not in known:assert E.add_member_variable(bp,n,t)
assert E.compile_blueprint(bp)
for name,var,axis in [('MoveForward','ForwardInput','GetForwardVector'),('MoveRight','SideInput','GetRightVector')]:
 g=d.Graph()
 for n in ['Delivery','Riding','RoadActive','ForwardInput','SideInput','InputBasisYaw','InputBasisValid']:g.get(n)
 g.setter('AxisValue',var,'entry','V');g.exec('entry','AxisValue');g.node('Phone','getfield',owner=CORE,var='PhoneOpen');g.link('Delivery','Delivery','Phone','self');g.branch('PhoneOpen','Phone','PhoneOpen');g.exec('AxisValue','PhoneOpen');g.setter('ClearAxis',var,value='0');g.exec('PhoneOpen','ClearAxis');g.exec('ClearAxis','result');g.call('Vehicle','BooleanOR',M);g.link('Riding','Riding','Vehicle','A');g.link('RoadActive','RoadActive','Vehicle','B');g.branch('InVehicle','Vehicle');g.exec('PhoneOpen','InVehicle','else');g.exec('InVehicle','result')
 for n in ['ForwardInput','SideInput']:
  g.call(n+'Abs','Abs',M);g.link(n,n,n+'Abs','A')
 g.call('AxisSum','Add_DoubleDouble',M);g.link('ForwardInputAbs','ReturnValue','AxisSum','A');g.link('SideInputAbs','ReturnValue','AxisSum','B');g.call('HasInput','Greater_DoubleDouble',M,B='.01');g.link('AxisSum','ReturnValue','HasInput','A');g.branch('Moving','HasInput');g.exec('InVehicle','Moving','else');g.setter('UnlockBasis','InputBasisValid',value='false');g.exec('Moving','UnlockBasis','else');g.exec('UnlockBasis','result');g.branch('BasisCached','InputBasisValid','InputBasisValid');g.exec('Moving','BasisCached');g.call('View','GetControlRotation','/Script/Engine.Pawn');g.call('Angles','BreakRotator',M);g.link('View','ReturnValue','Angles','InRot');g.setter('CacheBasis','InputBasisYaw','Angles','Yaw');g.exec('BasisCached','CacheBasis','else');g.setter('LockBasis','InputBasisValid',value='true');g.exec('CacheBasis','LockBasis');g.call('Basis','MakeRotator',M);g.link('InputBasisYaw','InputBasisYaw','Basis','Yaw');g.call('Direction',axis,M);g.link('Basis','ReturnValue','Direction','InRot');g.call('Move','AddMovementInput','/Script/Engine.Pawn');g.link('Direction','ReturnValue','Move','WorldDirection');g.link('entry','V','Move','ScaleValue');g.exec('BasisCached','Move');g.exec('LockBasis','Move');g.exec('Move','result');build(g,name,[{'name':'V','category':'real'}])
save(bp)
unreal.log('CONTROLS_AND_DEVELOPER_ENTRY_PASS')
