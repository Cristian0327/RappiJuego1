from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');s=(P/'build_traffic_probe.py').read_text();needle="# Foreach loop output uses LoopBody rather than then."
extra="""
g.call('StopNearby','NearbyTrafficClearance',TM);g.link('ManagerCast','AsBP Traffic Manager','StopNearby','self');g.link('Each','Array Element','StopNearby','Visitor');g.call('StopJunction','JunctionClearance',TM);g.link('ManagerCast','AsBP Traffic Manager','StopJunction','self');g.link('Each','Array Element','StopJunction','Visitor');g.call('StopLeader','FollowingClearance',V);g.link('Each','Array Element','StopLeader','self');field(g,'OwnsJunction','ArcJunctionRef',('Each','Array Element'),V);g.call('JunctionName','GetObjectName',K);g.link('OwnsJunction','ArcJunctionRef','JunctionName','Object');g.links.remove(['Each','then',end,'execute']);g.exec('Each','StopNearby','LoopBody');g.exec('StopNearby','StopJunction');g.exec('StopJunction',end);line('V2CAUSE',[('Age','Age','real'),('Each','Array Index','int'),('StopNearby','ReturnValue','real'),('StopJunction','ReturnValue','real'),('StopLeader','ReturnValue','real'),('JunctionName','ReturnValue','str')],end)
"""
assert needle in s;s=s.replace(needle,extra+'\n'+needle);exec(compile(s,'DebugRealTraffic','exec'),{});unreal.log('V2_DEBUG_TRAFFIC_READY')
