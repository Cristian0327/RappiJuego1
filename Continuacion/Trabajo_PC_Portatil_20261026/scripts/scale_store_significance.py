import unreal,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent;backup=Path((R/'optimization_backup_path.txt').read_text());asset='World/BlueprintWorld/Optimization/BP_StoreDistanceBudget.uasset';src=Path(unreal.Paths.project_content_dir())/asset;dst=backup/'Content'/asset;dst.parent.mkdir(parents=True,exist_ok=True)
if not dst.exists():shutil.copy2(src,dst)
source=(R/'scripts/scale_service_significance.py').read_text(encoding='utf-8-sig')
# The existing store variant budgets actor updates, without disabling store collision or data.
source=source[source.index("source=(R/'work/build_service_distance_budget.py')"):]
inject="""
source=source.replace('BP_ServiceDistanceBudget','BP_StoreDistanceBudget').replace("[('Road','BP_VoxelRoadVehicle'),('Owner','BP_TwoWheelerCitizen'),('Police','BP_PoliceOfficer')]","[('Store','BP_DeliveryStore')]").replace("ActorClass='/Game/Traffic/Services/'+typ","ActorClass='/Game/Delivery/BlueprintGameplay/Stores/'+typ")
source=source.replace("g.link('Each','LoopBody','Apply','execute')",'').replace("g.exec('Hide','BudgetActor')","g.link('Each','LoopBody','BudgetActor','execute')").replace("g.exec('BudgetActor','BudgetPhysics')",'').replace("g.link('BudgetPhysics','then','EachSkin','Exec')","g.link('BudgetActor','then','EachSkin','Exec')")
source=source.replace(';;',';')
"""
source=source.replace('assert old in source;source=source.replace(old,new.rstrip())','assert old in source;source=source.replace(old,new.rstrip())\n'+inject)
exec(compile(source,'QualityStoreBudget','exec'),{'__file__':__file__,'R':R,'unreal':unreal})
unreal.log('QUALITY_STORE_SIGNIFICANCE_READY')
