import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};s=(r/'work/build_pure_phone_navigation.py').read_text();exec(compile(s[:s.index('# Explicit declarations')],'PurePhoneMapSetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'});UI='/Script/UMG.WidgetBlueprintLibrary';SLATE='/Script/UMG.SlateBlueprintLibrary';A='/Script/Engine.Actor';V='/Script/CoreUObject.Vector';V2='/Script/CoreUObject.Vector2D';known=[str(x) for x in E.list_member_variable_names(bp)];geometry=unreal.get_default_object(unreal.load_class(None,'/Game/World/BlueprintWorld/BP_CityGeometry.BP_CityGeometry_C'))
for n,t in [('MapBuildings',E.get_array_type(E.get_struct_type(unreal.load_object(None,V)))),('MapExtents',E.get_array_type(E.get_struct_type(unreal.load_object(None,V2)))),('MapNorthRoads',E.get_array_type(E.get_basic_type_by_name('real'))),('MapEastRoads',E.get_array_type(E.get_basic_type_by_name('real')))]:
 if n not in known:assert E.add_member_variable(bp,n,t)
E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class())
for n,source in [('MapBuildings','BuildingCenters'),('MapExtents','BuildingExtents'),('MapNorthRoads','NorthRoads'),('MapEastRoads','EastRoads')]:c.set_editor_property(n,list(geometry.get_editor_property(source)))
class MapGraph(d.Graph):
 def build(self,n,params=None,pure=False):
  spec={'nodes':self.nodes,'links':self.links,'variables':self.variables}
  if params is not None:spec.update(parameters=params,pure=pure,const=pure)
  for x in self.nodes:
   if x.get('kind')=='call' and not x.get('owner'):x['owner']=PHONE
  assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,n,json.dumps(spec)),n
# A single widget supplies both the closed minimap and the full map page.
g=MapGraph();g.get('Delivery');g.get('Page');g.get('PreviewMoto');g.get('MiniMap');g.get('App1_Bike_01');g.get('App1_Moto_01');g.call('Valid','IsValid',K);g.link('Delivery','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');g.node('Open','getfield',owner=CORE,var='PhoneOpen');g.link('Delivery','Delivery','Open','self');g.branch('Phone','Open','PhoneOpen');g.exec('Ready','Phone');g.node('Small','return');g.link('MiniMap','MiniMap','Small','ReturnValue');g.exec('Phone','Small','else');g.call('MapPage','EqualEqual_IntInt',M,B='1');g.link('Page','Page','MapPage','A');g.branch('IsMap','MapPage');g.exec('Phone','IsMap');g.exec('IsMap','result','else');g.branch('Mode','PreviewMoto','PreviewMoto');g.exec('IsMap','Mode')
for tag,widget,edge in [('Bike','App1_Bike_01','else'),('Moto','App1_Moto_01','then')]:g.node(tag,'return');g.link(widget,widget,tag,'ReturnValue');g.exec('Mode',tag,edge)
g.build('GetActiveMapPanel',[{'name':'ReturnValue','category':'object','object':W,'out':True}],pure=True)
g=MapGraph();g.call('P','BreakVector',M);g.link('entry','Position','P','InVec');g.call('C','BreakVector',M);g.link('entry','Center','C','InVec')
for tag,axis,full,small,invert in [('X','Y',60000,11000,False),('Y','X',90000,16000,True)]:
 g.call(tag+'Delta','Subtract_DoubleDouble',M);g.link('P',axis,tag+'Delta','A');g.link('C',axis,tag+'Delta','B');g.call(tag+'Span','SelectFloat',M,A=str(full),B=str(small));g.link('entry','FullMap',tag+'Span','bPickA');g.call(tag+'Ratio','Divide_DoubleDouble',M);g.link(tag+'Delta','ReturnValue',tag+'Ratio','A');g.link(tag+'Span','ReturnValue',tag+'Ratio','B');g.call(tag+'Norm','Subtract_DoubleDouble' if invert else 'Add_DoubleDouble',M,A='.5');g.link(tag+'Ratio','ReturnValue',tag+'Norm','B')
