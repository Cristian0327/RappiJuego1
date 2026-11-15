import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/World/BlueprintWorld/BP_WorldState');assert bp;c=unreal.get_default_object(bp.generated_class());checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
for t in range(0,1441,15):
 p=t%1440;expected=6+p/80 if p<960 else (18+(p-960)/40)%24;actual=c.call_method('HourForCycle',(float(t),));check('hour_'+str(t),abs(actual-expected)<.001)
for t in [0,12.9,13,15.9,16,28.9,29,31.9,32]:
 c.set_editor_property('Elapsed',t);phase=t%32;check('ns_'+str(t),c.call_method('TrafficNSGreen')==(phase<13));check('ew_'+str(t),c.call_method('TrafficEWGreen')==(16<=phase<29))
for pos,expected in [(unreal.Vector(0,28000,0),'Cerros orientales'),(unreal.Vector(-23000,-22000,0),'Ciudad Bolivar'),(unreal.Vector(-23000,0,0),'Sur / Restrepo'),(unreal.Vector(0,12000,0),'Centro / La Candelaria'),(unreal.Vector(0,0,0),'Centro'),(unreal.Vector(12000,0,0),'Chapinero / Parque 93'),(unreal.Vector(30000,0,0),'Norte / Usaquen')]:check('district_'+expected,c.call_method('DistrictAt',(pos,))==expected)
c.set_editor_property('CycleMinutes',24);c.set_editor_property('CycleSeconds',1439);c.set_editor_property('GameDay',1);c.call_method('AdvanceClock',(2.0,));check('clock_wrap',abs(c.get_editor_property('CycleSeconds')-1)<.001);check('day_counter',c.get_editor_property('GameDay')==2)
for i in range(24):
 paint=c.call_method('TrafficPaintFor',(i,));reference=c.get_editor_property('TrafficPaintPalette')[i%12];check('paint_'+str(i),abs(paint.r-reference.r)<.001 and abs(paint.g-reference.g)<.001 and abs(paint.b-reference.b)<.001)
# Test changes are in memory only, never saved into defaults.
(r/'work/pure_world_state_validation.json').write_text(json.dumps({'status':'PASS','checks':checks},indent=2));unreal.log('PURE_WORLD_STATE_RUNTIME_VM_PASS checks='+str(len(checks)))
