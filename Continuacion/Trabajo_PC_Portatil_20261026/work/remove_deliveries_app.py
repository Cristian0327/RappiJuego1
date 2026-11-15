import unreal
phone=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone')
assert unreal.DeliveryEditorLibrary.remove_deliveries_app(phone)
assert unreal.EditorAssetLibrary.save_loaded_asset(phone,only_if_is_dirty=False)
assert unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset('/Game/Delivery/Core/BPC_DeliveryGameplay'),only_if_is_dirty=False)
unreal.log('DELIVERIES_APP_REMOVED_ORDERS_PRESERVED')
