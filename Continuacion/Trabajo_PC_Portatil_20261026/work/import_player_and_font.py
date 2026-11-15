import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
try:
 for name in ['migrate_player_drive_camera.py','import_phone_pixel_font.py']:
  exec(compile((root/'work'/name).read_text(encoding='utf-8-sig'),str(root/'work'/name),'exec'),{'__name__':'__main__'})
finally:unreal.SystemLibrary.quit_editor()
