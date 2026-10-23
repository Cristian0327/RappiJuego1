import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
s=(r/'work/build_pure_road_interaction.py').read_text(encoding='utf-8-sig');exec(compile(s[:s.index("for fn in ['EnterRoad'")],'ExistingRoadSetup','exec'))
bk=r/'Recuperacion_Migracion_Blueprints/2026-10-19_closed_cabin';bk.mkdir(parents=True,exist_ok=True);src=r/'RappiJuego1/Content/Delivery/BlueprintGameplay/Player/BP_RoadInteraction.uasset'
if not (bk/src.name).exists():shutil.copy2(src,bk/src.name)
# Reapply only the current road lifecycle, leaving traffic and controls untouched.
s=(r/'work/fix_car_entry_yield.py').read_text(encoding='utf-8-sig');part=s[s.index('# Existing transition lifecycle'):s.index('# Independent geometric player clearance')]
part=part.replace("A='218',B='110'","A='205',B='85'")
part=part.replace('exec(compile(body,\'RoadEntryRestore\',\'exec\'))', """
body=body.replace(\"g.exec('NeutralRotation','IdleMode')\",\"target(g,'RestoreVisible','SetVisibility',SC,'Hero','Mesh',bNewVisibility='true',bPropagateToChildren='true');g.exec('NeutralRotation','RestoreVisible');g.exec('RestoreVisible','IdleMode')\")
exec(compile(body,'RoadEntryRestore','exec'))
""")
part=part.replace("exec(compile(body,'RoadSeatedCompletion','exec'))", """
body=body.replace(\"g.exec('FollowSeat','result')\",\"target(g,'ClosedCabin','SetVisibility',SC,'Hero','Mesh',bNewVisibility='false',bPropagateToChildren='true');g.exec('FollowSeat','ClosedCabin');g.exec('ClosedCabin','result')\")
body=body.replace(\"g.exec('Seek','CloseNow')\",\"op(g,'OutsideEntering','Less_DoubleDouble',out('Progress'),B='.85');op(g,'OutsideExiting','Greater_DoubleDouble',out('Progress'),B='.15');op(g,'NotExiting','Not_PreBool',out('Exiting'));op(g,'ShowExit','BooleanAND',out('OutsideExiting'),out('Exiting'));op(g,'ShowEnter','BooleanAND',out('OutsideEntering'),out('NotExiting'));op(g,'BodyVisible','BooleanOR',out('ShowExit'),out('ShowEnter'));target(g,'TransitionVisible','SetVisibility',SC,'Hero','Mesh',bPropagateToChildren='true');g.link('BodyVisible','ReturnValue','TransitionVisible','bNewVisibility');g.exec('Seek','TransitionVisible');g.exec('TransitionVisible','CloseNow')\")
exec(compile(body,'RoadClosedCabinCompletion','exec'))
""")
s=(r/'work/build_pure_road_interaction.py').read_text(encoding='utf-8-sig');exec(compile(part,'ClosedCabinLifecycle','exec'));assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('CLOSED_CABIN_PATCH_PASS')
# Focused runtime regression: visibility is restored on exit, cabin remains opaque, prior controls preserved.
s=(r/'work/build_car_entry_yield_qa.py').read_text(encoding='utf-8-sig');s=s.replace('BP_TestCarEntryYield','BP_TestClosedCabin').replace('CAR_ENTRY_YIELD ','CLOSED_CABIN ').replace("/Game/QA/CarEntryYield'","/Game/QA/ClosedCabin'")
s=s.replace("p0=phase('ExitCar',4)","""p0=phase('HiddenDriver',3.8);g.call('DriverVisible','IsVisible',SC);g.link('Mesh','Mesh','DriverVisible','self');g.call('DriverConcealed','Not_PreBool',M);g.link('DriverVisible','ReturnValue','DriverConcealed','A');report('DRIVER_HIDDEN_INSIDE_CLOSED_CABIN',p0,'DriverConcealed')
p0=phase('ExitCar',4)""")
s=s.replace("p0=phase('TrafficRoute',6.4)","""p0=phase('VisibleAfterExit',6.3);g.call('ExitVisible','IsVisible',SC);g.link('Mesh','Mesh','ExitVisible','self');report('DRIVER_VISIBLE_AFTER_EXIT',p0,'ExitVisible')
p0=phase('TrafficRoute',6.4)""")
exec(compile(s,'ClosedCabinRegression','exec'))


