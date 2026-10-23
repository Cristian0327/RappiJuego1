from pathlib import Path
source=Path(__file__).with_name('build_progression_art.py').read_text(encoding='utf-8-sig')
exec(source[:source.index('\nsetup_render()')])
setup_render()
for family,count in [('Bike',5),('Moto',6)]:
 for variant in ['Cargo','BMX' if family=='Bike' else 'Sport']:
  for stage in range(count):
   if family=='Bike':bike(stage)
   else:moto(stage)
   if variant=='Cargo':
    box('DeliveryRack',(-.68,0,.78),(.45,.50,.055),'Steel')
    box('InsulatedBox',(-.76,0,1.02),(.43,.46,.44),'Orange')
    box('BoxLid',(-.76,0,1.26),(.45,.48,.06),'Rubber')
    for y in [-.24,.24]:box('Reflector',(-.76,y,1.03),(.27,.015,.05),'Lamp')
    box('BoxLatch',(-.99,0,1.1),(.025,.08,.13),'Chrome')
   elif family=='Bike':
    beam('TopTube',(-.15,0,.77),(.38,0,.77),.075,'Paint')
    for x in [-.62,.62]:box('AxlePegs',(x,0,.33),(.06,.45,.06),'Chrome')
    box('HandlebarPad',(.42,0,1.02),(.11,.22,.095),'Orange')
   else:
    for y in [-.22,.22]:
     box('SportFairing',(.15,y,.73),(.72,.09,.37),'Paint')
     box('AeroStep',(.45,y,.90),(.25,.09,.24),'Paint')
     box('RaceStripe',(.14,y*1.25,.76),(.52,.025,.07),'Orange')
    box('TailCowl',(-.50,0,.97),(.25,.39,.18),'Paint')
   export('SM_'+family+variant+'Stage'+str(stage),addwheels=True)
print('VEHICLE_CATALOG_READY',flush=True)
