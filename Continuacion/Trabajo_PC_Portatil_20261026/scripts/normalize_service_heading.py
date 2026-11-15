from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/traffic_gameplay_repair/implement.py'
exec(compile(p.read_text().split('# Recovery never')[0],str(p),'exec'))
p=root/'scripts/fix_service_tick_groups.py';s=p.read_text();start=s.index("groups={");end=s.index("b=use('/Game/World/BogotaUrban/BP_BogotaServiceSignals')",start)
exec(compile(s[start:end],'PlanarServiceHeading','exec'))
unreal.log('PLANAR_SERVICE_HEADING_READY')
