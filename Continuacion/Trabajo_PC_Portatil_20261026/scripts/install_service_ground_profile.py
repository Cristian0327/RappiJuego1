"""Restore normal grounded floor detection instead of the legacy 5 cm step profile."""
from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/install_service_physical_guard.py';exec(compile(p.read_text(),str(p),'exec'))
link=['GuardAfterControl','then','MovementAfterGuard','execute'];assert link in g.links;g.links.remove(link)
g.node('GroundMovementCast','cast',type=CM);g.link('ControlledMovement','ReturnValue','GroundMovementCast','Object')
g.node('RestoreGroundStep','setfield',owner=CM,var='MaxStepHeight',defaults={'MaxStepHeight':'30'});g.link('GroundMovementCast','AsCharacter Movement Component','RestoreGroundStep','self')
g.call('RestoreGroundSlope','SetWalkableFloorAngle',CM,InWalkableFloorAngle='45');g.link('GroundMovementCast','AsCharacter Movement Component','RestoreGroundSlope','self')
g.call('InitializeGroundMode','SetMovementMode',CM,NewMovementMode='MOVE_Walking');g.link('GroundMovementCast','AsCharacter Movement Component','InitializeGroundMode','self')
g.exec('GuardAfterControl','RestoreGroundStep');g.exec('RestoreGroundStep','RestoreGroundSlope');g.exec('RestoreGroundSlope','InitializeGroundMode');g.exec('InitializeGroundMode','MovementAfterGuard');build(b,g,'EnsureServiceProxies',[]);save(b)
unreal.log('SERVICE_GROUND_PROFILE_READY')

