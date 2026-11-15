"""Author engine-only runtime graphics UI. No C++ runtime module is required."""
import unreal,json,sys
from pathlib import Path
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'Herramientas'));import blueprint_graph as d
if not json.loads((R/'static_lod_optimization.json').read_text()).get('retained_original_assets'):
 legacy=R/'scripts/retain_legacy_station_asset.py';exec(compile(legacy.read_text(),str(legacy),'exec'),{'__file__':str(legacy)})
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
FOLDER='/Game/World/BlueprintWorld/Optimization';M=d.M;GS='/Script/Engine.GameUserSettings';G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';U='/Script/UMG.UserWidget';W='/Script/UMG.Widget';UI='/Script/UMG.WidgetBlueprintLibrary';PC='/Script/Engine.PlayerController';STR='/Script/Engine.KismetStringLibrary';TXT=d.T
factory=unreal.WidgetBlueprintFactory();factory.set_editor_property('parent_class',unreal.UserWidget)
destination=unreal.load_asset(FOLDER+'/WBP_GraphicsSettings') or T.create_asset('WBP_GraphicsSettings',FOLDER,unreal.WidgetBlueprint,factory)
unreal.DeliveryEditorLibrary.bind_widget_delegate_graph(destination,'[]')
for graph in json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(destination))['graphs']:
 if graph['name'] not in ['UserConstructionScript','EventGraph','PhoneActions']:E.remove_function_graph(destination,graph['name'])
bp=unreal.load_asset(FOLDER+'/WBP_GraphicsLayout') or T.create_asset('WBP_GraphicsLayout',FOLDER,unreal.WidgetBlueprint,factory)
template=destination if unreal.find_object(unreal.find_object(destination,'WidgetTree'),'Root') else unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone')
assert unreal.DeliveryEditorLibrary.clone_engine_widget_designer(template,bp)
tree=unreal.find_object(bp,'WidgetTree');canvas=unreal.find_object(tree,'Root');assert canvas;canvas.clear_children()
widgets={}
aliases={}
def new(cls,name):
 obj=unreal.find_object(tree,name)
 if obj:return obj
 return unreal.new_object(cls,outer=tree,name=name)
def place(widget,x,y,w,h):
 slot=canvas.add_child_to_canvas(widget);slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(.5,.5),maximum=unreal.Vector2D(.5,.5)));slot.set_position(unreal.Vector2D(x,y));slot.set_size(unreal.Vector2D(w,h));return slot
def text(name,label,x,y,w,h,size):
 obj=new(unreal.TextBlock,name);obj.set_text(unreal.Text(label));font=obj.get_editor_property('font');font.set_editor_property('size',size);obj.set_editor_property('font',font);obj.set_color_and_opacity(unreal.SlateColor(specified_color=unreal.LinearColor(.88,.94,1,1)));place(obj,x,y,w,h);return obj
bg=new(unreal.Border,'GraphicsBackdrop');bg.set_brush_color(unreal.LinearColor(.012,.02,.035,.98));place(bg,-440,-330,880,660)
text('GraphicsTitle','BOGOTA VOXEL / GRAFICOS',-408,-307,810,40,25)
text('GraphicsHelp','F10 abre/cierra. 0 minima - 4 maxima. Cambios al pulsar APLICAR.',-408,-263,810,30,14)
def button(name,label,x,y,w):
 aliases[name]=name;obj=new(unreal.Button,name);obj.clear_children();obj.set_background_color(unreal.LinearColor(.06,.16,.23,1))
 labelobj=new(unreal.TextBlock,name+'Label');labelobj.set_text(unreal.Text(label));font=labelobj.get_editor_property('font');font.set_editor_property('size',16);labelobj.set_editor_property('font',font);obj.add_child(labelobj);place(obj,x,y,w,38);widgets[name]=obj
