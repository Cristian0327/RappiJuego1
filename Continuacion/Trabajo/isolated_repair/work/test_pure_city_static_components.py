import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);bp=unreal.load_asset('/Game/World/BlueprintWorld/BP_CityGeometry');actor=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());cdo=unreal.get_default_object(bp.generated_class());rows=[]
try:
 groups=actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent);assert len(groups)==29,len(groups)
 for c in groups:
  name=c.get_name().removeprefix('Geometry_');saved=list(cdo.get_editor_property(name));assert c.get_instance_count()==len(saved),(name,c.get_instance_count(),len(saved));error=0
  for i,expected in enumerate(saved):
   actual=c.get_instance_transform(i,False);error=max(error,(actual.translation-expected.translation).length(),(actual.scale3d-expected.scale3d).length());qa=actual.rotation;qb=expected.rotation;dot=abs(qa.x*qb.x+qa.y*qb.y+qa.z*qb.z+qa.w*qb.w);assert dot>.99999,(name,i,dot)
  assert error<.01,(name,error);assert c.get_editor_property('mobility')==unreal.ComponentMobility.STATIC;assert c.get_editor_property('can_ever_affect_navigation')==name.startswith('Solid_');rows.append({'group':name,'instances':len(saved),'maximum_coordinate_error_cm':error,'navigation':name.startswith('Solid_')})
 labels=actor.get_components_by_class(unreal.TextRenderComponent);assert len(labels)==13;total=sum(x['instances'] for x in rows);assert total==16480;actor.call_method('ReceiveBeginPlay');assert sum(c.get_instance_count() for c in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))==total
finally:actors.destroy_actor(actor)
(r/'work/pure_city_static_components_validation.json').write_text(json.dumps({'status':'PASS','instances':total,'labels':len(labels),'before_beginplay':True,'no_duplicate_on_beginplay':True,'groups':rows},indent=2));unreal.log('PURE_CITY_STATIC_PARITY_PASS instances=16480')
