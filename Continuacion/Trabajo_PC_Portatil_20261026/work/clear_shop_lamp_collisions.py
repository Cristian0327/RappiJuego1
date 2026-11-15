import unreal,json,shutil
from pathlib import Path
project=Path(unreal.Paths.project_dir());root=project.parents[1]
backup=root/'work/Backups/Bogota_before_lamp_clear.umap'
if not backup.exists():shutil.copy2(project/'Content/Maps/Bogota.umap',backup)
themes={r['Name']:r for r in json.loads((project/'DeliveryData/StoreThemes.json').read_text(encoding='utf-8-sig'))}
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
actors=unreal.EditorLevelLibrary.get_all_level_actors();city=next(a for a in actors if isinstance(a,unreal.BogotaCity))
shops=[a for a in actors if isinstance(a,unreal.DeliveryPoint)]
components={c.get_name():c for c in city.get_components_by_class(unreal.InstancedStaticMeshComponent)}
steel=components['Solid_21'];selected=[];removed=[]
for i in range(steel.get_instance_count()):
 t=steel.get_instance_transform(i,world_space=True);p=t.translation;size=t.scale3d*100
 if abs(size.x-45)>1 or abs(size.y-45)>1 or abs(size.z-800)>1:continue
 for shop in shops:
  row=themes[str(shop.get_editor_property('theme_id'))];at=shop.get_actor_location()
  in_parcel=abs(p.x-at.x)<row['WidthMeters']*50+60 and at.y-60<p.y<at.y+row['DepthMeters']*100+60
  in_door_approach=abs(p.x-at.x)<220 and at.y-350<p.y<at.y+200
  if in_parcel or in_door_approach:
   selected.append((i,p));removed.append({'shop':str(shop.get_editor_property('point_id')),'component':'Solid_21','index':i,'position':[p.x,p.y,p.z]});break
for name,height,offset in [('Decor_6',790,120),('Decor_15',758,220)]:
 c=components[name];indices=[]
 for i in range(c.get_instance_count()):
  p=c.get_instance_transform(i,world_space=True).translation
  if abs(p.z-height)<1 and any(abs(p.x-at.x)<1 and abs(abs(p.y-at.y)-offset)<1 for _,at in selected):indices.append(i)
 for i in reversed(indices):assert c.remove_instance(i)
for i,_ in reversed(selected):assert steel.remove_instance(i)
if selected:assert unreal.EditorLevelLibrary.save_current_level()
(root/'work/shop_lamp_collision_cleanup.json').write_text(json.dumps({'lamps':len(selected),'removed_instances':removed},indent=2))
unreal.log('SHOP_LAMP_CLEARANCE '+str(len(selected)))
