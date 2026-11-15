from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto')
for name in ['rebuild_standard_third_person_controls.py','build_standard_controls_qa.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{})
