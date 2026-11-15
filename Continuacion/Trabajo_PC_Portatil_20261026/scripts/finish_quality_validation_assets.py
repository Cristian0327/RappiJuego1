from pathlib import Path
import unreal
R=Path(__file__).resolve().parent.parent
for name in ['build_optimization_qa.py','add_graphics_preview_capture.py','build_optimization_matrix.py','verify_optimization_assets.py']:
 p=R/'scripts'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
unreal.log('QUALITY_VALIDATION_ASSETS_READY')
