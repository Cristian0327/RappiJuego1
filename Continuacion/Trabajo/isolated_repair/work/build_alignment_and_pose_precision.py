import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for n in ['migrate_rider_animation_pure_blueprint.py','build_two_wheeler_citizen.py','build_npc_facing_coordinator.py']:
 exec(compile((r/'work'/n).read_text(encoding='utf-8-sig'),str(r/'work'/n),'exec'),{'__file__':str(r/'work'/n)})
