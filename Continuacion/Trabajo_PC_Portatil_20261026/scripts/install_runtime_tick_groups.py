from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/traffic_gameplay_repair/implement.py'
exec(compile(p.read_text().split('# Recovery never')[0],str(p),'exec'))
p=root/'scripts/fix_service_tick_groups.py';s=p.read_text()
exec(compile(s[s.index('groups={'):s.index('def configure(actor):')],str(p),'exec'))
b=use('/Game/QA/BP_AdaptationTrafficProbe');g=d.Graph();g.call('ObserveAfterMovement','SetTickGroup',A,NewTickGroup='TG_PostUpdateWork');g.exec('entry','ObserveAfterMovement');g.exec('ObserveAfterMovement','result');build(b,g,'ReceiveBeginPlay');save(b)
unreal.log('RUNTIME_SERVICE_TICK_GROUPS_READY')
