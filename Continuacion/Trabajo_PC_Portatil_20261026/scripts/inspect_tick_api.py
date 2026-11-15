import unreal,json
from pathlib import Path
bp=unreal.load_asset('/Game/Traffic/Services/BP_VoxelRoadVehicle')
c=unreal.get_default_object(bp.generated_class());tick=c.get_editor_property('primary_actor_tick');value=tick.get_editor_property('tick_group')
report=dict(tick_api=[n for n in dir(unreal) if 'Tick' in n],group=str(value),group_type=str(type(value)),group_members=dir(type(value)))
Path(unreal.Paths.project_dir()).resolve().parent.joinpath('tick_api.json').write_text(json.dumps(report,indent=2))
