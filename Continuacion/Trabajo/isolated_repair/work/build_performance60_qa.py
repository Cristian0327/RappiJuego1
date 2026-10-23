from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent;s=(r/'work/build_pure_integrated_world_qa.py').read_text(encoding='utf-8-sig');s=s.replace('BP_TestPureIntegratedWorld','BP_TestPerformance60').replace('/Game/QA/PureIntegratedWorld','/Game/QA/PurePerformance60').replace("B='.0335'","B='.016667'").replace('AVERAGE_30_FPS','AVERAGE_60_FPS').replace('INTEGRATED.png','PERFORMANCE60.png');s=s.replace("B='120'","B='600'").replace("B='180'","B='600'");exec(compile(s,'Performance60QA','exec'))
