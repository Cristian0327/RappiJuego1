"""Scale the existing service budget without replacing vehicle physics or routes."""
import unreal,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent;backup=Path((R/'optimization_backup_path.txt').read_text());asset='World/BlueprintWorld/Optimization/BP_ServiceDistanceBudget.uasset';src=Path(unreal.Paths.project_content_dir())/asset;dst=backup/'Content'/asset;dst.parent.mkdir(parents=True,exist_ok=True)
if not dst.exists():shutil.copy2(src,dst)
source=(R/'work/build_service_distance_budget.py').read_text(encoding='utf-8-sig');source=source[:source.index("actors=unreal.get_editor_subsystem")]
old="g.build('ReceiveTick');assert E.compile_blueprint(bp)"
new="""
# Resolve the settings once per .25 s pass, outside the actor loop.
g.call('QualitySettings','GetGameUserSettings','/Script/Engine.GameUserSettings')
g.call('ViewQuality','GetViewDistanceQuality','/Script/Engine.GameUserSettings');g.link('QualitySettings','ReturnValue','ViewQuality','self')
g.call('QualityDistance','Multiply_IntInt',M,B='2000');g.link('ViewQuality','ReturnValue','QualityDistance','A')
g.call('Radius','Add_IntInt',M,B='4000');g.link('QualityDistance','ReturnValue','Radius','A')
g.call('RadiusSquared','Multiply_IntInt',M);g.link('Radius','ReturnValue','RadiusSquared','A');g.link('Radius','ReturnValue','RadiusSquared','B')
for node in g.nodes:
 if node['id']=='Far':node['defaults'].pop('B',None)
g.link('RadiusSquared','ReturnValue','Far','B')
for link in g.links:
 if link[0]=='entry' and link[1]=='then':link[0]='QualitySettings'
g.exec('entry','QualitySettings')
g.build('ReceiveTick');assert E.compile_blueprint(bp)
"""
assert old in source;source=source.replace(old,new.rstrip())
exec(compile(source,'QualityServiceSignificance','exec'),{'__file__':str(R/'work/build_service_distance_budget.py')})
unreal.log('QUALITY_SERVICE_SIGNIFICANCE_READY')
