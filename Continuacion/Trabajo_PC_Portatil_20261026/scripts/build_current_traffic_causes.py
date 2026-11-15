from pathlib import Path
import unreal

folder=Path(__file__).resolve().parent/'map_adaptation_v2'
debug=(folder/'build_debug_traffic.py').read_text()
extra=debug.split('extra="""',1)[1].split('"""',1)[0]
# Include the actual pawn seen by the front sensor for a stopped queue head.
pawn_probe="""
field(g,'SensorHalfLength','HalfLength',('Each','Array Element'),V);field(g,'SensorHalfWidth','HalfWidth',('Each','Array Element'),V)
g.call('SensorRot','MakeRotator',M);g.link('NextYaw','NextYaw','SensorRot','Yaw');g.call('SensorForward','GetForwardVector',M);g.link('SensorRot','ReturnValue','SensorForward','InRot')
op(g,'SensorNoseOffset','Multiply_VectorFloat',('SensorForward','ReturnValue'),('SensorHalfLength','HalfLength'));op(g,'SensorNose','Add_VectorVector',('NextPosition','NextPosition'),('SensorNoseOffset','ReturnValue'));op(g,'SensorStart','Add_VectorVector',('SensorNose','ReturnValue'),B='(X=0,Y=0,Z=100)');op(g,'SensorAhead','Multiply_VectorFloat',('SensorForward','ReturnValue'),B='1200');op(g,'SensorEnd','Add_VectorVector',('SensorStart','ReturnValue'),('SensorAhead','ReturnValue'))
g.node('SensorTypes','makearray',defaults={'[0]':'ObjectTypeQuery3'});g.call('SensorTrace','SphereTraceSingleForObjects',K,bTraceComplex='false',bIgnoreSelf='true',DrawDebugType='None');g.link('SensorTypes','Array','SensorTrace','ObjectTypes');g.link('SensorStart','ReturnValue','SensorTrace','Start');g.link('SensorEnd','ReturnValue','SensorTrace','End');g.link('SensorHalfWidth','HalfWidth','SensorTrace','Radius')
g.call('SensorHit','BreakHitResult',G);g.link('SensorTrace','OutHit','SensorHit','Hit');g.call('SensorActor','GetObjectName',K);g.link('SensorHit','HitActor','SensorActor','Object')
"""
extra=pawn_probe+extra
extra=extra.replace("g.exec('StopNearby','StopJunction')", "g.exec('StopNearby','SensorTrace');g.exec('SensorTrace','StopJunction')")
extra=extra.replace("('JunctionName','ReturnValue','str')],end)", "('JunctionName','ReturnValue','str'),('SensorActor','ReturnValue','str'),('SensorHit','Distance','real')],end)")
capacity_probe="""
field(g,'CauseMovement','ArcBestMovement',('ManagerCast','AsBP Traffic Manager'),TM);field(g,'CauseFreeGap','ExitFreeGap',('ManagerCast','AsBP Traffic Manager'),TM);field(g,'CauseReservedGap','ExitReservedGap',('ManagerCast','AsBP Traffic Manager'),TM)
"""
extra=capacity_probe+extra
extra=extra.replace("('SensorHit','Distance','real')],end)", "('SensorHit','Distance','real'),('CauseMovement','ArcBestMovement','int'),('CauseFreeGap','ExitFreeGap','real'),('CauseReservedGap','ExitReservedGap','real')],end)")
path=folder/'build_resume_diagnostics.py'
source=path.read_text()
marker="s=(P/'build_traffic_probe.py').read_text()"
assert marker in source
injection="\nneedle='# Foreach loop output uses LoopBody rather than then.'\ns=s.replace(needle,"+repr(extra)+"+'\\n'+needle)\n"
source=source.replace(marker,marker+injection,1)
if globals().get('probe_only',False):
    source=source.replace("exec(compile(s,'DetailedTrafficProbe','exec'),{})", "s=s[:s.index('unreal.EditorLoadingAndSavingUtils.load_map(')]\nexec(compile(s,'DetailedTrafficProbe','exec'),{})")
exec(compile(source,str(path),'exec'),{'__file__':str(path)})
unreal.log('CURRENT_TRAFFIC_CAUSES_READY')
