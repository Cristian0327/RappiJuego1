from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['build_service_traffic_cache.py','build_road_vehicle_blueprint.py','distribute_city_services.py']:
 p=r/'work'/name
 exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
p=r/'work/build_city_services_runtime_test.py'
s=p.read_text(encoding='utf-8-sig').replace('CityServicesAvoidanceTest','CityServicesOptimizedSafetyTest').replace("Index='0'","Index='12'",1).replace('(X=-650,Y=-850,Z=350)','(X=650,Y=-650,Z=250)')
exec(compile(s,str(p),'exec'),{'__file__':str(p)})
unreal.log('FINAL_SERVICE_OPTIMIZATION_PASS')
