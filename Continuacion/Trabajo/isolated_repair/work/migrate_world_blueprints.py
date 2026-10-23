import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
root=Path(unreal.Paths.project_dir()).parent
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.BogotaCity)
bp=unreal.load_asset('/Game/World/BP_BogotaCity') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_BogotaCity','/Game/World',unreal.Blueprint,factory)
reports=[];A='/Script/Engine.KismetArrayLibrary'

g=Graph();g.get('TrafficPaintPalette');g.call('Count','Array_Length',A);g.link('TrafficPaintPalette','TrafficPaintPalette','Count','TargetArray')
g.call('Index','Percent_IntInt',M);g.link('entry','VehicleIndex','Index','A');g.link('Count','ReturnValue','Index','B')
g.call('Paint','Array_Get',A);g.link('TrafficPaintPalette','TrafficPaintPalette','Paint','TargetArray');g.link('Index','ReturnValue','Paint','Index');g.link('Paint','Item','result','ReturnValue');g.exec('entry','result');reports.append(g.build('TrafficPaintFor'))

for name,low,high in [('TrafficNSGreen',0,13),('TrafficEWGreen',16,29)]:
 g=Graph();g.get('Elapsed');g.call('Phase','FMod',M,Divisor='32');g.link('Elapsed','Elapsed','Phase','Dividend')
 g.call('BeforeRed','Less_DoubleDouble',M,B=str(high));g.link('Phase','Remainder','BeforeRed','A')
 if low:
  g.call('AfterGreen','GreaterEqual_DoubleDouble',M,B=str(low));g.link('Phase','Remainder','AfterGreen','A');g.call('Green','BooleanAND',M);g.link('AfterGreen','ReturnValue','Green','A');g.link('BeforeRed','ReturnValue','Green','B');source='Green'
 else:source='BeforeRed'
 g.link(source,'ReturnValue','result','ReturnValue');g.exec('entry','result');reports.append(g.build(name))

g=Graph();g.call('Phase','FMod',M,Divisor='1440');g.link('entry','Seconds','Phase','Dividend')
g.call('Day','Less_DoubleDouble',M,B='960');g.link('Phase','Remainder','Day','A')
g.call('DayHours','Divide_DoubleDouble',M,B='80');g.link('Phase','Remainder','DayHours','A');g.call('FromDawn','Add_DoubleDouble',M,B='6');g.link('DayHours','ReturnValue','FromDawn','A')
g.call('AfterSunset','Subtract_DoubleDouble',M,B='960');g.link('Phase','Remainder','AfterSunset','A');g.call('NightHours','Divide_DoubleDouble',M,B='40');g.link('AfterSunset','ReturnValue','NightHours','A');g.call('FromDusk','Add_DoubleDouble',M,B='18');g.link('NightHours','ReturnValue','FromDusk','A');g.call('Night24','FMod',M,Divisor='24');g.link('FromDusk','ReturnValue','Night24','Dividend')
g.call('Hour','SelectFloat',M);g.link('FromDawn','ReturnValue','Hour','A');g.link('Night24','Remainder','Hour','B');g.link('Day','ReturnValue','Hour','bPickA');g.link('Hour','ReturnValue','result','ReturnValue');g.exec('entry','result');reports.append(g.build('HourForCycle'))

for name,skip in [('AdvanceClock',False),('AdvanceTime',True)]:
 g=Graph();g.variables.append({'name':'PreviousCycle','default':'180'});g.get('CycleSeconds');g.get('GameDay');g.get('PreviousCycle');g.setter('Remember','PreviousCycle','CycleSeconds','CycleSeconds');g.exec('entry','Remember')
 if not skip:
  g.get('CycleMinutes');g.call('SafeMinutes','FMax',M,B='1');g.link('CycleMinutes','CycleMinutes','SafeMinutes','A');g.call('Rate','Divide_DoubleDouble',M,A='24');g.link('SafeMinutes','ReturnValue','Rate','B');g.call('Step','Multiply_DoubleDouble',M);g.link('entry','Dt','Step','A');g.link('Rate','ReturnValue','Step','B')
 g.call('Advance','Add_DoubleDouble',M,**({'B':'360'} if skip else {}));g.link('CycleSeconds','CycleSeconds','Advance','A')
 if not skip:g.link('Step','ReturnValue','Advance','B')
 g.call('Wrap','FMod',M,Divisor='1440');g.link('Advance','ReturnValue','Wrap','Dividend');g.setter('SetClock','CycleSeconds','Wrap','Remainder');g.exec('Remember','SetClock')
 g.call('NewDay','Less_DoubleDouble',M);g.link('CycleSeconds','CycleSeconds','NewDay','A');g.link('PreviousCycle','PreviousCycle','NewDay','B');g.branch('Midnight','NewDay');g.exec('SetClock','Midnight')
 g.call('NextDay','Add_IntInt',M,B='1');g.link('GameDay','GameDay','NextDay','A');g.setter('DayCounter','GameDay','NextDay');g.exec('Midnight','DayCounter')
 if skip:
  g.call('Refresh','RefreshWorldLighting');g.exec('DayCounter','Refresh');g.exec('Midnight','Refresh','else');g.exec('Refresh','result')
 else:g.exec('DayCounter','result');g.exec('Midnight','result','else')
 reports.append(g.build(name))

