from pathlib import Path
script=Path(__file__).parent/'build_commercial_district_blender.py'
exec(script.read_text(encoding='utf-8').split('\nnew_products()')[0])
for row in CAT:
 if row['category']!=1:interior(row)
(ROOT/'work/pickup_shelves_manifest.json').write_text(json.dumps(REPORT,indent=2))
