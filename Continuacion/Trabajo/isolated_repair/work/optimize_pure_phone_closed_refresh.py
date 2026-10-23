import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};s=(r/'work/build_pure_phone_navigation.py').read_text();exec(compile(s[:s.index('# Explicit declarations')],'PurePhoneLayoutSetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'});LAY='/Script/UMG.WidgetLayoutLibrary';CS='/Script/UMG.CanvasPanelSlot';BORDER='/Script/UMG.Border';known=[str(x) for x in E.list_member_variable_names(bp)]

reports=[]
def field(g,id,name):g.node(id,'getfield',owner=CORE,var=name);g.link('Delivery','Delivery',id,'self')
def valid(g):
 g.get('Delivery');g.call('Valid','IsValid',K);g.link('Delivery','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');return 'Ready'

g=Graph();last=valid(g);g.get('LastPhoneOpen');g.get('UIRefreshAge');field(g,'Open','PhoneOpen');g.call('Changed','NotEqual_BoolBool',M);g.link('LastPhoneOpen','LastPhoneOpen','Changed','A');g.link('Open','PhoneOpen','Changed','B');g.branch('NewOpenState','Changed');g.exec(last,'NewOpenState');g.setter('RememberOpen','LastPhoneOpen','Open','PhoneOpen');g.exec('NewOpenState','RememberOpen');g.call('PageVisibility','ApplyPageVisibility');g.exec('RememberOpen','PageVisibility');g.call('Layout','ComputePhoneLayout');g.exec('PageVisibility','Layout');g.exec('NewOpenState','Layout','else');g.call('HUD','ApplyHUDVisibility');g.exec('Layout','HUD');g.call('Age','Add_DoubleDouble',M);g.link('UIRefreshAge','UIRefreshAge','Age','A');g.link('entry','InDeltaTime','Age','B');g.setter('Advance','UIRefreshAge','Age');g.exec('HUD','Advance');g.call('Due','GreaterEqual_DoubleDouble',M,B='.1');g.link('UIRefreshAge','UIRefreshAge','Due','A');g.branch('RefreshDue','Due');g.exec('Advance','RefreshDue');g.exec('RefreshDue','result','else');g.setter('Reset','UIRefreshAge',value='0');g.exec('RefreshDue','Reset');g.call('Text','RefreshText');g.branch('OpenRefresh','Open','PhoneOpen');g.exec('Reset','OpenRefresh');g.exec('OpenRefresh','Text');g.exec('OpenRefresh','result','else');g.exec('Text','result');g.links=[x for x in g.links if x not in [['Ready','then','NewOpenState','execute'],['HUD','then','Advance','execute'],['Reset','then','OpenRefresh','execute']]];g.exec('Ready','Advance');g.exec('Reset','NewOpenState');g.exec('HUD','OpenRefresh');g.build('Tick',override=True)
assert E.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('PURE_PHONE_CLOSED_REFRESH_PASS')


