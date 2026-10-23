import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;hs=sub.k2_gather_subobject_data_for_blueprint(bp);root=next(h for h in hs if str(lib.get_variable_name(lib.get_data(h)))=='VehicleRoot')
def add(name,cls):
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  if str(lib.get_variable_name(lib.get_data(h)))==name:return lib.get_object_for_blueprint(lib.get_data(h),bp)
 h,why=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=cls,blueprint_context=bp));assert not str(why);assert sub.rename_subobject(h,unreal.Text(name));return lib.get_object_for_blueprint(lib.get_data(h),bp)
box=add('VehicleCollision',unreal.BoxComponent);box.set_box_extent(unreal.Vector(250,110,100));box.set_editor_property('relative_location',unreal.Vector(0,0,100));box.set_collision_profile_name('BlockAllDynamic');box.set_editor_property('can_ever_affect_navigation',False);box.set_editor_property('generate_overlap_events',False)
for name in ['SignalFL','SignalFR','SignalRL','SignalRR']:
 light=add(name,unreal.PointLightComponent);light.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);light.set_editor_property('intensity',40.);light.set_editor_property('attenuation_radius',180.);light.set_editor_property('light_color',unreal.Color(255,150,12,255));light.set_editor_property('cast_shadows',False);light.set_editor_property('visible',False)
assert E.compile_blueprint(bp);d.bp=bp;g=d.Graph();g.get('SteerAngle');g.call('Time','GetGameTimeInSeconds','/Script/Engine.KismetSystemLibrary');g.call('Phase','Percent_FloatFloat',d.M,B='.8');g.link('Time','ReturnValue','Phase','A');g.call('LitPhase','Less_DoubleDouble',d.M,B='.4');g.link('Phase','ReturnValue','LitPhase','A')
for side,fn in [('Left','Less_DoubleDouble'),('Right','Greater_DoubleDouble')]:
 g.call(side+'Turn',fn,d.M,B='-4' if side=='Left' else '4');g.link('SteerAngle','SteerAngle',side+'Turn','A');g.call(side+'Lit','BooleanAND',d.M);g.link(side+'Turn','ReturnValue',side+'Lit','A');g.link('LitPhase','ReturnValue',side+'Lit','B')
last='entry'
for name,side in [('SignalFL','Left'),('SignalFR','Right'),('SignalRL','Left'),('SignalRR','Right')]:g.get(name);g.call(name+'Set','SetVisibility','/Script/Engine.SceneComponent',bPropagateToChildren='false');g.link(name,name,name+'Set','self');g.link(side+'Lit','ReturnValue',name+'Set','bNewVisibility');g.exec(last,name+'Set');last=name+'Set'
g.exec(last,'result');g.build('ReceiveTick');assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());tick=c.get_editor_property('primary_actor_tick');tick.set_editor_property('tick_interval',.1);c.set_editor_property('primary_actor_tick',tick);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
models=json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']
for spec in models:
 child=unreal.load_asset(spec['asset']);assert E.compile_blueprint(child);c=unreal.get_default_object(child.generated_class());hl=spec['half_length'];hw=spec['half_width'];scale=spec['scale'];bus=c.get_editor_property('Bus')
 for h in sub.k2_gather_subobject_data_for_blueprint(child):
  name=str(lib.get_variable_name(lib.get_data(h)));obj=lib.get_object_for_blueprint(lib.get_data(h),child)
  if name=='VehicleCollision':obj.set_box_extent(unreal.Vector(hl,hw,145 if bus else 90));obj.set_editor_property('relative_location',unreal.Vector(0,0,145 if bus else 90))
  elif name in ['HeadlightLeft','HeadlightRight']:obj.set_editor_property('intensity',1800.);obj.set_editor_property('relative_location',unreal.Vector(hl-17,(-1 if name=='HeadlightLeft' else 1)*hw*.65,115 if bus else 65*scale))
  elif name.startswith('Signal'):obj.set_editor_property('relative_location',unreal.Vector((hl-35)*(1 if name[6]=='F' else -1),hw*.75*(-1 if name[-1]=='L' else 1),85 if bus else 65*scale))
 assert unreal.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
(r/'work/pure_traffic_collision_lights.json').write_text(json.dumps({'models':len(models),'headlight_lumens_each':1800,'collision_boxes':True,'steering_signal_blink':'.8second period, >4degree steering','status':'COMPILED_PENDING_RENDER_REVIEW'},indent=2));unreal.log('PURE_TRAFFIC_COLLISION_AND_LIGHTS_PASS')
