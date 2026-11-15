"""Guard physical following when a closed route visits one road more than once."""
from pathlib import Path
import unreal

path = Path(__file__).resolve().parent / 'map_adaptation_v2/fix_shared_corridors.py'
source = path.read_text()
marker = "build(b,g,'ClearanceFromVehicle'"
# Self pins are implicit in get nodes, so read our own snapshot directly.
extra = """
g.get('PreviousPosition');g.get('PreviousYaw')
g.call('PhysicalOwnRotation','MakeRotator',M);g.link('PreviousYaw','PreviousYaw','PhysicalOwnRotation','Yaw')
g.call('PhysicalOwnForward','GetForwardVector',M);g.link('PhysicalOwnRotation','ReturnValue','PhysicalOwnForward','InRot')
op(g,'PhysicalDelta','Subtract_VectorVector',('MappedOtherPosition','PreviousPosition'),('PreviousPosition','PreviousPosition'))
op(g,'PhysicalAhead','Dot_VectorVector',('PhysicalDelta','ReturnValue'),('PhysicalOwnForward','ReturnValue'))
op(g,'PhysicalIsAhead','Greater_DoubleDouble',('PhysicalAhead','ReturnValue'),B='0')
op(g,'PhysicalAlignment','Dot_VectorVector',('PhysicalOwnForward','ReturnValue'),('OtherForward','ReturnValue'))
op(g,'PhysicalAligned','Greater_DoubleDouble',('PhysicalAlignment','ReturnValue'),B='.95')
op(g,'PhysicalFollowing','BooleanAND',('PhysicalIsAhead','ReturnValue'),('PhysicalAligned','ReturnValue'))
g.call('PhysicalFollowingGap','SelectFloat',M,B='100000000');g.link('Envelope','ReturnValue','PhysicalFollowingGap','A');g.link('PhysicalFollowing','ReturnValue','PhysicalFollowingGap','bPickA')
for original, answer in [('SafeGap','result'),('MappedSafe','MappedResult')]:
    g.links.remove([original,'ReturnValue',answer,'ReturnValue'])
    name=original+'PhysicalMin';op(g,name,'FMin',(original,'ReturnValue'),('PhysicalFollowingGap','ReturnValue'));g.link(name,'ReturnValue',answer,'ReturnValue')
"""
assert marker in source
source = source.replace(marker, extra + '\n' + marker, 1)
exec(compile(source, str(path), 'exec'), {'__file__':str(path)})
unreal.log('REPEATED_ROUTE_PHYSICAL_FOLLOWING_READY')
