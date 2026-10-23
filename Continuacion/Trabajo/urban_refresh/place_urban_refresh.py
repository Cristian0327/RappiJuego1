import unreal,json,sys,math,collections,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');W=U.parent/'new_map_audit';plan=json.loads((U/'placement_plan.json').read_text());city=json.loads((W/'integration_plan.json').read_text());sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;folder='/Game/World/BogotaUrban';M=d.M;K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics';A='/Script/Engine.Actor';AL='/Script/Engine.KismetArrayLibrary';mat=unreal.load_asset(folder+'/M_BogotaUrban');emit=unreal.load_asset(folder+'/M_BogotaSignalEmission')
# Preserve a recoverable copy before replacing the previous station fixtures.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not EL.does_asset_exist('/Game/QA/BeforeBogotaUrbanRefresh'):assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/BeforeBogotaUrbanRefresh')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_path_name().startswith(folder+'/') or a.get_class().get_name()=='BP_MapaFixtures_C':actors.destroy_actor(a)
# Dynamic actors are few; repeating furniture and markings use instanced mesh components.
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(folder+'/BP_BogotaUrbanDressing') or T.create_asset('BP_BogotaUrbanDressing',folder,unreal.Blueprint,f);assert E.compile_blueprint(bp);groups=collections.defaultdict(list)
def tr(pos,yaw=0,scale=(1,1,1)):return unreal.Transform(location=unreal.Vector(*pos),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(*scale))
def group(mesh,pos,yaw=0,scale=(1,1,1)):groups[mesh].append(tr(pos,yaw,scale))
for item in plan['furniture']:
 typ=item['type'];yaw=item['yaw']+180 if typ in ['Farola','Banca'] else item['yaw'];group('SM_Bogota_'+typ,item['position'],yaw)
 if typ=='Farola':
  group('SM_Bogota_FarolaLuz',item['position'],yaw);actors.spawn_actor_from_class(unreal.load_asset(folder+'/BP_BogotaStreetLight').generated_class(),unreal.Vector(*item['position']))
for s in plan['crossings']:
 group('SM_Bogota_CruceAccesible',s['position'],s['yaw']);yaw=math.radians(s['yaw']);t=(math.cos(yaw),math.sin(yaw));rr=(-t[1],t[0])
 for sign in [-1,1]:
  at=unreal.Vector(s['position'][0]+t[0]*(-sign*800)+rr[0]*sign*(s['halfwidth']-35),s['position'][1]+t[1]*(-sign*800)+rr[1]*sign*(s['halfwidth']-35),20);a=actors.spawn_actor_from_class(unreal.load_asset(folder+'/BP_BogotaSignal').generated_class(),at,unreal.Rotator(pitch=0,yaw=s['yaw']+(180 if sign<0 else 0),roll=0));a.set_actor_label('Semáforo peatonal y vehicular')
# New station shells retain the original bus stop positions and boarding datum.
for i,s in enumerate(city['stations']):
 pos=[s['position'][0],s['position'][1],0];a=actors.spawn_actor_from_class(unreal.load_asset(folder+'/BP_BogotaTransmiStation').generated_class(),unreal.Vector(*pos),unreal.Rotator(pitch=0,yaw=s['yaw'],roll=0));a.set_editor_property('StationId',i);a.set_actor_label('Estación TransMilenio '+str(i+1));ang=math.radians(s['yaw'])
 for x in [-900,-500]:
  q=[pos[0]+math.cos(ang)*x,pos[1]+math.sin(ang)*x,90];group('SM_Bogota_Banca',q,s['yaw'])
 for x in [-1050,1050]:actors.spawn_actor_from_class(unreal.load_asset(folder+'/BP_BogotaStreetLight').generated_class(),unreal.Vector(pos[0]+math.cos(ang)*x,pos[1]+math.sin(ang)*x,20))
