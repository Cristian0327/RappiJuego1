from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];docs=root/'RappiJuego1/Docs'
r=json.loads((root/'work/BlueprintFinalMapQA/Saved/map_routes_validation.json').read_text(encoding='utf-8-sig'))
w=json.loads((root/'work/weather_validation.json').read_text(encoding='utf-8-sig'))
checks={k:r[k]==0 for k in ['pedestrian_vehicle_contact_samples','moving_vehicle_overlap_samples','pedestrian_close_contact_samples','parked_vehicle_overlap_samples','wall_penetration_samples','airborne_samples','invalid_positions','unplanned_stalls','static_vehicle_overlap_samples','illegal_crossings']}
checks['right_hand_traffic']=r['wrong_side_traffic_segments']==0 and r['right_hand_traffic_straight_segments']>0
checks['live_collision_control']=r['wall_collision_positive_control']
checks['all_vehicles_progress']=r['minimum_vehicle_travel_cm']>100000
checks['vehicles_no_deadlock']=r['longest_vehicle_stop_seconds']<90
checks['crossings_continue']=r['crossings_completed']>=50
checks['avoidance_scenarios']=r['avoidance_scenarios']['failures']==0
traffic=r['isolated_traffic_and_render_cadence'];checks['isolated_car_contacts']=traffic['overlap_frames']==0;checks['render_cadence']=traffic['moving_render_frames']>=118 and traffic['hitch_time_loss_cm']<1
weather=r['weather_rendering'];checks['rain_transitions']=weather['rain_started_gradually'] and weather['rain_stopped_gradually'];checks['rain_under_roofs']=weather['roof_hits']==weather['roof_occlusion_probes'] and weather['roof_occlusion_probes']>0 and weather['visible_drops_below_surface']==0;checks['weather_policy']=w['status']=='PASS'
report={'status':'PASS' if all(checks.values()) else 'FAIL','date':'2026-10-15','engine':'5.8.3','checks':checks,'map':r,'weather_policy':w}
(docs/'validacion_mapa_clima.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'status':report['status'],'failed':[k for k,v in checks.items() if not v]},ensure_ascii=False))
assert all(checks.values()),checks