g.call('NormalizedVector','MakeVector2D',M);g.link('XNorm','ReturnValue','NormalizedVector','X');g.link('YNorm','ReturnValue','NormalizedVector','Y');g.link('NormalizedVector','ReturnValue','result','ReturnValue');g.exec('entry','result');g.build('MapNormalizedPoint',[{'name':'Position','category':'struct','object':V},{'name':'Center','category':'struct','object':V},{'name':'FullMap','category':'bool'},{'name':'ReturnValue','category':'struct','object':V2,'out':True}],pure=True)
# Paint with standard engine drawing nodes. Thick, non-antialiased lines form voxel rectangles.
g=MapGraph();g.get('Delivery');g.get('MapBuildings');g.get('MapNorthRoads');g.get('MapEastRoads');g.call('Map','GetActiveMapPanel');g.call('Valid','IsValid',K);g.link('Map','ReturnValue','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');g.call('MapGeom','GetCachedGeometry',W);g.link('Map','ReturnValue','MapGeom','self');g.call('RootGeom','GetCachedGeometry',W);g.call('LocalSize','GetLocalSize',SLATE);g.link('MapGeom','ReturnValue','LocalSize','Geometry');g.call('MapStartAbs','LocalToAbsolute',SLATE,LocalCoordinate='(X=0,Y=0)');g.link('MapGeom','ReturnValue','MapStartAbs','Geometry');g.call('MapEndAbs','LocalToAbsolute',SLATE);g.link('MapGeom','ReturnValue','MapEndAbs','Geometry');g.link('LocalSize','ReturnValue','MapEndAbs','LocalCoordinate')
for tag,src in [('Start','MapStartAbs'),('End','MapEndAbs')]:g.call(tag,'AbsoluteToLocal',SLATE);g.link('RootGeom','ReturnValue',tag,'Geometry');g.link(src,'ReturnValue',tag,'AbsoluteCoordinate');g.call(tag+'XY','BreakVector2D',M);g.link(tag,'ReturnValue',tag+'XY','InVec')
g.call('Width','Subtract_DoubleDouble',M);g.link('EndXY','X','Width','A');g.link('StartXY','X','Width','B');g.call('Height','Subtract_DoubleDouble',M);g.link('EndXY','Y','Height','A');g.link('StartXY','Y','Height','B');g.node('Open','getfield',owner=CORE,var='PhoneOpen');g.link('Delivery','Delivery','Open','self');g.call('Owner','GetOwner','/Script/Engine.ActorComponent');g.link('Delivery','Delivery','Owner','self');g.call('Here','K2_GetActorLocation',A);g.link('Owner','ReturnValue','Here','self');g.call('Center','SelectVector',M,A='(X=0,Y=0,Z=0)');g.link('Open','PhoneOpen','Center','bPickA');g.link('Here','ReturnValue','Center','B')
def point(id,xnode,xpin,ynode,ypin):
 g.call(id,'MakeVector2D',M);g.link(xnode,xpin,id,'X');g.link(ynode,ypin,id,'Y');return id

def line(id,start,a,b,color,thickness='2',tnode=None):
 g.call(id,'DrawLine',UI,Tint=color,bAntiAlias='false',Thickness=thickness);g.link('entry','Context',id,'Context');g.link(a,'ReturnValue',id,'PositionA');g.link(b,'ReturnValue',id,'PositionB')
 if tnode:g.link(tnode,'ReturnValue',id,'Thickness')
 g.exec(start,id);return id
