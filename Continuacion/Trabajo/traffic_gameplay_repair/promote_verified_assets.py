from pathlib import Path
import hashlib,json,re,shutil,os,datetime
P=Path(__file__).resolve().parent
stage=P.parent/'isolated_repair/BlueprintAuthoring/Content'
original=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1/Content')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return (P/name).read_text(encoding='utf-8',errors='replace')
def last_int(log,name):
 vals=re.findall(re.escape(name)+r'=(\d+)',log)
 assert vals,name
 return int(vals[-1])
audit=json.loads(read('final_asset_audit.json'));assert all(audit['checks'].values())
physics=read('physics_runtime3.log');assert 'CURB_CLIMBED=true' in physics;assert last_int(physics,'BODY_OVERLAPS_80')==0;assert last_int(physics,'BODY_OVERLAPS_115')==0;assert last_int(physics,'PHYSICS_CARS_MOVED')>=140;assert 'Accessed None' not in physics
phone=read('phone_moduleless_runtime.log');assert last_int(phone,'SHOP_PURCHASED_AFTER')>last_int(phone,'SHOP_PURCHASED_BEFORE');assert last_int(phone,'BIKE_PAINT')==1;assert last_int(phone,'NAVIGATION_POINTS')>2;assert 'WAYPOINT_AFTER_CLEAR=false' in phone
lifecycle=read('lifecycle_runtime2.log');states=[int(x) for x in re.findall(r'ORDER_STATE_\d+=(\d+)',lifecycle)];assert 3 in states and states[-1]==0
transit=read('compact_station_runtime.log');assert transit.count('TRANSIT_VISIBLE_SEATED=true')==4;assert transit.count('TRANSIT_ALIGHT_RESTORED=true')==4
patrol=read('patrol_runtime2.log');moving=last_int(patrol,'PATROL_MOVING_SAMPLES');bad=last_int(patrol,'PATROL_MISALIGNED_SAMPLES');assert moving>=20 and bad/moving<.05,(moving,bad)
assert 'PURE_PHONE_CONTROL_BINDINGS_PASS buttons=159 bindings=161' in read('phone_controls_build.log')
baseline=json.loads(read('staged_asset_manifest.json'));rows=[]
for item in baseline:
 rel=Path(item['path']);src=stage/rel;dst=original/rel
 assert src.is_file()
 assert (digest(dst) if dst.exists() else None)==item['original_sha256'],'Original changed while working: '+str(rel)
 rows.append(dict(path=item['path'],source_sha256=digest(src),original_sha256=item['original_sha256']))
backup=P/'promotion_backup';backup.mkdir(exist_ok=True)
# Back up every existing target before the first replacement, including .umap.
for row in rows:
 rel=Path(row['path']);src=original/rel;dst=backup/rel
 if src.exists():
  assert not dst.exists(),'Backup already exists: '+str(dst)
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert digest(dst)==row['original_sha256']
journal=[]
try:
 for row in sorted(rows,key=lambda x:x['path'].endswith('.umap')):
  rel=Path(row['path']);src=stage/rel;dst=original/rel;dst.parent.mkdir(parents=True,exist_ok=True);temp=dst.with_name(dst.name+'.codex-repair-pending');assert not temp.exists();shutil.copy2(src,temp);assert digest(temp)==row['source_sha256'];os.replace(temp,dst);journal.append(row);assert digest(dst)==row['source_sha256']
except Exception:
 for row in reversed(journal):
  rel=Path(row['path']);dst=original/rel;saved=backup/rel
  if saved.exists():shutil.copy2(saved,dst)
  elif dst.exists():dst.unlink()
 raise
report=dict(promoted_assets=len(journal),assets=journal,backup=str(backup),checks=audit['checks'],physics=dict(curb_climbed=True,moving_cars=last_int(physics,'PHYSICS_CARS_MOVED'),body_overlaps_at_80s=0,body_overlaps_at_115s=0),delivery=dict(completed=True,states=states),phone=dict(buttons=159,bindings=161,purchase=True,paint=True,route_points=last_int(phone,'NAVIGATION_POINTS'),waypoint_clear=True),transit=dict(visible_seated=4,alighted=4),patrol=dict(moving_samples=moving,misaligned_samples=bad),verification_scope='Targeted mechanics plus one full signal cycle; not a performance benchmark',original_project=str(original.parent/'BogotaVoxel.uproject'))
(P/'final_repair_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PROMOTED_AND_HASH_VERIFIED',len(journal))
