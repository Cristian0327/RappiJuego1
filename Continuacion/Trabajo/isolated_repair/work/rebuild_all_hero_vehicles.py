from pathlib import Path
r=Path(__file__).parent
for name in ['rebuild_HeroBikePedal.py','rebuild_HeroMotoRide.py']:
 p=r/name
 exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
