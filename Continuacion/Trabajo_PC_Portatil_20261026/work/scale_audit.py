import unreal,json
from pathlib import Path
r={}
for path in ['/Game/VoxelExplorer/SK_VoxelExplorer','/Game/Traffic/Detailed/SK_Private','/Game/Traffic/Detailed/SK_TransMilenio']:
 m=unreal.load_asset(path);b=m.get_bounds();r[path]={'size':[b.box_extent.x*2,b.box_extent.y*2,b.box_extent.z*2],'origin':[b.origin.x,b.origin.y,b.origin.z]}
Path(__file__).resolve().parent.joinpath('scale_audit.json').write_text(json.dumps(r))
