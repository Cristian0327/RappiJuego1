from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/traffic_gameplay_repair/implement.py'
exec(compile(p.read_text().split('# Recovery never')[0],str(p),'exec'))
b=use('/Game/Traffic/Services/BP_VoxelRoadVehicle');addvar(b,'BodyContactLogTime',real);assert E.compile_blueprint(b)
g=d.Graph();g.get('BodyContactLogTime');g.get('CapsuleComponent')
g.call('SelfActor','GetOwner','/Script/Engine.ActorComponent');g.link('CapsuleComponent','CapsuleComponent','SelfActor','self');g.call('SelfName','GetObjectName',K);g.link('SelfActor','ReturnValue','SelfName','Object')
g.call('Clock','GetGameTimeInSeconds',K);op(g,'SinceLast','Subtract_DoubleDouble',('Clock','ReturnValue'),('BodyContactLogTime','BodyContactLogTime'));op(g,'Due','Greater_DoubleDouble',('SinceLast','ReturnValue'),B='.5')
g.call('NormalXYZ','BreakVector',M);g.link('entry','HitNormal','NormalXYZ','InVec');op(g,'NormalZ','Abs',('NormalXYZ','Z'));op(g,'SideHit','Less_DoubleDouble',('NormalZ','ReturnValue'),B='.8');op(g,'ShouldLog','BooleanAND',('Due','ReturnValue'),('SideHit','ReturnValue'));g.branch('LogHit','ShouldLog');g.exec('entry','LogHit');g.setter('RememberTime','BodyContactLogTime','Clock');g.exec('LogHit','RememberTime')
for tag,pin in [('OtherActor','Other'),('OtherComponent','OtherComp')]:g.call(tag,'GetObjectName',K);g.link('entry',pin,tag,'Object')
g.call('Position','K2_GetActorLocation',A)
fields=[('Clock','ReturnValue','real'),('SelfName','ReturnValue','str'),('OtherActor','ReturnValue','str'),('OtherComponent','ReturnValue','str'),('entry','HitLocation','vec'),('entry','HitNormal','vec'),('Position','ReturnValue','vec')]
prev=None
for i,(src,pin,typ) in enumerate(fields):
    name='Contact'+str(i)
    if typ!='str':
        fn,inp={'real':('Conv_DoubleToString','InDouble'),'vec':('Conv_VectorToString','InVec')}[typ];g.call(name,fn,'/Script/Engine.KismetStringLibrary');g.link(src,pin,name,inp);value=(name,'ReturnValue')
    else:value=(src,pin)
    g.call(name+'Join','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='V2CONTACT|' if prev is None else '')
    if prev:g.link(*prev,name+'Join','A')
    g.link(*value,name+'Join','B');g.call(name+'Sep','Concat_StrStr','/Script/Engine.KismetStringLibrary',B='|');g.link(name+'Join','ReturnValue',name+'Sep','A');prev=(name+'Sep','ReturnValue')
g.call('PrintContact','PrintString',K,bPrintToScreen='false');g.link(*prev,'PrintContact','InString');g.exec('RememberTime','PrintContact');build(b,g,'ReceiveHit');save(b)
p=root/'scripts/build_current_traffic_causes.py';exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p),'probe_only':True})
unreal.log('COLLISION_DIAGNOSTICS_READY')
