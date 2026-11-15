import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
try:
 exec((root/'work/migrate_phone_garage.py').read_text(encoding='utf-8-sig'))
 exec((root/'work/migrate_phone_selection.py').read_text(encoding='utf-8-sig'))
finally:
 unreal.SystemLibrary.quit_editor()
