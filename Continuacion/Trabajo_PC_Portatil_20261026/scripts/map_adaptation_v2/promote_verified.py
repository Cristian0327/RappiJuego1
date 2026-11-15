import json,hashlib,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;assert json.loads((P/'final_acceptance.json').read_text())['passed'];src=P.parent/'isolated_repair/ModulelessRuntime';dest=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1');backup=P/'promotion_backup';stage=P/'portable_package/BogotaVoxel';rows=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for file in (src/'Content').rglob('*'):
 if not file.is_file() or file.relative_to(src/'Content').parts[0]=='QA':continue
 rel=file.relative_to(src);sha=digest(file);target=dest/rel;before=digest(target) if target.exists() else None
 if before!=sha:
  old=backup/rel
  if target.exists() and not old.exists():old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,old)
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target);assert digest(target)==sha;rows.append(dict(path=rel.as_posix(),before=before,after=sha))
 portable=stage/rel
 if not portable.exists() or digest(portable)!=sha:portable.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,portable)
 assert digest(portable)==digest(target)==sha
# Use the verified moduleless descriptor; retain the user's saved game unchanged.
for rel in [Path('BogotaVoxel.uproject')]:
 target=dest/rel;old=backup/rel
 if not old.exists():shutil.copy2(target,old)
 shutil.copy2(src/rel,target);shutil.copy2(src/rel,stage/rel)
(P/'full_promotion_verified.json').write_text(json.dumps(dict(status='VERIFIED',assets=rows),indent=2));print('PROMOTED_AND_PORTABLE_IDENTICAL',len(rows))
