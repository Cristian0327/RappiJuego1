from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/build_pure_road_interaction.py').read_text(encoding='utf-8-sig')
start=s.index('# Restore the character')
end=s.index("build(g,'RestoreRoadRider')",start)+len("build(g,'RestoreRoadRider')")
exec(compile(s[:s.index("for fn in ['EnterRoad'")]+s[start:end],'UprightRoadExitOnly','exec'))
assert E.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('PURE_ROAD_EXIT_UPRIGHT_FIXED')
