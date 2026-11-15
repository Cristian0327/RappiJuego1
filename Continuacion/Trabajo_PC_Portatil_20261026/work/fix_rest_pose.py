from pathlib import Path
p=Path('work/prepare_mixamo_autorig.py');s=p.read_text().replace('Quaternion,Vector','Quaternion,Vector,Matrix').replace('b.matrix_basis.identity()','b.matrix_basis=Matrix.Identity(4)');s=s.replace('sign*math.radians(55)','-sign*math.radians(65)');p.write_text(s)
p=Path('work/compare_manual_rig.py');s=p.read_text().replace('b.matrix_basis.identity()','b.matrix_basis=Matrix.Identity(4)');p.write_text(s)
