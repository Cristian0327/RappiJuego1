import unreal,json
from pathlib import Path
bp=unreal.load_asset('/Game/Delivery/Core/BPC_DeliveryGameplay');obj=unreal.get_default_object(bp.generated_class())
values=[obj.reward_for_distance(d,1) for d in [0,500,900,10000]]
assert values==[5000,27500,50000,50000],values
Path(unreal.Paths.project_saved_dir(),'blueprint_reward_test.json').write_text(json.dumps({'status':'PASS','values':values}))
unreal.log('BLUEPRINT_REWARD_VALUES_PASS '+str(values))
