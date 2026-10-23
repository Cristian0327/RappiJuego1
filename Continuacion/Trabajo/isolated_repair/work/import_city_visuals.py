from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ['import_street_crowd.py','harmonize_crowd_material.py','import_crowd_all_animation.py']:
 p=root/'work'/name
 exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p)})
