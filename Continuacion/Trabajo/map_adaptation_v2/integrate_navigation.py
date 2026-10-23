from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');OLD=P.parent/'traffic_gameplay_repair';PHONE='/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone.WBP_BlueprintPhone_C';STORE='/Game/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore.BP_DeliveryStore_C';ORDER='/Game/Delivery/BlueprintSchema/ST_DeliveryOrder.ST_DeliveryOrder';TXT='/Script/Engine.KismetTextLibrary';STR='/Script/Engine.KismetStringLibrary';homes=json.loads((P/'homes.json').read_text());m=json.loads((P/'manifest.json').read_text())
# Reuse the route-table runtime with the geometry-verified, current street graph.
s=(OLD/'repair_road_navigation.py').read_text();s=s.replace("assert 'isolated_repair' in root.parts","assert 'isolated_repair' in root.parts\nP=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')");exec(compile(s,'ActualStreetNavigation','exec'),globals());P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
# Publish only real, reachable residential positions. Every pickup is obtained
# from its actual shop actor and stable ID, never an offline placement plan.
b=use(AS);addvar(b,'ConfiguredHomes',E.get_array_type(vec));E.set_blueprint_variable_instance_editable(b,'ConfiguredHomes',True);assert E.compile_blueprint(b);c=unreal.get_default_object(b.generated_class());c.set_editor_property('ConfiguredHomes',[unreal.Vector(*h['point']) for h in homes]);save(b)
g=d.Graph()
for n in ['ConfiguredHomes','Homes','Stores','Routes','Delivery','CustomerNames']:g.get(n)
g.setter('Core','Delivery','entry','TargetDelivery');g.exec('entry','Core');g.setter('RealHomes','Homes','ConfiguredHomes','ConfiguredHomes');g.exec('Core','RealHomes');last='RealHomes'
for n in ['Stores','Routes']:
 g.call('Clear'+n,'Array_Clear',AL);g.link(n,n,'Clear'+n,'TargetArray');g.exec(last,'Clear'+n);last='Clear'+n
g.call('FindStores','GetAllActorsOfClass',G,ActorClass=STORE);g.exec(last,'FindStores');g.node('EachStore','foreach');g.link('FindStores','OutActors','EachStore','Array');g.link('FindStores','then','EachStore','Exec');g.node('Shop','cast',type=STORE);g.link('EachStore','Array Element','Shop','Object');sp='AsBP Delivery Store';g.call('EnsureShop','EnsureStoreBuilt',STORE);g.link('Shop',sp,'EnsureShop','self');g.link('EachStore','LoopBody','EnsureShop','execute');g.call('RememberShop','Array_Add',AL);g.link('Stores','Stores','RememberShop','TargetArray');g.link('EachStore','Array Element','RememberShop','NewItem');g.exec('EnsureShop','RememberShop');g.call('Pickup','K2_GetActorLocation',A);g.link('EachStore','Array Element','Pickup','self');g.node('EachHome','foreach');g.link('Homes','Homes','EachHome','Array');g.link('RememberShop','then','EachHome','Exec');g.node('Order','make',type=ORDER)
for n,var in [('StoreID','PointID'),('Grocery','Grocery'),('StoreKind','StoreKind'),('GoodsCost','PurchaseBudget'),('PickupName','PlaceName')]:field(g,'Shop'+var,var,('Shop',sp),STORE);g.link('Shop'+var,var,'Order',n)
g.link('Pickup','ReturnValue','Order','Pickup');g.link('EachHome','Array Element','Order','Dropoff');g.call('Distance','Vector_Distance2D',M);g.link('Pickup','ReturnValue','Distance','V1');g.link('EachHome','Array Element','Distance','V2');op(g,'Meters','Divide_DoubleDouble',('Distance','ReturnValue'),B='100');g.link('Meters','ReturnValue','Order','DistanceMeters');g.call('NameCount','Array_Length',AL);g.link('CustomerNames','CustomerNames','NameCount','TargetArray');op(g,'CustomerIndex','Percent_IntInt',('EachHome','Array Index'),('NameCount','ReturnValue'));g.call('Name','Array_Get',AL);g.link('CustomerNames','CustomerNames','Name','TargetArray');g.link('CustomerIndex','ReturnValue','Name','Index');g.call('HouseName','Concat_StrStr',STR,A='Casa de ');g.link('Name','Item','HouseName','B');g.call('HouseText','Conv_StringToText',TXT);g.link('HouseName','ReturnValue','HouseText','InString');g.link('HouseText','ReturnValue','Order','DropoffName');g.call('AddRoute','Array_Add',AL);g.link('Routes','Routes','AddRoute','TargetArray');g.link('Order','DeliveryOrder','AddRoute','NewItem');g.link('EachHome','LoopBody','AddRoute','execute');g.node('Publish','setfield',owner=C,var='ResidentialRoutes');g.link('Delivery','Delivery','Publish','self');g.link('Routes','Routes','Publish','ResidentialRoutes');g.link('EachStore','Completed','Publish','execute');g.call('Count','Array_Length',AL);g.link('Routes','Routes','Count','TargetArray');g.link('Count','ReturnValue','result','RouteCount');g.exec('Publish','result');build(b,g,'BuildRoutesFor',[dict(name='TargetDelivery',category='object',object=C),dict(name='RouteCount',category='int',out=True)]);save(b)
# The full-map projection and its click inverse use exactly the same real spans.
s=(OLD/'repair_map_data.py').read_text();s=s[:s.index('plan=json.loads')];s=s.replace('88000','104000').replace('64000','84000');exec(compile(s,'CurrentMapProjection','exec'),globals());P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');b=use(PHONE);c=unreal.get_default_object(b.generated_class());boxes=[]
for it in m['instances']:
 if 'bounds' not in it or 'Relieve' in it['source']:continue
 lo,hi=it['bounds']
 if hi[2]-lo[2]<2.3:continue
 boxes.append([lo[0]*100,-hi[1]*100,hi[0]*100,-lo[1]*100])
c.set_editor_property('MapBuildings',[unreal.Vector((q[0]+q[2])*.5,(q[1]+q[3])*.5,0) for q in boxes]);c.set_editor_property('MapExtents',[unreal.Vector2D((q[2]-q[0])*.5,(q[3]-q[1])*.5) for q in boxes]);starts=[];ends=[]
from math import dist
paths=[[(p[0]*100,-p[1]*100,0) for p in r['center']] for r in m['roads']]+[[[p[0],p[1],0] for p in r['samples']] for r in json.loads((P/'streets.json').read_text())['secondary_roads']]
for points in paths:
 chosen=[points[0]]
 for q in points[1:]:
  if dist(q,chosen[-1])>=300:chosen.append(q)
 if chosen[-1]!=points[-1]:chosen.append(points[-1])
 for a,z in zip(chosen,chosen[1:]):starts.append(unreal.Vector(*a));ends.append(unreal.Vector(*z))
c.set_editor_property('CityRoadStarts',starts);c.set_editor_property('CityRoadEnds',ends);save(b)
s=(OLD/'repair_map_data.py').read_text();s=s[s.index('# Rebuild only the input event'):s.index("unreal.log('MAP_DATA")];s=s.replace('64000','84000').replace('88000','104000');exec(compile(s,'ExactMapClickInverse','exec'),globals());P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in aa.get_all_level_actors():
 if a.get_class().get_name()=='BP_ResidentialRouteAssembler_C':a.set_editor_property('ConfiguredHomes',[unreal.Vector(*h['point']) for h in homes])
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_REAL_SHOPS_AND_HOMES_NAVIGATION_READY shops=20 homes='+str(len(homes)))
