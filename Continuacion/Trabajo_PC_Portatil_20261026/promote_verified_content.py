"""Promote the isolated project with per-file rollback copies and hashes."""
from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime

root = Path(__file__).resolve().parent
source = root / 'ModulelessRuntime' / 'Content'
target = root.parent / 'BogotaVoxel' / 'Content'
backup = root / ('promotion_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

changes = []
for path in sorted(source.rglob('*')):
    if not path.is_file():
        continue
    relative = path.relative_to(source)
    destination = target / relative
    new_hash = digest(path)
    old_hash = digest(destination) if destination.exists() else None
    if old_hash == new_hash:
        continue
    changes.append(dict(path=str(relative), before=old_hash, after=new_hash))

backup.mkdir(parents=True)
journal = backup / 'manifest.json'
journal.write_text(json.dumps(dict(status='prepared', source=str(source), target=str(target), files=changes), indent=2))
for change in changes:
    relative = Path(change['path'])
    destination = target / relative
    if destination.exists():
        original = backup / 'Content' / relative
        original.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(destination, original)
        assert digest(original) == change['before']
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / relative, destination)
    assert digest(destination) == change['after']
journal.write_text(json.dumps(dict(status='complete', source=str(source), target=str(target), files=changes), indent=2))
print(json.dumps(dict(changed_files=len(changes), backup=str(backup))))
