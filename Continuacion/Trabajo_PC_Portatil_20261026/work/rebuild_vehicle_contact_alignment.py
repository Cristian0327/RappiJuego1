from pathlib import Path
r=Path(__file__).parent
for name in ['rebuild_HeroBikePedal.py','rebuild_HeroMotoRide.py','rebuild_moto_rider_pose.py','validate_all_police_driver_fit.py']:
 p=r/name
 exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
