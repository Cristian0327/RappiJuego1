import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_corrections');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;M=d.M;K='/Script/Engine.KismetSystemLibrary';AL='/Script/Engine.KismetArrayLibrary';SC='/Script/Engine.SceneComponent';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C';folder='/Game/World/BogotaUrban';plan=json.loads((U/'signal_approach_plan.json').read_text())
def build(bp,g,name,params=None):
 if params is None:g.build(name)
 else:assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps(dict(nodes=g.nodes,links=g.links,parameters=params)))
def op(g,n,fn,a=None,b=None,**kw):
 g.call(n,fn,M,**kw)
 if a:g.link(*a,n,'A')
 if b:g.link(*b,n,'B')
 return(n,'ReturnValue')
def phase(g):g.call('Time','GetGameTimeInSeconds',K);g.call('Phase','FMod',M,Divisor='110');g.link('Time','ReturnValue','Phase','Dividend')
def range_on(g,name,lo,hi):
 op(g,name+'Low','GreaterEqual_DoubleDouble',('Phase','Remainder'),B=str(lo));op(g,name+'High','Less_DoubleDouble',('Phase','Remainder'),B=str(hi));return op(g,name,'BooleanAND',(name+'Low','ReturnValue'),(name+'High','ReturnValue'))
def choose_bool(g,name,a,b,pick):
 op(g,name+'PickA','BooleanAND',pick,a);op(g,name+'NotPick','Not_PreBool',pick);op(g,name+'PickB','BooleanAND',(name+'NotPick','ReturnValue'),b);return op(g,name,'BooleanOR',(name+'PickA','ReturnValue'),(name+'PickB','ReturnValue'))
def select_phase(g,name,a,b,single):
 ib=op(g,name+'IsB','EqualEqual_IntInt',('SignalGroup','SignalGroup'),B='1');one=op(g,name+'Single','EqualEqual_IntInt',('SignalGroup','SignalGroup'),B='2');ab=choose_bool(g,name+'AB',b,a,ib);return choose_bool(g,name,single,ab,one)
bp=unreal.load_asset(folder+'/BP_BogotaSignal');d.bp=bp
if 'SignalGroup' not in [str(v) for v in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,'SignalGroup',E.get_basic_type_by_name('int'))
E.set_blueprint_variable_instance_editable(bp,'SignalGroup',True);assert E.compile_blueprint(bp);unreal.get_default_object(bp.generated_class()).set_editor_property('SignalGroup',2);g=d.Graph();phase(g);g.get('SignalGroup');green=select_phase(g,'Green',range_on(g,'GreenA',0,36),range_on(g,'GreenB',44,80),range_on(g,'GreenSingle',0,80));amber=select_phase(g,'Amber',range_on(g,'AmberA',36,40),range_on(g,'AmberB',80,84),range_on(g,'AmberSingle',80,84));op(g,'NotRed','BooleanOR',green,amber);red=op(g,'Red','Not_PreBool',('NotRed','ReturnValue'));ped=range_on(g,'Ped',88,104);pedred=op(g,'PedRed','Not_PreBool',ped);last='entry'
for component,src in [('Verde',green),('Amarillo',amber),('Rojo',red),('Peaton',ped),('PeatonRojo',pedred)]:
 g.get(component);g.call(component+'Visible','SetVisibility',SC,bPropagateToChildren='true');g.link(component,component,component+'Visible','self');g.link(*src,component+'Visible','bNewVisibility');g.exec(last,component+'Visible');last=component+'Visible'
g.exec(last,'result');build(bp,g,'ReceiveTick');assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Every road approach evaluates its own green phase, width and stop line.
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficManager');d.bp=bp;known=[str(v) for v in E.list_member_variable_names(bp)]
for n,t in [('UrbanSignalGroups',E.get_array_type(E.get_basic_type_by_name('int'))),('UrbanRoadWidths',E.get_array_type(E.get_basic_type_by_name('real'))),('UrbanStopOffsets',E.get_array_type(E.get_basic_type_by_name('real')))]:
 if n not in known:assert E.add_member_variable(bp,n,t)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());rows=plan['approaches']
for n,v in [('UrbanCrossingCenters',[unreal.Vector(*v['position']) for v in rows]),('UrbanCrossingForwards',[unreal.Vector(*v['forward']) for v in rows]),('UrbanSignalGroups',[v['signal_group'] for v in rows]),('UrbanRoadWidths',[v['road_width'] for v in rows]),('UrbanStopOffsets',[v['stop_offset'] for v in rows])]:c.set_editor_property(n,v)
g=d.Graph();phase(g)
for n in ['UrbanCrossingCenters','UrbanCrossingForwards','UrbanSignalGroups','UrbanRoadWidths','UrbanStopOffsets','SignalGap']:g.get(n)
g.setter('Reset','SignalGap',value='100000000');g.exec('entry','Reset');g.node('Each','foreach');g.link('UrbanCrossingCenters','UrbanCrossingCenters','Each','Array');g.link('Reset','then','Each','Exec')
for n,array in [('Axis','UrbanCrossingForwards'),('Group','UrbanSignalGroups'),('Width','UrbanRoadWidths'),('Stop','UrbanStopOffsets')]:
 g.call(n,'Array_Get',AL);g.link(array,array,n,'TargetArray');g.link('Each','Array Index',n,'Index')
