from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');b=use(TM);spec=json.loads((P/'BP_TrafficManager_ArcClearance_spec.json').read_text())
for node in spec['nodes']:
 if node['id']=='BodyMargin':node['defaults']['B']='680'
assert unreal.DeliveryEditorLibrary.build_logic_graph(b,'ArcClearance',json.dumps(spec));assert E.compile_blueprint(b);save(b);unreal.log('V2_STOPLINES_CLEAR_TURNING_SWEEPS')
