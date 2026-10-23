import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/Delivery/Animation/ABP_StreetCane');out={'graphs':[],'iterators':[n for n in dir(unreal) if 'Iterator' in n]}
for path in [bp.get_path_name()+':AnimGraph',bp.get_path_name()+'.AnimGraph',bp.get_path_name()+':EditorData.AnimGraph']:
 o=unreal.find_object(None,path)
 if not o:continue
 row={'path':o.get_path_name()}
 try:
  nodes=o.get_editor_property('nodes');row['nodes']=[{'path':n.get_path_name(),'class':n.get_class().get_name()} for n in nodes]
 except Exception as e:row['error']=str(e)
 out['graphs'].append(row)
(r/'work/cane_animation_graph_objects.json').write_text(json.dumps(out,indent=2));unreal.log('CANE_GRAPH_OBJECT_PROBE_PASS')
