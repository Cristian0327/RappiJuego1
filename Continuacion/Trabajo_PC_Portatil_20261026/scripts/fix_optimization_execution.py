from pathlib import Path
import unreal
R=Path(__file__).resolve().parent.parent
for name in ['build_shader_warmup.py','build_optimization_matrix.py','verify_optimization_assets.py']:
 p=R/'scripts'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
unreal.log('OPTIMIZATION_EXECUTION_PINS_FIXED')