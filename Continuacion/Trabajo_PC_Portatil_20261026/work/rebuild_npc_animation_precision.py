from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for n in ['migrate_npc_animation_base.py','build_rebuilt_npc_animation_test.py']:
 p=r/'work'/n;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__name__':'__main__'})
