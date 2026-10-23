import unreal,json,sys,math,shutil,collections
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;M=d.M;A='/Script/Engine.Actor';K='/Script/Engine.KismetSystemLibrary';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C';plan=json.loads((W/'integration_plan.json').read_text());actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);backup=r/'Recuperacion_Migracion_Blueprints/2026-10-20_new_map'
for rel in ['Traffic/Transit/BP_StationPassenger.uasset','Traffic/Services/BP_VoxelRoadVehicle.uasset']:
 p=backup/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():shutil.copy2(r/'RappiJuego1/Content'/rel,p)
# Crowd already compiled and saved.
# Transit stops use full positions and vehicle-local forward/lateral distances on curved streets.
bp=unreal.load_asset(V.rsplit('.',1)[0]);d.bp=bp
if 'TransitStopPositions' not in [str(n) for n in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,'TransitStopPositions',E.get_array_type(E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'))))
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());c.set_editor_property('TransitStopPositions',[unreal.Vector(s['bus_stop'][0],s['bus_stop'][1],14) for s in plan['stations']])
s=(r/'work/build_pure_transit_station_stops.py').read_text(encoding='utf-8-sig');s=s[:s.index('for spec in json.loads')];s=s.replace("'Parked','TransitStops'","'Parked','TransitStopPositions'").replace("g.link('TransitStops','TransitStops','Each','Array')","g.link('TransitStopPositions','TransitStopPositions','Each','Array')");s=s.replace("g.exec('ResetCandidate','StraightRoad')",'').replace("g.link('StraightRoad','then','Each','Exec')","g.link('ResetCandidate','then','Each','Exec')")
a=s.index("op(g,'DeltaX'");b=s.index("op(g,'Upcoming'",a)
s=s[:a]+"op(g,'StopDelta','Subtract_VectorVector',('Each','Array Element'),('NextPosition','NextPosition'));op(g,'Ahead','Dot_VectorVector',('StopDelta','ReturnValue'),('Forward','ReturnValue'));op(g,'SideDelta','Cross_VectorVector',('StopDelta','ReturnValue'),('Forward','ReturnValue'));g.call('SideAxes','BreakVector',M);g.link('SideDelta','ReturnValue','SideAxes','InVec');op(g,'AbsSide','Abs',('SideAxes','Z'));op(g,'SameStopLane','Less_DoubleDouble',('AbsSide','ReturnValue'),B='240');"+s[b:]
s=s.replace("['Closer','InApproach','NotLast']","['SameStopLane','Closer','InApproach','NotLast']").replace("'TransitDwell',value='10'","'TransitDwell',value='18'");exec(compile(s.replace(';;',';'),'CurvedTransitStops','exec'),{})
# Reuse the existing ordered doorway, visible passenger and alighting handoff; remove world-axis assumptions.
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/fix_station_motorcycle_spacing.py').read_text();s=s[:s.index('# Spread authored')];s=s.replace("exec(compile(s,'OrderedTransitDoorQueue','exec'),{})","s=s.replace(\"g.call('PlatformAlign','MakeVector',M,Y='0',Z='198');g.link('DoorAxes','X','PlatformAlign','X')\",\"g.call('PlatformLocal','MakeVector',M,X='380',Y='-330',Z='164');g.call('PlatformAlign','TransformLocation',M);g.link('BusTransform','ReturnValue','PlatformAlign','T');g.link('PlatformLocal','ReturnValue','PlatformAlign','Location')\");s=s.replace(\"g.call('ExitOffset','MakeVector',M);g.link('ExitSpacing','ReturnValue','ExitOffset','X')\",\"g.call('BusExitForward','GetActorForwardVector',A);g.link('BusActor','BusActor','BusExitForward','self');g.call('ExitOffset','Multiply_VectorFloat',M);g.link('BusExitForward','ReturnValue','ExitOffset','A');g.link('ExitSpacing','ReturnValue','ExitOffset','B')\");exec(compile(s,'RotatedStationPassengers','exec'),{})");exec(compile(s,'StationQueueReuse','exec'),{})
# Service vehicles retain their current visual build, with authored LOD to prevent police-panel reduction artifacts.
bp=unreal.load_asset('/Game/Traffic/Services/BP_VoxelRoadVehicle');d.bp=bp;src=(r/'work/build_road_vehicle_blueprint.py').read_text(encoding='utf-8-sig');part=src[src.index('d.bp=bp;g=d.Graph()'):src.index("build(g,'ReceiveBeginPlay')")];part=part.replace("g.exec('BodyMat','NoCollision')","g.call('RigidBodyLOD','SetForcedLOD',SKIN,InNewForcedLOD='1');g.link('VehicleVisual','VehicleVisual','RigidBodyLOD','self');g.exec('BodyMat','RigidBodyLOD');g.exec('RigidBodyLOD','NoCollision')");SYS=K;GAME='/Script/Engine.GameplayStatics';POSE='/Script/Engine.PoseableMeshComponent';SKIN='/Script/Engine.SkinnedMeshComponent';SKEL='/Script/Engine.SkeletalMeshComponent';exec(compile(part,'ServiceBodyVisualLOD','exec'));g.build('ReceiveBeginPlay');assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False)
for path in ['/Game/Traffic/Detailed/T_TrafficPixelAtlas','/Game/Traffic/Services/T_ServicePixelAtlas']:
 tex=unreal.load_asset(path);tex.set_editor_property('never_stream',True);tex.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);EL.save_loaded_asset(tex,only_if_is_dirty=False)
