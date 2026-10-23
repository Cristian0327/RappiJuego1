import unreal,json
from pathlib import Path
project=Path(unreal.Paths.project_dir());root=project.parents[1]
themes={r['Name']:r for r in json.loads((project/'DeliveryData/StoreThemes.json').read_text(encoding='utf-8-sig'))}
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
actors=unreal.EditorLevelLibrary.get_all_level_actors();city=next(a for a in actors if isinstance(a,unreal.BogotaCity))
shops=[a for a in actors if isinstance(a,unreal.DeliveryPoint)]
components={c.get_name():c for c in city.get_components_by_class(unreal.InstancedStaticMeshComponent)}
trunks=components['Solid_10'];selected=[];removed=[]
for i in range(trunks.get_instance_count()):
 transform=trunks.get_instance_transform(i,world_space=True);p=transform.translation
 for shop in shops:
  row=themes[str(shop.get_editor_property('theme_id'))];at=shop.get_actor_location()
  if abs(p.x-at.x)<row['WidthMeters']*50+75 and at.y-75<p.y<at.y+row['DepthMeters']*100+75:
   selected.append((i,p));removed.append({'shop':str(shop.get_editor_property('point_id')),'component':'Solid_10','index':i,'position':[p.x,p.y,p.z]});break
for name in ['Decor_8','Decor_9']:
 component=components[name];indices=[]
 for i in range(component.get_instance_count()):
  p=component.get_instance_transform(i,world_space=True).translation
  if p.z>500 and any(abs(p.x-at.x)<1 and abs(p.y-at.y)<1 for _,at in selected):indices.append(i);removed.append({'component':name,'index':i,'position':[p.x,p.y,p.z]})
 for i in reversed(indices):assert component.remove_instance(i)
for i,_ in reversed(selected):assert trunks.remove_instance(i)
if removed:
 assert unreal.EditorLevelLibrary.save_current_level()
(root/'work/shop_tree_collision_cleanup.json').write_text(json.dumps({'trees':len(selected),'removed_instances':removed},indent=2))
unreal.log('SHOP_TREE_CLEARANCE '+str(len(selected)))
