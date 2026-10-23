from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['fix_entry_obstacles.py','integrate_navigation.py','verify_physical_streets.py','build_debug_traffic.py','build_product_lifecycle.py']:
 unreal.log('V2_ENTRY_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
