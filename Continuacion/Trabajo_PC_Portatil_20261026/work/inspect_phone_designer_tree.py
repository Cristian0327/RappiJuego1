import unreal,json,collections
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone');tree=unreal.find_object(bp,'WidgetTree');assert tree;root=unreal.find_object(tree,'Root');assert root;out=[];queue=collections.deque([(root,None,0)])
while queue:
 w,parent,depth=queue.popleft();row={'name':w.get_name(),'class':unreal.Object.get_class(w).get_path_name(),'parent':parent,'depth':depth}
 if isinstance(w,unreal.TextBlock):row['text']=str(w.get_text())
 try:
  slot=w.get_editor_property('slot')
  if isinstance(slot,unreal.CanvasPanelSlot):
   p=slot.get_position();z=slot.get_size();a=slot.get_alignment();row['slot']={'position':[p.x,p.y],'size':[z.x,z.y],'alignment':[a.x,a.y]}
 except Exception:pass
 out.append(row)
 if isinstance(w,unreal.PanelWidget):
  for child in w.get_all_children():queue.append((child,w.get_name(),depth+1))
(r/'work/phone_designer_tree.json').write_text(json.dumps({'root':root.get_name(),'widgets':out,'count':len(out),'classes':dict(collections.Counter(x['class'] for x in out))},indent=2,ensure_ascii=False));unreal.log('PHONE_DESIGNER_TREE_INSPECT_PASS count='+str(len(out)))
