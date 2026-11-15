import unreal,json,re
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;project=Path(unreal.Paths.project_dir());unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);counts={'female_officers':0,'male_officers':0,'female_police_riders':0,'male_police_riders':0};models=set();officers=set();entries=[]
for a in actors.get_all_level_actors():
 label=a.get_actor_label()
 if label.startswith('Policia_Sector_'):
  model=a.get_editor_property('mesh').get_editor_property('skeletal_mesh').get_name();officers.add(model);counts['female_officers' if 'Female' in model else 'male_officers']+=1;entries.append({'label':label,'model':model})
 elif label.startswith(('Moto_Civil_Sector_','Moto_Policia_Sector_')):
  model=a.get_editor_property('DriveModel').get_name();rider=a.get_editor_property('RiderModel').get_name();models.add(model);entries.append({'label':label,'model':model,'rider':rider})
  if label.startswith('Moto_Policia_'):counts['female_police_riders' if 'Female' in rider else 'male_police_riders']+=1
assert counts=={'female_officers':12,'male_officers':12,'female_police_riders':3,'male_police_riders':3},counts;assert len(models)==8,models;assert len(officers)==4,officers
paths=['/Game/VoxelExplorer/'+n for n in ['AN_Idle','AN_MixamoWalk','AN_Walk_InPlace','AN_BikePedal','AN_MotoRide','AN_MixamoJump']]+['/Game/Crowd/'+n for n in ['AN_CrowdWalk_Mixamo','AN_CrowdIdle','AN_CrowdCane','AN_CrowdEnterCar']]+['/Game/Traffic/Services/AN_MotorcycleRider']+['/Game/Delivery/People/A_'+role+'_'+clip for role in ['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor'] for clip in ['Walk','Work']];clips=[]
for path in paths:
 a=unreal.load_asset(path);assert a,path;clips.append({'asset':path,'length_seconds':a.get_play_length(),'rate_scale':a.get_editor_property('rate_scale'),'skeleton':a.get_editor_property('skeleton').get_path_name()})
for name in ['BP_PoliceOfficer','BP_VoxelRoadVehicle','BP_CivilMotorcycle','BP_PoliceMotorcycle','BP_PoliceRoadPatrol']:
 b=unreal.load_asset('/Game/Traffic/Services/'+name);assert unreal.BlueprintEditorLibrary.compile_blueprint(b);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(b));assert not any(g['native_calls'] for g in audit['graphs']),name
report={'status':'PASS','counts':counts,'motorcycle_variants':sorted(models),'officer_variants':sorted(officers),'actors':entries,'rebuilt_active_animation_assets':clips,'full_project_blueprint_migration_complete':False,'note':'New services use Engine.Character and Blueprint behaviors. Existing project still has custom native parent classes.'}
(project/'Docs/variaciones_y_animaciones_2026-10-16.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));unreal.log('VARIATIONS_AND_27_ANIMATION_ASSETS_AUDIT_PASS')
