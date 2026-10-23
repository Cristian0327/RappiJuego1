from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for n in ['build_visible_transit_passenger.py','build_transit_presentation_manager.py']:
 exec(compile((r/'work'/n).read_text(encoding='utf-8-sig'),str(r/'work'/n),'exec'),{'__file__':str(r/'work'/n)})
