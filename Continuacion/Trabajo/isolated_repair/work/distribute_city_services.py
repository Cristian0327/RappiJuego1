import unreal,math,json,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;root=Path(unreal.Paths.project_dir());f='/Game/Traffic/Services';E=unreal.BlueprintEditorLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
base=unreal.load_asset(f+'/BP_VoxelRoadVehicle');police=unreal.load_asset(f+'/BP_PoliceOfficer');assert base and police
for b,names in [(base,['Route','RouteIndex','DriveModel','RiderModel']),(police,['PatrolPoints','PatrolIndex'])]:
 for name in names:E.set_blueprint_variable_instance_editable(b,name,True)
 assert E.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
# Blueprint child variants retain the same reusable road behavior.
def child(name,model,rider,car=False):
 p=f+'/'+name
 if unreal.EditorAssetLibrary.does_asset_exist(p):b=unreal.load_asset(p)
 else:
  factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',base.generated_class());b=tools.create_asset(name,f,unreal.Blueprint,factory)
 assert E.compile_blueprint(b);c=unreal.get_default_object(b.generated_class());c.set_editor_property('DriveModel',unreal.load_asset(f+'/'+model));c.set_editor_property('DriveMaterial',unreal.load_asset(f+'/M_ServiceVoxel'));c.set_editor_property('RiderModel',unreal.load_asset(rider) if rider else None);c.set_editor_property('RiderMaterial',unreal.load_asset(f+'/M_ServiceVoxel') if rider and 'PoliceOfficer' in rider else unreal.load_asset('/Game/Crowd/MI_Crowd'));c.set_editor_property('RiderAnimation',unreal.load_asset(f+'/AN_PatrolDriver') if car else unreal.load_asset(f+'/AN_MotorcycleRider'));c.set_editor_property('GroundOffset',140.0 if car else 120.0);c.set_editor_property('WheelRadius',40.0 if car else 36.0);c.set_editor_property('RoadSpeed',580.0 if car else 650.0);c.set_editor_property('WheelNames',['wheel_0_L','wheel_0_R','wheel_1_L','wheel_1_R'] if car else ['wheel_front','wheel_rear']);c.get_editor_property('capsule_component').set_capsule_size(125 if car else 56,140 if car else 120);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False);return b
civil=child('BP_CivilMotorcycle','SK_MotoCivilBlue','/Game/Crowd/People/SK_Citizen12');moto=child('BP_PoliceMotorcycle','SK_MotoPolice',f+'/SK_PoliceOfficer');patrol=child('BP_PoliceRoadPatrol','SK_PolicePatrol',f+'/SK_PoliceOfficer',True)
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-16_policias_ciudad/Bogota.umap';backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(root/'Content/Maps/Bogota.umap',backup)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
if not any(a.get_actor_label()=='City_ServiceTrafficCache' for a in actors.get_all_level_actors()):
 manager=actors.spawn_actor_from_class(unreal.load_asset(f+'/BP_ServiceTrafficCache').generated_class(),unreal.Vector());manager.set_actor_label('City_ServiceTrafficCache')
for a in actors.get_all_level_actors():
 if str(a.get_actor_label()) in ['Policia_Voxel_BP','Patrulla_Voxel_BP'] or str(a.get_actor_label()).startswith(('Policia_Sector_','Moto_Civil_Sector_','Moto_Policia_Sector_','Patrulla_Sector_')):actors.destroy_actor(a)
counts={'foot_police':0,'civil_motorcycles':0,'police_motorcycles':0,'road_patrols':0};manifest=[]
north=[-36000,-24000,-12000,0,12000,24000,36000];east=[-22000,-11000,0,11000,22000]
for row in range(4):
 for col in range(6):
  x0=north[col]+1420;x1=north[col+1]-1420;y0=east[row]+(1850 if east[row]==0 else 1450);y1=east[row+1]-(1850 if east[row+1]==0 else 1450);points=[unreal.Vector(x0,y0,155),unreal.Vector(x1,y0,155),unreal.Vector(x1,y1,155),unreal.Vector(x0,y1,155)];i=(row+col)%4;position=points[i];a=actors.spawn_actor_from_class(police.generated_class(),position,unreal.Rotator(pitch=0,yaw=[0,90,180,-90][i],roll=0));a.set_actor_label('Policia_Sector_'+str(row*6+col+1).zfill(2));a.set_editor_property('PatrolPoints',points);a.set_editor_property('PatrolIndex',(i+1)%4);officer_variant=['SK_PoliceOfficer','SK_PoliceOfficerFemale01','SK_PoliceOfficerMale02','SK_PoliceOfficerFemale02'][(row*6+col)%4];a.get_editor_property('mesh').set_skeletal_mesh_asset(unreal.load_asset(f+'/'+officer_variant));counts['foot_police']+=1;manifest.append({'label':a.get_actor_label(),'kind':'foot_police','route':[[v.x,v.y,v.z] for v in points]})