for i,name in enumerate(['MINIMA','BAJA','MEDIA','ALTA','MAXIMA']):button('Preset'+str(i),name,-408+i*164,-218,154)
text('GraphicsCustom','PERSONALIZADA / pulsa una opcion para cambiarla',-408,-164,810,28,16)
groups=[('View','Distancia','ViewDistance'),('Shadow','Sombras','Shadow'),('Texture','Texturas','Texture'),('AA','Antialiasing','AntiAliasing'),('Effects','Efectos','VisualEffect'),('Post','Posprocesado','PostProcessing'),('Foliage','Vegetacion','Foliage'),('Shading','Materiales','Shading'),('Reflection','Reflejos','Reflection')]
extras=[('Resolution','Resolucion interna'),('FPS','Limite FPS'),('VSync','VSync'),('Dynamic','Priorizar 60 FPS'),('Output','Pantalla: 720p / nativa'),('Window','Ventana / sin bordes')]
for i,(name,label,*_) in enumerate(groups+extras):button(name,label,-408+(i%2)*414,-124+(i//2)*43,400)
text('GraphicsStatus','Detalle cercano original. La distancia adapta el coste del mundo.',-408,220,810,28,14)
button('Apply','APLICAR Y GUARDAR',-408,271,400);button('Close','VOLVER AL JUEGO',6,271,400)
assert unreal.DeliveryEditorLibrary.clone_engine_widget_designer(bp,destination)
bp=destination
c=unreal.get_default_object(bp.generated_class());c.set_editor_property('is_focusable',True)
P=bp.generated_class().get_path_name();reports=[]
def build(g,name,params=None,override=False):
 if any(n['id']=='Settings' for n in g.nodes):
  for link in g.links:
   if link[0]=='entry' and link[1]=='then':link[0]='Settings'
  g.exec('entry','Settings')
 spec=dict(nodes=g.nodes,links=g.links)
 if not override:spec['parameters']=params or []
 assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps(spec)),name
 reports.append(name)
def settings(g):g.call('Settings','GetGameUserSettings',GS)
def callsetting(g,id,fn,**defaults):
 if fn=='ApplyNonResolutionSettings':fn='ApplySettings';defaults={'bCheckForCommandLineOverrides':'false'}
 g.call(id,fn,GS,**defaults);g.link('Settings','ReturnValue',id,'self')
def stub(name):g=d.Graph();g.exec('entry','result');build(g,name)
for name in ['RefreshLabels','ApplyGraphics','CloseGraphics']:stub(name)
g=d.Graph();settings(g);callsetting(g,'Priority','IsDynamicResolutionEnabled');g.branch('Prefer60','Priority');g.exec('entry','Prefer60');callsetting(g,'CompatibleScale','SetResolutionScaleValueEx',NewScaleValue='55');g.exec('Prefer60','CompatibleScale');callsetting(g,'Apply','ApplyNonResolutionSettings');g.exec('CompatibleScale','Apply');g.exec('Prefer60','Apply','else');callsetting(g,'Save','SaveSettings');g.exec('Apply','Save');g.call('Refresh','RefreshLabels',P);g.exec('Save','Refresh');g.exec('Refresh','result');build(g,'ApplyGraphics')
bindings=[]
for i,scale in enumerate([55,70,85,100,100]):
 g=d.Graph();settings(g);callsetting(g,'Preset','SetOverallScalabilityLevel',Value=str(i));g.exec('entry','Preset');callsetting(g,'Scale','SetResolutionScaleValueEx',NewScaleValue=str(scale));callsetting(g,'Manual','SetDynamicResolutionEnabled',bEnable='false');g.exec('Preset','Manual');g.exec('Manual','Scale');g.call('Refresh','RefreshLabels',P);g.exec('Scale','Refresh');g.exec('Refresh','result');fn='ChoosePreset'+str(i);build(g,fn);bindings.append(dict(widget='Preset'+str(i),delegate='OnClicked',function=fn))
for name,label,method in groups:
 g=d.Graph();settings(g);callsetting(g,'Get','Get'+method+'Quality');g.call('Next','Add_IntInt',M,B='1');g.link('Get','ReturnValue','Next','A');g.call('Wrap','Percent_IntInt',M,B='5');g.link('Next','ReturnValue','Wrap','A');callsetting(g,'Set','Set'+method+'Quality');g.link('Wrap','ReturnValue','Set','Value');g.exec('entry','Set');g.call('Refresh','RefreshLabels',P);g.exec('Set','Refresh');g.exec('Refresh','result');fn='Cycle'+name;build(g,fn);bindings.append(dict(widget=name,delegate='OnClicked',function=fn))
# Resolution changes do not change the desktop/window size, so no risky display transition.
g=d.Graph();settings(g);callsetting(g,'Current','GetResolutionScaleInformationEx');g.call('Next','Add_DoubleDouble',M,B='15');g.link('Current','CurrentScaleValue','Next','A');g.call('Over','Greater_DoubleDouble',M,B='100');g.link('Next','ReturnValue','Over','A');g.call('Value','SelectFloat',M,A='55');g.link('Next','ReturnValue','Value','B');g.link('Over','ReturnValue','Value','bPickA');callsetting(g,'Set','SetResolutionScaleValueEx');g.link('Value','ReturnValue','Set','NewScaleValue');callsetting(g,'Manual','SetDynamicResolutionEnabled',bEnable='false');g.exec('entry','Manual');g.exec('Manual','Set');g.call('Refresh','RefreshLabels',P);g.exec('Set','Refresh');g.exec('Refresh','result');build(g,'CycleResolution');bindings.append(dict(widget='Resolution',delegate='OnClicked',function='CycleResolution'))
g=d.Graph();settings(g);callsetting(g,'Get','GetFrameRateLimit');g.call('Under30','Less_DoubleDouble',M,B='29');g.link('Get','ReturnValue','Under30','A');g.branch('A','Under30');g.exec('entry','A');callsetting(g,'Set30','SetFrameRateLimit',NewLimit='30');g.exec('A','Set30');g.call('Under60','Less_DoubleDouble',M,B='59');g.link('Get','ReturnValue','Under60','A');g.branch('B','Under60');g.exec('A','B','else');callsetting(g,'Set60','SetFrameRateLimit',NewLimit='60');g.exec('B','Set60');g.call('Under120','Less_DoubleDouble',M,B='119');g.link('Get','ReturnValue','Under120','A');g.branch('C','Under120');g.exec('B','C','else');callsetting(g,'Set120','SetFrameRateLimit',NewLimit='120');callsetting(g,'SetUnlimited','SetFrameRateLimit',NewLimit='0');g.exec('C','Set120');g.exec('C','SetUnlimited','else');g.call('Refresh','RefreshLabels',P)
for n in ['Set30','Set60','Set120','SetUnlimited']:g.exec(n,'Refresh')
g.exec('Refresh','result');build(g,'CycleFPS');bindings.append(dict(widget='FPS',delegate='OnClicked',function='CycleFPS'))
g=d.Graph();settings(g);callsetting(g,'Get','IsVSyncEnabled');g.call('Flip','Not_PreBool',M);g.link('Get','ReturnValue','Flip','A');callsetting(g,'Set','SetVSyncEnabled');g.link('Flip','ReturnValue','Set','bEnable');g.exec('entry','Set');g.call('Refresh','RefreshLabels',P);g.exec('Set','Refresh');g.exec('Refresh','result');build(g,'CycleVSync');bindings.append(dict(widget='VSync',delegate='OnClicked',function='CycleVSync'))
# Label refresh uses GetWidgetFromName, keeping designer and graph loosely coupled.
g=d.Graph();settings(g);callsetting(g,'Current','GetScreenResolution');g.node('XY','break',type='/Script/CoreUObject.IntPoint');g.link('Current','ReturnValue','XY','IntPoint');g.call('Is720','EqualEqual_IntInt',M,B='1280');g.link('XY','X','Is720','A');g.branch('Native','Is720');g.exec('entry','Native');callsetting(g,'Desktop','GetDesktopResolution');callsetting(g,'UseNative','SetScreenResolution');g.link('Desktop','ReturnValue','UseNative','Resolution');g.exec('Native','UseNative');callsetting(g,'Use720','SetScreenResolution',Resolution='(X=1280,Y=720)');g.exec('Native','Use720','else');g.call('Refresh','RefreshLabels',P);g.exec('UseNative','Refresh');g.exec('Use720','Refresh');g.exec('Refresh','result');build(g,'CycleOutput');bindings.append(dict(widget='Output',delegate='OnClicked',function='CycleOutput'))
g=d.Graph();settings(g);callsetting(g,'Mode','GetFullscreenMode');g.call('Windowed','EqualEqual_ByteByte',M,B='2');g.link('Mode','ReturnValue','Windowed','A');g.branch('Choose','Windowed');g.exec('entry','Choose');callsetting(g,'Borderless','SetFullscreenMode',InFullscreenMode='WindowedFullscreen');callsetting(g,'WindowedMode','SetFullscreenMode',InFullscreenMode='Windowed');g.exec('Choose','Borderless');g.exec('Choose','WindowedMode','else');g.call('Refresh','RefreshLabels',P);g.exec('Borderless','Refresh');g.exec('WindowedMode','Refresh');g.exec('Refresh','result');build(g,'CycleWindow');bindings.append(dict(widget='Window',delegate='OnClicked',function='CycleWindow'))
g=d.Graph();settings(g);callsetting(g,'Get','IsDynamicResolutionEnabled');g.call('Flip','Not_PreBool',M);g.link('Get','ReturnValue','Flip','A');callsetting(g,'Set','SetDynamicResolutionEnabled');g.link('Flip','ReturnValue','Set','bEnable');g.exec('entry','Set');callsetting(g,'Target60','SetFrameRateLimit',NewLimit='60');g.exec('Set','Target60');g.call('Refresh','RefreshLabels',P);g.exec('Target60','Refresh');g.exec('Refresh','result');build(g,'CycleDynamic');bindings.append(dict(widget='Dynamic',delegate='OnClicked',function='CycleDynamic'))
g=d.Graph();settings(g);last='entry'
labeldata=[]
for name,label,method in groups:
 callsetting(g,'Get'+name,'Get'+method+'Quality');g.call('Num'+name,'Conv_IntToString',STR);g.link('Get'+name,'ReturnValue','Num'+name,'InInt');labeldata.append((name,label+': ','Num'+name,'ReturnValue'))
callsetting(g,'GetResolution','GetResolutionScaleInformationEx');g.call('ResolutionInt','FTrunc',M);g.link('GetResolution','CurrentScaleValue','ResolutionInt','A');g.call('NumResolution','Conv_IntToString',STR);g.link('ResolutionInt','ReturnValue','NumResolution','InInt');labeldata.append(('Resolution','Resolucion interna %: ','NumResolution','ReturnValue'))
callsetting(g,'GetFPS','GetFrameRateLimit');g.call('FPSInt','FTrunc',M);g.link('GetFPS','ReturnValue','FPSInt','A');g.call('NumFPS','Conv_IntToString',STR);g.link('FPSInt','ReturnValue','NumFPS','InInt');labeldata.append(('FPS','Limite FPS (0 libre): ','NumFPS','ReturnValue'))
callsetting(g,'GetVSync','IsVSyncEnabled');g.call('VSyncInt','Conv_BoolToInt',M);g.link('GetVSync','ReturnValue','VSyncInt','InBool');g.call('NumVSync','Conv_IntToString',STR);g.link('VSyncInt','ReturnValue','NumVSync','InInt');labeldata.append(('VSync','VSync (0 no / 1 si): ','NumVSync','ReturnValue'))
callsetting(g,'GetDynamic','IsDynamicResolutionEnabled');g.call('DynamicInt','Conv_BoolToInt',M);g.link('GetDynamic','ReturnValue','DynamicInt','InBool');g.call('NumDynamic','Conv_IntToString',STR);g.link('DynamicInt','ReturnValue','NumDynamic','InInt');labeldata.append(('Dynamic','Priorizar 60 FPS (0 no / 1 si): ','NumDynamic','ReturnValue'))
callsetting(g,'OutputRead','GetScreenResolution');g.node('OutputXY','break',type='/Script/CoreUObject.IntPoint');g.link('OutputRead','ReturnValue','OutputXY','IntPoint')
for axis in ['X','Y']:g.call('Output'+axis,'Conv_IntToString',STR);g.link('OutputXY',axis,'Output'+axis,'InInt')
g.call('OutputWidth','Concat_StrStr',STR,B=' x ');g.link('OutputX','ReturnValue','OutputWidth','A');g.call('OutputSize','Concat_StrStr',STR);g.link('OutputWidth','ReturnValue','OutputSize','A');g.link('OutputY','ReturnValue','OutputSize','B');labeldata.append(('Output','Pantalla: ','OutputSize','ReturnValue'))
callsetting(g,'WindowMode','GetFullscreenMode');g.call('ModeIsWindowed','EqualEqual_ByteByte',M,B='2');g.link('WindowMode','ReturnValue','ModeIsWindowed','A');g.call('WindowName','SelectString',M,A='Ventana',B='Sin bordes');g.link('ModeIsWindowed','ReturnValue','WindowName','bPickA');labeldata.append(('Window','Modo: ','WindowName','ReturnValue'))
for name,prefix,source,pin in labeldata:
 g.get(name+'Label');g.call('Label'+name,'Concat_StrStr',STR,A=prefix);g.link(source,pin,'Label'+name,'B');g.call('Text'+name,'Conv_StringToText',TXT);g.link('Label'+name,'ReturnValue','Text'+name,'InString');g.call('Set'+name,'SetText','/Script/UMG.TextBlock');g.link(name+'Label',name+'Label','Set'+name,'self');g.link('Text'+name,'ReturnValue','Set'+name,'InText');g.exec(last,'Set'+name);last='Set'+name
callsetting(g,'ProfileRead','GetOverallScalabilityLevel');previous=None
for i,label in enumerate(['MINIMA','BAJA','MEDIA','ALTA','MAXIMA']):
 tag='Profile'+str(i);g.call(tag+'Matches','EqualEqual_IntInt',M,B=str(i));g.link('ProfileRead','ReturnValue',tag+'Matches','A');g.call(tag,'SelectString',M,A=label,**({'B':'PERSONALIZADA'} if previous is None else {}));g.link(tag+'Matches','ReturnValue',tag,'bPickA')
 if previous:g.link(previous,'ReturnValue',tag,'B')
 previous=tag
g.get('GraphicsCustom');g.call('ProfileLabel','Concat_StrStr',STR,A='PERFIL: ');g.link(previous,'ReturnValue','ProfileLabel','B');g.call('ProfileText','Conv_StringToText',TXT);g.link('ProfileLabel','ReturnValue','ProfileText','InString');g.call('SetProfile','SetText','/Script/UMG.TextBlock');g.link('GraphicsCustom','GraphicsCustom','SetProfile','self');g.link('ProfileText','ReturnValue','SetProfile','InText');g.exec(last,'SetProfile');g.exec('SetProfile','result');build(g,'RefreshLabels')
g=d.Graph();g.call('Controller','GetPlayerController',G,PlayerIndex='0');g.call('Input','SetInputMode_GameOnly',UI,bFlushInput='true');g.link('Controller','ReturnValue','Input','PlayerController');g.call('Resume','SetGamePaused',G,bPaused='false');g.exec('entry','Resume');g.exec('Resume','Input');g.node('Cursor','setfield',owner=PC,var='bShowMouseCursor',defaults={'bShowMouseCursor':'false'});g.link('Controller','ReturnValue','Cursor','self');g.exec('Input','Cursor');g.call('Remove','RemoveFromParent',W);g.exec('Cursor','Remove');g.exec('Remove','result');build(g,'CloseGraphics')
for name,fn in [('Apply','ApplyGraphics'),('Close','CloseGraphics')]:bindings.append(dict(widget=name,delegate='OnClicked',function=fn))
for binding in bindings:binding['widget']=aliases[binding['widget']]
assert unreal.DeliveryEditorLibrary.bind_widget_delegate_graph(bp,json.dumps(bindings))
g=d.Graph();g.call('Refresh','RefreshLabels',P);g.exec('entry','Refresh');g.exec('Refresh','result');build(g,'Construct',override=True)
g=d.Graph();g.call('Key','GetKey','/Script/Engine.KismetInputLibrary');g.link('entry','InKeyEvent','Key','Input');last='entry';edge='then'
g.call('Handled','Handled',UI);g.call('Unhandled','Unhandled',UI);g.link('Unhandled','ReturnValue','result','ReturnValue');g.node('Done','return');g.link('Handled','ReturnValue','Done','ReturnValue')
for i,key in enumerate(['F10','Escape']):
 n='Key'+str(i);g.call(n,'EqualEqual_KeyKey','/Script/Engine.KismetInputLibrary',B=key);g.link('Key','ReturnValue',n,'A');g.branch(n+'Check',n);g.exec(last,n+'Check',edge);g.call(n+'Close','CloseGraphics',P);g.exec(n+'Check',n+'Close');g.exec(n+'Close','Done');last=n+'Check';edge='else'
g.exec(last,'result',edge);build(g,'OnPreviewKeyDown',override=True)
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
widgetbp=bp;factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
bp=unreal.load_asset(FOLDER+'/BP_GraphicsSettings') or T.create_asset('BP_GraphicsSettings',FOLDER,unreal.Blueprint,factory)
if 'Menu' not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,'Menu',E.get_object_reference_type(widgetbp.generated_class()))
assert E.compile_blueprint(bp);ACTOR=bp.generated_class().get_path_name()
g=d.Graph();settings(g);callsetting(g,'Load','LoadSettings',bForceReload='false');g.exec('entry','Load');callsetting(g,'Apply','ApplyNonResolutionSettings');callsetting(g,'Priority','IsDynamicResolutionEnabled');g.branch('Prefer60','Priority');g.exec('Load','Prefer60');callsetting(g,'CompatibleScale','SetResolutionScaleValueEx',NewScaleValue='55');g.exec('Prefer60','CompatibleScale');g.exec('CompatibleScale','Apply');g.exec('Prefer60','Apply','else');g.exec('Apply','result');build(g,'ReceiveBeginPlay',override=True)
g=d.Graph();g.get('Menu');g.call('Valid','IsValid',K);g.link('Menu','Menu','Valid','Object');g.branch('Have','Valid');g.exec('entry','Have');g.call('InViewport','IsInViewport',U);g.link('Menu','Menu','InViewport','self');g.branch('Open','InViewport');g.exec('Have','Open');g.call('Close','CloseGraphics',P);g.link('Menu','Menu','Close','self');g.exec('Open','Close');g.exec('Close','result');g.call('Controller','GetPlayerController',G,PlayerIndex='0');g.call('Create','Create',UI,WidgetType=P);g.link('Controller','ReturnValue','Create','OwningPlayer');g.exec('Have','Create','else');g.exec('Open','Create','else');g.node('Cast','cast',type=P);g.link('Create','ReturnValue','Cast','Object');g.setter('SaveMenu','Menu','Cast','AsWBP Graphics Settings');g.exec('Create','SaveMenu');g.call('Add','AddToViewport',U,ZOrder='100');g.link('Menu','Menu','Add','self');g.exec('SaveMenu','Add');g.call('Input','SetInputMode_UIOnlyEx',UI,InMouseLockMode='DoNotLock',bFlushInput='true');g.link('Controller','ReturnValue','Input','PlayerController');g.link('Menu','Menu','Input','InWidgetToFocus');g.call('Pause','SetGamePaused',G,bPaused='true');g.exec('Add','Pause');g.exec('Pause','Input');g.node('Cursor','setfield',owner=PC,var='bShowMouseCursor',defaults={'bShowMouseCursor':'true'});g.link('Controller','ReturnValue','Cursor','self');g.exec('Input','Cursor');g.exec('Cursor','result');build(g,'ToggleGraphics')
assert unreal.DeliveryEditorLibrary.build_blueprint_input_graph(bp,json.dumps([dict(kind='action',name='GraphicsMenu',pressed='ToggleGraphics')]))
c=unreal.get_default_object(bp.generated_class());c.set_editor_property('auto_receive_input',unreal.AutoReceiveInput.PLAYER0);tick=c.get_editor_property('primary_actor_tick');tick.set_editor_property('start_with_tick_enabled',False);c.set_editor_property('primary_actor_tick',tick);assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
(R/'graphics_settings_build.json').write_text(json.dumps(dict(status='compiled',widget=widgetbp.get_path_name(),actor=bp.get_path_name(),functions=reports,bindings=bindings),indent=2))
unreal.log('GRAPHICS_SETTINGS_READY')



