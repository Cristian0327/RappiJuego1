import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
s=(r/'work/build_pure_playable_world_integration.py').read_text(encoding='utf-8-sig');s=s[:s.index("for path in [folder+'/BP_StreetCitizen'")];exec(compile(s,'RestoreCrowdRadius','exec'),{})
exec(compile((r/'work/build_pure_station_passenger.py').read_text(encoding='utf-8-sig'),'BudgetStationPassengers','exec'),{})
unreal.log('PURE_STATION_WAIT_BUDGET_PASS')
