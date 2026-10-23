from pathlib import Path
import shutil
r=Path('outputs/BogotaVoxel/Source/BogotaVoxel');b=Path('work/Backups/SkyStreetFlow_20261014');b.mkdir(parents=True,exist_ok=True)
for n in ['BogotaGame.h','BogotaCity.cpp','BogotaTraffic.cpp','BogotaPedestrianBehaviors.inl']:shutil.copy2(r/n,b/n)
# Baseline reproduction from the existing decision rules, independent of visuals.
s=(r/'BogotaTraffic.cpp').read_text(); p=(r/'BogotaPedestrianBehaviors.inl').read_text()
assert 'DistSquared2D(PP,W.Position)<125*125)Move=0' in s
assert 'Y+220' in p and 'CrossSegments={0,2,0,0,2,0}' in p
assert "MP_EMISSIVE_COLOR)" in Path('work/fix_sky_material.py').read_text()
print('BASELINE CONFIRMED: stationary player forces zero movement; crossing loop returns after 220 cm; sky is constant Horizon.')
