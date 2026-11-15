from pathlib import Path
import sys
sys.argv+=['--no-render']
r=Path(__file__).parent
for name in ['build_patrol_hollow_cabin.py','build_service_voxel_models.py','rebuild_car_driver_pose.py']:
 p=r/name
 exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
