import unreal,hashlib,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
p=r/'work/build_pure_street_citizen_foundation.py'
exec(compile(p.read_text(),str(p),'exec'))
sha=hashlib.sha256((r/'RappiJuego1/Content/Crowd/AN_CrowdCane.uasset').read_bytes()).hexdigest()
assert sha=='1742c809c0799c7abc0b7167d415febafb2dd6290787335d39536e9bccfc461e'
(r/'work/cane_preservation_validation.json').write_text(json.dumps({'idle_rate':0,'idle_start':0,'walk_rate':.95,'original_clip_sha256':sha,'status':'PASS'},indent=2))
unreal.log('CANE_PRESERVATION_PASS')
