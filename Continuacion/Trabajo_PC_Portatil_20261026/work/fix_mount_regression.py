import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider');d.bp=bp
R=bp.generated_class().get_path_name();M=d.M;SC='/Script/Engine.SceneComponent';SK='/Script/Engine.SkeletalMeshComponent'
p=r/'RappiJuego1/Content/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.uasset'
b=r/'Recuperacion_Migracion_Blueprints/2026-10-20_mount_regression/BP_BlueprintRider.uasset';b.parent.mkdir(parents=True,exist_ok=True)
if not b.exists():shutil.copy2(p,b)
def build(g,n,params=[]):
 assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,n,json.dumps({'nodes':g.nodes,'links':g.links,'parameters':params})),n
s=(r/'work/extend_pure_rider_transition_update.py').read_text(encoding='utf-8-sig')
s=s[s.index("g=d.Graph()\nfor n in ['TransitionState','TransitionAge'"):s.index(';assert E.compile_blueprint(bp)')]
# Restore the previously working fast approach; only exit uses eased late transfer.
needle="g.link('Progress','ReturnValue','Location','Alpha')"
replacement="""g.call('ApproachRatio','Divide_DoubleDouble',M,B='.3');g.link('Progress','ReturnValue','ApproachRatio','A');g.call('Approach','FClamp',M,Min='0',Max='1');g.link('ApproachRatio','ReturnValue','Approach','Value');g.call('ExitDelay','Subtract_DoubleDouble',M,B='.35');g.link('Progress','ReturnValue','ExitDelay','A');g.call('ExitRatio','Divide_DoubleDouble',M,B='.60');g.link('ExitDelay','ReturnValue','ExitRatio','A');g.call('ExitT','FClamp',M,Min='0',Max='1');g.link('ExitRatio','ReturnValue','ExitT','Value');g.call('ExitT2','Multiply_DoubleDouble',M);g.link('ExitT','ReturnValue','ExitT2','A');g.link('ExitT','ReturnValue','ExitT2','B');g.call('ExitTwice','Multiply_DoubleDouble',M,B='2');g.link('ExitT','ReturnValue','ExitTwice','A');g.call('ExitFactor','Subtract_DoubleDouble',M,A='3');g.link('ExitTwice','ReturnValue','ExitFactor','B');g.call('ExitSmooth','Multiply_DoubleDouble',M);g.link('ExitT2','ReturnValue','ExitSmooth','A');g.link('ExitFactor','ReturnValue','ExitSmooth','B');g.call('AnchorBlend','SelectFloat',M);g.link('Exiting','ReturnValue','AnchorBlend','bPickA');g.link('ExitSmooth','ReturnValue','AnchorBlend','A');g.link('Approach','ReturnValue','AnchorBlend','B');g.link('AnchorBlend','ReturnValue','Location','Alpha')"""
assert needle in s;s=s.replace(needle,replacement)
exec(compile(s,'SeparateEntryExitAnchors','exec'))
assert E.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('MOUNT_REGRESSION_PATCH_PASS')
