import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/Delivery/BlueprintGameplay/Player';name='BP_BlueprintRider';path=folder+'/'+name;f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Character);bp=unreal.load_asset(path) or T.create_asset(name,folder,unreal.Blueprint,f);CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';M=d.M;S='/Script/Engine.KismetSystemLibrary';sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;source=unreal.get_default_object(unreal.load_class(None,'/Game/Delivery/Vehicles/BP_DeliveryRider.BP_DeliveryRider_C'));components=[]
def inventory():
 result={}
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  o=lib.get_object_for_blueprint(lib.get_data(h),bp)
  if o:result[o.get_name()]=(h,o)
 return result
handles=sub.k2_gather_subobject_data_for_blueprint(bp);root=handles[0]
def add(n,cls,parent=root):
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  o=lib.get_object_for_blueprint(lib.get_data(h),bp)
  if o and o.get_name().removesuffix('_GEN_VARIABLE')==n:return h,o
 h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent,new_class=cls,blueprint_context=bp));assert not str(reason),str(reason);assert sub.rename_subobject(h,unreal.Text(n));o=lib.get_object_for_blueprint(lib.get_data(h),bp);assert o,n;components.append(n);return h,o
coreHandle,coreTemplate=add('Delivery',unreal.load_class(None,CORE));boomH,boom=add('CameraBoom',unreal.SpringArmComponent);camH,cam=add('Camera',unreal.CameraComponent,boomH)
for n in ['target_arm_length','socket_offset','use_pawn_control_rotation','enable_camera_lag','camera_lag_speed']:
 boom.set_editor_property(n,source.get_editor_property('CameraBoom').get_editor_property(n))
for n in ['field_of_view','use_pawn_control_rotation']:cam.set_editor_property(n,source.get_editor_property('Camera').get_editor_property(n))
boom.set_editor_property('relative_location',unreal.Vector());cam.set_editor_property('relative_location',unreal.Vector());cam.attach_to_component(boom,'SpringEndpoint',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
# Copy the existing authored vehicle component templates without a project-native parent.
parents={};last=root
for n,parentName in [('Bicycle',None),('FrontWheel','Bicycle'),('RearWheel','Bicycle'),('LeftPedal','Bicycle'),('RightPedal','Bicycle')]:
 old=unreal.find_object(source,'BicycleFrame' if n=='Bicycle' else n);assert old,n;h,o=add(n,unreal.StaticMeshComponent,parents.get(parentName,root));parents[n]=h
 for p in ['relative_location','relative_rotation','relative_scale3d','hidden_in_game','visible']:o.set_editor_property(p,old.get_editor_property(p))
 o.set_static_mesh(old.get_editor_property('static_mesh'));o.set_collision_profile_name('NoCollision')
 for i in range(old.get_num_materials()):o.set_material(i,old.get_material(i))
known=[str(x) for x in E.list_member_variable_names(bp)]
for n,t in {**{n:E.get_basic_type_by_name('real') for n in ['ForwardInput','SideInput','BikeSpeed']},**{n:E.get_basic_type_by_name('bool') for n in ['Sprint','Riding']}}.items():
 if n not in known:assert E.add_member_variable(bp,n,t)
 E.set_blueprint_variable_instance_editable(bp,n,True)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());mesh=c.get_editor_property('mesh');oldmesh=source.get_editor_property('mesh');mesh.set_skeletal_mesh_asset(oldmesh.get_skeletal_mesh_asset());mesh.set_relative_location(unreal.Vector(0,0,-90),False,True);mesh.set_relative_rotation(unreal.Rotator(pitch=0,yaw=-90,roll=0),False,True);mesh.set_collision_profile_name('NoCollision');mesh.set_anim_instance_class(unreal.load_class(None,'/Game/Delivery/Animation/ABP_DeliveryRider.ABP_DeliveryRider_C'))
for i in range(oldmesh.get_num_materials()):mesh.set_material(i,oldmesh.get_material(i))
c.get_editor_property('capsule_component').set_capsule_size(34,90);move=c.get_editor_property('character_movement');oldmove=source.get_editor_property('character_movement')
for p in ['orient_rotation_to_movement','rotation_rate','max_walk_speed','jump_z_velocity','air_control','max_step_height','braking_deceleration_walking']:move.set_editor_property(p,oldmove.get_editor_property(p))
for p in ['use_controller_rotation_yaw','use_controller_rotation_pitch','use_controller_rotation_roll']:c.set_editor_property(p,False)
reports=[];remap={'/Script/BogotaVoxel.BogotaPlayer':bp.generated_class().get_path_name(),'/Script/BogotaVoxel.DeliveryComponent':CORE}
class Graph(d.Graph):
 def build(self,n):
  for x in self.nodes:
   if x.get('kind') in ['call','getfield','setfield']:
    old=x.get('owner','');x['owner']=remap.get(old,old) or bp.generated_class().get_path_name()
  assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,n,json.dumps({'nodes':self.nodes,'links':self.links,'variables':self.variables,'signature_owner':'/Script/BogotaVoxel.BogotaPlayer','type_remap':remap})),n;reports.append(n);return {'function':n}
