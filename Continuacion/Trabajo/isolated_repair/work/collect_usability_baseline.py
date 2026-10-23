from pathlib import Path
import shutil,json
root=Path.cwd();source=root/'work/UsabilityProfile/EngineBaseline';out=root/'outputs/Revision_Usabilidad/Antes';out.mkdir(parents=True,exist_ok=True)
for p in source.rglob('usability_validation.json'):shutil.copy2(p,out/'validacion.json')
for p in source.rglob('QA_*.png'):shutil.copy2(p,out/p.name)
r=json.loads((out/'validacion.json').read_text(encoding='utf-8-sig'));print(r['total'],'checks,',len(r['failures']),'failures');print([p.name for p in out.glob('*.png')])