# Existing store entrances keep their connected walkways; color agrees with ochre sidewalks.
flat=T.create_asset('M_BogotaPavingBorder',folder,unreal.Material,unreal.MaterialFactoryNew()) if not unreal.load_asset(folder+'/M_BogotaPavingBorder') else unreal.load_asset(folder+'/M_BogotaPavingBorder');ME=unreal.MaterialEditingLibrary;ME.delete_all_material_expressions(flat);col=ME.create_material_expression(flat,unreal.MaterialExpressionConstant3Vector);col.set_editor_property('constant',unreal.LinearColor(.55,.36,.18,1));ME.connect_material_property(col,'',unreal.MaterialProperty.MP_BASE_COLOR);rough=ME.create_material_expression(flat,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.88);ME.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);ME.set_material_usage(flat,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);ME.recompile_material(flat);assert EL.save_loaded_asset(flat,only_if_is_dirty=False)
for shop in city['shops']:
 for a,b in zip(shop['walk_link'],shop['walk_link'][1:]):
  dx=b[0]-a[0];dy=b[1]-a[1];group('PavingLink',[(a[0]+b[0])/2,(a[1]+b[1])/2,10],math.degrees(math.atan2(dy,dx)),((math.hypot(dx,dy)+70)/100,2,.2))
known=[str(v) for v in E.list_member_variable_names(bp)];root=ss.k2_gather_subobject_data_for_blueprint(bp)[0]
for i,(name,transforms) in enumerate(groups.items()):
 n='UrbanPart'+str(i);h=next((h for h in ss.k2_gather_subobject_data_for_blueprint(bp) if str(lib.get_variable_name(lib.get_data(h)))==n),None)
 if not h:h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.HierarchicalInstancedStaticMeshComponent,blueprint_context=bp));assert not str(reason);ss.rename_subobject(h,unreal.Text(n))
 o=lib.get_object_for_blueprint(lib.get_data(h),bp);o.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube' if name=='PavingLink' else folder+'/Geometry/'+name));o.set_material(0,flat if name=='PavingLink' else emit if name.endswith('FarolaLuz') else mat);o.set_collision_profile_name('NoCollision' if name.endswith('FarolaLuz') else 'BlockAll');o.set_editor_property('can_ever_affect_navigation',not name.endswith('FarolaLuz'));o.set_editor_property('mobility',unreal.ComponentMobility.STATIC);o.set_editor_property('instance_end_cull_distance',24000)
 if n+'Transforms' not in known:assert E.add_member_variable(bp,n+'Transforms',E.get_array_type(E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform'))))
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());d.bp=bp;g=d.Graph();last='entry'
for i,transforms in enumerate(groups.values()):
 n='UrbanPart'+str(i);v=n+'Transforms';c.set_editor_property(v,transforms);g.get(n);g.get(v);g.call(n+'Clear','ClearInstances','/Script/Engine.InstancedStaticMeshComponent');g.link(n,n,n+'Clear','self');g.exec(last,n+'Clear');g.call(n+'Add','AddInstances','/Script/Engine.InstancedStaticMeshComponent',bShouldReturnIndices='false',bWorldSpace='false',bUpdateNavigation='true');g.link(n,n,n+'Add','self');g.link(v,v,n+'Add','InstanceTransforms');g.exec(n+'Clear',n+'Add');last=n+'Add'
g.exec(last,'result');g.build('UserConstructionScript');assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False);actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('Mobiliario Bogotá - Blender')
# Seated ambient citizens are visible and use the existing Mixamo sitting animation.
models=json.loads((r/'work/pure_crowd_models.json').read_text());benches=[v for v in plan['furniture'] if v['type']=='Banca']
for i,item in enumerate(benches[::3]):
 c=unreal.get_default_object(unreal.load_asset(models[(i*7+1)%len(models)]['asset']).generated_class());source=c.get_editor_property('mesh');a=actors.spawn_actor_from_class(unreal.load_asset(folder+'/BP_BogotaBenchOccupant').generated_class(),unreal.Vector(*item['position']),unreal.Rotator(pitch=0,yaw=item['yaw']+270,roll=0));mesh=a.get_component_by_class(unreal.SkeletalMeshComponent);mesh.set_skinned_asset_and_update(source.get_skinned_asset(),True);mesh.set_world_scale3d(source.get_editor_property('relative_scale3d'))
 for k,material in enumerate(source.get_materials()):mesh.set_material(k,material)
