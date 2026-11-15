import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/Delivery/Animation/ABP_StreetCane');report=[]
for graph in bp.get_editor_property('function_graphs'):
 for node in graph.get_editor_property('nodes'):
  if node.get_class().get_name()=='AnimGraphNode_SequencePlayer':
   data=node.get_editor_property('node');row={'graph':graph.get_name(),'node':node.get_name(),'y':node.get_editor_property('node_pos_y'),'play_rate':data.get_editor_property('play_rate')};report.append(row)
(r/'work/cane_animation_graph_inventory.json').write_text(json.dumps(report,indent=2));unreal.log('CANE_ANIMATION_GRAPH_ACCESS_PASS')