# Capture the original station geometry, including its floor and roof.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');city=next(a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_CityGeometry_C');city.call_method('ReceiveBeginPlay');template=[]
for comp in city.get_components_by_class(unreal.InstancedStaticMeshComponent):
 for i in range(comp.get_instance_count()):
  tr=comp.get_instance_transform(i,world_space=True);p=tr.translation;sc=tr.scale3d
  if abs(p.x+27000)<2100 and abs(p.y)<420 and abs(sc.x)*50<2200 and abs(sc.y)*50<=420 and p.z+abs(sc.z)*50>70 and p.z-abs(sc.z)*50>=-30:template.append((comp.static_mesh,comp.get_material(0),unreal.Vector(p.x+27000,p.y,p.z-20),sc,tr.rotation.rotator().yaw))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');byclass=collections.defaultdict(list)
for a in actors.get_all_level_actors():byclass[a.get_class().get_name()].append(a)
# Existing shops retain their themes, IDs and product behavior; their room footprint fits the new city.
stores=sorted(byclass['BP_DeliveryStore_C'],key=lambda a:int(a.get_name().rsplit('_',1)[1]));assert len(stores)==20
for a,s in zip(stores,plan['shops']):
 a.set_actor_location(unreal.Vector(s['entrance'][0],s['entrance'][1],20),False,True);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=s['store_yaw'],roll=0),True);a.set_editor_property('HalfWidth',500.);a.set_editor_property('HalfDepth',450.);a.set_editor_property('Built',False)
for a in byclass['BP_ResidentialRouteAssembler_C']:
 b=plan['building_footprints'];a.set_editor_property('BuildingCenters',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in b]);a.set_editor_property('BuildingExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in b])
walk=plan['walk_routes'];lanes=plan['lanes'];counts=collections.Counter()
def prop(a,n,v):
 try:a.set_editor_property(n,v);return True
 except:return False
for cl,items in byclass.items():
 for k,a in enumerate(items):
  if cl=='BP_PoliceOfficer_C':
   route=walk[(k*7)%len(walk)];a.set_actor_location(unreal.Vector(route[0][0],route[0][1],108),False,True);prop(a,'PatrolPoints',[unreal.Vector(*v) for v in route]);prop(a,'PatrolIndex',1);counts['police']+=1
  elif cl in ['BP_CivilMotorcycle_C','BP_PoliceMotorcycle_C','BP_PoliceRoadPatrol_C']:
   route=lanes[(k+2)%6];j=(k*137+len(items)*37)%len(route);a.set_actor_location(unreal.Vector(route[j][0],route[j][1],154 if cl=='BP_PoliceRoadPatrol_C' else 134),False,True);prop(a,'Route',[unreal.Vector(v[0],v[1],14) for v in route]);prop(a,'RouteIndex',(j+1)%len(route));counts[cl]+=1
  elif cl=='BP_TwoWheelerCitizen_C':
   route=lanes[k%6];j=(k*177+99)%len(route);a.set_actor_location(unreal.Vector(route[j][0],route[j][1],102),False,True);prop(a,'Route',[unreal.Vector(v[0],v[1],14) for v in route]);prop(a,'RouteIndex',(j+1)%len(route));prop(a,'RoadMode',True);counts['two_wheelers']+=1
  elif cl.startswith('BP_TaxiPassenger') or cl.startswith('BP_CrosswalkCitizen'):
   route=walk[(k+len(counts)*5+counts['service_walkers']*7)%len(walk)];a.set_actor_location(unreal.Vector(route[0][0],route[0][1],108),False,True);prop(a,'Route',[unreal.Vector(*v) for v in route]);prop(a,'RouteIndex',1);prop(a,'CrossSegments',[False]*len(route));counts['service_walkers']+=1
  elif cl=='BP_StationPassenger_C':
   si=a.get_editor_property('Station')%4;slot=a.get_editor_property('PassengerId')%4;s=plan['stations'][si];yaw=math.radians(s['yaw']);x=s['position'][0]+math.cos(yaw)*(380+slot*160);y=s['position'][1]+math.sin(yaw)*(380+slot*160);a.set_actor_location(unreal.Vector(x,y,178),False,True);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=s['yaw'],roll=0),True);counts['station_passengers']+=1
