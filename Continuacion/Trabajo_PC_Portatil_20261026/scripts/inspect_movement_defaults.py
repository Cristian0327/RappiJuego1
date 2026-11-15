import unreal,json
from pathlib import Path
rows=[]
for name in ['BP_VoxelRoadVehicle','BP_CivilMotorcycle','BP_PoliceMotorcycle','BP_PoliceRoadPatrol','BP_TwoWheelerCitizen']:
    bp=unreal.load_asset('/Game/Traffic/Services/'+name);a=unreal.get_default_object(bp.generated_class());m=a.get_editor_property('character_movement');cap=a.get_editor_property('capsule_component');row=dict(name=name,component_class=m.get_class().get_path_name(),capsule_half_height=cap.get_scaled_capsule_half_height(),capsule_radius=cap.get_scaled_capsule_radius(),profile=str(cap.get_collision_profile_name()))
    for prop in ['gravity_scale','default_land_movement_mode','movement_mode','max_walk_speed','max_fly_speed','braking_deceleration_walking','braking_friction','use_separate_braking_friction','air_control','falling_lateral_friction','max_step_height','max_simulation_iterations','max_simulation_time_step','constrain_to_plane','plane_constraint_normal','plane_constraint_origin','snap_to_plane_at_start','project_nav_mesh_walking']:
        try:row[prop]=str(m.get_editor_property(prop))
        except Exception as e:row[prop]=str(e)
    rows.append(row)
Path(unreal.Paths.project_dir()).resolve().parent.joinpath('movement_defaults_inspected.json').write_text(json.dumps(rows,indent=2))
