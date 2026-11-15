"""Copy only verified optimization assets, preserving the current source project."""
from pathlib import Path
import hashlib,shutil,json,sys
R=Path(__file__).resolve().parent;A=R/'BlueprintAuthoring';P=R.parent/'BogotaVoxel';mode=sys.argv[1] if len(sys.argv)>1 else 'runtime';target=R/'ModulelessRuntime' if mode=='runtime' else P
backup=Path((R/'optimization_backup_path.txt').read_text());lod=json.loads((R/'static_lod_optimization.json').read_text());assert lod['status']=='verified',lod['status']
paths=[x['path'] for x in lod['assets']]+json.loads((R/'skeletal_lod_streaming.json').read_text())
paths += ['/Game/World/BlueprintWorld/Optimization/'+x for x in ['WBP_GraphicsSettings','BP_GraphicsSettings','WBP_ShaderWarmup','BP_ServiceDistanceBudget','BP_StoreDistanceBudget']]
paths += ['/Game/World/BlueprintWorld/Crowd/BP_CrowdVisibility','/Game/QA/BP_GraphicsSettingsQA','/Game/QA/BP_OptimizationFrameProbe','/Game/QA/GraphicsSettingsQA','/Game/QA/OptimizationBenchmark','/Game/Maps/MapaCompleto_Integration']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=[]
for package in dict.fromkeys(paths):
 extension='.umap' if package in ['/Game/QA/GraphicsSettingsQA','/Game/QA/OptimizationBenchmark','/Game/Maps/MapaCompleto_Integration'] else '.uasset'
 relative=Path(package[6:]+extension);source=A/'Content'/relative;dest=target/'Content'/relative;assert source.exists(),source
 for suffix in [extension,'.uexp','.ubulk']:
  src=source.with_suffix(suffix);dst=dest.with_suffix(suffix)
  if not src.exists():continue
  if mode!='runtime' and dst.exists():
   previous=backup/'Content'/dst.relative_to(target/'Content');previous.parent.mkdir(parents=True,exist_ok=True)
   if previous.exists():assert sha(previous)==sha(dst),(str(dst),'source changed while optimization was running')
   else:shutil.copy2(dst,previous)
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst)
  manifest.append(dict(path=str(dst),sha256=sha(dst)))
for name in ['DefaultEngine.ini','DefaultScalability.ini','DefaultGameUserSettings.ini','DefaultInput.ini']:
 if mode=='runtime':shutil.copy2(P/'Config'/name,target/'Config'/name)
if mode=='runtime':shutil.copy2(P/'BogotaVoxel.uproject',target/'BogotaVoxel.uproject')
(R/('optimization_'+mode+'_manifest.json')).write_text(json.dumps(manifest,indent=2));print(json.dumps(dict(status='verified',mode=mode,files=len(manifest)),indent=2))
