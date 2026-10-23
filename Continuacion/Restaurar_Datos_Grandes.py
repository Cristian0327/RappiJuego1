from pathlib import Path
import gzip,shutil,json,hashlib
repo=Path(__file__).resolve().parent.parent
for row in json.loads((repo/'Continuacion/DATOS_GRANDES.json').read_text(encoding='utf-8')):
 target=repo/row['original']
 if target.exists() and target.stat().st_size==row['bytes']:
  print('Existe:',row['original']);continue
 packed=target.with_name(target.name+'.restaurando.gz')
 with packed.open('wb') as out:
  for name in row['parts']:
   with (repo/name).open('rb') as part:shutil.copyfileobj(part,out,1024*1024)
 with gzip.open(packed,'rb') as source,target.open('wb') as out:shutil.copyfileobj(source,out,1024*1024)
 assert target.stat().st_size==row['bytes']
 if row.get('sha256'):
  with target.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
 packed.unlink();print('Restaurado:',row['original'])
