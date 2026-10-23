import unreal,math,json,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);folder='/Game/Traffic/Services';bp=unreal.load_asset(folder+'/BP_TwoWheelerCitizen');root=Path(unreal.Paths.project_dir());backup=r/'Recuperacion_Migracion_Blueprints/2026-10-16_interacciones_animadas/Bogota_antes_ciclistas.umap';backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(root/'Content/Maps/Bogota.umap',backup)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
for o in a.get_all_level_actors():
 if o.get_actor_label().startswith(('Ciclista_Propietario_','Motociclista_Propietario_')):a.destroy_actor(o)
def rounded(x0,x1,y0,y1):
 rad=600;out=[]
 for j,(cx,cy) in enumerate([(x1-rad,y0+rad),(x1-rad,y1-rad),(x0+rad,y1-rad),(x0+rad,y0+rad)]):
  for k in range(13):
   ang=math.radians(-90+j*90+k*7.5);out.append(unreal.Vector(cx+math.cos(ang)*rad,cy+math.sin(ang)*rad,150))
 return out
manifest=[]
for i,(col,row) in enumerate([(0,0),(2,0),(4,0),(1,1),(4,1),(0,2),(2,3),(5,3)]):
 x0=-36000+col*12000;y0=-22000+row*11000;route=rounded(x0+1040,x0+12000-1040,y0+1040,y0+11000-1040);index=[3,16,29,42][i%4];pos=route[index];nxt=route[(index+1)%len(route)];yaw=math.degrees(math.atan2(nxt.y-pos.y,nxt.x-pos.x));o=a.spawn_actor_from_class(bp.generated_class(),pos,unreal.Rotator(yaw=yaw));o.set_actor_label('Ciclista_Propietario_'+str(i+1).zfill(2));o.set_editor_property('Route',route);o.set_editor_property('RouteIndex',(index+1)%len(route));o.set_editor_property('AgentId',100+i);o.set_editor_property('VehicleModel',unreal.load_asset('/Game/Traffic/Bicycles/SK_BicycleCivil'+['Blue','Red','Yellow'][i%3]));o.set_editor_property('RideSeconds',35+i*4);o.set_editor_property('StartParked',False);mesh=o.get_editor_property('mesh');mesh.set_skeletal_mesh_asset(unreal.load_asset('/Game/Crowd/People/SK_Citizen'+str([0,1,12,13,16,20,38,55][i]).zfill(2)));manifest.append({'actor':o.get_actor_label(),'position':[pos.x,pos.y,pos.z],'model':i%3,'lifecycle':'ride_park_dismount_walk_return_mount'})
for j,(col,row) in enumerate([(1,3),(4,3),(0,1),(5,0)]):
 x0=-36000+col*12000;y0=-22000+row*11000;route=rounded(x0+580,x0+12000-580,y0+580,y0+11000-580);index=7;pos=route[index];nxt=route[index+1];yaw=math.degrees(math.atan2(nxt.y-pos.y,nxt.x-pos.x));o=a.spawn_actor_from_class(bp.generated_class(),pos,unreal.Rotator(yaw=yaw));o.set_actor_label('Motociclista_Propietario_'+str(j+1).zfill(2));o.set_editor_property('Route',route);o.set_editor_property('RouteIndex',index+1);o.set_editor_property('AgentId',200+j);o.set_editor_property('Bicycle',False);o.set_editor_property('RoadMode',True);o.set_editor_property('RideSeconds',38+j*7);o.set_editor_property('VehicleModel',unreal.load_asset(folder+'/'+['SK_MotoCivilRed','SK_MotoCivilPurple','SK_MotoPolice','SK_MotoPoliceGreen'][j]));mesh=o.get_editor_property('mesh');mesh.set_skeletal_mesh_asset(unreal.load_asset(['/Game/Crowd/People/SK_Citizen12','/Game/Crowd/People/SK_Citizen13',folder+'/SK_PoliceOfficer',folder+'/SK_PoliceOfficerFemale01'][j]));mesh.set_material(0,unreal.load_asset(folder+'/M_ServiceVoxel' if j>=2 else '/Game/Crowd/MI_Crowd'));manifest.append({'actor':o.get_actor_label(),'position':[pos.x,pos.y,pos.z],'kind':'civil_motorcycle' if j<2 else 'police_motorcycle','lifecycle':'ride_park_dismount_walk_return_mount'})
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True);(root/'Docs/ciclistas_blueprints.json').write_text(json.dumps(manifest,indent=2));unreal.log('CITY_CYCLIST_LIFECYCLE_PLACEMENT_PASS')
