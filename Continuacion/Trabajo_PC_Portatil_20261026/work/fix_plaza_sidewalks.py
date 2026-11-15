import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
city=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.BogotaCity))
changes=[]
for old,half,delta in [(-10200,800,500),(-1500,700,-600)]:
 count=0
 # Use the old footprint as a one-time migration guard; rerunning is safe.
 components=city.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
 found=False
 for c in components:
  if not c.get_name().startswith('Solid_'):continue
  for i in range(c.get_instance_count()):
   t=c.get_instance_transform(i,world_space=True);p=t.translation;scale=t.scale3d
   if abs(p.x-old)<1 and abs(p.y-16500)<1 and abs(scale.x)>10 and abs(scale.y)>10 and abs(scale.z)>3 and p.z<1200:found=True;break
  if found:break
 if not found:
  changes.append({'old_x':old,'already_moved':True});continue
 for c in city.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
  if not (c.get_name().startswith('Solid_') or c.get_name().startswith('Decor_')):continue
  for i in range(c.get_instance_count()):
   t=c.get_instance_transform(i,world_space=True);p=t.translation
   if abs(p.x-old)<=half+90 and abs(p.y-16500)<=3090 and p.z>55:
    c.modify();t.translation=unreal.Vector(p.x+delta,p.y,p.z);c.update_instance_transform(i,t,world_space=True,mark_render_state_dirty=True,teleport=True);count+=1
 changes.append({'old_x':old,'new_x':old+delta,'moved_instances':count})
city.call_method('BuildMapMetadata');unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(root/'work/plaza_sidewalk_migration.json').write_text(json.dumps(changes,indent=2));unreal.log('PLAZA_SIDEWALKS '+json.dumps(changes))
