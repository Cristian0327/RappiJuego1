import unreal
bp=unreal.load_asset('/Game/Delivery/Core/BPC_DeliveryGameplay')
assert unreal.DeliveryEditorLibrary.build_reward_graph(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp)
unreal.log('REWARD_BLUEPRINT_GRAPH_SAVED')
