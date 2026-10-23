import json,hashlib,shutil
from pathlib import Path
W=Path(__file__).resolve().parent.parent;P=W/'map_adaptation_v2';src=W/'isolated_repair/ModulelessRuntime';repo=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1');backup=P/'delivery_pause_backup';rows=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,q):q.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,q)
for p in (src/'Content').rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(src);q=repo/rel;new=sha(p);old=sha(q) if q.exists() else None
 if old!=new:
  if q.exists():copy(q,backup/rel)
  copy(p,q);assert sha(q)==new;rows.append(dict(path=rel.as_posix(),before=old,after=new))
if sha(src/'BogotaVoxel.uproject')!=sha(repo/'BogotaVoxel.uproject'):
 copy(repo/'BogotaVoxel.uproject',backup/'BogotaVoxel.uproject');copy(src/'BogotaVoxel.uproject',repo/'BogotaVoxel.uproject')
context=repo/'Continuacion';copy(P/'CONTINUAR_EN_OTRO_PC.md',context/'CONTINUAR_EN_OTRO_PC.md');copy(P/'EVIDENCIAS_ESTADO.json',context/'EVIDENCIAS_ESTADO.json');(P/'pause_consolidation_manifest.json').write_text(json.dumps(rows,indent=2));copy(P/'pause_consolidation_manifest.json',context/'CONSOLIDACION_PAUSA.json')
allowed={'.py','.md','.json','.txt','.csv','.png','.jpg','.jpeg','.wkt','.npy','.npz','.fbx','.log','.h','.cpp','.cs','.ps1','.bat'};skip={'portable_package','product_userdata','visual_userdata','__pycache__','python_deps','asset_backup','promotion_backup','delivery_pause_backup','Binaries','Intermediate','DerivedDataCache','Saved','.git'}
folders=['map_adaptation_v2','compact_city','new_map_audit','traffic_gameplay_repair','urban_corrections','urban_refresh','urban_safety','texture_cycle','isolated_repair/work']
for folder in folders:
 base=W/folder
 for p in base.rglob('*'):
  if p.is_file() and p.suffix.lower() in allowed and not any(part in skip for part in p.relative_to(base).parts):copy(p,context/'Trabajo'/p.relative_to(W))
for p in W.iterdir():
 if p.is_file() and p.suffix.lower() in {'.py','.md','.json','.txt'}:copy(p,context/'Trabajo'/p.name)
for p in (W/'isolated_repair/Herramientas').rglob('*'):
 if p.is_file() and p.suffix.lower() in allowed:copy(p,context/'Herramientas_Grafos'/p.relative_to(W/'isolated_repair/Herramientas'));copy(p,context/'Trabajo/isolated_repair/Herramientas'/p.relative_to(W/'isolated_repair/Herramientas'))
art=P/'portable_package/BogotaVoxel/Fuentes_Blender'
for p in art.rglob('*'):
 if p.is_file() and p.suffix!='.blend1':copy(p,repo/'Fuentes_Blender'/p.relative_to(art))
# Optional graph authoring tool, separate from the moduleless playable project.
optional=context/'Herramientas_Autoria';editor=W/'isolated_repair/BlueprintAuthoring';copy(editor/'BogotaVoxel.uproject',optional/'BogotaVoxel.uproject')
for p in (editor/'Binaries').rglob('*'):
 if p.is_file() and p.suffix.lower() in {'.dll','.modules','.target'}:copy(p,optional/'Binaries'/p.relative_to(editor/'Binaries'))
source=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/Recuperacion_Migracion_Blueprints/2026-10-19_native_retirement/Source')
for p in source.rglob('*'):
 if p.is_file():copy(p,optional/'Source'/p.relative_to(source))
copy(P/'portable_package/BogotaVoxel/LEEME_TRASLADO.txt',repo/'LEEME_TRASLADO.txt');copy(P/'portable_package/BogotaVoxel/Abrir_Proyecto.bat',repo/'Abrir_Proyecto.bat')
(repo/'LEEME_TRASLADO.txt').write_text((repo/'LEEME_TRASLADO.txt').read_text()+"\nESTADO DE DESARROLLO PAUSADO: el tráfico aún acumula colas. Leer Continuacion/CONTINUAR_EN_OTRO_PC.md.\n",encoding='utf-8')
print('CONSOLIDATED_DEVELOPMENT_SNAPSHOT',len(rows));print('repo',repo)
