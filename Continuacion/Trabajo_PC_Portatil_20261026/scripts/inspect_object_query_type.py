import unreal,json
from pathlib import Path
p=unreal.BlueprintEditorLibrary.get_basic_type_by_name('byte')
result=dict(type=str(type(p)),attributes=dir(p))
try:
    p.set_editor_property('pin_sub_category_object',unreal.load_object(None,'/Script/Engine.EObjectTypeQuery'))
    result['success']=True
except Exception as e:result['error']=str(e)
Path(unreal.Paths.project_dir()).resolve().parent.joinpath('object_query_type.json').write_text(json.dumps(result,indent=2))
