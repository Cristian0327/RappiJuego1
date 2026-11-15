import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;out={'materials':[],'cars':[]}
for path in unreal.EditorAssetLibrary.list_assets('/Game/Traffic',True,False):
 a=unreal.EditorAssetLibrary.find_asset_data(path)
 if str(a.asset_class_path.asset_name)=='Material':
  m=a.get_asset();out['materials'].append({'path':m.get_path_name(),'blend':str(m.get_editor_property('blend_mode')),'two_sided':m.get_editor_property('two_sided'),'base_node':str(unreal.MaterialEditingLibrary.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR))})
for row in json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']:
 b=unreal.load_asset(row['asset']);c=unreal.get_default_object(b.generated_class());pal=c.get_editor_property('PaintPalette');out['cars'].append({'asset':row['asset'],'palette_count':len(pal),'colors':[[p.r,p.g,p.b] for p in pal]})
(r/'work/current_vehicle_material_audit.json').write_text(json.dumps(out,indent=2));unreal.log('VEHICLE_MATERIAL_AUDIT_PASS')