# Background rectangle.
g.call('HalfH','Multiply_DoubleDouble',M,B='.5');g.link('Height','ReturnValue','HalfH','A');g.call('MidY','Add_DoubleDouble',M);g.link('StartXY','Y','MidY','A');g.link('HalfH','ReturnValue','MidY','B');point('BgA','StartXY','X','MidY','ReturnValue');point('BgB','EndXY','X','MidY','ReturnValue');last='Ready'
# Roads span the clipped map area and are culled when outside a moving minimap.
lastedge='then'
for prefix,array,axis,horizontal in [('North','MapNorthRoads','X',True),('East','MapEastRoads','Y',False)]:
 g.node(prefix+'Loop','foreach');g.link(array,array,prefix+'Loop','Array');g.link(last,lastedge,prefix+'Loop','Exec');g.call(prefix+'World','MakeVector',M);g.link(prefix+'Loop','Array Element',prefix+'World',axis);g.call(prefix+'Norm','MapNormalizedPoint');g.link(prefix+'World','ReturnValue',prefix+'Norm','Position');g.link('Center','ReturnValue',prefix+'Norm','Center');g.link('Open','PhoneOpen',prefix+'Norm','FullMap');g.call(prefix+'N','BreakVector2D',M);g.link(prefix+'Norm','ReturnValue',prefix+'N','InVec');coord='Y' if horizontal else 'X';g.call(prefix+'In','InRange_FloatFloat',M,Min='0',Max='1',InclusiveMin='true',InclusiveMax='true');g.link(prefix+'N',coord,prefix+'In','Value');g.branch(prefix+'Visible',prefix+'In');g.link(prefix+'Loop','LoopBody',prefix+'Visible','execute');g.call(prefix+'Pixels','Multiply_DoubleDouble',M);g.link(prefix+'N',coord,prefix+'Pixels','A');g.link('Height' if horizontal else 'Width','ReturnValue',prefix+'Pixels','B');g.call(prefix+'At','Add_DoubleDouble',M);g.link(prefix+'Pixels','ReturnValue',prefix+'At','A');g.link('StartXY',coord,prefix+'At','B')
 if horizontal:point(prefix+'A','StartXY','X',prefix+'At','ReturnValue');point(prefix+'B','EndXY','X',prefix+'At','ReturnValue')
 else:point(prefix+'A',prefix+'At','ReturnValue','StartXY','Y');point(prefix+'B',prefix+'At','ReturnValue','EndXY','Y')
 line(prefix+'Draw',prefix+'Visible',prefix+'A',prefix+'B','(R=.38,G=.49,B=.53,A=1)',thickness='5');last=prefix+'Loop';lastedge='Completed'
# Buildings use small square markers and stay inside the panel; no native map widget remains.
g.node('Buildings','foreach');g.link('MapBuildings','MapBuildings','Buildings','Array');g.link(last,'Completed','Buildings','Exec');g.call('HouseNorm','MapNormalizedPoint');g.link('Buildings','Array Element','HouseNorm','Position');g.link('Center','ReturnValue','HouseNorm','Center');g.link('Open','PhoneOpen','HouseNorm','FullMap');g.call('HouseXY','BreakVector2D',M);g.link('HouseNorm','ReturnValue','HouseXY','InVec')
for axis in ['X','Y']:g.call('HouseIn'+axis,'InRange_FloatFloat',M,Min='.02',Max='.98',InclusiveMin='true',InclusiveMax='true');g.link('HouseXY',axis,'HouseIn'+axis,'Value')
g.call('HouseIn','BooleanAND',M);g.link('HouseInX','ReturnValue','HouseIn','A');g.link('HouseInY','ReturnValue','HouseIn','B');g.branch('HouseVisible','HouseIn');g.link('Buildings','LoopBody','HouseVisible','execute')
def mapped_point(prefix,source):
 g.call(prefix+'XY','BreakVector2D',M);g.link(source,'ReturnValue',prefix+'XY','InVec')
 for axis,extent in [('X','Width'),('Y','Height')]:
  g.call(prefix+axis+'Scale','Multiply_DoubleDouble',M);g.call(prefix+axis+'Clamp','FClamp',M,Min='.015',Max='.985');g.link(prefix+'XY',axis,prefix+axis+'Clamp','Value');g.link(prefix+axis+'Clamp','ReturnValue',prefix+axis+'Scale','A');g.link(extent,'ReturnValue',prefix+axis+'Scale','B');g.call(prefix+axis,'Add_DoubleDouble',M);g.link(prefix+axis+'Scale','ReturnValue',prefix+axis,'A');g.link('StartXY',axis,prefix+axis,'B')
 return point(prefix,prefix+'X','ReturnValue',prefix+'Y','ReturnValue')
