import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=d.M;A='/Script/Engine.Actor';G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';UI='/Script/UMG.WidgetBlueprintLibrary';PC='/Script/Engine.PlayerController';H='/Script/Engine.HUD';STR='/Script/Engine.KismetStringLibrary';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';C='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C'
def build(bp,g,n,params=None):
 data={'nodes':g.nodes,'links':g.links}
 if params is not None:data['parameters']=params
 assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,n,json.dumps(data))
def create(n,parent):
 path='/Game/Delivery/BlueprintGameplay/UI';bp=unreal.load_asset(path+'/'+n)
 if not bp:f=unreal.BlueprintFactory();f.set_editor_property('parent_class',parent);bp=T.create_asset(n,path,unreal.Blueprint,f)
 assert E.compile_blueprint(bp);return bp
rider=unreal.load_asset(R.rsplit('.',1)[0]);d.bp=rider
# Escape always closes the phone before opening the pause overlay.
g=d.Graph();g.get('Delivery');g.call('Paused','IsGamePaused',G);g.call('Opposite','Not_PreBool',M);g.link('Paused','ReturnValue','Opposite','A');g.call('Change','SetBlueprintPause',R);g.link('Opposite','ReturnValue','Change','Paused');g.exec('entry','Change');g.exec('Change','result')
# Define target before the caller.
p=d.Graph();p.get('Delivery');p.node('Phone','getfield',owner=C,var='PhoneOpen');p.link('Delivery','Delivery','Phone','self');p.call('PhoneAndPause','BooleanAND',M);p.link('Phone','PhoneOpen','PhoneAndPause','A');p.link('entry','Paused','PhoneAndPause','B');p.branch('CloseFirst','PhoneAndPause');p.exec('entry','CloseFirst');p.call('Close','ClosePhoneForWorld',C);p.link('Delivery','Delivery','Close','self');p.exec('CloseFirst','Close');p.exec('Close','result');p.call('Cancel','EndAction',C);p.link('Delivery','Delivery','Cancel','self');p.exec('CloseFirst','Cancel','else');p.call('Pause','SetGamePaused',G);p.link('entry','Paused','Pause','bPaused');p.exec('Cancel','Pause');p.call('PC','GetPlayerController',G,PlayerIndex='0');p.call('Mode','SetInputMode_GameOnly',UI,bFlushInput='true');p.link('PC','ReturnValue','Mode','PlayerController');p.exec('Pause','Mode');p.node('Cursor','setfield',owner=PC,var='bShowMouseCursor');p.link('entry','Paused','Cursor','bShowMouseCursor');p.link('PC','ReturnValue','Cursor','self');p.exec('Mode','Cursor');p.node('Clicks','setfield',owner=PC,var='bEnableClickEvents',defaults={'bEnableClickEvents':'true'});p.link('PC','ReturnValue','Clicks','self');p.exec('Cursor','Clicks');p.node('Widget','getfield',owner=C,var='PhoneWidget');p.link('Delivery','Delivery','Widget','self');p.call('ValidWidget','IsValid',K);p.link('Widget','PhoneWidget','ValidWidget','Object');p.branch('HasWidget','ValidWidget');p.exec('Clicks','HasWidget');p.exec('HasWidget','result','else');p.branch('Hide','entry','Paused');p.exec('HasWidget','Hide')
for n,edge,visibility in [('HidePhone','then','Hidden'),('RestorePhone','else','Visible')]:
 p.call(n,'SetVisibility','/Script/UMG.Widget',InVisibility=visibility);p.link('Widget','PhoneWidget',n,'self');p.exec('Hide',n,edge);p.exec(n,'result')
build(rider,p,'SetBlueprintPause',[{'name':'Paused','category':'bool'}]);build(rider,g,'PausePressed',[]);assert E.compile_blueprint(rider)
s=(r/'work/bind_pure_rider_inputs.py').read_text(encoding='utf-8-sig');s=s.replace("('AnimatedMount','MountPressed','')","('AnimatedMount','MountPressed',''),('Pause','PausePressed','')");s=s.replace("audit['action_edges']==13","audit['action_edges']==14");exec(compile(s,'BindPause','exec'))
# The input builder creates Pause last. Set the final action node's editor flag.
# InputActionName is protected by Unreal's Python reflection.
action_nodes=[]
for obj in unreal.ObjectIterator():
 try: classname=obj.get_class().get_name()
 except (AttributeError,TypeError):continue
 if classname=='K2Node_InputAction' and obj.get_outer().get_path_name()==rider.get_path_name()+':PlayerInput':action_nodes.append(obj)
