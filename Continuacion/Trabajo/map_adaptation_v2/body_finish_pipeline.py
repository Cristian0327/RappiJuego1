from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['fix_shared_corridors.py','install_body_zones_and_platoons.py','install_signals.py','respace_clear_stoplines.py','fix_manager_instance.py','build_debug_traffic.py','build_food_lifecycle.py','build_current_physics.py']:
 unreal.log('V2_BODY_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
