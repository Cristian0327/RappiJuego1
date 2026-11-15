from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent

def run(path, source=None):
    source=path.read_text() if source is None else source
    exec(compile(source,str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})

inspect=root/'scripts/inspect_v14_following.py'
run(inspect,inspect.read_text().replace("inspect('v14')","inspect('v14_before_precise')"))
run(root/'scripts/fix_precise_motor_tracking.py')
old=root.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
helpers=root/'scripts/traffic_gameplay_repair/implement.py'
prefix="exec(compile(Path("+repr(str(helpers))+").read_text().split('# Recovery never')[0],'helpers','exec'))"
path=old/'fix_swept_clearance.py';lines=path.read_text().splitlines();lines[1]=prefix
source='\n'.join(lines).replace("('Length','Forward','60')","('Length','Forward','20')")
assert source!='\n'.join(lines);run(path,source)
path=old/'verify_swept_math.py';lines=path.read_text().splitlines();lines[1]=prefix
lines[3]="P=Path("+repr(str(root))+");import random"
source='\n'.join(lines).replace('(hl+60)','(hl+20)').replace('(ol+60)','(ol+20)').replace('swept_math_verification.json','swept_math_v15_verification.json')
run(path,source)
run(inspect,inspect.read_text().replace("inspect('v14')","inspect('v14_after_precise')"))
run(root/'scripts/build_current_traffic_causes.py')
run(root/'scripts/prepare_current_regressions.py')
unreal.log('PRECISE_TRACKING_BATCH_READY')
