from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
s=(P/'build_debug_traffic.py').read_text();s=s.replace("exec(compile(s,'DebugRealTraffic'", "s=s.replace(\"field(g,'Cars','Vehicles'\",\"field(g,'Cars','GridVehicles'\").replace(\"g.link('Cars','Vehicles','Each'\",\"g.link('Cars','GridVehicles','Each'\");exec(compile(s,'DebugRealTraffic'")
exec(compile(s,'ProxyDebugProbe','exec'),{})
