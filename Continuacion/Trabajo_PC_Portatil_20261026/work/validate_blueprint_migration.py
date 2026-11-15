import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
checks=[]
def check(name,value):
 checks.append({'id':name,'passed':bool(value)})
 assert value,name
for assetpath in unreal.EditorAssetLibrary.list_assets('/Game',recursive=True,include_folder=False):
 data=unreal.EditorAssetLibrary.find_asset_data(assetpath)
 if str(data.asset_class_path.asset_name) in ['Blueprint','WidgetBlueprint','AnimBlueprint']:
  asset=unreal.load_asset(assetpath);unreal.BlueprintEditorLibrary.compile_blueprint(asset);unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False)
exec(compile((root/'work/audit_blueprint_logic.py').read_text(encoding='utf-8-sig'),str(root/'work/audit_blueprint_logic.py'),'exec'))
bp=unreal.load_asset('/Game/World/BP_BogotaCity');city=unreal.get_default_object(bp.generated_class())
unreal.log('PALETTE_DEBUG '+str(city.get_editor_property('traffic_paint_palette')))
unreal.log('PAINT_DEBUG '+str([city.call_method('TrafficPaintFor',(i,)) for i in range(3)]))
paint=[city.call_method('TrafficPaintFor',(i,)) for i in range(100)]
check('twelve_paint_colors',len({(round(c.r,3),round(c.g,3),round(c.b,3)) for c in paint})==12)
for index in range(20):
 group=[paint[index+20*v] for v in range(4)]
 check('same_model_different_paint_'+str(index),len({(round(c.r,3),round(c.g,3),round(c.b,3)) for c in group})>=4)
for phase in [0,12.99,13,15.99,16,28.99,29,31.99,32,48]:
 city.set_editor_property('elapsed',phase)
 check('signal_ns_'+str(phase),city.call_method('TrafficNSGreen')==(phase%32<13))
 check('signal_ew_'+str(phase),city.call_method('TrafficEWGreen')==(16<=phase%32<29))
for seconds,hour in [(0,6),(180,8.25),(480,12),(960,18),(1200,0),(1439,5.975),(1440,6)]:
 check('clock_hour_'+str(seconds),abs(city.call_method('HourForCycle',(seconds,))-hour)<.001)
city.set_editor_property('cycle_seconds',1439);city.set_editor_property('game_day',0);city.set_editor_property('cycle_minutes',24)
city.call_method('AdvanceClock',(2,))
check('day_wrap',abs(city.get_editor_property('cycle_seconds')-1)<.001 and city.get_editor_property('game_day')==1)
city.set_editor_property('elapsed',0);city.set_editor_property('cycle_seconds',180);city.set_editor_property('game_day',0)
for position,name in [((0,28000,0),'Cerros orientales'),((-23000,-22000,0),'Ciudad Bolivar'),((-23000,0,0),'Sur / Restrepo'),((0,12000,0),'Centro / La Candelaria'),((0,0,0),'Centro'),((12000,0,0),'Chapinero / Parque 93'),((30000,0,0),'Norte / Usaquen')]:
 check('district_'+name,city.call_method('DistrictAt',(unreal.Vector(*position),))==name)

component=unreal.load_asset('/Game/Delivery/Core/BPC_DeliveryGameplay')
legacy=['GenerateIncomingOffer','ConfirmOffer','StartInteractionHold','ConfirmPickup','ConfirmDelivery','BuyUpgrade','IgnoreIncomingOffer','CancelHold','OpenClosePhone','ChangeVehicle','RefreshVehicleStats','SaveProgress']
for name in legacy:unreal.BlueprintEditorLibrary.remove_function_graph(component,name)
unreal.BlueprintEditorLibrary.compile_blueprint(component);unreal.EditorAssetLibrary.save_loaded_asset(component,only_if_is_dirty=False)
exec(compile((root/'work/audit_blueprint_logic.py').read_text(encoding='utf-8-sig'),str(root/'work/audit_blueprint_logic.py'),'exec'))
audit=json.loads((root/'work/blueprint_audit.json').read_text())
check('all_blueprints_compiled',all(b['compiled'] for b in audit))
check('no_legacy_wrapper_graphs',not any(g['name'] in legacy for b in audit for g in b['graphs']))
report={'status':'PASS','checks':checks,'removed_legacy_graphs':legacy,'blueprints':len(audit),'logic_nodes':sum(a['logic_nodes'] for a in audit)}
(root/'work/blueprint_migration_validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));unreal.log('BLUEPRINT_MIGRATION_VALIDATED '+str(len(checks)))

