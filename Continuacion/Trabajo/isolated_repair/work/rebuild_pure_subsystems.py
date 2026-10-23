from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['build_pure_delivery_data_core.py','build_pure_store.py','extend_pure_store_customers.py','extend_pure_store_motion.py','extend_pure_store_lighting.py','extend_pure_delivery_progress.py','extend_pure_delivery_shop_queries.py','extend_pure_delivery_marketplace.py','migrate_boost_input_interface.py','build_pure_residential_route_assembler.py','extend_pure_order_lifecycle.py','extend_pure_order_acceptance.py']:
 unreal.log('PURE_SUBSYSTEM_REBUILD '+name);exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),str(r/'work'/name),'exec'),{})
unreal.log('PURE_SUBSYSTEM_REBUILD_PASS')
