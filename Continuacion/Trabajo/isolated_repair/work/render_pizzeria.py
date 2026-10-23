from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'work/render_commercial_review.py').read_text()
source=source.replace("json.loads((ROOT/'work/commercial_catalog.json').read_text())","[{'label':'Pizza','depth':28,'width':24}]")
exec(compile(source,str(root/'work/render_commercial_review.py'),'exec'))
