import unreal,json
from pathlib import Path
project=Path(unreal.Paths.project_dir());root=project.parents[1]
for name in ['SM_PizzaFront_Voxel','SM_PizzaInterior_Voxel','SM_Pizza']:
 target='/Game/Delivery/Stores/'+name
 assert unreal.EditorAssetLibrary.does_asset_exist(target),'Import the Blender pizzeria first: '+target
rows=json.loads((project/'DeliveryData/StoreThemes.json').read_text(encoding='utf-8'))
if not any(r['Name']=='Pizza' for r in rows):
 rows.append(dict(Name='Pizza',Category=1,Title='Horno de la Cuadra',FrontMesh='/Game/Delivery/Stores/SM_PizzaFront_Voxel.SM_PizzaFront_Voxel',InteriorMesh='/Game/Delivery/Stores/SM_PizzaInterior_Voxel.SM_PizzaInterior_Voxel',ProductMeshes=['SM_Pizza'],ProductNames=['pizza artesanal recién horneada'],PurchaseBudget=29000,WidthMeters=24,DepthMeters=28,CounterDistanceMeters=20))
(project/'DeliveryData/StoreThemes.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
table=unreal.load_asset('/Game/Delivery/Data/DT_StoreThemes');assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_file(table,str(project/'DeliveryData/StoreThemes.json'));unreal.EditorAssetLibrary.save_loaded_asset(table)
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
shops=[a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a,unreal.DeliveryPoint)]
existing=[a for a in shops if str(a.get_editor_property('theme_id'))=='Pizza']
if existing:chosen=existing[0]
else:
 # Reuse a duplicate food venue's already-cleared parcel, preserving every existing category.
 counts={}
 for shop in shops:
  theme=str(shop.get_editor_property('theme_id'));counts[theme]=counts.get(theme,0)+1
 candidates=[s for s in shops if str(s.get_editor_property('theme_id')) in ['QuickMeals','BurgerGrill'] and counts[str(s.get_editor_property('theme_id'))]>1]
 assert candidates,'No safe duplicate restaurant parcel'
 chosen=sorted(candidates,key=lambda a:str(a.get_editor_property('point_id')))[-1]
 previous=next(r for r in rows if r['Name']==str(chosen.get_editor_property('theme_id')))
 # Runtime BuildStore reads these dimensions from DT_StoreThemes, overriding actor defaults.
 assert previous['WidthMeters']>=24 and previous['DepthMeters']>=28
 chosen.set_editor_property('theme_id',unreal.Name('Pizza'));chosen.set_editor_property('half_width',1200);chosen.set_editor_property('half_depth',1400)
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory('/Game/Delivery/Stores',only_if_is_dirty=True)
(root/'work/pizzeria_activated.json').write_text(json.dumps({'point_id':str(chosen.get_editor_property('point_id')),'location':str(chosen.get_actor_location()),'reused_cleared_parcel':True},indent=2))
