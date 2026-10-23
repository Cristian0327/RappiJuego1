import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
lines=[]
for n in ['SkeletalMeshEditorSubsystem','SkeletonEditorSubsystem','EditorSkeletalMeshLibrary']:
 c=getattr(unreal,n,None);lines.append(n+':'+str([x for x in dir(c) if 'skeleton' in x or 'assign' in x]))
for n in ['SK_BicycleCivilBlue','SK_BicycleCivil_Skeleton','SK_MotoCivilBlue_Skeleton']:
 a=unreal.load_asset('/Game/Traffic/Services/'+n);lines.append(n+':'+str(a))
 if isinstance(a,unreal.SkeletalMesh):lines.append('skeleton='+str(a.get_editor_property('skeleton')))
(r/'work/skeleton_api2.txt').write_text('\n'.join(lines))
