import unreal
from pathlib import Path
R=Path(__file__).resolve().parent.parent
for name in ['build_graphics_settings.py','build_optimization_qa.py','build_shader_warmup.py']:
 p=R/'scripts'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
unreal.log('GRAPHICS_COMPATIBILITY_READY')
