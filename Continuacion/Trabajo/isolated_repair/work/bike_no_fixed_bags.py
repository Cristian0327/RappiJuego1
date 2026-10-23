from pathlib import Path
source=Path(__file__).with_name('build_progression_art.py').read_text(encoding='utf-8-sig');exec(source[:source.index('\nsetup_render()')]);setup_render()
for stage in range(5):
 bike(stage)
 beam('ReinforcedFrame',(-.42,0,.42),(.34,0,.76),.055,'Steel')
 box('RearMudguard',(-.62,0,.69),(.44,.18,.035),'Paint')
 export('SM_BikeCargoStage'+str(stage),addwheels=True)
