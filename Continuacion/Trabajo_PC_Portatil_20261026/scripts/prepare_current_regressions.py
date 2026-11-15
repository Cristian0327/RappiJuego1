"""Rebuild acceptance maps from the current integration world only."""
from pathlib import Path
import unreal

root = Path(__file__).resolve().parent
for filename in ['build_current_physics.py', 'build_food_lifecycle.py', 'build_product_lifecycle.py']:
    path = root / 'map_adaptation_v2' / filename
    unreal.log('CURRENT_REGRESSION_BUILD ' + filename)
    exec(compile(path.read_text(), str(path), 'exec'), {'__file__': str(path), '__name__': '__main__'})
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
unreal.log('CURRENT_REGRESSIONS_READY')
