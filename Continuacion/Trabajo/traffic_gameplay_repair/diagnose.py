import unreal,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair');unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');S=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);aa=S.get_all_level_actors();asm=next(a for a in aa if a.get_class().get_name()=='BP_ResidentialRouteAssembler_C');owner=S.spawn_actor_from_class(unreal.load_class(None,'/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C'),unreal.Vector(0,0,500));core=owner.get_editor_property('Delivery');out={'core':str(core)}
try:
 count=asm.call_method('BuildRoutesFor',(core,));out['routes']=count;out['homes']=len(asm.get_editor_property('Homes'));out['stores']=len(asm.get_editor_property('Stores'));out['shop_tests']=[]
 for shop in asm.get_editor_property('Stores'):
  pos=shop.get_actor_location();out['shop_tests'].append([shop.get_name(),list(pos.to_tuple()),str(asm.call_method('ValidateDoor',(pos,shop)))])
 out['home_tests']=[]
 for p,e in list(zip(asm.get_editor_property('BuildingCenters'),asm.get_editor_property('BuildingExtents')))[:25]:
  pos=unreal.Vector(p.x,p.y-e.y-150,p.z);out['home_tests'].append([list(pos.to_tuple()),str(asm.call_method('ValidateDoor',(pos,None)))])
except Exception as e:out['error']=str(e)
for a in aa:
 if a.get_class().get_name()=='BP_TrafficManager_C':
  out['signals']={n:[list(v.to_tuple()) if hasattr(v,'to_tuple') else v for v in a.get_editor_property(n)] for n in ['UrbanCrossingCenters','UrbanCrossingForwards','UrbanSignalGroups','UrbanRoadWidths','UrbanStopOffsets']}
(P/'diagnosis.json').write_text(json.dumps(out,indent=2));unreal.log('DIAGNOSIS '+str({k:v for k,v in out.items() if k not in ['signals','home_tests','shop_tests']}))
