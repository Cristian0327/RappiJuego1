"""Reduce near AI/animation work at lower quality, retaining the far simulation."""
import unreal,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent;backup=Path((R/'optimization_backup_path.txt').read_text());asset='World/BlueprintWorld/Crowd/BP_CrowdVisibility.uasset';src=Path(unreal.Paths.project_content_dir())/asset;dst=backup/'Content'/asset;dst.parent.mkdir(parents=True,exist_ok=True)
if not dst.exists():shutil.copy2(src,dst)
source=(R/'work/build_pure_playable_world_integration.py').read_text(encoding='utf-8-sig');source=source[:source.index("for path in [folder+'/BP_StreetCitizen']")]
source=source.replace('list(range(64))','list(range(32))').replace("'tick_interval',.1","'tick_interval',.05").replace("B='64'","B='32'")
old="g.build('ReceiveTick');assert E.compile_blueprint(bp)"
new="""
g.call('QualitySettings','GetGameUserSettings','/Script/Engine.GameUserSettings')
g.call('ViewQuality','GetViewDistanceQuality','/Script/Engine.GameUserSettings');g.link('QualitySettings','ReturnValue','ViewQuality','self')
g.call('QualityDistance','Multiply_IntInt',M,B='1250');g.link('ViewQuality','ReturnValue','QualityDistance','A')
g.call('Radius','Add_IntInt',M,B='3500');g.link('QualityDistance','ReturnValue','Radius','A')
for node in g.nodes:
 if node['id']=='Far':node['defaults'].pop('B',None)
g.link('Radius','ReturnValue','Far','B')
for link in g.links:
 if link[0]=='entry' and link[1]=='then':link[0]='QualitySettings'
g.exec('entry','QualitySettings')
# Only notify visibility changes; retain SetFarMode's own interaction safeguards.
g.links.remove(['Each','LoopBody','Hide','execute'])
g.node('WasHidden','getfield',owner=A,var='bHidden');g.link('Citizen','Item','WasHidden','self')
g.call('VisibilityChanged','NotEqual_BoolBool',M);g.link('WasHidden','bHidden','VisibilityChanged','A');g.link('HideForDistanceOrRide','ReturnValue','VisibilityChanged','B')
g.branch('ApplyVisibility','VisibilityChanged');g.link('Each','LoopBody','ApplyVisibility','execute');g.exec('ApplyVisibility','Hide');g.exec('ApplyVisibility','ApplyInterval','else')
g.build('ReceiveTick');assert E.compile_blueprint(bp)
"""
assert old in source;source=source.replace(old,new.rstrip())
exec(compile(source,'QualityCrowdSignificance','exec'),{'__file__':str(R/'work/build_pure_playable_world_integration.py')})
unreal.log('QUALITY_CROWD_SIGNIFICANCE_READY')
