import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['build_pure_road_interaction.py','guard_pure_road_animation.py','finish_pure_road_codes_and_following.py','build_pure_road_interaction_qa.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{})
unreal.log('PURE_ROAD_FINAL_BATCH_PASS')