# Compact instanced fixture geometry: old stations, accessible ramps, shop footpaths and road markings.
fixtures=collections.defaultdict(list);cube=unreal.load_asset('/Engine/BasicShapes/Cube');white=unreal.load_asset('/Game/World/M_White');concrete=unreal.load_asset('/Game/World/M_Concrete') or unreal.load_asset('/Game/World/M_Stone');yellow=unreal.load_asset('/Game/World/M_Yellow')
if not concrete:concrete=unreal.load_asset('/Engine/BasicShapes/BasicShapeMaterial')
def rotvec(rot,v):
 a=math.radians(rot.yaw);return unreal.Vector(math.cos(a)*v.x-math.sin(a)*v.y,math.sin(a)*v.x+math.cos(a)*v.y,v.z)
def add(mesh,mat,pos,scale,yaw=0,pitch=0):fixtures[(mesh.get_path_name(),mat.get_path_name())].append(unreal.Transform(location=pos,rotation=unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),scale=scale))
for st in plan['stations']:
 base=unreal.Vector(st['position'][0],st['position'][1],0);rot=unreal.Rotator(pitch=0,yaw=st['yaw'],roll=0)
 for mesh,mat,pos,scale,yaw in template:add(mesh,mat,base+rotvec(rot,pos),scale,st['yaw']+yaw)
 for sign in [-1,1]:add(cube,concrete,base+rotvec(rot,unreal.Vector(sign*1900,0,47)),unreal.Vector(10,3,.12),st['yaw'],-sign*4.9)
 if white:
  for stripe in range(-12,13):add(cube,white,base+rotvec(rot,unreal.Vector(-2500,stripe*100,5)),unreal.Vector(4,.45,.02),st['yaw'])
for s in plan['shops']:
 path=s['walk_link']
 for a,b in zip(path,path[1:]):
  dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);add(cube,concrete,unreal.Vector((a[0]+b[0])/2,(a[1]+b[1])/2,10),unreal.Vector((length+70)/100,2,.2),math.degrees(math.atan2(dy,dx)))
# Build a reusable Blueprint that also displays in the editor.
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);folder='/Game/Maps/MapaCompleto';bp=unreal.load_asset(folder+'/BP_MapaFixtures') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_MapaFixtures',folder,unreal.Blueprint,f);d.bp=bp;ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;root=ss.k2_gather_subobject_data_for_blueprint(bp)[0];known=[str(x) for x in E.list_member_variable_names(bp)];tt=E.get_array_type(E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform')))
for i,((mesh,mat),transforms) in enumerate(fixtures.items()):
 name='Fixture%d'%i;h=next((h for h in ss.k2_gather_subobject_data_for_blueprint(bp) if str(lib.get_variable_name(lib.get_data(h)))==name),None)
 if not h:
  h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.HierarchicalInstancedStaticMeshComponent,blueprint_context=bp));assert not str(reason);ss.rename_subobject(h,unreal.Text(name))
 o=lib.get_object_for_blueprint(lib.get_data(h),bp);o.set_static_mesh(unreal.load_asset(mesh));o.set_material(0,unreal.load_asset(mat));o.set_collision_profile_name('BlockAll');o.set_editor_property('mobility',unreal.ComponentMobility.STATIC)
 var='FixtureTransforms%d'%i
 if var not in known:assert E.add_member_variable(bp,var,tt)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());g=d.Graph();last='entry'
for i,transforms in enumerate(fixtures.values()):
 name='Fixture%d'%i;var='FixtureTransforms%d'%i;c.set_editor_property(var,transforms);g.get(name);g.get(var);g.call(name+'Clear','ClearInstances','/Script/Engine.InstancedStaticMeshComponent');g.link(name,name,name+'Clear','self');g.exec(last,name+'Clear');g.call(name+'Add','AddInstances','/Script/Engine.InstancedStaticMeshComponent',bShouldReturnIndices='false',bWorldSpace='false',bUpdateNavigation='true');g.link(name,name,name+'Add','self');g.link(var,var,name+'Add','InstanceTransforms');g.exec(name+'Clear',name+'Add');last=name+'Add'
g.exec(last,'result');g.build('UserConstructionScript');assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False)
for old in actors.get_all_level_actors():
 if old.get_class().get_name()=='BP_MapaFixtures_C':actors.destroy_actor(old)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level();shutil.copy2(W/'integration_plan.json',r/'outputs/MapRebuild/integration_plan.json');(r/'outputs/MapRebuild/services_integration.json').write_text(json.dumps({'stores':20,'store_room_halfwidth':500,'store_room_halfdepth':450,'station_pieces':len(template),'fixtures':sum(len(v) for v in fixtures.values()),'service_counts':dict(counts)}));unreal.log('NEW_MAP_SERVICES_READY')
