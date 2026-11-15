from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/fix_precise_motor_tracking.py';s=p.read_text()
exec(compile(s[:s.index("for asset in ['/Game/Traffic/Services/BP_VoxelRoadVehicle'")],str(p),'exec'))
p=root/'scripts/build_current_traffic_causes.py'
exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p)})
unreal.log('INPUT_DIAGNOSTICS_READY')
