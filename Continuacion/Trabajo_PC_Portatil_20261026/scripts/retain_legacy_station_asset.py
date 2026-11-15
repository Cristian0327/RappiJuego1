"""Keep an unused legacy import intact; the map uses its normalized PhysicsFixed replacement."""
from pathlib import Path
import unreal,json,shutil
R=Path(__file__).resolve().parent.parent;asset='/Game/World/BogotaUrban/Geometry/SM_Bogota_EstacionTransmi_Compacta';relative=Path(asset[6:]+'.uasset');backup=Path((R/'optimization_backup_path.txt').read_text())/'Content'/relative
assert backup.exists();unreal.SystemLibrary.collect_garbage();shutil.copy2(backup,Path(unreal.Paths.project_content_dir())/relative)
p=R/'static_lod_optimization.json';report=json.loads(p.read_text());report['assets']=[row for row in report['assets'] if row['path']!=asset];report['retained_original_assets']=[dict(path=asset,reason='Unused legacy import has a stale scale of 100. The active normalized PhysicsFixed asset is optimized instead.')];p.write_text(json.dumps(report,indent=2));unreal.log('LEGACY_STATION_ASSET_PRESERVED')
