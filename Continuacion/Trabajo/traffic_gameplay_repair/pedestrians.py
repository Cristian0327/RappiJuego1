from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'RepairHelpers','exec'))
backup('/Game/World/BlueprintWorld/Crowd/BP_CrosswalkCitizen');old=d.Graph.build
# Protected crossing admission lasts six seconds, leaving sixteen seconds to clear.
def crossing_build(self,name):
 if name=='ReceiveTick':
  g=self;g.node('RoadObjects','makearray',defaults={'[0]':'ObjectTypeQuery2'});op(g,'GoalAtChest','Add_VectorVector',('Goal','Item'),B='(X=0,Y=0,Z=90)');g.call('RoadClear','SphereTraceSingleForObjects',K,Radius='70',bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true');g.link('At','ReturnValue','RoadClear','Start');g.link('GoalAtChest','ReturnValue','RoadClear','End');g.link('RoadObjects','Array','RoadClear','ObjectTypes')
  for l in g.links:
   if l[2:] == ['CanWalk','execute']:l[2]='RoadClear'
  g.exec('RoadClear','CanWalk');op(g,'NoRoadTraffic','Not_PreBool',('RoadClear','ReturnValue'));op(g,'AdmissionSafe','BooleanAND',('Window','ReturnValue'),('NoRoadTraffic','ReturnValue'))
  for l in g.links:
   if l==['Window','ReturnValue','Already','A']:l[0]='AdmissionSafe'
 return old(self,name)
d.Graph.build=crossing_build
try:
 s=(P.parent/'urban_refresh/fix_physical_crossings.py').read_text().split('# Filter fine paving')[0];s=s.replace("Divisor='66'","Divisor='110'").replace("B='46'","B='88'").replace("B='47.5'","B='94'");exec(compile(s,'CrossingAdmissionSafety','exec'),{})
finally:d.Graph.build=old
# Eliminate the old grid timers in lifecycle bicycles/motorcycles too, retaining animation graphs.
backup('/Game/Traffic/Services/BP_TwoWheelerCitizen');old=d.Graph.build
def bike_build(self,name):
 if name=='ReceiveTick' and d.bp.get_name()=='BP_TwoWheelerCitizen':
  g=self
  for l in list(g.links):
   if l[2]=='AtRed' and l[3] in ['A','B']:g.links.remove(l)
  for n in g.nodes:
   if n['id']=='AtRed':n['defaults']={'A':'false','B':'false'}
 return old(self,name)
d.Graph.build=bike_build
try:
 s=(root/'work/guard_motorcycles_road.py').read_text();s=s[:s.index("bp=unreal.load_asset(P.rsplit",s.index("finally:d.Graph.build"))];s=s.replace("guard=op('Constrain','BooleanAND',road,no_bike)","guard=op('Constrain','BooleanAND',road,road)");exec(compile(s,'RoadCycleNoLegacySignals','exec'),{})
finally:d.Graph.build=old
unreal.log('PROTECTED_PEDESTRIAN_CROSSINGS_AND_NO_LEGACY_RIDER_GRID')