# select_phase expects a named Group output: Array_Get has Item.

op(g,'GA','Less_DoubleDouble',('Phase','Remainder'),B='36');op(g,'GBLo','GreaterEqual_DoubleDouble',('Phase','Remainder'),B='44');op(g,'GBHi','Less_DoubleDouble',('Phase','Remainder'),B='80');op(g,'GB','BooleanAND',('GBLo','ReturnValue'),('GBHi','ReturnValue'));op(g,'GS','Less_DoubleDouble',('Phase','Remainder'),B='80');op(g,'IsB','EqualEqual_IntInt',('Group','Item'),B='1');op(g,'IsSingle','EqualEqual_IntInt',('Group','Item'),B='2');choose_bool(g,'AB',('GB','ReturnValue'),('GA','ReturnValue'),('IsB','ReturnValue'));choose_bool(g,'Green',('GS','ReturnValue'),('AB','ReturnValue'),('IsSingle','ReturnValue'));op(g,'Red','Not_PreBool',('Green','ReturnValue'));op(g,'Delta','Subtract_VectorVector',('Each','Array Element'),('entry','Position'));op(g,'Ahead','Dot_VectorVector',('Delta','ReturnValue'),('entry','Direction'));op(g,'Cross','Cross_VectorVector',('Delta','ReturnValue'),('entry','Direction'));g.call('CrossAxis','BreakVector',M);g.link('Cross','ReturnValue','CrossAxis','InVec');op(g,'Lateral','Abs',('CrossAxis','Z'));op(g,'InRoad','Less_DoubleDouble',('Lateral','ReturnValue'),('Width','Item'));op(g,'Align','Dot_VectorVector',('Axis','Item'),('entry','Direction'));op(g,'AbsAlign','Abs',('Align','ReturnValue'));op(g,'SameRoad','Greater_DoubleDouble',('AbsAlign','ReturnValue'),B='.90');op(g,'LineGap','Subtract_DoubleDouble',('Ahead','ReturnValue'),('Stop','Item'));op(g,'Gap','Subtract_DoubleDouble',('LineGap','ReturnValue'),('entry','VehicleHalfLength'));op(g,'Before','GreaterEqual_DoubleDouble',('Gap','ReturnValue'),B='-30');op(g,'Closer','Less_DoubleDouble',('Gap','ReturnValue'),('SignalGap','SignalGap'));cond='Red'
for i,n in enumerate(['InRoad','SameRoad','Before','Closer']):cond=op(g,'Valid'+str(i),'BooleanAND',(cond,'ReturnValue'),(n,'ReturnValue'))[0]
op(g,'NearbyDistance','VSizeXY',('Delta','ReturnValue'));op(g,'Nearby','Less_DoubleDouble',('NearbyDistance','ReturnValue'),B='10000');g.branch('NearApproach','Nearby');g.link('Each','LoopBody','NearApproach','execute');g.branch('Choose',cond);g.exec('NearApproach','Choose');g.setter('Keep','SignalGap','Gap');g.exec('Choose','Keep');op(g,'Safe','FMax',('SignalGap','SignalGap'),B='0');g.link('Safe','ReturnValue','result','ReturnValue');g.link('Each','Completed','result','execute');g.nodes=[n for n in g.nodes if n['id']!='GroupValue'];build(bp,g,'CrossingClearanceAt',[{'name':'Position','category':'struct','object':'/Script/CoreUObject.Vector'},{'name':'Direction','category':'struct','object':'/Script/CoreUObject.Vector'},{'name':'VehicleHalfLength','category':'real'},{'name':'ReturnValue','category':'real','out':True}])
g=d.Graph()
for n in ['NextPosition','NextYaw','HalfLength']:g.node(n,'getfield',owner=V,var=n);g.link('entry','Visitor',n,'self')
g.call('Rotation','MakeRotator',M);g.link('NextYaw','NextYaw','Rotation','Yaw');g.call('Direction','GetForwardVector',M);g.link('Rotation','ReturnValue','Direction','InRot');g.call('Clearance','CrossingClearanceAt',bp.generated_class().get_path_name());g.link('NextPosition','NextPosition','Clearance','Position');g.link('Direction','ReturnValue','Clearance','Direction');g.link('HalfLength','HalfLength','Clearance','VehicleHalfLength');g.exec('entry','Clearance');g.link('Clearance','ReturnValue','result','ReturnValue');g.exec('Clearance','result');build(bp,g,'JunctionClearance',[{'name':'Visitor','category':'object','object':V},{'name':'ReturnValue','category':'real','out':True}]);assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Match pedestrians to the protected all-red phase; preserve their physical swept walking and avoidance.
s=(U.parent/'urban_refresh/fix_physical_crossings.py').read_text();start=s.index("bp=unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrosswalkCitizen')") if "bp=unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrosswalkCitizen')" in s else 0
# Execute the existing physical walking builder with phase constants updated, without touching materials or lamps.
s=s[:s.index('# Filter fine paving')];s=s.replace("Divisor='66'","Divisor='110'").replace("B='46'","B='88'").replace("B='47.5'","B='89.5'");exec(compile(s,'Protected110SecondPedestrianPhase','exec'),{})
unreal.log('STRATEGIC_TWO_AXIS_SIGNALS_READY 110-second cycle')
