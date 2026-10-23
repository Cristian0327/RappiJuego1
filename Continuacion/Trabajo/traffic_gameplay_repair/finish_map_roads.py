import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
assert 'isolated_repair' in r.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair');b=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone');c=unreal.get_default_object(b.generated_class());starts=list(c.get_editor_property('CityRoadStarts'));ends=list(c.get_editor_property('CityRoadEnds'));seen=set()
def key(a,b):return tuple(sorted([(round(a.x),round(a.y)),(round(b.x),round(b.y))]))
for a,z in zip(starts,ends):seen.add(key(a,z))
added=0
for road in json.loads((P.parent/'urban_refresh/secondary_road_plan.json').read_text())['secondary_roads']:
 points=road['samples'];chosen=[points[0]]
 for p in points[1:]:
  if math.dist(p,chosen[-1])>=500:chosen.append(p)
 if chosen[-1]!=points[-1]:chosen.append(points[-1])
 for a,z in zip(chosen,chosen[1:]):
  va=unreal.Vector(a[0],a[1],0);vz=unreal.Vector(z[0],z[1],0);k=key(va,vz)
  if k in seen:continue
  seen.add(k);starts.append(va);ends.append(vz);added+=1
c.set_editor_property('CityRoadStarts',starts);c.set_editor_property('CityRoadEnds',ends);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False);(P/'map_road_drawing.json').write_text(json.dumps(dict(added_secondary_segments=added,total_segments=len(starts)),indent=2));unreal.log('SECONDARY_ROADS_VISIBLE_ON_MAP '+str(added))
