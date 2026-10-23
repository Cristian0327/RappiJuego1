import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
actors=unreal.EditorLevelLibrary.get_all_level_actors();city=next(a for a in actors if isinstance(a,unreal.BogotaCity));city.build_map_metadata();feet=city.get_editor_property('map_footprints');assert len(feet)>50,'Missing baked geometry metadata'
occupied=[];result=[]
def free(x,y):
 cx,cy=x,y+900
 for f in feet:
  p=f.get_editor_property('center');e=f.get_editor_property('extent')
  if abs(cx-p.x)<1050+e.x and abs(cy-p.y)<950+e.y:return False
 for px,py in occupied:
  if abs(cx-px)<2100 and abs(cy-py)<1900:return False
 return True
reserved={'Shop_2_3','Shop_4_3','Shop_5_3','Shop_3_1'}
subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in [a for a in actors if isinstance(a,unreal.DeliveryPoint) and str(a.get_editor_property('point_id')) in reserved]:subsystem.destroy_actor(actor)
actors=[a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a,unreal.DeliveryPoint)]
themes=['MarketLocal','MarketFresh','BurgerGrill','QuickMeals','TechRetail','TechComponents','Pharmacy','Florist']
for number,actor in enumerate(sorted(actors,key=lambda a:str(a.get_editor_property('point_id')))):
 pid=str(actor.get_editor_property('point_id'));_,ix,iy=pid.split('_');rx=[-36000,-24000,-12000,0,12000,24000][int(ix)];ry=[-22000,-11000,0,11000][int(iy)];found=None
 for dx in [6000,5700,6300,5400,6600,3400,3100,3700,2800,4000,2500]:
  for dy in [2100,2400,2700,3000]:
   if free(rx+dx,ry+dy):found=(rx+dx,ry+dy);break
  if found:break
 if not found:raise RuntimeError('No clear commercial plot for '+pid)
 actor.set_editor_property('theme_id',unreal.Name(themes[number%len(themes)]));actor.set_actor_location(unreal.Vector(*found,30),False,False);occupied.append((found[0],found[1]+900));result.append({'id':pid,'location':[*found,30],'reserved_footprint_m':[20,18]})
unreal.EditorLevelLibrary.save_current_level();(root/'work/commercial_placement_check.json').write_text(json.dumps({'actual_buildings':len(feet),'placed':result,'overlap':False},indent=2));unreal.log('LARGE_COMMERCIAL_PLACEMENT_PASS '+str(len(result)))
