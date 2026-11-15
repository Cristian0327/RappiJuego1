import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/build_pure_playable_world_integration.py').read_text(encoding='utf-8-sig');s=s[:s.index("for path in [folder+'/BP_StreetCitizen'")];s=s.replace("B='10000'","B='6000'");exec(compile(s,'CrowdLocalRadius','exec'),{})
exec(compile((r/'work/build_pure_morado_qa.py').read_text(encoding='utf-8-sig'),'MoradoQA','exec'),{})
unreal.log('PURE_RADIUS_AND_MORADO_QA_PASS')