g=Graph();g.call('Position','BreakVector',M);g.link('entry','P','Position','InVec')
def ret(id,text):g.node(id,'return',defaults={'ReturnValue':text})
for node,axis,bound in [('Hills','Z','0')]:pass
g.call('EastHills','Greater_DoubleDouble',M,B='27000');g.link('Position','Y','EastHills','A');g.branch('InHills','EastHills');g.exec('entry','InHills');ret('Hills','Cerros orientales');g.exec('InHills','Hills')
prior='InHills'
for label,limit,title in [('South',-22000,'Sur / Restrepo'),('Centre',1000,'Centro'),('Chapinero',24000,'Chapinero / Parque 93')]:
 g.call(label+'X','Less_DoubleDouble',M,B=str(limit));g.link('Position','X',label+'X','A');g.branch(label,label+'X');g.exec(prior,label,'else')
 if label in ['South','Centre']:
  fn='Less_DoubleDouble' if label=='South' else 'Greater_DoubleDouble';bound='-21000' if label=='South' else '11000'
  g.call(label+'Y',fn,M,B=bound);g.link('Position','Y',label+'Y','A');g.branch(label+'Area',label+'Y');g.exec(label,label+'Area');ret(label+'Special','Ciudad Bolivar' if label=='South' else 'Centro / La Candelaria');ret(label+'Other',title);g.exec(label+'Area',label+'Special');g.exec(label+'Area',label+'Other','else')
 else:ret(label+'Return',title);g.exec(label,label+'Return')
 prior=label
ret('North','Norte / Usaquen');g.exec(prior,'North','else');reports.append(g.build('DistrictAt'))

colors=[(.82,.84,.86),(.012,.018,.026),(.14,.17,.20),(.56,.60,.65),(.66,.025,.035),(.025,.15,.55),(.025,.31,.20),(.52,.32,.12),(.96,.58,.025),(.26,.08,.34),(.08,.48,.52),(.65,.70,.58)]
cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('traffic_paint_palette',[unreal.LinearColor(*c,1) for c in colors]);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)

unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
old=next((a for a in actors.get_all_level_actors() if isinstance(a,unreal.BogotaCity) and a.get_class()!=bp.generated_class()),None)
if old:
 new=actors.spawn_actor_from_class(bp.generated_class(),old.get_actor_location(),old.get_actor_rotation())
 new.call_method('BakeCity')
 oldparts={c.get_name():c for c in old.get_components_by_class(unreal.InstancedStaticMeshComponent)};counts={}
 for component in new.get_components_by_class(unreal.InstancedStaticMeshComponent):
  component.clear_instances()
  source=oldparts.get(component.get_name());count=source.get_instance_count() if source else 0
  if count:component.add_instances([source.get_instance_transform(i,world_space=False) for i in range(count)],False,False);counts[component.get_name()]=count
 new.set_editor_property('north_roads',old.get_editor_property('north_roads'));new.set_editor_property('east_roads',old.get_editor_property('east_roads'));new.set_editor_property('map_footprints',old.get_editor_property('map_footprints'));new.set_actor_label('BP_BogotaCity');actors.destroy_actor(old)
 assert sum(counts.values())>1000,counts
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(root/'work/world_blueprint_migration.json').write_text(json.dumps(reports,indent=2));unreal.log('WORLD_BLUEPRINTS_PASS '+str(len(reports)))
