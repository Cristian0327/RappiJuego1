import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;world=unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota');assert world;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in actors.get_all_level_actors():
 cls=a.get_class().get_path_name();label=a.get_actor_label()
 if cls.startswith('/Game/QA/') or label.startswith(('Patrulla_Sector_','Moto_Civil_Sector_','Moto_Policia_Sector_')) or isinstance(a,unreal.CameraActor):
  row={'label':label,'class':cls}
  if label.startswith(('Patrulla_Sector_','Moto_Civil_Sector_','Moto_Policia_Sector_')):row['speed']=a.get_editor_property('RoadSpeed')
  rows.append(row)
data={'qa_actors_in_playable_map':[x for x in rows if x['class'].startswith('/Game/QA/')],'vehicles':[x for x in rows if 'speed' in x],'cameras':[x for x in rows if x['class']=='/Script/Engine.CameraActor']};assert not data['qa_actors_in_playable_map'],data;assert len(data['vehicles'])==24;assert all(x['speed']==(580 if x['label'].startswith('Patrulla') else 650) for x in data['vehicles']),data
(r/'RappiJuego1/Docs/validacion_mapa_sin_pruebas.json').write_text(json.dumps(data,indent=2));unreal.log('PLAYABLE_MAP_NO_TEST_ACTORS_AND_NORMAL_SPEEDS_PASS')
