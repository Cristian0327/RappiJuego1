import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;K='/Script/Engine.KismetSystemLibrary'
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-20_drive_doors'
for rel in ['Delivery/BlueprintGameplay/Player/BP_BlueprintRider.uasset','World/BlueprintWorld/Traffic/BP_TrafficVehicle.uasset']:
 p=backup/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():shutil.copy2(r/'RappiJuego1/Content'/rel,p)
# Retain the existing sweep, terrain support, and wheel updates; tune only manual driving.
s=(r/'work/build_pure_manual_road_motion.py').read_text(encoding='utf-8-sig')
s=s.replace("A='540',B='1800'","A='250',B='1000'").replace("InterpSpeed='700'","InterpSpeed='250'").replace("out('Steer'),B='32'","out('Steer'),B='22'")
s=s.replace("op(g,'WheelSteer','Multiply_DoubleDouble',out('Steer'),B='22')","g.get('SteerAngle');g.call('SmoothSteering','FInterpTo',M,InterpSpeed='4');g.link('SteerAngle','SteerAngle','SmoothSteering','Current');op(g,'RequestedWheel','Multiply_DoubleDouble',out('Steer'),B='22');g.link('RequestedWheel','ReturnValue','SmoothSteering','Target');g.link('entry','Dt','SmoothSteering','DeltaTime');op(g,'WheelSteer','FClamp',out('SmoothSteering'),Min='-22',Max='22')")
# Brake faster than accelerating, including when S is pressed before reversing.
s=s.replace("g.call('SpeedStep','FInterpTo_Constant',M,InterpSpeed='250')","op(g,'InputMagnitude','Abs',out('Throttle'));op(g,'Coasting','Less_DoubleDouble',out('InputMagnitude'),B='.01');op(g,'Opposing','Multiply_DoubleDouble',out('Throttle'),('Speed','Speed'));op(g,'Braking','Less_DoubleDouble',out('Opposing'),B='0');g.call('BrakeRate','SelectFloat',M,A='700',B='250');g.link('Braking','ReturnValue','BrakeRate','bPickA');g.call('AccelRate','SelectFloat',M,A='380');g.link('BrakeRate','ReturnValue','AccelRate','B');g.link('Coasting','ReturnValue','AccelRate','bPickA');g.call('SpeedStep','FInterpTo_Constant',M);g.link('AccelRate','ReturnValue','SpeedStep','InterpSpeed')")
exec(compile(s,'ComfortableManualDriving','exec'))
# Pure rider function: modest top speed, progressive throttle and responsive braking.
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider');d.bp=bp
R=bp.generated_class().get_path_name()
def build(g,n,params,pure=False):
 assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,n,json.dumps({'nodes':g.nodes,'links':g.links,'parameters':params,'pure':pure,'const':pure}))
g=d.Graph();g.get('BikeSpeed');g.get('ForwardInput')
g.call('Limit','FClamp',M,Min='0',Max='1000');g.link('entry','TopSpeed','Limit','Value');g.call('TargetRaw','Multiply_DoubleDouble',M);g.link('ForwardInput','ForwardInput','TargetRaw','A');g.link('Limit','ReturnValue','TargetRaw','B');g.call('Target','FClamp',M,Min='-220',Max='1000');g.link('TargetRaw','ReturnValue','Target','Value')
g.call('InputAbs','Abs',M);g.link('ForwardInput','ForwardInput','InputAbs','A');g.call('Coasting','Less_DoubleDouble',M,B='.01');g.link('InputAbs','ReturnValue','Coasting','A');g.call('Product','Multiply_DoubleDouble',M);g.link('ForwardInput','ForwardInput','Product','A');g.link('BikeSpeed','BikeSpeed','Product','B');g.call('Brake','Less_DoubleDouble',M,B='0');g.link('Product','ReturnValue','Brake','A');g.call('Rate','SelectFloat',M,A='650',B='220');g.link('Brake','ReturnValue','Rate','bPickA');g.call('CoastRate','SelectFloat',M,A='320');g.link('Rate','ReturnValue','CoastRate','B');g.link('Coasting','ReturnValue','CoastRate','bPickA');g.call('Step','FInterpTo_Constant',M);g.link('BikeSpeed','BikeSpeed','Step','Current');g.link('Target','ReturnValue','Step','Target');g.link('entry','Dt','Step','DeltaTime');g.link('CoastRate','ReturnValue','Step','InterpSpeed');g.link('Step','ReturnValue','result','ReturnValue');g.exec('entry','result');build(g,'AdvanceDriveSpeed',[{'name':'Dt','category':'real'},{'name':'TopSpeed','category':'real'},{'name':'ReturnValue','category':'real','out':True}])
# Keep keyboard steering and free-look; reduce the turn rate at speed.
g=d.Graph();g.get('SideInput');g.call('Steer','FClamp',M,Min='-1',Max='1');g.link('SideInput','SideInput','Steer','Value')
s=(r/'work/build_combined_vehicle_controls.py').read_text(encoding='utf-8-sig');body=s[s.index("g.get('BikeSpeed');"):s.index("g.build('SteeringAngle')")];body=body.replace("B='200'","B='350'").replace("B='75'","B='38'");exec(body);build(g,'SteeringAngle',[{'name':'Dt','category':'real'},{'name':'ReturnValue','category':'real','out':True}],True);assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Generated skeletal reductions damaged the rigid voxel panels/UVs. Use their authored mesh.
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');d.bp=bp
s=(r/'work/extend_pure_traffic_doors.py').read_text(encoding='utf-8-sig');s=s[:s.index('g=d.Graph()\nfor n in')];s=s.replace("g=d.Graph();g.get('Body');last='entry'","g=d.Graph();g.get('Body');g.call('RigidVoxelLOD','SetForcedLOD','/Script/Engine.SkinnedMeshComponent',InNewForcedLOD='1');g.link('Body','Body','RigidVoxelLOD','self');g.exec('entry','RigidVoxelLOD');last='RigidVoxelLOD'");exec(compile(s,'PreserveRigidVehiclePanels','exec'));assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('COMFORTABLE_DRIVING_SOLID_DOORS_PASS')
