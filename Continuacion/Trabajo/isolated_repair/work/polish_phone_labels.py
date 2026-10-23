import unreal
phone=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone')
tree=unreal.find_object(phone,'WidgetTree')
for name in ['HomeMapLabel','HomeOrdersLabel','HomeWorkshopLabel','HomeDeliveriesLabel','HomeCargoLabel','HomeVehiclesLabel']:
 label=unreal.find_object(tree,name)
 assert label,name
 label.set_shadow_color_and_opacity(unreal.LinearColor(0.01,0.02,0.03,1))
 label.set_shadow_offset(unreal.Vector2D(1,2))
unreal.BlueprintEditorLibrary.compile_blueprint(phone)
unreal.EditorAssetLibrary.save_loaded_asset(phone)
unreal.SystemLibrary.quit_editor()
