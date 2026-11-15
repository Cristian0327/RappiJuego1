from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
for name in ['fix_precise_motor_tracking.py','build_current_traffic_causes.py','prepare_current_regressions.py']:
    path=root/'scripts'/name
    exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
unreal.log('PHYSICAL_TICK_ORDER_BATCH_READY')
