from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['import_boarding_walk_rebuilt.py','build_rebuilt_npc_animation_test.py']:
 p=r/'work'/name
 exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
