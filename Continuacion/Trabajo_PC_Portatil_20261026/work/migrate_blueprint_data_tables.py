import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;T=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.DataTableFunctionLibrary;folder='/Game/Delivery/BlueprintSchema/Tables';unreal.EditorAssetLibrary.make_directory(folder);report=[]
for name,struct in [('DT_Upgrades','DeliveryUpgrade'),('DT_StoreThemes','DeliveryShopTheme'),('DT_Vehicles','DeliveryVehicleSpec')]:
 source=unreal.load_asset('/Game/Delivery/Data/'+name);targetstruct=unreal.load_asset('/Game/Delivery/BlueprintSchema/ST_'+struct);assert source and targetstruct;path=folder+'/'+name;target=unreal.load_asset(path)
 if not target:
  f=unreal.DataTableFactory();f.set_editor_property('struct',targetstruct);target=T.create_asset(name,folder,unreal.DataTable,f)
 original=L.export_data_table_to_json_string(source);assert original;assert L.fill_data_table_from_json_string(target,original,targetstruct),name;assert unreal.EditorAssetLibrary.save_loaded_asset(target,only_if_is_dirty=False);exported=L.export_data_table_to_json_string(target);a=json.loads(original);b=json.loads(exported);assert len(a)==len(b),(name,len(a),len(b));assert {x['Name'] for x in a}=={x['Name'] for x in b};report.append({'asset':path,'source':source.get_path_name(),'rows':len(a),'struct':targetstruct.get_path_name(),'source_sample':a[:1],'converted_sample':b[:1]})
(r/'work/blueprint_data_table_migration.json').write_text(json.dumps({'status':'STAGING_NOT_PROMOTED','tables':report},ensure_ascii=False,indent=2),encoding='utf-8');unreal.log('BLUEPRINT_DATA_TABLE_MIGRATION_PASS tables=3')
