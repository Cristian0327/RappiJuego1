import unreal,json,sys,re
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/BlueprintWorld/Traffic';f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(folder+'/BP_TrafficVehicle') or T.create_asset('BP_TrafficVehicle',folder,unreal.Blueprint,f)
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;root=sub.k2_gather_subobject_data_for_blueprint(bp)[0]
def add(name,cls,parent):
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  if str(lib.get_variable_name(lib.get_data(h)))==name:return h,lib.get_object_for_blueprint(lib.get_data(h),bp)
 h,why=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent,new_class=cls,blueprint_context=bp));assert not str(why);assert sub.rename_subobject(h,unreal.Text(name));return h,lib.get_object_for_blueprint(lib.get_data(h),bp)
rootH,rootObj=add('VehicleRoot',unreal.SceneComponent,root);assert sub.make_new_scene_root(root,rootH,bp);assert E.compile_blueprint(bp)
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
 if str(lib.get_variable_name(lib.get_data(h)))=='VehicleRoot':rootH=h
bodyH,body=add('Body',unreal.PoseableMeshComponent,rootH);body.set_collision_profile_name('NoCollision');body.set_editor_property('can_ever_affect_navigation',False);body.set_editor_property('ld_max_draw_distance',24000.)
for side in [-1,1]:
 h,o=add('HeadlightLeft' if side<0 else 'HeadlightRight',unreal.SpotLightComponent,bodyH);o.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE);o.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);o.set_editor_property('intensity',220.);o.set_editor_property('attenuation_radius',2400.);o.set_editor_property('inner_cone_angle',8.);o.set_editor_property('outer_cone_angle',36.);o.set_editor_property('cast_shadows',False);o.set_editor_property('visible',False);o.set_editor_property('light_color',unreal.Color(255,235,204));o.set_editor_property('relative_rotation',unreal.Rotator(pitch=-10,yaw=0,roll=0))
V=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'));X=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform'));F=E.get_basic_type_by_name('real');B=E.get_basic_type_by_name('bool');I=E.get_basic_type_by_name('int');N=E.get_basic_type_by_name('name');known=[str(x) for x in E.list_member_variable_names(bp)]
types={'Lane':E.get_object_reference_type(unreal.load_class(None,folder+'/BP_TrafficLane.BP_TrafficLane_C')),'Distance':F,'PreviousDistance':F,'Speed':F,'CruiseSpeed':F,'HalfLength':F,'HalfWidth':F,'WheelRadius':F,'ModelScale':F,'Bus':B,'Taxi':B,'PlayerControlled':B,'Parked':B,'DoorTargetLeft':F,'DoorTargetRight':F,'DoorAlphaLeft':F,'DoorAlphaRight':F,'WheelAngle':F,'PreviousWheelAngle':F,'SteerAngle':F,'PaintIndex':I,'BodyMaterial':E.get_object_reference_type(unreal.MaterialInstanceDynamic),'DoorNames':E.get_array_type(N),'DoorRest':E.get_array_type(X),'WheelNames':E.get_array_type(N),'WheelRest':E.get_array_type(X),'PreviousPosition':V,'NextPosition':V,'PreviousYaw':F,'NextYaw':F,'PoseAlpha':F}
for n,t in types.items():
 if n not in known:assert E.add_member_variable(bp,n,t)
assert E.compile_blueprint(bp);cdo=unreal.get_default_object(bp.generated_class())
for n,v in {'CruiseSpeed':975.,'HalfLength':260.,'HalfWidth':125.,'WheelRadius':36.,'ModelScale':1.12,'DoorNames':[unreal.Name('door_L'),unreal.Name('door_R')],'WheelNames':[unreal.Name('wheel_0_L'),unreal.Name('wheel_0_R'),unreal.Name('wheel_1_L'),unreal.Name('wheel_1_R')]}.items():cdo.set_editor_property(n,v)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Each vehicle has its own component templates and authored dimensions; no runtime catalog native structs.
models=re.findall(r'\{TEXT\("([^"]+)"\),([\d.]+)f?,([\d.]+)f?,([\d.]+)f?\}',(r/'RappiJuego1/Source/BogotaVoxel/TrafficModelCatalog.inl').read_text());assert len(models)==22
result=[]
for name,hl,hw,wr in models+[('TransMilenio','915','135','49')]:
 asset='BP_Traffic_'+name;factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',bp.generated_class());child=unreal.load_asset(folder+'/'+asset) or T.create_asset(asset,folder,unreal.Blueprint,factory);assert E.compile_blueprint(child);isbus=name=='TransMilenio';scale=1 if isbus else 1.18 if float(hl)<210 else 1.12
 mesh=unreal.load_asset('/Game/Traffic/Detailed/SK_'+name);assert mesh,name;mat=unreal.load_asset('/Game/Traffic/Detailed/M_TrafficVoxelVertex');assert mat
 for h in sub.k2_gather_subobject_data_for_blueprint(child):
  n=str(lib.get_variable_name(lib.get_data(h)));o=lib.get_object_for_blueprint(lib.get_data(h),child)
  if n=='Body':o.set_skeletal_mesh(mesh);o.set_material(0,mat);o.set_editor_property('relative_scale3d',unreal.Vector(scale,scale,scale))
  elif n in ['HeadlightLeft','HeadlightRight']:o.set_editor_property('relative_location',unreal.Vector(float(hl)-15,(-1 if n=='HeadlightLeft' else 1)*float(hw)*.65,115 if isbus else 65))
 cdo=unreal.get_default_object(child.generated_class())
 for n,v in {'HalfLength':float(hl)*scale,'HalfWidth':float(hw)*scale,'WheelRadius':float(wr)*scale,'ModelScale':scale,'Bus':isbus,'Taxi':name.startswith('Taxi'),'CruiseSpeed':850. if isbus else 975.,'DoorNames':[unreal.Name('bus_door_a'),unreal.Name('bus_door_b')] if isbus else [unreal.Name('door_L'),unreal.Name('door_R')],'WheelNames':[unreal.Name('wheel_'+str(axle)+'_'+side) for axle in range(3 if isbus else 2) for side in ['L','R']]}.items():cdo.set_editor_property(n,v)
 assert E.compile_blueprint(child);assert unreal.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False);result.append({'name':name,'asset':folder+'/'+asset,'scale':scale,'half_length':float(hl)*scale,'half_width':float(hw)*scale})
(r/'work/pure_traffic_vehicle_foundation.json').write_text(json.dumps({'status':'STAGING','models':result,'pending':['Blueprint door and wheel poses','Paint and lighting runtime','Fixed simulation and interpolated movement','Signals, following and NPC interaction']},indent=2));unreal.log('PURE_TRAFFIC_VEHICLE_FOUNDATION_PASS models='+str(len(result)))
