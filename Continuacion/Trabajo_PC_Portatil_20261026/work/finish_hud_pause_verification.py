from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for filename in ['build_pure_hud_pause.py','build_pure_pause_qa.py']:
 exec(compile((r/'work'/filename).read_text(encoding='utf-8-sig'),filename,'exec'),{'__name__':'__main__'})
unreal.log('HUD_PAUSE_VERIFICATION_READY')
