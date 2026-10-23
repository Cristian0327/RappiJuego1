import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore');c=unreal.get_default_object(bp.generated_class());out={}
for fn,args in [('GetUpgradeSpec',(unreal.Name('BikePedals'),)),('GetVehicleSpec',(unreal.Name('BikeCity'),)),('GetSelectedOffer',()),('FindActiveOrderIndex',(unreal.Guid(),)),('ProfileSlot',())]:
 try:
  v=c.call_method(fn,args=args);out[fn]={'value':str(v),'type':str(type(v))};
  if isinstance(v,tuple):out[fn]['members']=[str(type(x)) for x in v]
 except Exception as e:out[fn]={'error':str(e)}
(r/'work/pure_data_python_probe.json').write_text(json.dumps(out,indent=2));unreal.log('PURE_DATA_PYTHON_PROBE_DONE')
