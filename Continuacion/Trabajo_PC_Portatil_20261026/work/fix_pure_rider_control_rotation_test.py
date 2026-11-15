from pathlib import Path
for path in ['work/prepare_pure_rider_mount_runtime.py','work/build_pure_rider_mount_runtime.py']:
 p=Path(path);s=p.read_text(encoding='utf-8-sig');s=s.replace("g.call('AimMouse','SetControlRotation','/Script/Engine.Controller',NewRotation='(Pitch=0,Yaw=50,Roll=0)')", "g.call('AimRotation','MakeRotator',M,Yaw='50');g.call('AimMouse','SetControlRotation','/Script/Engine.Controller');g.link('AimRotation','ReturnValue','AimMouse','NewRotation')");p.write_text(s,encoding='utf-8')
