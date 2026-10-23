import unreal, json
from pathlib import Path
root = Path(unreal.Paths.project_dir())
tools = unreal.AssetToolsHelpers.get_asset_tools()
report = []

def blueprint(name, folder, parent):
    path = folder + '/' + name
    asset = unreal.load_asset(path)
    if not asset:
        is_widget = 'Widget' in parent
        factory = unreal.WidgetBlueprintFactory() if is_widget else unreal.BlueprintFactory()
        factory.set_editor_property('parent_class', unreal.load_class(None, parent))
        asset = tools.create_asset(name, folder, unreal.WidgetBlueprint if is_widget else unreal.Blueprint, factory)
    if not asset:
        raise RuntimeError('No se creó ' + path)
    report.append(path)
    return asset

table = unreal.load_asset('/Game/Delivery/Data/DT_Upgrades')
if not table:
    factory = unreal.DataTableFactory()
    factory.set_editor_property('struct', unreal.load_object(None, '/Script/BogotaVoxel.DeliveryUpgrade'))
    table = tools.create_asset('DT_Upgrades', '/Game/Delivery/Data', unreal.DataTable, factory)
if not unreal.DataTableFunctionLibrary.fill_data_table_from_csv_file(table, str(root / 'DeliveryData/Upgrades.csv')):
    raise RuntimeError('Falló importación de DT_Upgrades')
report.append('/Game/Delivery/Data/DT_Upgrades')

gameplay = blueprint('BPC_DeliveryGameplay', '/Game/Delivery/Core', '/Script/BogotaVoxel.DeliveryComponent')
for name, fn in [('GenerateIncomingOffer','GenerateOffer'),('ConfirmOffer','AcceptOffer'),('StartInteractionHold','BeginAction'),('ConfirmPickup','CollectOrder'),('ConfirmDelivery','CompleteOrder'),('BuyUpgrade','PurchaseUpgrade'),('IgnoreIncomingOffer','IgnoreOffer'),('CancelHold','EndAction'),('OpenClosePhone','TogglePhone'),('ChangeVehicle','SwitchVehicle'),('RefreshVehicleStats','RebuildStats'),('SaveProgress','SaveProfile')]:
    if not unreal.DeliveryEditorLibrary.add_action_graph(gameplay, name, fn):
        raise RuntimeError('Falló graph ' + name)
phone = blueprint('WBP_VoxelPhone', '/Game/Delivery/UI', '/Script/BogotaVoxel.DeliveryPhoneWidget')
for name, fn in [('ShowHome','OpenHome'),('ShowMapApp','OpenMap'),('ShowOrdersApp','OpenOrders'),('ShowUpgradesApp','OpenShop')]:
    unreal.DeliveryEditorLibrary.add_action_graph(phone, name, fn)
recipient = blueprint('BP_VoxelCustomer', '/Game/Delivery/Orders', '/Script/BogotaVoxel.DeliveryRecipient')
point = blueprint('BP_DeliveryBuilding', '/Game/Delivery/Orders', '/Script/BogotaVoxel.DeliveryPoint')
player = blueprint('BP_DeliveryRider', '/Game/Delivery/Vehicles', '/Script/BogotaVoxel.BogotaPlayer')
mode = blueprint('BP_DeliveryGameMode', '/Game/Delivery/Core', '/Script/BogotaVoxel.BogotaGameMode')
for bp in [gameplay,phone,recipient,point,player,mode]:
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_directory('/Game/Delivery', only_if_is_dirty=False, recursive=True)

player_cdo = unreal.get_default_object(player.generated_class())
if not unreal.DeliveryEditorLibrary.set_gameplay_component(player,gameplay.generated_class()):
    raise RuntimeError('No se pudo asignar el Blueprint del componente al jugador')
unreal.BlueprintEditorLibrary.compile_blueprint(player)
player_cdo = unreal.get_default_object(player.generated_class())
component = player_cdo.get_editor_property('delivery')
if component.get_class() != gameplay.generated_class():
    raise RuntimeError('El jugador no utiliza el componente Blueprint de repartos')
component.set_editor_property('upgrades', table)
component.set_editor_property('phone_class', phone.generated_class())
component.set_editor_property('recipient_class', recipient.generated_class())
unreal.get_default_object(mode.generated_class()).set_editor_property('default_pawn_class', player.generated_class())
unreal.EditorAssetLibrary.save_directory('/Game/Delivery', only_if_is_dirty=False, recursive=True)
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
world = unreal.EditorLevelLibrary.get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode', mode.generated_class())
existing = {str(a.get_editor_property('point_id')):a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.DeliveryPoint)}
for ix,x in enumerate([-36000,-24000,-12000,0,12000,24000,36000]):
    for iy,y in enumerate([-22000,-11000,0,11000,22000]):
        if ix==6 or iy==4:
            continue
        pid='Shop_%d_%d'%(ix,iy)
        actor=existing.get(pid)
        if not actor:
            actor=unreal.EditorLevelLibrary.spawn_actor_from_class(point.generated_class(),unreal.Vector(x+1750,y+2300,30))
        actor.set_actor_label('Repartos_'+pid)
        actor.set_editor_property('point_id',unreal.Name(pid))
        actor.set_editor_property('place_name',unreal.Text('Tienda %02d'%(ix*4+iy+1)))
unreal.EditorLevelLibrary.save_current_level()
import runpy
runpy.run_path(str(root.parents[1] / 'work/import_delivery_art.py'))
(root / 'Saved/delivery_assets.json').write_text(json.dumps({'assets':report,'map':'/Game/Maps/Bogota'},indent=2),encoding='utf-8')
unreal.log('DELIVERY_ASSETS_CREATED')
