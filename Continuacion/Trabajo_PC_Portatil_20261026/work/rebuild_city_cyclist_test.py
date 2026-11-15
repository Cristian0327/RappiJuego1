import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for n in ['build_two_wheeler_runtime_test.py','build_cyclist_visual_observer.py']:
 exec(compile((r/'work'/n).read_text(encoding='utf-8-sig'),str(r/'work'/n),'exec'))
