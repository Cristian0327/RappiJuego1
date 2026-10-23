import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
b=unreal.load_asset('/Game/Traffic/Services/BP_PoliceOfficer');o=unreal.get_default_object(b.generated_class());m=o.get_editor_property('mesh');a={'constructor':str(unreal.Rotator(0,90,0)),'mesh_rotation':str(m.get_editor_property('relative_rotation')),'rotation_rate':str(o.get_editor_property('character_movement').get_editor_property('rotation_rate')),'route':str(o.get_editor_property('PatrolPoints')),'index':o.get_editor_property('PatrolIndex')};(r/'work/police_defaults.json').write_text(json.dumps(a,indent=2))
