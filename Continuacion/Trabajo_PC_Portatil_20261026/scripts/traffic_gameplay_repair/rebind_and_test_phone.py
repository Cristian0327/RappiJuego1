from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
assert 'isolated_repair' in r.parts
exec(compile((r/'work/bind_pure_phone_controls.py').read_text(encoding='utf-8-sig'),'RebindPhoneControls','exec'),{})
p=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/traffic_gameplay_repair/build_phone_actions_probe.py')
exec(compile(p.read_text(),str(p),'exec'),{})
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
