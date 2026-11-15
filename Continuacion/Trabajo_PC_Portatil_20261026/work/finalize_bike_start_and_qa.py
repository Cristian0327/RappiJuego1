import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/build_two_wheeler_citizen.py').read_text(encoding='utf-8-sig');prefix=s[:s.index('# Components and the initial grounded state.')];a=s.index('g=d.Graph();g.variables=');b=s.index("g.build('ReceiveBeginPlay')",a)+len("g.build('ReceiveBeginPlay')")
body=s[a:b]
body=body.replace("g.exec('Ride','RidingState')", "g.call('InitialRideRate','SelectFloat',M,A='0',B='1');g.link('Bicycle','Bicycle','InitialRideRate','bPickA');g.call('InitialPlayback','SetPlayRate',SK);g.link('Mesh','Mesh','InitialPlayback','self');g.link('InitialRideRate','ReturnValue','InitialPlayback','Rate');g.exec('Ride','InitialPlayback');g.exec('InitialPlayback','RidingState')")
exec(compile(prefix+'\n'+body,'BicycleStopAtInitialRed','exec'))
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('BICYCLE_INITIAL_POSE_FROZEN_UNTIL_MOVING')
p=r/'work/build_bike_patrol_corrections_qa.py';exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
