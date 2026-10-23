exec(compile(__import__('pathlib').Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
r=root
assert 'isolated_repair' in root.parts, 'Navigation authoring must run in the isolated copy'
PHONE='/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone.WBP_BlueprintPhone_C';b=use(PHONE);vec=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'));addvar(b,'NavigationPoints',E.get_array_type(vec));assert E.compile_blueprint(b)
# Recompute a navigable route to the active pickup/delivery or user waypoint.
g=d.Graph()
for n in ['Delivery','NavigationPoints','MiniMap','App1_Bike_01','App1_Moto_01']:g.get(n)
g.call('Valid','IsValid',K);g.link('Delivery','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');g.call('Clear','Array_Clear',AL);g.link('NavigationPoints','NavigationPoints','Clear','TargetArray');g.exec('Ready','Clear');last='Clear'
# Parent OnPaint executes before children. Transparent map placeholders allow
# the road, route and destination drawing to remain visible.
for n in []:
 g.node(n+'Image','cast',type='/Script/UMG.Image');g.link(n,n,n+'Image','Object');g.call(n+'Tint','SetColorAndOpacity','/Script/UMG.Image',InColorAndOpacity='(R=1,G=1,B=1,A=0)');g.link(n+'Image','AsImage',n+'Tint','self');g.exec(last,n+'Tint');last=n+'Tint'
field(g,'State','State',('Delivery','Delivery'),C);op(g,'Active','GreaterEqual_ByteByte',('State','State'),B='2');field(g,'Marked','HasWaypoint',('Delivery','Delivery'),C);op(g,'HasTarget','BooleanOR',('Active','ReturnValue'),('Marked','HasWaypoint'));g.branch('Target','HasTarget');g.exec(last,'Target');g.exec('Target','result','else');g.call('Order','GetOrderTarget',C);g.link('Delivery','Delivery','Order','self');field(g,'Waypoint','Waypoint',('Delivery','Delivery'),C);g.call('Destination','SelectVector',M);g.link('Active','ReturnValue','Destination','bPickA');g.link('Order','ReturnValue','Destination','A');g.link('Waypoint','Waypoint','Destination','B');g.call('Owner','GetOwner','/Script/Engine.ActorComponent');g.link('Delivery','Delivery','Owner','self');g.call('Here','K2_GetActorLocation',A);g.link('Owner','ReturnValue','Here','self');g.call('Path','FindPathToLocationSynchronously','/Script/NavigationSystem.NavigationSystemV1');g.link('Here','ReturnValue','Path','PathStart');g.link('Destination','ReturnValue','Path','PathEnd');g.link('Owner','ReturnValue','Path','PathfindingContext');g.exec('Target','Path');g.call('HavePath','IsValid',K);g.link('Path','ReturnValue','HavePath','Object');g.branch('PathReady','HavePath');g.exec('Path','PathReady');g.exec('PathReady','result','else');field(g,'Points','PathPoints',('Path','ReturnValue'),'/Script/NavigationSystem.NavigationPath');g.setter('Keep','NavigationPoints','Points','PathPoints');g.exec('PathReady','Keep');g.exec('Keep','result');build(b,g,'UpdateNavigation',[]);save(b)
# Reuse the established curved-street paint; append the computed route before
# painting player and destination markers.
s=(P.parent/'finalize_new_map_metadata.py').read_text();chunk=s[s.index("bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone')"):s.index('# Existing point mapping')]
chunk=chunk.replace("s=s.replace(\"g.build('OnPaint')\",insert+\"\\ng.build('OnPaint')\")", "s=s.replace(\"g.build('OnPaint')\",insert+\"\\ng.build('OnPaint')\")")
# Intercept only OnPaint so setup code cannot reset the current map data.
map_cdo=unreal.get_default_object(unreal.load_asset(PHONE.split('.')[0]).generated_class())
preserved_map_data={n:list(map_cdo.get_editor_property(n)) for n in ['MapBuildings','MapExtents','MapNorthRoads','MapEastRoads','CityRoadStarts','CityRoadEnds']}
original=unreal.DeliveryEditorLibrary.build_logic_graph
def augment(bp,name,spec):
 if name=='OnPaint':
  data=json.loads(spec);g=d.Graph();g.nodes=data['nodes'];g.links=data['links'];g.get('NavigationPoints');g.node('RouteSegments','foreach');g.link('NavigationPoints','NavigationPoints','RouteSegments','Array');g.links.remove(['Buildings','Completed','PlayerDraw','execute']);g.link('Buildings','Completed','RouteSegments','Exec');g.link('RouteSegments','Completed','PlayerDraw','execute');op(g,'HasPrevious','Greater_IntInt',('RouteSegments','Array Index'),B='0');g.branch('Segment','HasPrevious');g.link('RouteSegments','LoopBody','Segment','execute');op(g,'PreviousIndex','Subtract_IntInt',('RouteSegments','Array Index'),B='1');g.call('PreviousPoint','Array_Get',AL);g.link('NavigationPoints','NavigationPoints','PreviousPoint','TargetArray');g.link('PreviousIndex','ReturnValue','PreviousPoint','Index')
  for tag,src,pin in [('RouteA','PreviousPoint','Item'),('RouteB','RouteSegments','Array Element')]:
   g.call(tag+'Norm','MapNormalizedPoint',PHONE);g.link(src,pin,tag+'Norm','Position');g.link('MapCacheCenter','MapCacheCenter',tag+'Norm','Center');g.link('Open','PhoneOpen',tag+'Norm','FullMap');g.call(tag+'XY','BreakVector2D',M);g.link(tag+'Norm','ReturnValue',tag+'XY','InVec')
   for axis,extent in [('X','Width'),('Y','Height')]:
    op(g,tag+axis+'Scale','Multiply_DoubleDouble',(tag+'XY',axis),(extent,'ReturnValue'));op(g,tag+axis,'Add_DoubleDouble',(tag+axis+'Scale','ReturnValue'),('StartXY',axis))
   g.call(tag,'MakeVector2D',M);g.link(tag+'X','ReturnValue',tag,'X');g.link(tag+'Y','ReturnValue',tag,'Y')
  # Segments outside the panel are skipped, avoiding lines over other UI.
  gates=[]
  for tag in ['RouteA','RouteB']:
   for axis in ['X','Y']:
    n=tag+axis+'Inside';g.call(n,'InRange_FloatFloat',M,Min='0',Max='1',InclusiveMin='true',InclusiveMax='true');g.link(tag+'XY',axis,n,'Value');gates.append(n)
  prev=gates[0]
  for i,n in enumerate(gates[1:]):op(g,'RouteGate'+str(i),'BooleanAND',(prev,'ReturnValue'),(n,'ReturnValue'));prev='RouteGate'+str(i)
  g.branch('RouteVisible',prev);g.exec('Segment','RouteVisible');g.call('RouteDraw','DrawLine','/Script/UMG.WidgetBlueprintLibrary',Tint='(R=.05,G=.9,B=.95,A=1)',bAntiAlias='true',Thickness='4');g.link('entry','Context','RouteDraw','Context');g.link('RouteA','ReturnValue','RouteDraw','PositionA');g.link('RouteB','ReturnValue','RouteDraw','PositionB');g.exec('RouteVisible','RouteDraw');data['nodes']=g.nodes;data['links']=g.links;spec=json.dumps(data)
 result=original(bp,name,spec)
 if name=='OnPaint':
  global overlay
  factory=unreal.WidgetBlueprintFactory();factory.set_editor_property('parent_class',unreal.UserWidget);overlay=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_NavigationOverlay') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('WBP_NavigationOverlay','/Game/Delivery/BlueprintGameplay/UI',unreal.WidgetBlueprint,factory)
  addvar(overlay,'OriginalPhone',E.get_object_reference_type(unreal.load_class(None,PHONE)));assert E.compile_blueprint(overlay)
  data=json.loads(spec);data['nodes'].append(dict(id='OriginalPhone',kind='get',var='OriginalPhone'))
  for n in data['nodes']:
   if n['id']=='OriginalPhone':continue
   if n['kind']=='get':
    n['kind']='getfield';n['owner']=PHONE;data['links'].append(['OriginalPhone','OriginalPhone',n['id'],'self'])
   if n['kind']=='call' and n.get('owner') in ['',PHONE]:
    n['owner']=PHONE;data['links'].append(['OriginalPhone','OriginalPhone',n['id'],'self'])
   if n['id']=='RootGeom':data['links'].append(['OriginalPhone','OriginalPhone','RootGeom','self'])
  assert original(overlay,'OnPaint',json.dumps(data));assert E.compile_blueprint(overlay);save(overlay)
 return result
chunk=chunk.replace("exec(compile(s,'CurvedPhoneMapPaint','exec'))", "exec(compile(s.replace('unreal.DeliveryEditorLibrary.build_logic_graph(', 'augment('),'CurvedPhoneMapPaint','exec'))")
exec(compile(chunk,'CurvedNavigationPaint','exec'),globals())
phone_asset=unreal.load_asset(PHONE.split('.')[0]);map_cdo=unreal.get_default_object(phone_asset.generated_class())
for n,v in preserved_map_data.items():map_cdo.set_editor_property(n,v)
save(phone_asset)
# The map is painted in an input-transparent foreground widget. The phone's
# opaque screen background otherwise covers its own OnPaint drawings.
b=use(PHONE);g=d.Graph();g.exec('entry','result');build(b,g,'OnPaint');save(b)
# Independent map updater retains the existing phone keyboard/mouse bindings.
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);b=unreal.load_asset('/Game/World/BogotaUrban/BP_MapNavigation') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_MapNavigation','/Game/World/BogotaUrban',unreal.Blueprint,f);d.bp=b;g=d.Graph();g.call('Pawn','GetPlayerPawn',G,PlayerIndex='0');g.node('Rider','cast',type=R);g.link('Pawn','ReturnValue','Rider','Object');field(g,'Core','Delivery',('Rider','AsBP Blueprint Rider'),R);g.call('Valid','IsValid',K);g.link('Core','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');field(g,'Phone','PhoneWidget',('Core','Delivery'),C);g.call('HavePhone','IsValid',K);g.link('Phone','PhoneWidget','HavePhone','Object');g.branch('Visible','HavePhone');g.exec('Ready','Visible');g.exec('Visible','result','else');g.call('Update','UpdateNavigation',PHONE);g.link('Phone','PhoneWidget','Update','self');g.exec('Visible','Update');g.exec('Update','result');
# OVERLAY_INIT
addvar(b,'Overlay',E.get_object_reference_type(overlay.generated_class()));assert E.compile_blueprint(b);g.get('Overlay');g.links.remove(['Update','then','result','execute']);g.call('OverlayValid','IsValid',K);g.link('Overlay','Overlay','OverlayValid','Object');g.branch('HaveOverlay','OverlayValid');g.exec('Update','HaveOverlay');g.exec('HaveOverlay','result');g.call('PC','GetPlayerController',G,PlayerIndex='0');g.call('CreateOverlay','Create','/Script/UMG.WidgetBlueprintLibrary',WidgetType=overlay.generated_class().get_path_name());g.link('PC','ReturnValue','CreateOverlay','OwningPlayer');g.exec('HaveOverlay','CreateOverlay','else');g.node('OverlayCast','cast',type=overlay.generated_class().get_path_name());g.link('CreateOverlay','ReturnValue','OverlayCast','Object');g.setter('KeepOverlay','Overlay','OverlayCast','AsWBP Navigation Overlay');g.exec('CreateOverlay','KeepOverlay');g.node('SetPhone','setfield',owner=overlay.generated_class().get_path_name(),var='OriginalPhone');g.link('Overlay','Overlay','SetPhone','self');g.link('Phone','PhoneWidget','SetPhone','OriginalPhone');g.exec('KeepOverlay','SetPhone');g.call('InputTransparent','SetVisibility','/Script/UMG.Widget',InVisibility='HitTestInvisible');g.link('Overlay','Overlay','InputTransparent','self');g.exec('SetPhone','InputTransparent');g.call('ShowOverlay','AddToViewport','/Script/UMG.UserWidget',ZOrder='20');g.link('Overlay','Overlay','ShowOverlay','self');g.exec('InputTransparent','ShowOverlay');g.exec('ShowOverlay','result')
g.node('PhoneCast','cast',type=PHONE);g.link('Phone','PhoneWidget','PhoneCast','Object')
for link in g.links:
 if link[0]=='Phone' and link[2] in ['Update','SetPhone']:link[0]='PhoneCast';link[1]='AsWBP Blueprint Phone'
build(b,g,'ReceiveTick');c=unreal.get_default_object(b.generated_class());tick=c.get_editor_property('primary_actor_tick');tick.set_editor_property('tick_interval',1.);c.set_editor_property('primary_actor_tick',tick);save(b)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in aa.get_all_level_actors():
 if a.get_class().get_name()=='BP_MapNavigation_C':aa.destroy_actor(a)
aa.spawn_actor_from_class(b.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('NAVIGATION_REPAIR_DONE')
