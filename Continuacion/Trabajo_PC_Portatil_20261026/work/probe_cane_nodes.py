import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/Delivery/Animation/ABP_StreetCane');out=[]
for o in unreal.ObjectIterator():
 try:
  path=o.get_path_name();cls=o.get_class().get_name()
 except Exception:continue
 if bp.get_path_name()+':' not in path or 'SequencePlayer' not in cls:continue
 row={'path':o.get_path_name()}
 for p in ['node_pos_y','node']:
  try:
   v=o.get_editor_property(p);row[p]=str(v)
   if p=='node':
    for q in ['play_rate','sequence']:
     try:row[q]=str(v.get_editor_property(q))
     except Exception as e:row[q]=str(e)
  except Exception as e:row[p]=str(e)
 out.append(row)
(r/'work/cane_nodes_probe.json').write_text(json.dumps(out,indent=2));unreal.log('CANE_NODES_PASS')

