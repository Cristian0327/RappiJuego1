from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
s=(P/'build_debug_traffic.py').read_text();s=s.replace("exec(compile(s,'DebugRealTraffic'", "s=s.replace(\"field(g,'Cars','Vehicles'\",\"field(g,'Cars','GridVehicles'\").replace(\"g.link('Cars','Vehicles','Each'\",\"g.link('Cars','GridVehicles','Each'\");exec(compile(s,'DebugRealTraffic'")
exec(compile(s,'ProxyDebugProbe','exec'),{})
