import unreal,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');assert 'isolated_repair' in Path(unreal.Paths.project_dir()).parts
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);out=[]
for store in [a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_DeliveryStore_C']:
 row=dict(name=store.get_name(),point_id=str(store.get_editor_property('PointID')),built_before=store.get_editor_property('Built'),products_before=len(store.get_editor_property('StoreProducts')),yaw=store.get_actor_rotation().yaw)
 store.call_method('ReceiveBeginPlay');row['built_after']=store.get_editor_property('Built');row['kind']=store.get_editor_property('StoreKind');row['products']=[];store.call_method('PresentOrder',(unreal.GuidLibrary.new_guid(),0))
 for j,c in enumerate(store.get_editor_property('StoreProducts')):
  p=store.call_method('ProductPosition',(j,));row['products'].append(dict(mesh=c.static_mesh.get_path_name() if c.static_mesh else None,visible=c.is_visible(),hidden=c.get_editor_property('hidden_in_game'),world=list(c.get_world_location().to_tuple()),expected=list(p.to_tuple()),bounds=str(c.get_local_bounds())))
 out.append(row);unreal.log('STORE_PRODUCT_AUDIT '+store.get_name()+' count='+str(len(row['products'])))
(P/'store_products_before.json').write_text(json.dumps(out,indent=2));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_STORE_PRODUCT_AUDIT_READY')
