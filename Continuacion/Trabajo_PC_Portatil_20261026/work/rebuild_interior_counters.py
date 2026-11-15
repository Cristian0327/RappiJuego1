from pathlib import Path
root=Path(__file__).resolve().parents[1]
exec((root/'work/build_commercial_district_blender.py').read_text().split('\nnew_products()')[0])
for row in CAT:
 if row['label']!='Pizza':interior(row)
# The pizzeria has its own oven and wall details.
import runpy
runpy.run_path(str(root/'work/build_pizzeria_blender.py'),run_name='__main__')
