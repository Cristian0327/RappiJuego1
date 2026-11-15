import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve().parent
rows=[]
for level in ['/Game/Maps/MapaCompleto_Integration','/Game/QA/AdaptationTraffic']:
    unreal.EditorLoadingAndSavingUtils.load_map(level)
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        name=a.get_class().get_name()
        if name not in ['BP_CivilMotorcycle_C','BP_PoliceMotorcycle_C','BP_PoliceRoadPatrol_C','BP_TwoWheelerCitizen_C','BP_BogotaServiceSignals_C']:continue
        group=str(a.get_editor_property('primary_actor_tick').get_editor_property('tick_group'))
        row=dict(map=level,name=a.get_name(),actor_group=group)
        if name=='BP_BogotaServiceSignals_C':assert 'TG_PRE_PHYSICS' in group
        else:
            move=a.get_editor_property('character_movement');row.update(movement_group=str(move.get_editor_property('primary_component_tick').get_editor_property('tick_group')),rvo=move.get_editor_property('use_rvo_avoidance'),min_analog=move.get_editor_property('min_analog_walk_speed'))
            assert 'TG_POST_PHYSICS' in row['movement_group'] and not row['rvo'] and row['min_analog']==0,row
        rows.append(row)
assert len(rows)==74,len(rows)
bp=unreal.load_asset('/Game/Traffic/Services/BP_ServiceTravelHeading');c=unreal.get_default_object(bp.generated_class());heading_group=str(c.get_editor_property('primary_component_tick').get_editor_property('tick_group'));assert 'TG_POST_UPDATE_WORK' in heading_group
(root/'service_tick_groups_verified.json').write_text(json.dumps(dict(actors=rows,heading_group=heading_group),indent=2))
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('SERVICE_TICK_GROUPS_VERIFIED')
