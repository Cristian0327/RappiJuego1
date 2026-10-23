import unreal,json,sys,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/BlueprintWorld/Traffic';f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);base=unreal.load_asset(folder+'/BP_TrafficLane') or T.create_asset('BP_TrafficLane',folder,unreal.Blueprint,f)
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
handles=sub.k2_gather_subobject_data_for_blueprint(base);curve=None
for h in handles:
 if str(lib.get_variable_name(lib.get_data(h)))=='Route':curve=lib.get_object_for_blueprint(lib.get_data(h),base)
if not curve:
 h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=handles[0],new_class=unreal.SplineComponent,blueprint_context=base));assert not str(reason);assert sub.rename_subobject(h,unreal.Text('Route'));curve=lib.get_object_for_blueprint(lib.get_data(h),base)
curve.set_editor_property('can_ever_affect_navigation',False)
known=[str(x) for x in E.list_member_variable_names(base)]
for n,t in [('LaneGroup',E.get_basic_type_by_name('int')),('BusOnly',E.get_basic_type_by_name('bool')),('CruiseSpeed',E.get_basic_type_by_name('real'))]:
 if n not in known:assert E.add_member_variable(base,n,t)
assert E.compile_blueprint(base);d.bp=base;M=d.M;S='/Script/Engine.SplineComponent'
for name,fn,out_type in [('RouteLength','GetSplineLength','real'),('SamplePosition','GetLocationAtDistanceAlongSpline','struct'),('SampleHeading','GetDirectionAtDistanceAlongSpline','struct')]:
 g=d.Graph();g.get('Route');g.call('Sample',fn,S,**({'CoordinateSpace':'World'} if name!='RouteLength' else {}));g.link('Route','Route','Sample','self');params=[]
 if name!='RouteLength':
  g.call('Length','GetSplineLength',S);g.link('Route','Route','Length','self');g.call('Modulo','FMod',M);g.link('entry','Distance','Modulo','Dividend');g.link('Length','ReturnValue','Modulo','Divisor');g.call('Positive','Add_DoubleDouble',M);g.link('Modulo','Remainder','Positive','A');g.link('Length','ReturnValue','Positive','B');g.call('Wrap','FMod',M);g.link('Positive','ReturnValue','Wrap','Dividend');g.link('Length','ReturnValue','Wrap','Divisor');g.link('Wrap','Remainder','Sample','Distance');params.append({'name':'Distance','category':'real'})
 params.append(dict(name='ReturnValue',category=out_type,**({'object':'/Script/CoreUObject.Vector'} if out_type=='struct' else {}),out=True));g.link('Sample','ReturnValue','result','ReturnValue');g.exec('entry','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(base,name,json.dumps({'nodes':g.nodes,'links':g.links,'parameters':params,'pure':True,'const':True}))
assert E.compile_blueprint(base);assert unreal.EditorAssetLibrary.save_loaded_asset(base,only_if_is_dirty=False)
def rounded(x0,x1,y0,y1,radius,reverse):
 points=[]
 for c,(x,y) in enumerate([(x1-radius,y0+radius),(x1-radius,y1-radius),(x0+radius,y1-radius),(x0+radius,y0+radius)]):
  for step in range(13):
   a=math.radians(-90+c*90+step*7.5);points.append(unreal.Vector(x+math.cos(a)*radius,y+math.sin(a)*radius,35))
 return list(reversed(points)) if reverse else points
report=[]
for lane in range(7):
 name='BP_TrafficLane_'+str(lane);factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',base.generated_class());bp=unreal.load_asset(folder+'/'+name) or T.create_asset(name,folder,unreal.Blueprint,factory);assert E.compile_blueprint(bp)
 # Inherited component overrides are authored on a transient actor, then copied to the child CDO via inherited SCS override handle.
 spline=None
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  if str(lib.get_variable_name(lib.get_data(h)))=='Route':spline=lib.get_object_for_blueprint(lib.get_data(h),bp)
 assert spline
 if lane==6:points=rounded(-33500,35000,-330,330,330,True)
 else:
  circuit=lane//2;rev=lane%2!=0;offset=-270 if rev else 270;points=rounded([-36000,-24000,-12000][circuit]+offset,[36000,24000,12000][circuit]-offset,[-22000,-11000,-22000][circuit]+offset,[22000,11000,22000][circuit]-offset,420,rev)
 spline.set_spline_points(points,unreal.SplineCoordinateSpace.LOCAL,False)
 for i in range(len(points)):spline.set_spline_point_type(i,unreal.SplinePointType.LINEAR,False)
 spline.set_closed_loop(True,True);cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('LaneGroup',lane);cdo.set_editor_property('BusOnly',lane==6);cdo.set_editor_property('CruiseSpeed',850 if lane==6 else 975)
 assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);report.append({'lane':lane,'points':len(points),'length':spline.get_spline_length(),'asset':folder+'/'+name})
(r/'work/pure_traffic_lane_foundation.json').write_text(json.dumps({'status':'STAGING','lanes':report,'pending':['Runtime spline persistence and wrap validation','Signal reservations and following','Vehicle presentation and pedestrians','Main promotion']},indent=2));unreal.log('PURE_TRAFFIC_LANE_FOUNDATION_PASS')
