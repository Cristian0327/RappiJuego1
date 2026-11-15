"""Preserve HUD polling; rebuild the canvas only when open state/viewport changes."""
import unreal,json,sys,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;P='/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone';CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';K='/Script/Engine.KismetSystemLibrary';M=d.M;GS='/Script/Engine.GameplayStatics'
src=Path(unreal.Paths.project_content_dir())/'Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone.uasset';backup=R/'AdversarialQA_20261026'/'before';backup.mkdir(parents=True,exist_ok=True)
if not (backup/src.name).exists():shutil.copy2(src,backup/src.name)
b=unreal.load_asset(P);known=[str(x) for x in E.list_member_variable_names(b)]
for name in ['UIViewportX','UIViewportY','LayoutRebuildCount','UILayoutPage']:
 if name not in known:assert E.add_member_variable(b,name,E.get_basic_type_by_name('int'))
if 'UILayoutMoto' not in known:assert E.add_member_variable(b,'UILayoutMoto',E.get_basic_type_by_name('bool'))
assert E.compile_blueprint(b);c=unreal.get_default_object(b.generated_class());c.set_editor_property('UIViewportX',-1);c.set_editor_property('UIViewportY',-1);c.set_editor_property('UILayoutPage',-1)
g=d.Graph()
for n in ['Delivery','UIRefreshAge','LastPhoneOpen','UIViewportX','UIViewportY','LayoutRebuildCount']:g.get(n)
g.call('Valid','IsValid',K);g.link('Delivery','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else')
g.call('Age','Add_DoubleDouble',M);g.link('UIRefreshAge','UIRefreshAge','Age','A');g.link('entry','InDeltaTime','Age','B');g.setter('Advance','UIRefreshAge','Age');g.exec('Ready','Advance')
g.call('Due','GreaterEqual_DoubleDouble',M,B='.1');g.link('UIRefreshAge','UIRefreshAge','Due','A');g.branch('RefreshDue','Due');g.exec('Advance','RefreshDue');g.exec('RefreshDue','result','else');g.setter('Reset','UIRefreshAge',value='0');g.exec('RefreshDue','Reset')
g.node('Open','getfield',owner=CORE,var='PhoneOpen');g.link('Delivery','Delivery','Open','self');g.call('Changed','NotEqual_BoolBool',M);g.link('LastPhoneOpen','LastPhoneOpen','Changed','A');g.link('Open','PhoneOpen','Changed','B');g.branch('NewOpenState','Changed');g.exec('Reset','NewOpenState')
g.setter('RememberOpen','LastPhoneOpen','Open','PhoneOpen');g.exec('NewOpenState','RememberOpen');g.call('PageVisibility','ApplyPageVisibility');g.exec('RememberOpen','PageVisibility')
g.call('Controller','GetPlayerController',GS,PlayerIndex='0');g.call('Viewport','GetViewportSize','/Script/Engine.PlayerController');g.link('Controller','ReturnValue','Viewport','self')
for axis in ['X','Y']:
 g.call(axis+'Changed','NotEqual_IntInt',M);g.link('UIViewport'+axis,'UIViewport'+axis,axis+'Changed','A');g.link('Viewport','Size'+axis,axis+'Changed','B');g.setter('Store'+axis,'UIViewport'+axis,'Viewport','Size'+axis)
g.call('SizeChanged','BooleanOR',M);g.link('XChanged','ReturnValue','SizeChanged','A');g.link('YChanged','ReturnValue','SizeChanged','B')
for n in ['Page','PreviewMoto','UILayoutPage','UILayoutMoto']:g.get(n)
g.call('PageChanged','NotEqual_IntInt',M);g.link('Page','Page','PageChanged','A');g.link('UILayoutPage','UILayoutPage','PageChanged','B');g.call('ModeChanged','NotEqual_BoolBool',M);g.link('PreviewMoto','PreviewMoto','ModeChanged','A');g.link('UILayoutMoto','UILayoutMoto','ModeChanged','B');g.call('PageOrMode','BooleanOR',M);g.link('PageChanged','ReturnValue','PageOrMode','A');g.link('ModeChanged','ReturnValue','PageOrMode','B');g.call('LayoutDirty','BooleanOR',M);g.link('SizeChanged','ReturnValue','LayoutDirty','A');g.link('PageOrMode','ReturnValue','LayoutDirty','B')
g.branch('Resize','LayoutDirty');g.exec('NewOpenState','Resize','else');g.exec('Resize','StoreX');g.exec('PageVisibility','StoreX');g.exec('StoreX','StoreY');g.setter('StorePage','UILayoutPage','Page','Page');g.setter('StoreMode','UILayoutMoto','PreviewMoto','PreviewMoto');g.exec('StoreY','StorePage');g.exec('StorePage','StoreMode')
g.call('Layout','ComputePhoneLayout');g.exec('StoreMode','Layout');g.call('CountLayout','Add_IntInt',M,B='1');g.link('LayoutRebuildCount','LayoutRebuildCount','CountLayout','A');g.setter('RememberCount','LayoutRebuildCount','CountLayout');g.exec('Layout','RememberCount')
g.call('HUD','ApplyHUDVisibility');g.exec('RememberCount','HUD');g.exec('Resize','HUD','else');g.branch('OpenRefresh','Open','PhoneOpen');g.exec('HUD','OpenRefresh');g.call('Text','RefreshText');g.exec('OpenRefresh','Text');g.exec('OpenRefresh','result','else');g.exec('Text','result')
for node in g.nodes:
 if node.get('kind')=='call' and not node.get('owner'):node['owner']=b.generated_class().get_path_name()
assert unreal.DeliveryEditorLibrary.build_logic_graph(b,'Tick',json.dumps(dict(nodes=g.nodes,links=g.links)))
assert E.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
unreal.log('PHONE_LAYOUT_CACHE_READY')
