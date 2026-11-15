import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;folder='/Game/Delivery/BlueprintSchema';unreal.EditorAssetLibrary.make_directory(folder);report=json.loads(unreal.DeliveryEditorLibrary.create_blueprint_gameplay_schema(folder));assert 'error' not in report,report;assert len(report['enums'])==3 and len(report['structs'])==6,report;expected={'DeliveryUpgrade':6,'DeliveryShopTheme':10,'DeliveryOrder':12,'ActiveDelivery':6,'DeliveryVehicleSpec':6,'MapFootprint':2}
for row in report['enums']+report['structs']:
 asset=unreal.load_asset(row['asset']);assert asset;assert unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False)
for row in report['structs']:
 name=row['source'].split('.')[-1];assert len(row['fields'])==expected[name],(name,row['fields']);assert len({f['friendly_name'] for f in row['fields']})==expected[name]
reg=unreal.AssetRegistryHelpers.get_asset_registry();opts=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True);native=[]
for row in report['enums']+report['structs']:
 package=row['asset'].split('.')[0];bad=[str(x) for x in (reg.get_dependencies(package,opts) or []) if str(x).startswith('/Script/BogotaVoxel')]
 if bad:native.append({'asset':package,'dependencies':bad})
assert not native,native;report['status']='STAGING_SCHEMA_PASS';report['runtime_native_dependencies']=native;(r/'work/blueprint_gameplay_schema.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');unreal.log('BLUEPRINT_GAMEPLAY_SCHEMA_PASS enums=3 structs=6 fields=42')
