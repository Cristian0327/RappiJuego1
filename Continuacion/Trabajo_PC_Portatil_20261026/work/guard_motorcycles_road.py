import unreal,json,sys,math,re
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;P='/Game/Traffic/Services/BP_TwoWheelerCitizen.BP_TwoWheelerCitizen_C';bp=unreal.load_asset(P.rsplit('.',1)[0]);d.bp=bp
g=d.Graph()
for n in ['Bicycle','RoadMode','State','Route','RouteIndex']:g.get(n)
def op(n,fn,a=None,b=None,**kw):
 g.call(n,fn,M,**kw)
 if a:g.link(*a,n,'Value' if fn=='FClamp' else 'A')
 if b:g.link(*b,n,'B')
 return(n,'ReturnValue')
no_bike=op('Motorcycle','Not_PreBool',('Bicycle','Bicycle'));riding=op('Riding','Less_DoubleDouble',('State','State'),B='2');road=op('RoadRiding','BooleanAND',('RoadMode','RoadMode'),riding);guard=op('Constrain','BooleanAND',road,no_bike);g.branch('Guard',*guard);g.exec('entry','Guard');g.node('Fallback','return');g.link('entry','DesiredDirection','Fallback','ReturnValue');g.exec('Guard','Fallback','else')
g.call('Count','Array_Length','/Script/Engine.KismetArrayLibrary');g.link('Route','Route','Count','TargetArray');enough=op('Enough','Greater_IntInt',('Count','ReturnValue'),B='1');g.branch('ValidRoute',*enough);g.exec('Guard','ValidRoute');g.exec('ValidRoute','Fallback','else');prev=op('Previous','Add_IntInt',('RouteIndex','RouteIndex'),('Count','ReturnValue'));minus=op('MinusOne','Subtract_IntInt',prev,B='1');index=op('PreviousIndex','Percent_IntInt',minus,('Count','ReturnValue'))
for name,idx in [('Anchor',index),('Goal',('RouteIndex','RouteIndex'))]:
 g.call(name,'Array_Get','/Script/Engine.KismetArrayLibrary');g.link('Route','Route',name,'TargetArray');g.link(*idx,name,'Index')
segment=op('Segment','Subtract_VectorVector',('Goal','Item'),('Anchor','Item'));forward=op('Forward','Normal2D',segment);right=op('Right','Cross_VectorVector',forward,B='(X=0,Y=0,Z=1)');g.call('At','K2_GetActorLocation','/Script/Engine.Actor');delta=op('Offset','Subtract_VectorVector',('At','ReturnValue'),('Anchor','Item'));side=op('Side','Dot_VectorVector',delta,right);inputside=op('InputSide','Dot_VectorVector',('entry','DesiredDirection'),right);look=op('LookAhead','Multiply_DoubleDouble',inputside,B='220');pred=op('PredictedSide','Add_DoubleDouble',side,look);mag=op('Magnitude','Abs',pred);off=op('OutsideLane','Greater_DoubleDouble',mag,B='140');g.branch('Outside',*off);g.exec('ValidRoute','Outside');g.exec('Outside','Fallback','else');gain=op('Correction','Divide_DoubleDouble',side,B='120');clamp=op('BoundedCorrection','FClamp',gain,Min='-1',Max='1');lateral=op('CorrectionVector','Multiply_VectorFloat',right,clamp);signed=op('ForwardDot','Dot_VectorVector',('entry','DesiredDirection'),forward);reverse=op('Reversing','Less_DoubleDouble',signed,B='0');g.call('Sign','SelectFloat',M,A='-1',B='1');g.link(*reverse,'Sign','bPickA');heading=op('TravelForward','Multiply_VectorFloat',forward,('Sign','ReturnValue'));safe=op('Centered','Subtract_VectorVector',heading,lateral);normal=op('SafeDirection','Normal2D',safe);g.link(*normal,'result','ReturnValue');g.exec('Outside','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'KeepMotorcycleOnRoad',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'DesiredDirection','category':'struct','object':'/Script/CoreUObject.Vector'},{'name':'ReturnValue','category':'struct','object':'/Script/CoreUObject.Vector','out':True}],'pure':True,'const':True}));assert E.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Add the guard to the existing corrected avoidance/pedalling graph, preserving its other logic.
oldbuild=d.Graph.build
def guarded(self,name):
 if d.bp.get_name()=='BP_TwoWheelerCitizen':
  count=0
  for node in list(self.nodes):
   for pin,value in list(node.get('defaults',{}).items()):
    if not isinstance(value,str) or 'Pitch=' not in value or 'Yaw=' not in value:continue
    vals=dict(re.findall(r'(Pitch|Yaw|Roll)=([-+0-9.]+)',value))
    if len(vals)!=3:continue
    tag='ExplicitNpcRotation'+str(count);count+=1;self.call(tag,'MakeRotator',M,**vals);self.link(tag,'ReturnValue',node['id'],pin);del node['defaults'][pin]
 if name=='ReceiveTick' and d.bp.get_name()=='BP_TwoWheelerCitizen':
  wire=next(x for x in self.links if x[2:] == ['Walk','WorldDirection']);self.links.remove(wire);self.call('RoadSurfaceGuard','KeepMotorcycleOnRoad',P);self.link(wire[0],wire[1],'RoadSurfaceGuard','DesiredDirection');self.link('RoadSurfaceGuard','ReturnValue','Walk','WorldDirection')
 return oldbuild(self,name)
d.Graph.build=guarded
try:
 s=(r/'work/fix_requested_animations.py').read_text(encoding='utf-8-sig');s=s[s.index('# NPCs share'):s.index('# A dedicated sprint graph')];exec(compile(s,'PreserveCorrectedCyclesWithRoadGuard','exec'),{'r':r})
finally:d.Graph.build=oldbuild
bp=unreal.load_asset(P.rsplit('.',1)[0]);E.set_blueprint_variable_instance_editable(bp,'State',True);assert E.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(500,400,120))
try:
 a.set_editor_property('Bicycle',False);a.set_editor_property('RoadMode',True);a.set_editor_property('State',0.);a.set_editor_property('Route',[unreal.Vector(0,0,120),unreal.Vector(1000,0,120)]);a.set_editor_property('RouteIndex',1);v=a.call_method('KeepMotorcycleOnRoad',(unreal.Vector(1,1,0),));assert v.y<0
 a.set_actor_location(unreal.Vector(500,0,120),False,True);v=a.call_method('KeepMotorcycleOnRoad',(unreal.Vector(1,0,0),));assert v.x>.99 and abs(v.y)<.01
 a.set_editor_property('Bicycle',True);v=a.call_method('KeepMotorcycleOnRoad',(unreal.Vector(0,1,0),));assert v.y>.99
 a.call_method('ReceiveBeginPlay');yaw=a.get_editor_property('mesh').get_editor_property('relative_rotation').yaw;assert abs(unreal.MathLibrary.normalize_axis(yaw+90))<1,('rider_basis',yaw)
 (r/'work/motorcycle_road_guard_validation.json').write_text(json.dumps({'checks':4,'status':'PASS','road_only':True,'no_teleport':True},indent=2));unreal.log('MOTORCYCLE_ROAD_BOUNDARY_PASS')
finally:actors.destroy_actor(a)