# Use the existing crosswalk controller with explicit routes aligned to the new road angle.
old=[a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_CrosswalkCitizen_C']
for a in old:actors.destroy_actor(a)
for i,s in enumerate(plan['crossings']):
 ang=math.radians(s['yaw']);t=unreal.Vector(math.cos(ang),math.sin(ang),0);rr=unreal.Vector(-t.y,t.x,0);base=unreal.Vector(*s['position']);w=s['halfwidth']-120;local=[(-250,-w),(-250,w),(0,w),(250,w),(250,w),(250,-w),(0,-w),(-250,-w)];points=[base+t*x+rr*y+unreal.Vector(0,0,20) for x,y in local]
 for side in [0,4]:
  a=actors.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrosswalkCitizen').generated_class(),points[side]+unreal.Vector(0,0,88));a.set_editor_property('Route',points);a.set_editor_property('RouteIndex',side+1);m=a.get_component_by_class(unreal.SkeletalMeshComponent);c=unreal.get_default_object(unreal.load_asset(models[(i*3+side)%len(models)]['asset']).generated_class());src=c.get_editor_property('mesh');m.set_skinned_asset_and_update(src.get_skinned_asset(),True)
  for k,material in enumerate(src.get_materials()):m.set_material(k,material)
  m.set_anim_instance_class(unreal.load_class(None,'/Game/Delivery/Animation/ABP_StreetCitizen.ABP_StreetCitizen_C'))
# Increase the ordinary city population with four staggered starts per sidewalk loop.
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/finish_new_map_crowd.py').read_text(),'UrbanCrowdPopulation','exec'),{})
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_CrowdManager_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrowdManager').generated_class(),unreal.Vector())
# More traffic, with explicit separation and rebuilt per-lane leaders rather than overlapping spawns.
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficManager');c=unreal.get_default_object(bp.generated_class());la=[actors.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i)).generated_class(),unreal.Vector()) for i in range(7)];mod=[];lanes=[];dists=[];pts=[];paints=[]
for i in range(150):
 bus=i>=144;li=6 if bus else i%6;mi=22 if bus else 20+(i//5)%2 if i%5==0 else i%20;length=la[li].call_method('RouteLength');distance=length*((i*.61803398875)%1)
 for attempt in range(1000):
  point=la[li].call_method('SamplePosition',(distance,))
  if all((point-q).length()>1100 for q in pts):break
  distance=(distance+850)%length
 else:raise RuntimeError('Traffic spawn separation failed '+str(i))
 mod.append(mi);lanes.append(li);dists.append(distance);pts.append(point);paints.append(i%80)
for a in la:actors.destroy_actor(a)
leaders=[]
for i,li in enumerate(lanes):
 group=sorted([j for j in range(len(lanes)) if lanes[j]==li],key=lambda j:dists[j]);leaders.append(group[(group.index(i)+1)%len(group)])
for n,val in [('ModelIndices',mod),('LaneIndices',lanes),('InitialDistances',dists),('PaintIndices',paints),('LeaderIndices',leaders)]:c.set_editor_property(n,val)
assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_TrafficManager_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
for a in actors.get_all_level_actors():
 if a.get_class().get_name()=='BP_WorldState_C':a.set_editor_property('RainStartChance',.28);a.set_editor_property('DryWeatherHold',unreal.Vector2D(180,360));a.set_editor_property('WetWeatherHold',unreal.Vector2D(45,80))
assert unreal.EditorLoadingAndSavingUtils.save_current_level();D=r/'outputs/BogotaUrban';D.mkdir(exist_ok=True,parents=True);shutil.copy2(U/'Mobiliario_Bogota_Voxel.blend',D/'Mobiliario_Bogota_Voxel.blend');shutil.copy2(U/'placement_plan.json',D/'placement_plan.json');(D/'integration.json').write_text(json.dumps({'crossings':len(plan['crossings']),'signals':len(plan['crossings'])*2,'stations':4,'furniture':dict(collections.Counter(v['type'] for v in plan['furniture'])),'traffic':150,'ordinary_pedestrians':len(city['pedestrians']),'crossing_pedestrians':24,'seated_citizens':len(benches[::3])},indent=2));unreal.log('BOGOTA_URBAN_MAP_PLACED')
