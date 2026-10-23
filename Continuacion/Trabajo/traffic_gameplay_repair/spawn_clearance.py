from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'RepairHelpers','exec'))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);start=next(a for a in aa.get_all_level_actors() if isinstance(a,unreal.PlayerStart)).get_actor_location();bp=use('/Game/World/BlueprintWorld/Crowd/BP_CrowdManager');c=unreal.get_default_object(bp.generated_class());positions=list(c.get_editor_property('SpawnPositions'));routes=list(c.get_editor_property('CitySpawnRoutes'));points=list(c.get_editor_property('CityRoutePoints'));indices=list(c.get_editor_property('StartIndices'));count=0
for i,pos in enumerate(positions):
 if (pos-start).length()>1000:continue
 route=points[routes[i]*32:(routes[i]+1)*32]
 for j,p in enumerate(route):
  q=unreal.Vector(p.x,p.y,p.z+88)
  if (q-start).length()>1100 and all((q-v).length()>180 for k,v in enumerate(positions) if k!=i):positions[i]=q;indices[i]=(j+1)%32;count+=1;break
c.set_editor_property('SpawnPositions',positions);c.set_editor_property('StartIndices',indices);save(bp);assert unreal.EditorLoadingAndSavingUtils.save_current_level();(P/'spawn_clearance.json').write_text(json.dumps(dict(moved_pedestrian_spawns=count,player_clear_radius_cm=1000)));unreal.log('PLAYER_INITIAL_AREA_CLEARED '+str(count))
