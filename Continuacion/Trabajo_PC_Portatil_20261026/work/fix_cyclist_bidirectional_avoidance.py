import unreal,sys,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;s=(r/'work/build_two_wheeler_citizen.py').read_text(encoding='utf-8-sig');prefix=s[:s.index('# Components and the initial grounded state.')];exec(compile(prefix,'TwoWheelerExistingSetup','exec'))
start=s.index("g=d.Graph();fields(g);op(g,'ClockNext'");end=s.index("try:g.build('ReceiveTick')",start);body=s[start:end]
# Try the opposite shoulder when the preferred shoulder is blocked. Respect red lights independently.
old="op(g,'SideStrength','Multiply_DoubleDouble',('AvoidSide','AvoidSide'),B='1.1')"
body=body.replace(old,"op(g,'SideStrength','Multiply_DoubleDouble',('AvoidSide','AvoidSide'),B='2.5')")
body=body.replace("B='130'","B='240'")
needle="op(g,'SideFree','Not_PreBool',out('SideTrace'))"
replacement="""op(g,'PreferredFree','Not_PreBool',out('SideTrace'));op(g,'OppositeVector','Multiply_VectorFloat',out('SideVector'),B='-1');op(g,'OppositeSum','Add_VectorVector',out('GoalDirection'),out('OppositeVector'));op(g,'OppositeDirection','Normal2D',out('OppositeSum'));op(g,'OppositeLook','Multiply_VectorFloat',out('OppositeDirection'),B='240');op(g,'OppositeEnd','Add_VectorVector',out('At'),out('OppositeLook'));g.call('OppositeTrace','SphereTraceSingle',S,TraceChannel='TraceTypeQuery1',bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true');g.link('At','ReturnValue','OppositeTrace','Start');g.link('OppositeEnd','ReturnValue','OppositeTrace','End');g.link('TraceRadius','ReturnValue','OppositeTrace','Radius');g.exec('SideTrace','OppositeTrace');op(g,'OppositeFree','Not_PreBool',out('OppositeTrace'));op(g,'SideFree','BooleanOR',out('PreferredFree'),out('OppositeFree'));g.call('ChosenSide','SelectVector',M);g.link('SideDirection','ReturnValue','ChosenSide','A');g.link('OppositeDirection','ReturnValue','ChosenSide','B');g.link('PreferredFree','ReturnValue','ChosenSide','bPickA');op(g,'FlipSide','Multiply_DoubleDouble',('AvoidSide','AvoidSide'),B='-1');g.call('NewSide','SelectFloat',M);g.link('AvoidSide','AvoidSide','NewSide','A');g.link('FlipSide','ReturnValue','NewSide','B');g.link('PreferredFree','ReturnValue','NewSide','bPickA');g.setter('RememberSide','AvoidSide','NewSide');g.exec('OppositeTrace','RememberSide')"""
assert needle in body;body=body.replace(needle,replacement);body=body.replace("g.link('SideDirection','ReturnValue','TravelDirection','A')","g.link('ChosenSide','ReturnValue','TravelDirection','A')");body=body.replace("g.exec('SideTrace','Walk')","g.exec('RememberSide','Walk')");body=body.replace("op(g,'Detour','BooleanAND',out('CanWalkAround'),out('Blocked'))","op(g,'Detour','BooleanAND',out('CanWalkAround'),out('Obstacle'))");body=body.replace("op(g,'Go','BooleanAND',out('CanMove'),out('NeedsMovement'))","op(g,'NoRedStop','Not_PreBool',out('RedStop'));op(g,'AllowedMove','BooleanAND',out('CanMove'),out('NoRedStop'));op(g,'Go','BooleanAND',out('AllowedMove'),out('NeedsMovement'))")
body=body.replace("g.exec('OppositeTrace','RememberSide')",'').replace("g.exec('RememberSide','Walk')","g.exec('OppositeTrace','Walk');g.exec('Walk','RememberSide')").replace("g.exec('Walk','FinishFrame')","g.exec('RememberSide','FinishFrame')")
body=body.replace(';;',';');exec(compile(body,'BidirectionalAvoidanceTick','exec'));g.node('PawnTypes','makearray',defaults={'[0]':'ObjectTypeQuery3'})
for tag in ['LookTrace','SideTrace','OppositeTrace']:
 pawn=tag+'Pawn';g.call(pawn,'SphereTraceSingleForObjects',S,bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true');g.link('PawnTypes','Array',pawn,'ObjectTypes')
 for link in list(g.links):
  if link[2]==tag and link[3] in ['Start','End','Radius']:g.link(link[0],link[1],pawn,link[3])
 for link in g.links:
  if link[0]==tag and link[1]=='then':link[0]=pawn
  if link[0]==tag and link[1]=='ReturnValue':link[0]=tag+'Occupied'
 g.exec(tag,pawn);g.call(tag+'Occupied','BooleanOR',M);g.link(tag,'ReturnValue',tag+'Occupied','A');g.link(pawn,'ReturnValue',tag+'Occupied','B')
g.build('ReceiveTick');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('CYCLIST_BIDIRECTIONAL_AVOIDANCE_COMPILED')
