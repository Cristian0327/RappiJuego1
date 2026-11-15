import unreal,json,traceback
from pathlib import Path
R=Path(__file__).resolve().parent.parent
report={}
try:
 factory=unreal.WidgetBlueprintFactory();factory.set_editor_property('parent_class',unreal.UserWidget)
 b=unreal.load_asset('/Game/World/BlueprintWorld/Optimization/WBP_GraphicsSettings') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('WBP_GraphicsSettings','/Game/World/BlueprintWorld/Optimization',unreal.WidgetBlueprint,factory)
 assert unreal.DeliveryEditorLibrary.clone_engine_widget_designer(unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone'),b)
 tree=unreal.find_object(b,'WidgetTree');report['tree']=str(tree)
 if not tree:tree=b.get_editor_property('widget_tree')
 report['tree_class']=str(tree.get_class());report['tree_props']=dir(tree)
 canvas=tree.get_editor_property('RootWidget');report['root']=str(canvas)
 canvas.clear_children()
 button=unreal.new_object(unreal.Button,outer=tree,name='TestButton');canvas.add_child(button)
 button.set_editor_property('bIsVariable',True)
 report['compile']=unreal.BlueprintEditorLibrary.compile_blueprint(b)
 report['save']=unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
except Exception:report['error']=traceback.format_exc()
(R/'graphics_api.json').write_text(json.dumps(report,indent=2,default=str))
