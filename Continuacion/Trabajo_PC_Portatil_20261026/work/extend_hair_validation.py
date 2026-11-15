from pathlib import Path
p=Path('work/validate_head_motion.py');s=p.read_text().replace("ids=[v.index for v in o.data.vertices if v.co.z>=150]", "ids=[v.index for v in o.data.vertices if any(o.vertex_groups[g.group].name=='head' for g in v.groups)]");p.write_text(s)
