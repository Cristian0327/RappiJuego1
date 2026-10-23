import unreal,json
report=[]
for name in ['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']:
 mesh=unreal.load_asset('/Game/Delivery/People/SK_'+name)
 slots=mesh.get_editor_property('materials');before=len(slots)
 slot=slots[0];slot.set_editor_property('material_interface',unreal.load_asset('/Game/Delivery/People/NPC_Atlas'));slot.set_editor_property('material_slot_name','NPC_Atlas')
 subsystem=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
 indices=[subsystem.get_lod_material_slot(mesh,lod,section) for lod in range(subsystem.get_lod_count(mesh)) for section in range(subsystem.get_num_sections(mesh,lod))]
 unreal.log('NPC_SECTIONS '+name+' slots='+str(before)+' sections='+str(indices))
 # Preserve importer indices: unused slots do not generate render sections.
 assert len(indices)==1,str(indices)
 report.append({'name':name,'importer_slots':before,'render_sections':len(indices),'used_material_slots':len(set(indices))})
from pathlib import Path
(Path(unreal.Paths.project_dir()).parents[1]/'outputs/DeliveryArt/People/material_validation.json').write_text(json.dumps(report,indent=2))
unreal.log('NPC_RENDER_SECTIONS_VALIDATED '+str(report))
