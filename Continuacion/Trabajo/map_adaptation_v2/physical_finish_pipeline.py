from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['install_compact_station.py','install_station_move.py','integrate_navigation.py','verify_physical_streets.py']:
 unreal.log('V2_PHYSICAL_FINISH_START '+name);exec(compile((P/name).read_text(),name,'exec'),{});unreal.log('V2_PHYSICAL_FINISH_PASS '+name)
