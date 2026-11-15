import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
bp=unreal.load_asset('/Game/Delivery/Vehicles/BP_DeliveryRider')
g=Graph()
for v in ['WalkReferenceSpeed','MinimumWalkRate','MaximumWalkRate']:g.get(v)
g.call('SafeReference','FMax',M,B='1');g.link('WalkReferenceSpeed','WalkReferenceSpeed','SafeReference','A');g.call('Cadence','Divide_DoubleDouble',M);g.link('entry','Speed','Cadence','A');g.link('SafeReference','ReturnValue','Cadence','B');g.call('SafeMaximum','FMax',M);g.link('MinimumWalkRate','MinimumWalkRate','SafeMaximum','A');g.link('MaximumWalkRate','MaximumWalkRate','SafeMaximum','B');g.call('Rate','FClamp',M);g.link('Cadence','ReturnValue','Rate','Value');g.link('MinimumWalkRate','MinimumWalkRate','Rate','Min');g.link('SafeMaximum','ReturnValue','Rate','Max');g.link('Rate','ReturnValue','result','ReturnValue');g.exec('entry','result');report=g.build('GetWalkPlayRate');unreal.EditorAssetLibrary.save_loaded_asset(bp)
p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());data['player_animation_graphs']=[report];p.write_text(json.dumps(data,indent=2));unreal.log('LOCOMOTION_BLUEPRINT_SAVED '+json.dumps(report))
