from pathlib import Path
_task_root=Path(__file__).resolve().parents[1]
for _task_file in ['import_street_crowd.py','harmonize_crowd_material.py','import_crowd_all_animation.py','fix_map_lighting.py']:
 _task_path=_task_root/'work'/_task_file
 exec(compile(_task_path.read_text(),str(_task_path),'exec'),{'__file__':str(_task_path)})
