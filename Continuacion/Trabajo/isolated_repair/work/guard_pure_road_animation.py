import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/build_pure_rider_post_animation.py').read_text(encoding='utf-8-sig')
# The existing coordinator must not replace the road entry/driving animation with the walking AnimBP.
s=s.replace("exec(compile(s,'PureRiderPostAnimationCoordinator','exec'))", "s=s.replace(\"g.branch('Transitioning','Busy')\",\"g.node('RoadFlag','getfield',owner=R,var='RoadActive');g.link('Rider','AsBP Blueprint Rider','RoadFlag','self');g.call('EitherBusy','BooleanOR',M);g.link('Busy','ReturnValue','EitherBusy','A');g.link('RoadFlag','RoadActive','EitherBusy','B');g.branch('Transitioning','EitherBusy')\");exec(compile(s,'PureRiderPostAnimationCoordinator','exec'))")
exec(compile(s,'RoadAnimationOwnership','exec'),{})
unreal.log('PURE_ROAD_ANIMATION_OWNERSHIP_PASS')
