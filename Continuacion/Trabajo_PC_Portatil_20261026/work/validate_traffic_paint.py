import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
bp=unreal.load_asset('/Game/World/BP_BogotaCity')
r=json.loads(unreal.DeliveryEditorLibrary.validate_traffic_paint(bp.generated_class()))
assert r['blueprint_city'] and r['private_models']==20 and r['private_colors']>=12 and r['minimum_colors_per_model']>=4 and r['invalid_paint_masks']==0 and r['invalid_material_parents']==0 and r['colored_parked_cars']==12,r
r['status']='PASS';(root/'work/traffic_paint_validation.json').write_text(json.dumps(r,indent=2));unreal.log('TRAFFIC_PAINT_VALIDATION '+json.dumps(r))

