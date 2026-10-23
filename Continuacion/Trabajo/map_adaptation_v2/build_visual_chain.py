from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['build_overview.py','build_food_lifecycle.py']:
 exec(compile((P/name).read_text(),name,'exec'),{})
