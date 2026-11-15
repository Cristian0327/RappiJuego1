import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;rates=[]
for name in ['import_hero_locomotion_rebuilt.py','build_police_blueprint.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
items=json.loads((r/'outputs/DeliveryArt/AnimationRebuild/stance_speeds.json').read_text())+json.loads((r/'outputs/DeliveryArt/AnimationRebuild/run_cane_stance_speeds.json').read_text())
for item in items:
 clip=item['clip'];speed=item['stance_speed_cm_s']
 if not speed:continue
 path=None;reference=50
 if clip=='AN_CrowdWalk_Rebuilt':path='/Game/Crowd/AN_CrowdWalk_Mixamo';reference=140
 elif clip=='AN_CrowdCane_Rebuilt':path='/Game/Crowd/AN_CrowdCane';reference=38/.95
 elif clip=='AN_HeroWalk_Rebuilt':path='/Game/VoxelExplorer/AN_Walk_InPlace';reference=390
 elif clip=='AN_HeroRun_Rebuilt':path='/Game/VoxelExplorer/AN_MixamoWalk';reference=390
 elif clip.startswith(('AN_Crowd','AN_Hero')):continue
 else:path='/Game/Delivery/People/A_'+clip[3:-len('Walk_Rebuilt')]+'_Walk'
 asset=unreal.load_asset(path);assert asset,path;asset.set_editor_property('rate_scale',reference/speed);assert unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False);rates.append({'asset':path,'stance_speed_cm_s':speed,'reference_cm_s':reference,'rate_scale':reference/speed})
(r/'RappiJuego1/Docs/sincronizacion_animaciones.json').write_text(json.dumps(rates,indent=2));unreal.log('MEASURED_MOTION_CALIBRATION_PASS')
p=r/'work/build_city_services_runtime_test.py';s=p.read_text(encoding='utf-8-sig').replace('CityServicesAvoidanceTest','CityServicesMotionTest');exec(compile(s,str(p),'exec'),{'__file__':str(p)})
