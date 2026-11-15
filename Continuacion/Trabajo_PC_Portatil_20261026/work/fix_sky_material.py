from pathlib import Path
script=Path(__file__).with_name('build_complete_sky.py')
exec(compile(script.read_text(encoding='utf-8-sig'),str(script),'exec'),{'__file__':str(script)})
