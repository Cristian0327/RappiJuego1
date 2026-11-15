import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
assert unreal.load_asset('/Game/Traffic/Detailed/SK_TransMilenioG66')
s=(r/'work/add_pure_morado_spawn.py').read_text(encoding='utf-8-sig');s=s[:s.index("s=(r/'work/build_pure_developer_codes.py')")]
s=s.replace("g.exec('Finish','Material')","g.call('G66Body','SetSkinnedAssetAndUpdate','/Script/Engine.SkinnedMeshComponent',NewMesh='/Game/Traffic/Detailed/SK_TransMilenioG66.SK_TransMilenioG66',bReinitPose='true');g.link('Body','Body','G66Body','self');g.exec('Finish','G66Body');g.exec('G66Body','Material')")
exec(compile(s,'UseAuthoredPurpleG66Mesh','exec'),{})
unreal.log('MORADO_USES_ACTUAL_G66_MODEL_PASS')
