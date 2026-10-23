import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
(r/'work/skeleton_api.txt').write_text(str([x for x in dir(unreal.Skeleton) if any(y in x for y in ['merge','bone','mesh'])])+ '\n'+str([x for x in dir(unreal.SkeletalMesh) if any(y in x for y in ['skeleton','bone'])]))
