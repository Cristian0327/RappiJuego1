from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['lamp_lens_finish.py','respace_clear_stoplines.py','fix_manager_instance.py','build_debug_traffic.py','build_product_lifecycle.py']:
 unreal.log('V2_SWEEP_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
