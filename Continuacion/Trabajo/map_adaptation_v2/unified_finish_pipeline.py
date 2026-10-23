from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for n in ['unify_service_controllers.py','fix_service_braking.py','build_proxy_debug.py']:
 unreal.log('V2_UNIFIED_STAGE '+n);exec(compile((P/n).read_text(),n,'exec'),{})
