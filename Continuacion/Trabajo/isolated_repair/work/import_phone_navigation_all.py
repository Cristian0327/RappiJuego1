import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
try:
 for script in ['migrate_phone_navigation.py','migrate_action_recipient.py']:
  exec((root/'work'/script).read_text(encoding='utf-8-sig'))
finally:
 unreal.SystemLibrary.quit_editor()