assert action_nodes
last_node=max(action_nodes,key=lambda x:int(x.get_name().rsplit('_',1)[-1]))
last_node.set_editor_property('bExecuteWhenPaused',True)
unreal.log('PAUSE_NODE_ENABLED '+last_node.get_path_name())
assert E.compile_blueprint(rider);assert unreal.EditorAssetLibrary.save_loaded_asset(rider,only_if_is_dirty=False)
bp=create('BP_BlueprintHUD',unreal.HUD);d.bp=bp
for name,typ in [('HudPosition',E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'))),('HudSpeed',E.get_basic_type_by_name('real')),('HudReady',E.get_basic_type_by_name('bool'))]:
 if name not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,name,typ)
assert E.compile_blueprint(bp)
t=d.Graph();t.get('HudPosition');t.get('HudReady');t.call('Player','GetPlayerPawn',G,PlayerIndex='0');t.call('Valid','IsValid',K);t.link('Player','ReturnValue','Valid','Object');t.branch('Ready','Valid');t.exec('entry','Ready');t.exec('Ready','result','else');t.call('At','K2_GetActorLocation',A);t.link('Player','ReturnValue','At','self');t.call('Distance','Vector_Distance',M);t.link('At','ReturnValue','Distance','V1');t.link('HudPosition','HudPosition','Distance','V2');t.call('Dt','FMax',M,B='.0001');t.link('entry','DeltaSeconds','Dt','A');t.call('Velocity','Divide_DoubleDouble',M);t.link('Distance','ReturnValue','Velocity','A');t.link('Dt','ReturnValue','Velocity','B');t.call('Choose','SelectFloat',M,B='0');t.link('Velocity','ReturnValue','Choose','A');t.link('HudReady','HudReady','Choose','bPickA');t.setter('Speed','HudSpeed','Choose');t.exec('Ready','Speed');t.setter('Position','HudPosition','At');t.exec('Speed','Position');t.setter('Initialized','HudReady',value='true');t.exec('Position','Initialized');t.exec('Initialized','result');build(bp,t,'ReceiveTick')
g=d.Graph();g.call('Player','GetPlayerPawn',G,PlayerIndex='0');g.node('Rider','cast',type=R);g.link('Player','ReturnValue','Rider','Object');g.call('Valid','IsValid',K);g.link('Rider','AsBP Blueprint Rider','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');g.node('Data','getfield',owner=R,var='Delivery');g.link('Rider','AsBP Blueprint Rider','Data','self');g.call('CoreValid','IsValid',K);g.link('Data','Delivery','CoreValid','Object');g.branch('CoreReady','CoreValid');g.exec('Ready','CoreReady');g.exec('CoreReady','result','else');g.call('IsPaused','IsGamePaused',G);g.branch('PauseOverlay','IsPaused');g.exec('CoreReady','PauseOverlay');last='PauseOverlay';edge='else';centered=False
g.call('HalfWidth','Divide_IntInt',M,B='2');g.link('entry','SizeX','HalfWidth','A');g.call('HalfHeight','Divide_IntInt',M,B='2');g.link('entry','SizeY','HalfHeight','A')
def rect(n,x,y,w,h,color):
 global last,edge
 g.call(n,'DrawRect',H,ScreenX=str(x),ScreenY=str(y),ScreenW=str(w),ScreenH=str(h),RectColor=color);g.exec(last,n,edge);last=n;edge='then'
 if centered:
  g.call(n+'X','Add_IntInt',M,B=str(int(x)-640));g.link('HalfWidth','ReturnValue',n+'X','A');g.link(n+'X','ReturnValue',n,'ScreenX');g.call(n+'Y','Add_IntInt',M,B=str(int(y)-360));g.link('HalfHeight','ReturnValue',n+'Y','A');g.link(n+'Y','ReturnValue',n,'ScreenY')
 return n
def text(n,txt,x,y,scale=1.2,color='(R=.88,G=.96,B=.91,A=1)'):
 global last,edge
 g.call(n,'DrawText',H,Text=txt,ScreenX=str(x),ScreenY=str(y),Scale=str(scale),Font='/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font',TextColor=color);g.exec(last,n,edge);last=n;edge='then'
 if centered:
  g.call(n+'X','Add_IntInt',M,B=str(int(x)-640));g.link('HalfWidth','ReturnValue',n+'X','A');g.link(n+'X','ReturnValue',n,'ScreenX');g.call(n+'Y','Add_IntInt',M,B=str(int(y)-360));g.link('HalfHeight','ReturnValue',n+'Y','A');g.link(n+'Y','ReturnValue',n,'ScreenY')
 return n
def right(n,x):
 g.call(n,'Subtract_IntInt',M,B=str(x));g.link('entry','SizeX',n,'A');return n
right('RightEdge',300);g.node('PhoneOpen','getfield',owner=C,var='PhoneOpen');g.link('Data','Delivery','PhoneOpen','self');g.branch('PhoneClosed','PhoneOpen','PhoneOpen');g.exec(last,'PhoneClosed',edge);g.exec('PhoneClosed','result');last='PhoneClosed';edge='else'
rect('Frame',0,16,284,96,'(R=.035,G=.07,B=.085,A=.96)');g.link('RightEdge','ReturnValue','Frame','ScreenX');rect('Panel',0,20,276,88,'(R=.075,G=.15,B=.17,A=.98)');g.call('PanelX','Add_IntInt',M,B='4');g.link('RightEdge','ReturnValue','PanelX','A');g.link('PanelX','ReturnValue','Panel','ScreenX');text('Title','RUTA / BOGOTA',0,27,1.2,'(R=.19,G=.9,B=.83,A=1)');g.call('TextX','Add_IntInt',M,B='14');g.link('RightEdge','ReturnValue','TextX','A');g.link('TextX','ReturnValue','Title','ScreenX');g.node('Balance','getfield',owner=C,var='Balance');g.link('Data','Delivery','Balance','self');g.call('Money','Conv_IntToString',STR);g.link('Balance','Balance','Money','InInt');g.call('Wallet','Concat_StrStr',STR,A='$ ');g.link('Money','ReturnValue','Wallet','B');text('Cash','',0,55);g.link('TextX','ReturnValue','Cash','ScreenX');g.link('Wallet','ReturnValue','Cash','Text');g.call('Velocity','GetVelocity',A);g.link('Rider','AsBP Blueprint Rider','Velocity','self');g.call('Length','VSize',M);g.link('Velocity','ReturnValue','Length','A');g.call('Kmh','Multiply_DoubleDouble',M,B='.036');g.get('HudSpeed');g.link('HudSpeed','HudSpeed','Kmh','A');g.call('Rounded','Round',M);g.link('Kmh','ReturnValue','Rounded','A');g.call('SpeedText','Conv_IntToString',STR);g.link('Rounded','ReturnValue','SpeedText','InInt');g.call('Units','Concat_StrStr',STR,B=' km/h');g.link('SpeedText','ReturnValue','Units','A');text('Speed','',0,80,1);g.link('TextX','ReturnValue','Speed','ScreenX');g.link('Units','ReturnValue','Speed','Text');g.call('Bottom','Subtract_IntInt',M,B='90');g.link('entry','SizeY','Bottom','A');rect('ControlsPanel',280,0,670,68,'(R=.04,G=.10,B=.12,A=.94)');g.link('Bottom','ReturnValue','ControlsPanel','ScreenY');text('Controls','[TAB] Celular   [E] Accion   [F] Subir / bajar',296,0,1.1);g.call('ControlY','Add_IntInt',M,B='12');g.link('Bottom','ReturnValue','ControlY','A');g.link('ControlY','ReturnValue','Controls','ScreenY');text('Movement','[WASD] Mover   [MOUSE] Mirar / dirigir   [ESC] Pausa',296,0,1);g.call('MovementY','Add_IntInt',M,B='38');g.link('Bottom','ReturnValue','MovementY','A');g.link('MovementY','ReturnValue','Movement','ScreenY');g.exec(last,'result')
# Canvas pause remains visible while simulation is stopped.
last='PauseOverlay';edge='then';rect('Shade',0,0,10000,10000,'(R=.005,G=.02,B=.025,A=.78)');centered=True;rect('PauseFrame',400,180,480,350,'(R=.025,G=.055,B=.07,A=1)');rect('PausePanel',408,188,464,334,'(R=.075,G=.15,B=.17,A=1)');text('PausedTitle','PAUSA',440,218,2,'(R=.2,G=.9,B=.84,A=1)');text('PausedTip','[ESC] Volver a la ciudad',440,275,1.3);text('PausedHelp','Tu recorrido queda detenido.',440,320,1.1);text('PausedSave','El progreso se guarda al jugar.',440,360,1.1);text('PausedFooter','BOGOTA VOXEL',440,460,1,'(R=.9,G=.63,B=.25,A=1)');g.exec(last,'result');build(bp,g,'ReceiveDrawHUD');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
gm=unreal.load_asset('/Game/World/BlueprintWorld/BP_BlueprintGameMode');assert gm;unreal.get_default_object(gm.generated_class()).set_editor_property('hud_class',bp.generated_class());assert unreal.EditorAssetLibrary.save_loaded_asset(gm,only_if_is_dirty=False)
unreal.log('PURE_HUD_PAUSE_COMPILED')
