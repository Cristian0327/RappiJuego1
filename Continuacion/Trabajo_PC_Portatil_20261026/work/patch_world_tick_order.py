from pathlib import Path
p=Path('work/integrate_pure_world_presentation.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace("g.exec('UseNew','result');g.exec('UseExisting','result');g.build('ReceiveBeginPlay')", "g.get('WorldState');g.call('StateFirst','AddTickPrerequisiteActor','/Script/Engine.Actor');g.link('WorldState','WorldState','StateFirst','PrerequisiteActor');g.exec('UseNew','StateFirst');g.exec('UseExisting','StateFirst');g.exec('StateFirst','result');g.build('ReceiveBeginPlay')")
p.write_text(s,encoding='utf-8')
