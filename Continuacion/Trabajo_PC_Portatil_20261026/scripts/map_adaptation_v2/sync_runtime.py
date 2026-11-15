import json,hashlib,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;source=P.parent/'isolated_repair/BlueprintAuthoring/Content';dest=P.parent/'isolated_repair/ModulelessRuntime/Content';rows=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for file in source.rglob('*'):
 if not file.is_file() or file.suffix not in ['.uasset','.umap','.ubulk','.uexp']:continue
 rel=file.relative_to(source);target=dest/rel;sha=digest(file)
 if target.exists() and target.stat().st_size==file.stat().st_size and digest(target)==sha:continue
 target.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(file,target);assert digest(target)==sha;rows.append(dict(path=str(rel).replace('\\','/'),sha256=sha))
(P/'runtime_sync_manifest.json').write_text(json.dumps(rows,indent=2));print('V2_RUNTIME_SYNC_VERIFIED',len(rows))
