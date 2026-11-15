exec((__import__('pathlib').Path(__file__).parent/'import_corrected_rigs.py').read_text().split('for file in (art/')[0])
for label in ['FreshMarket','FastFood','Components']:
 for suffix in ['Front','Interior']:
  o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=True;o.import_textures=False;o.automated_import_should_detect_type=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False
  for asset in import_file(art/'Shops'/('SM_'+label+suffix+'.fbx'),'/Game/Delivery/Stores',o):
   if isinstance(asset,unreal.StaticMesh):asset.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);unreal.EditorAssetLibrary.save_loaded_asset(asset)
for name in ['GPU','RAM','CircuitBoard','ToolKit','Coffee','Salad','Bread','Carrots','Bananas','Nuggets','Pizza']:
 o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=True;o.import_textures=False;o.automated_import_should_detect_type=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False
 import_file(art/'HighFidelity'/('SM_'+name+'.fbx'),'/Game/Delivery/Stores',o)
exec((root/'work/fix_store_materials.py').read_text(encoding='utf-8'))
rows=[]
for id,category,label,title,meshes,names,budget in [
 ('MarketLocal',0,'Market','Mercado Don Lucho',['Milk','Rice','Apples'],['leche','arroz','manzanas'],18500),
 ('MarketFresh',0,'FreshMarket','La Canasta Verde',['Bread','Carrots','Bananas'],['pan artesanal','zanahorias','bananos'],24500),
 ('BurgerGrill',1,'Restaurant','La Plancha del Barrio',['Burger'],['hamburguesa a la parrilla y papas'],22000),
 ('QuickMeals',1,'FastFood','Parada Amarilla',['Nuggets'],['nuggets recién preparados'],19000),
 ('TechRetail',2,'Tech','Circuito 7',['Headphones','Keyboard','PhoneBox'],['audífonos','teclado','celular'],265000),
 ('TechComponents',2,'Components','Laboratorio 24',['GPU','RAM','CircuitBoard'],['tarjeta gráfica','memoria RAM','placa de desarrollo'],485000),
 ('Pharmacy',3,'Pharmacy','Droguería Buen Vecino',['FirstAid','Medicine','Medicine'],['botiquín','medicamento sellado','medicamento de la receta'],32000),
 ('Florist',4,'Florist','Flores de la Sabana',['Bouquet','Bouquet','Bouquet'],['ramo rojo','ramo mixto','ramo de regalo'],45000)]:
 rows.append(dict(Name=id,Category=category,Title=title,FrontMesh='/Game/Delivery/Stores/SM_'+label+'Front.SM_'+label+'Front',InteriorMesh='/Game/Delivery/Stores/SM_'+label+'Interior.SM_'+label+'Interior',ProductMeshes=['SM_'+x for x in meshes],ProductNames=names,PurchaseBudget=budget,WidthMeters=14 if label=='Florist' else 20,DepthMeters=12 if label=='Florist' else 18 if label in ['Market','FreshMarket','Pharmacy'] else 16))
file=project/'DeliveryData/StoreThemes.json';file.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
table=unreal.load_asset('/Game/Delivery/Data/DT_StoreThemes')
if not table:
 factory=unreal.DataTableFactory();factory.struct=unreal.DeliveryShopTheme.static_struct();table=tools.create_asset('DT_StoreThemes','/Game/Delivery/Data',unreal.DataTable,factory)
assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_file(table,str(file))
unreal.EditorAssetLibrary.save_loaded_asset(table)
unreal.log('BOGOTA_STORE_VARIANTS_IMPORTED '+str(len(rows)))
