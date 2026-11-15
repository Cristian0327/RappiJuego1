import unreal,json,hashlib
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
source=r/'work/build_pure_street_citizen_foundation.py';s=source.read_text(encoding='utf-8-sig');s=s.replace("value='1' if cane else None", "value='.95' if cane else None")
needle="assert unreal.DeliveryEditorLibrary.build_character_animation_blueprint(name,skel,idle,walk,clips['AN_CrowdBikePedal'],idle,idle);d.bp=bp"
replacement="assert unreal.DeliveryEditorLibrary.build_character_animation_blueprint(name,skel,idle,walk,clips['AN_CrowdBikePedal'],idle,idle);\n if cane:\n  idle_node=unreal.find_object(None,bp.get_path_name()+':AnimGraph.AnimGraphNode_SequencePlayer_0');assert idle_node;idle_data=idle_node.get_editor_property('node');idle_data.set_editor_property('play_rate',0.);idle_data.set_editor_property('start_position',0.);idle_node.set_editor_property('node',idle_data)\n d.bp=bp"
assert needle in s;s=s.replace(needle,replacement);source.write_text(s,encoding='utf-8')
exec(compile(s,str(source),'exec'))
bp=unreal.load_asset('/Game/Delivery/Animation/ABP_StreetCane');node=unreal.find_object(None,bp.get_path_name()+':AnimGraph.AnimGraphNode_SequencePlayer_0');assert node.get_editor_property('node').get_editor_property('play_rate')==0
p=r/'RappiJuego1/Content/Crowd/AN_CrowdCane.uasset';sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='1742c809c0799c7abc0b7167d415febafb2dd6290787335d39536e9bccfc461e9bccfc461e'[:0] if False else sha=='1742c809c0799c7abc0b7167d415febafb2dd6290787335d39536e9bccfc461e'
(r/'work/cane_preservation_validation.json').write_text(json.dumps({'idle_rate':0,'idle_start':0,'walk_rate':.95,'original_clip_sha256':sha,'status':'PASS'},indent=2));unreal.log('CANE_PRESERVATION_PASS')
