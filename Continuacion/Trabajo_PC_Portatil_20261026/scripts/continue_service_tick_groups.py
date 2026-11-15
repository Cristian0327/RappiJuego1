from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/traffic_gameplay_repair/implement.py'
exec(compile(p.read_text().split('# Recovery never')[0],str(p),'exec'))
p=root/'scripts/fix_service_tick_groups.py';s=p.read_text()
exec(compile(s[s.index('groups={'):],str(p),'exec'))