mapped_point('House','HouseNorm');g.call('HouseEndX','Add_DoubleDouble',M,B='6');g.link('HouseX','ReturnValue','HouseEndX','A');point('HouseEnd','HouseEndX','ReturnValue','HouseY','ReturnValue');line('HouseDraw','HouseVisible','House','HouseEnd','(R=.23,G=.34,B=.39,A=1)',thickness='6')
# Player and active destination are bright voxel markers.
last='Buildings';edge='Completed'
for tag,pos,cond,color in [('Player','Here',None,'(R=.05,G=.95,B=.85,A=1)'),('Target',None,'State','(R=1,G=.64,B=.16,A=1)')]:
 g.call(tag+'Norm','MapNormalizedPoint');g.link('Center','ReturnValue',tag+'Norm','Center');g.link('Open','PhoneOpen',tag+'Norm','FullMap')
 if pos:g.link(pos,'ReturnValue',tag+'Norm','Position')
 else:
  g.call('TargetAt','GetOrderTarget',CORE);g.link('Delivery','Delivery','TargetAt','self');g.node('MapState','getfield',owner=CORE,var='State');g.link('Delivery','Delivery','MapState','self');g.call('ActiveOrder','GreaterEqual_ByteByte',M,B='2');g.link('MapState','State','ActiveOrder','A');g.node('MarkedWaypoint','getfield',owner=CORE,var='HasWaypoint');g.link('Delivery','Delivery','MarkedWaypoint','self');g.node('WaypointAt','getfield',owner=CORE,var='Waypoint');g.link('Delivery','Delivery','WaypointAt','self');g.call('TargetExists','BooleanOR',M);g.link('ActiveOrder','ReturnValue','TargetExists','A');g.link('MarkedWaypoint','HasWaypoint','TargetExists','B');g.branch('ShowTarget','TargetExists');g.exec(last,'ShowTarget',edge);g.exec('ShowTarget','result','else');last='ShowTarget';edge='then';g.call('ActualTarget','SelectVector',M);g.link('ActiveOrder','ReturnValue','ActualTarget','bPickA');g.link('TargetAt','ReturnValue','ActualTarget','A');g.link('WaypointAt','Waypoint','ActualTarget','B');g.link('ActualTarget','ReturnValue',tag+'Norm','Position')
 mapped_point(tag+'Point',tag+'Norm');g.call(tag+'EndX','Add_DoubleDouble',M,B='5');g.link(tag+'PointX','ReturnValue',tag+'EndX','A');point(tag+'End',tag+'EndX','ReturnValue',tag+'PointY','ReturnValue');g.call(tag+'Draw','DrawLine',UI,Tint=color,bAntiAlias='false',Thickness='5');g.link('entry','Context',tag+'Draw','Context');g.link(tag+'Point','ReturnValue',tag+'Draw','PositionA');g.link(tag+'End','ReturnValue',tag+'Draw','PositionB');g.exec(last,tag+'Draw',edge);last=tag+'Draw';edge='then'
g.exec(last,'result',edge);g.build('OnPaint');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);(r/'work/pure_phone_map_migration.json').write_text(json.dumps({'status':'STAGING_PAINT_COMPILED','building_markers':len(c.get_editor_property('MapBuildings')),'native_map_widget':False,'pending':['Click targeting/controller cursor','Marker culling/state guards','Full building footprints','Runtime visual verification']},indent=2));unreal.log('PURE_PHONE_MAP_PAINT_BUILD_PASS')



