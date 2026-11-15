import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;unreal.EditorLoadingAndSavingUtils.new_blank_map(False);a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.load_class(None,'/Game/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore.BP_DeliveryStore_C'),unreal.Vector());a.call_method('ReceiveBeginPlay');person=a.get_editor_property('WalkingCustomers')[0];at=person.get_editor_property('relative_location');unreal.log('CAPSULE_API '+str(unreal.SystemLibrary.capsule_trace_single_for_objects.__doc__));unreal.log('STORE_DEBUG '+str({'at':str(at),'actor':str(a.get_actor_location()),'paths':str(a.get_editor_property('CustomerPathEnd')),'speeds':str(a.get_editor_property('CustomerSpeeds')),'waits':str(a.get_editor_property('CustomerWaits')),'stops':str(a.get_editor_property('CustomerStops'))}));hit=unreal.SystemLibrary.capsule_trace_single_for_objects(a,unreal.Vector(at.x,at.y,at.z+95),unreal.Vector(at.x,at.y+1,at.z+95),35,80,[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],False,[],unreal.DrawDebugTrace.NONE,False);unreal.log('STORE_HIT '+str(hit));
if isinstance(hit,tuple):
 for x in hit:
  if isinstance(x,unreal.HitResult):
   for n in ['blocking_hit','start_penetrating','actor','component','impact_point','impact_normal','penetration_depth']:
    try:unreal.log('STORE_HIT_'+n+' '+str(x.get_editor_property(n)))
    except Exception as e:unreal.log('STORE_HIT_ERROR '+str(e))

a.set_editor_property('CustomerWaits',[0.,0.])
for i in range(6):
 a.call_method('UpdateCustomer',args=(0,.1))
 unreal.log('STORE_STEP '+str(i)+' at='+str(person.get_editor_property('relative_location'))+' waits='+str(a.get_editor_property('CustomerWaits'))+' stops='+str(a.get_editor_property('CustomerStops')))
unreal.log('STORE_LENGTHS '+str({n:len(a.get_editor_property(n)) for n in ['WalkingCustomers','CustomerStops','CustomerWaits','CustomerPathStart','CustomerPathEnd','CustomerSpeeds','CustomerWalkClips','CustomerIdleClips']}))
