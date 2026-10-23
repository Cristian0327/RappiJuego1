import unreal,json,collections
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;T=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.BlueprintEditorLibrary;source=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone');folder='/Game/Delivery/BlueprintGameplay/UI';name='WBP_BlueprintPhone';path=folder+'/'+name;factory=unreal.WidgetBlueprintFactory();factory.set_editor_property('parent_class',unreal.UserWidget);bp=unreal.load_asset(path) or T.create_asset(name,folder,unreal.WidgetBlueprint,factory);assert unreal.DeliveryEditorLibrary.clone_engine_widget_designer(source,bp);assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);tree=unreal.find_object(bp,'WidgetTree');root=unreal.find_object(tree,'Root');assert root;queue=collections.deque([root]);widgets=[]
while queue:
 w=queue.popleft();widgets.append(w)
 if isinstance(w,unreal.PanelWidget):queue.extend(w.get_all_children())
assert len(widgets)==368,len(widgets);assert not any(unreal.Object.get_class(w).get_path_name().startswith('/Script/BogotaVoxel') for w in widgets);classes=collections.Counter(unreal.Object.get_class(w).get_path_name() for w in widgets);assert classes['/Script/UMG.Button']==159;original=json.loads((r/'work/phone_designer_tree.json').read_text());byname={w.get_name():w for w in widgets};slot_checks=0
for row in original['widgets']:
 w=byname[row['name']]
 if 'slot' not in row:continue
 slot=w.get_editor_property('slot');assert isinstance(slot,unreal.CanvasPanelSlot)
 for field,method in [('position','get_position'),('size','get_size'),('alignment','get_alignment')]:
  value=getattr(slot,method)();assert [value.x,value.y]==row['slot'][field],(row['name'],field,value,row['slot'][field]);slot_checks+=1
reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);deps=reg.get_dependencies(path,unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)) or [];assert not any(str(x).startswith('/Script/BogotaVoxel') for x in deps),deps;(r/'work/pure_phone_designer_migration.json').write_text(json.dumps({'status':'STAGING_DESIGNER_ONLY','asset':path,'parent':'/Script/UMG.UserWidget','widgets':len(widgets),'classes':dict(classes),'layout_value_checks':slot_checks,'legacy_custom_widgets_replaced':59,'native_widget_classes':0,'pending':['All phone lifecycle and page logic','Map drawing and click targeting','Garage preview','Bindings and input integration']},indent=2));unreal.log('PURE_PHONE_DESIGNER_CLONE_PASS widgets='+str(len(widgets))+' layout_checks='+str(slot_checks))
