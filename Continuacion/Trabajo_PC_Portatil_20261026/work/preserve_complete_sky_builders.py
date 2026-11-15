from pathlib import Path
import shutil
p=Path('work/build_world_assets.py');shutil.copy2(p,Path('work/Backups/SkyStreetFlow_20261014/build_world_assets.py'))
s=p.read_text(encoding='utf-8-sig');a=s.index(" sky=asset('M_Sky'");z=s.index(" for name in ['SM_Bicycle'",a)
s=s[:a]+" asset('M_Sky',unreal.Material,unreal.MaterialFactoryNew())\n sky_builder=BASE/'work/build_complete_sky.py'\n exec(compile(sky_builder.read_text(encoding='utf-8-sig'),str(sky_builder),'exec'),{'__file__':str(sky_builder)})\n"+s[z:];p.write_text(s,encoding='utf-8')
p=Path('work/fix_sky_material.py');shutil.copy2(p,Path('work/Backups/SkyStreetFlow_20261014/fix_sky_material.py'))
p.write_text("from pathlib import Path\nscript=Path(__file__).with_name('build_complete_sky.py')\nexec(compile(script.read_text(encoding='utf-8-sig'),str(script),'exec'),{'__file__':str(script)})\n",encoding='utf-8')
for p in [Path('work/build_world_assets.py'),Path('work/fix_sky_material.py')]:compile(p.read_text(encoding='utf-8-sig'),str(p),'exec')
print('Sky generators now preserve the complete dynamic sky.')
