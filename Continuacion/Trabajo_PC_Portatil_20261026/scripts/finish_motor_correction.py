from pathlib import Path
import unreal
root=Path(__file__).resolve().parent
for filename in ['restore_verified_crossings.py','fix_motor_service_corners.py','build_current_traffic_causes.py','prepare_current_regressions.py']:
    path=root/filename
    exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
unreal.log('MOTOR_CORRECTION_BATCH_READY')
