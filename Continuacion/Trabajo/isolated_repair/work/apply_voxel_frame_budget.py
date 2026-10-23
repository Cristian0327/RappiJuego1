from pathlib import Path
import shutil,unreal
r=Path(unreal.Paths.project_dir()).parent;p=r/'RappiJuego1/Config/DefaultEngine.ini';backup=r/'Recuperacion_Migracion_Blueprints/2026-10-20_vehicle_usability/DefaultEngine.ini'
if not backup.exists():shutil.copy2(p,backup)
s=p.read_text(encoding='utf-8-sig').replace('r.AntiAliasingMethod=2','r.AntiAliasingMethod=1')
section='[ConsoleVariables]'
if section not in s:s+='\n'+section+'\n'
lines=['r.DynamicRes.OperationMode=2','r.DynamicRes.FrameTimeBudget=16.666667','r.DynamicRes.MinScreenPercentage=60','r.DynamicRes.MaxScreenPercentage=100']
idx=s.index(section)+len(section);s=s[:idx]+'\n'+'\n'.join(lines)+s[idx:];p.write_text(s,encoding='utf-8');unreal.log('VOXEL_ADAPTIVE_GPU_BUDGET_PASS')
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_smooth_vehicle_runtime_qa.py').read_text(),'FinalQueueIsolationAndMotion','exec'),{})