def rounded(x0,x1,y0,y1):
 radius=700;points=[]
 for j,(cx,cy) in enumerate([(x1-radius,y0+radius),(x1-radius,y1-radius),(x0+radius,y1-radius),(x0+radius,y0+radius)]):
  for k in range(13):
   angle=math.radians(-90+j*90+k*7.5);points.append(unreal.Vector(cx+math.cos(angle)*radius,cy+math.sin(angle)*radius,160))
 return points
def place(points,distance):
 for i,p in enumerate(points):
  q=points[(i+1)%len(points)];length=math.hypot(q.x-p.x,q.y-p.y)
  if distance<length:
   t=distance/length;return unreal.Vector(p.x+(q.x-p.x)*t,p.y+(q.y-p.y)*t,180),(i+1)%len(points),math.degrees(math.atan2(q.y-p.y,q.x-p.x))
  distance-=length
 raise AssertionError('Invalid loop distance')
loops=[(-12000,0,11000,22000),(-36000,-24000,11000,22000),(24000,36000,11000,22000),(-24000,-12000,-22000,-11000),(0,12000,-22000,-11000),(12000,24000,0,11000)]
for district,bounds in enumerate(loops):
 x0,x1,y0,y1=bounds;points=rounded(x0+580,x1-580,y0+580,y1-580);length=sum(math.hypot(points[(i+1)%len(points)].x-p.x,points[(i+1)%len(points)].y-p.y) for i,p in enumerate(points))
 for slot in range(4):
  is_patrol=slot==3 and district<5;is_police=slot==2;blueprint=patrol if is_patrol else moto if is_police else civil;kind='road_patrols' if is_patrol else 'police_motorcycles' if is_police else 'civil_motorcycles';prefix='Patrulla' if is_patrol else 'Moto_Policia' if is_police else 'Moto_Civil';position,index,yaw=place(points,length*((slot+.15)/4));a=actors.spawn_actor_from_class(blueprint.generated_class(),position,unreal.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label(prefix+'_Sector_'+str(district+1)+'_'+str(slot+1));a.set_editor_property('Route',points);a.set_editor_property('RouteIndex',index)
  if not is_patrol and not is_police:
   variant=['SK_MotoCivilBlue','SK_MotoCivilRed','SK_MotoCourier','SK_MotoCivilYellow','SK_MotoCivilPurple','SK_MotoCivilWhite'][(district*2+slot)%6];a.set_editor_property('DriveModel',unreal.load_asset(f+'/'+variant));a.set_editor_property('RiderModel',unreal.load_asset('/Game/Crowd/People/SK_Citizen'+str([0,1,12,13,16,20,38,55][(district+slot)%8]).zfill(2)))
  if is_police:
   a.set_editor_property('DriveModel',unreal.load_asset(f+'/'+['SK_MotoPolice','SK_MotoPoliceGreen'][district%2]));a.set_editor_property('RiderModel',unreal.load_asset(f+'/'+['SK_PoliceOfficer','SK_PoliceOfficerFemale01','SK_PoliceOfficerMale02','SK_PoliceOfficerFemale02'][district%4]))
  if is_patrol:a.set_editor_property('RiderModel',unreal.load_asset(f+'/'+['SK_PoliceOfficer','SK_PoliceOfficerFemale01','SK_PoliceOfficerMale02','SK_PoliceOfficerFemale02'][district%4]))
  counts[kind]+=1;manifest.append({'label':a.get_actor_label(),'kind':kind,'initial_position':[position.x,position.y,position.z],'route_points':len(points)})
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True);(root/'Docs/distribucion_servicios_ciudad.json').write_text(json.dumps({'status':'PLACED_RUNTIME_TEST_PENDING','counts':counts,'actors':manifest},indent=2),encoding='utf-8');unreal.log('CITY_SERVICE_DISTRIBUTION_PASS '+json.dumps(counts))

