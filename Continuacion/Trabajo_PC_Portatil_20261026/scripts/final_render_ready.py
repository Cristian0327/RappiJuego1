from pathlib import Path
import unreal
R=Path(__file__).resolve().parent.parent
for name in ['prepare_final_phone_visual.py','save_final_phone_map.py']:
 p=R/'scripts'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
unreal.log('FINAL_RENDER_SEQUENCE_READY')
