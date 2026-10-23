import unreal,sys,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
from collections import defaultdict
# Only re-author the rider frame here. Recompiling the core and its circular UI in the same process can invalidate Python wrappers during editor shutdown.
E=unreal.BlueprintEditorLibrary;CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';M=d.M;K="/Script/Engine.KismetSystemLibrary"
def basic(n):return E.get_basic_type_by_name(n)
s=(r/'work/enable_pure_rider_frame.py').read_text(encoding='utf-8-sig');exec(compile(s[s.index('# Character frame'):],'PureRiderFrameOnly','exec'));unreal.log('PURE_RIDER_FRAME_ONLY_PASS')


