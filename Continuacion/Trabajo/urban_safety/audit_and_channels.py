import unreal,json,sys,math,shutil
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_safety');root=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;ME=unreal.MaterialEditingLibrary;M=d.M;G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';S='/Script/Engine.Actor';unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');rows=[]
for actor in A.get_all_level_actors():
 if actor.get_class().get_name() in ['BP_MapaCompletoGeometry_C','BP_BogotaUrbanDressing_C']:
  for c in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
   mesh=c.get_editor_property('static_mesh')
   if mesh:rows.append(dict(actor=actor.get_class().get_name(),component=c.get_name(),mesh=mesh.get_path_name(),transforms=[dict(location=list(c.get_instance_transform(i,True).translation.to_tuple()),scale=list(c.get_instance_transform(i,True).scale3d.to_tuple()),rotation=list(c.get_instance_transform(i,True).rotation.rotator().to_tuple())) for i in range(c.get_instance_count())]))
(P/'actual_instances.json').write_text(json.dumps(rows))
rider=unreal.get_default_object(unreal.load_asset('/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider').generated_class());mov=rider.get_editor_property('character_movement');(P/'movement_before.json').write_text(json.dumps({n:str(mov.get_editor_property(n)) for n in ['max_step_height','walkable_floor_angle','perch_radius_threshold','use_flat_base_for_floor_checks','movement_mode','max_fly_speed']}))
# Diagnostic materials expose actual rendered vertex and UV channels independently.
materials=[]
for mode in ['Vertex','Atlas','Mask','Tint']:
 path='/Game/QA/M_CarDiagnostic'+mode;mat=unreal.load_asset(path) or T.create_asset('M_CarDiagnostic'+mode,'/Game/QA',unreal.Material,unreal.MaterialFactoryNew());ME.delete_all_material_expressions(mat);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);mat.set_editor_property('two_sided',True)
 if mode=='Vertex':v=ME.create_material_expression(mat,unreal.MaterialExpressionVertexColor)
 elif mode=='Atlas':v=ME.create_material_expression(mat,unreal.MaterialExpressionTextureSample);v.set_editor_property('texture',unreal.load_asset('/Game/Traffic/Detailed/T_TrafficPixelAtlas'))
 elif mode=='Mask':v=ME.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate);v.set_editor_property('coordinate_index',1)
 else:v=ME.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);v.set_editor_property('constant',unreal.LinearColor(.8,.02,.04,1))
 ME.connect_material_property(v,'RGB' if mode=='Atlas' else '',unreal.MaterialProperty.MP_EMISSIVE_COLOR);ME.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);ME.recompile_material(mat);EL.save_loaded_asset(mat,only_if_is_dirty=False);materials.append(mat)
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset('/Game/QA/BP_TextureChannelProbe') or T.create_asset('BP_TextureChannelProbe','/Game/QA',unreal.Blueprint,f);vec=E.get_object_reference_type(unreal.Actor)
for n,t in [('Camera',vec),('Age',E.get_basic_type_by_name('real')),('Stage',E.get_basic_type_by_name('int'))]+[('Car'+str(i),E.get_object_reference_type(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C'))) for i in range(4)]:
 if n not in [str(x) for x in E.list_member_variable_names(bp)]:E.add_member_variable(bp,n,t)
 E.set_blueprint_variable_instance_editable(bp,n,True)
assert E.compile_blueprint(bp);d.bp=bp;g=d.Graph()
for n in ['Camera','Age','Stage']+['Car'+str(i) for i in range(4)]:g.get(n)
g.call('NextAge','Add_DoubleDouble',M);g.link('Age','Age','NextAge','A');g.link('entry','DeltaSeconds','NextAge','B');g.setter('Clock','Age','NextAge');g.exec('entry','Clock');last='Clock';edge='then'
for i,(at,mode) in enumerate([(1,'materials'),(3,'shot'),(4,'quit')]):
 tag='T'+str(i);g.call(tag+'Time','Greater_DoubleDouble',M,B=str(at));g.link('Age','Age',tag+'Time','A');g.call(tag+'Stage','EqualEqual_IntInt',M,B=str(i));g.link('Stage','Stage',tag+'Stage','A');g.call(tag+'Due','BooleanAND',M);g.link(tag+'Time','ReturnValue',tag+'Due','A');g.link(tag+'Stage','ReturnValue',tag+'Due','B');g.branch(tag,tag+'Due');g.exec(last,tag,edge);end=tag
 if mode=='materials':
  g.call('PC','GetPlayerController',G,PlayerIndex='0');g.call('View','SetViewTargetWithBlend','/Script/Engine.PlayerController',BlendTime='0');g.link('PC','ReturnValue','View','self');g.link('Camera','Camera','View','NewViewTarget');g.exec(end,'View');end='View'
  for j,mat in enumerate(materials):
   g.node('Body'+str(j),'getfield',owner='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C',var='Body');g.link('Car'+str(j),'Car'+str(j),'Body'+str(j),'self');g.call('Material'+str(j),'SetMaterial','/Script/Engine.PrimitiveComponent',ElementIndex='0',Material=mat.get_path_name());g.link('Body'+str(j),'Body','Material'+str(j),'self');g.exec(end,'Material'+str(j));end='Material'+str(j)
 else:g.call(tag+'Action','ExecuteConsoleCommand',K,Command='quit' if mode=='quit' else 'HighResShot 1600x900 filename="'+str(P/'car_channels.png').replace('\\','/')+'"');g.exec(end,tag+'Action');end=tag+'Action'
 g.setter(tag+'Next','Stage',value=str(i+1));g.exec(end,tag+'Next');g.exec(tag+'Next','result');last=tag;edge='else'
g.exec(last,'result',edge);g.build('ReceiveTick');assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/TextureChannels');unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/TextureChannels');probe=A.spawn_actor_from_class(bp.generated_class(),unreal.Vector());models=json.loads((root/'work/pure_traffic_vehicle_foundation.json').read_text())['models']
for i in range(4):
 actor=A.spawn_actor_from_class(unreal.load_asset(models[0]['asset']).generated_class(),unreal.Vector(0,i*600,11000));actor.set_actor_tick_enabled(False);probe.set_editor_property('Car'+str(i),actor)
pos=unreal.Vector(2000,1000,12500);cam=A.spawn_actor_from_class(unreal.CameraActor,pos,unreal.MathLibrary.find_look_at_rotation(pos,unreal.Vector(0,900,11070)));cam.get_component_by_class(unreal.CameraComponent).set_field_of_view(70);probe.set_editor_property('Camera',cam);assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('ACTUAL_INSTANCES_AND_TEXTURE_DIAGNOSTIC_READY')