# Existing reviewed movement and camera rules are copied as owned Blueprint functions.
for script,allowed in [('migrate_rider_input.py',{'MoveForward','MoveRight','Turn','Look','StartSprint','EndSprint','JumpOrBrake','StopJump','StopForPhone','ActionReleased','PickupReleased','PickupPressed','VehiclePressed'}),('migrate_player_drive_camera.py',{'WalkingSpeed','AdvanceDriveSpeed','SteeringAngle','UpdateCameraRig'})]:
 s=(r/'work'/script).read_text(encoding='utf-8-sig');a=s.index('def valid_delivery') if script=='migrate_rider_input.py' else s.index('g=Graph()');b=s.index('assert unreal.EditorAssetLibrary.save_loaded_asset');body=s[a:b];base=Graph
 class SelectedGraph(base):
  def build(self,n):return super().build(n) if n in allowed else {'skipped':n}
 exec(compile(body,'PureRiderMovement','exec'),{'Graph':SelectedGraph,'M':M,'D':CORE,'P':'/Script/Engine.Pawn','C':'/Script/Engine.Character','SYS':S,'bp':bp,'reports':[]})
# Animation and boost can query this Character through the same generic Blueprint interfaces.
for iface,fn in [('/Game/Delivery/Animation/BPI_RiderAnimationState.BPI_RiderAnimationState_C','QueryRiderAnimationState'),('/Game/Delivery/Interfaces/BPI_DeliveryRiderInput.BPI_DeliveryRiderInput_C','QueryDeliveryInputState')]:
 g=d.Graph();g.get('Riding');g.link('Riding','Riding','result','Mounted');g.exec('entry','result')
 if fn=='QueryRiderAnimationState':
  g.get('Delivery');g.call('HasCore','IsValid',S);g.link('Delivery','Delivery','HasCore','Object');g.branch('Ready','HasCore');g.links.remove(['entry','then','result','execute']);g.exec('entry','Ready');g.exec('Ready','result');g.node('Missing','return',defaults={'Motorcycle':'false'});g.link('Riding','Riding','Missing','Mounted');g.exec('Ready','Missing','else');g.node('Vehicle','getfield',owner=CORE,var='Vehicle');g.link('Delivery','Delivery','Vehicle','self');g.call('Moto','EqualEqual_ByteByte',M,B='1');g.link('Vehicle','Vehicle','Moto','A');g.link('Moto','ReturnValue','result','Motorcycle')
 else:
  g.get('Sprint');g.get('ForwardInput');g.call('Abs','Abs',M);g.link('ForwardInput','ForwardInput','Abs','A');g.call('Throttle','Greater_DoubleDouble',M,B='.1');g.link('Abs','ReturnValue','Throttle','A');g.link('Sprint','Sprint','result','WantsBoost');g.link('Throttle','ReturnValue','result','HasThrottle')
 assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,fn,json.dumps({'interface_owner':iface,'nodes':g.nodes,'links':g.links}))
g=d.Graph();g.get('Camera');g.get('CameraBoom');g.call('Attach','K2_AttachToComponent','/Script/Engine.SceneComponent',SocketName='SpringEndpoint',LocationRule='KeepRelative',RotationRule='KeepRelative',ScaleRule='KeepRelative',bWeldSimulatedBodies='false');g.link('Camera','Camera','Attach','self');g.link('CameraBoom','CameraBoom','Attach','Parent');g.exec('entry','Attach');g.exec('Attach','result');d.bp=bp;g.build('ReceiveBeginPlay');
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['parent']=='/Script/Engine.Character' and not any(g['native_calls'] for g in audit['graphs']);(r/'work/pure_rider_foundation.json').write_text(json.dumps({'status':'STAGING_NOT_PROMOTED','asset':path,'components_created':components,'functions':reports,'audit':audit,'pending':['Input event bindings and frame simulation','Full mounting and vehicles','Pure phone and world integration']},indent=2));unreal.log('PURE_RIDER_FOUNDATION_BUILD_PASS functions='+str(len(reports)))

