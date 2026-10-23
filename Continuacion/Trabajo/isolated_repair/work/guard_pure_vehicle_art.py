from pathlib import Path
p=Path('work/build_pure_vehicle_art_component.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace("block=block.replace(\"g.get('Body');\",'');", "block=block.replace(\"g.get('Body');\",'');block=block.replace(\"g.link('entry','then','Loop','Exec')\",\"g.call('TargetValid','IsValid',K);g.link('entry','Target','TargetValid','Object');g.branch('HasTarget','TargetValid');g.exec('entry','HasTarget');g.exec('HasTarget','result','else');g.link('HasTarget','then','Loop','Exec')\");")
p.write_text(s,encoding='utf-8')
