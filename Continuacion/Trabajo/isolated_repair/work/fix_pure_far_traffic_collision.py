from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/integrate_pure_traffic_manager_runtime.py').read_text(encoding='utf-8-sig')
start=s.index("g=d.Graph();g.get('Vehicles');g.node('Each'")
end=s.index("build(g,'RenderTraffic',[{'name':'Alpha','category':'real'}])",start)+len("build(g,'RenderTraffic',[{'name':'Alpha','category':'real'}])")
exec(compile(s[:s.index("g=d.Graph();g.get('WorldState')")]+s[start:end],'FarTrafficRenderOnly','exec'))
assert E.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('PURE_FAR_TRAFFIC_COLLISION_FIXED')
