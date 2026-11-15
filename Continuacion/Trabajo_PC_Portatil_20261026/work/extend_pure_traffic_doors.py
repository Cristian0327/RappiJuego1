import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');d.bp=bp;E=unreal.BlueprintEditorLibrary;M=d.M;AL='/Script/Engine.KismetArrayLibrary';PO='/Script/Engine.PoseableMeshComponent';SK='/Script/Engine.SkinnedMeshComponent';P=bp.generated_class().get_path_name()
known=[str(x) for x in E.list_member_variable_names(bp)]
if 'DoorPoseDirty' not in known:assert E.add_member_variable(bp,'DoorPoseDirty',E.get_basic_type_by_name('bool'))
assert E.compile_blueprint(bp)
def build(g,name,params=[]):assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps({'nodes':g.nodes,'links':g.links,'parameters':params}))
g=d.Graph();g.get('Body');last='entry'
for prefix in ['Door','Wheel']:
 g.get(prefix+'Names');g.get(prefix+'Rest');g.call('Clear'+prefix,'Array_Clear',AL);g.link(prefix+'Rest',prefix+'Rest','Clear'+prefix,'TargetArray');g.exec(last,'Clear'+prefix);g.node('Each'+prefix,'foreach');g.link(prefix+'Names',prefix+'Names','Each'+prefix,'Array');g.link('Clear'+prefix,'then','Each'+prefix,'Exec');g.call('Read'+prefix,'GetBoneTransformByName',PO,BoneSpace='ComponentSpace');g.link('Body','Body','Read'+prefix,'self');g.link('Each'+prefix,'Array Element','Read'+prefix,'BoneName');g.link('Each'+prefix,'LoopBody','Read'+prefix,'execute');g.call('Save'+prefix,'Array_Add',AL);g.link(prefix+'Rest',prefix+'Rest','Save'+prefix,'TargetArray');g.link('Read'+prefix,'ReturnValue','Save'+prefix,'NewItem');g.exec('Read'+prefix,'Save'+prefix);last='Each'+prefix
 if prefix=='Door':
  # Next loop starts only after this loop completes.
  last='EachDoor'
  g.call('DoorCacheComplete','Array_Length',AL);g.link('DoorRest','DoorRest','DoorCacheComplete','TargetArray')
# Override clear-wheel exec: foreach uses Completed, not then.
g.links=[x for x in g.links if x!=['EachDoor','then','ClearWheel','execute']];g.link('EachDoor','Completed','ClearWheel','execute');g.setter('MarkDirty','DoorPoseDirty',value='true');g.link('EachWheel','Completed','MarkDirty','execute');g.exec('MarkDirty','result');build(g,'CacheReferencePose')
g=d.Graph()
for n in ['Body','Bus','DoorNames','DoorRest','DoorAlphaLeft','DoorAlphaRight','DoorTargetLeft','DoorTargetRight','Speed']:g.get(n)
g.call('AbsSpeed','Abs',M);g.link('Speed','Speed','AbsSpeed','A');g.call('Moving','Greater_DoubleDouble',M,B='20');g.link('AbsSpeed','ReturnValue','Moving','A');g.branch('SafetyClose','Moving');g.exec('entry','SafetyClose');g.setter('CloseLeft','DoorTargetLeft',value='0');g.setter('CloseRight','DoorTargetRight',value='0');g.exec('SafetyClose','CloseLeft');g.exec('CloseLeft','CloseRight');last='CloseRight'
g.get('DoorPoseDirty')
for side in ['Left','Right']:
 g.call(side+'Difference','Subtract_DoubleDouble',M);g.link('DoorAlpha'+side,'DoorAlpha'+side,side+'Difference','A');g.link('DoorTarget'+side,'DoorTarget'+side,side+'Difference','B');g.call(side+'Abs','Abs',M);g.link(side+'Difference','ReturnValue',side+'Abs','A');g.call(side+'NeedsBlend','Greater_DoubleDouble',M,B='.0001');g.link(side+'Abs','ReturnValue',side+'NeedsBlend','A')
g.call('NeedsBlend','BooleanOR',M);g.link('LeftNeedsBlend','ReturnValue','NeedsBlend','A');g.link('RightNeedsBlend','ReturnValue','NeedsBlend','B');g.call('ShouldUpdate','BooleanOR',M);g.link('NeedsBlend','ReturnValue','ShouldUpdate','A');g.link('DoorPoseDirty','DoorPoseDirty','ShouldUpdate','B');g.branch('NeedPose','ShouldUpdate');g.exec('CloseRight','NeedPose');g.exec('SafetyClose','NeedPose','else');g.exec('NeedPose','result','else');last='NeedPose'
for side in ['Left','Right']:
 g.call('Approach'+side,'FInterpTo_Constant',M,InterpSpeed='2.5');g.link('DoorAlpha'+side,'DoorAlpha'+side,'Approach'+side,'Current');g.link('DoorTarget'+side,'DoorTarget'+side,'Approach'+side,'Target');g.link('entry','Dt','Approach'+side,'DeltaTime');g.setter('Alpha'+side,'DoorAlpha'+side,'Approach'+side);g.exec(last,'Alpha'+side)
 if side=='Left':pass
 last='Alpha'+side
g.node('EachDoor','foreach');g.link('DoorNames','DoorNames','EachDoor','Array');g.link(last,'then','EachDoor','Exec');g.call('Rest','Array_Get',AL);g.link('DoorRest','DoorRest','Rest','TargetArray');g.link('EachDoor','Array Index','Rest','Index');g.call('Parts','BreakTransform',M);g.link('Rest','Item','Parts','InTransform');g.call('Location','BreakVector',M);g.link('Parts','Location','Location','InVec');g.call('IsLeft','Less_DoubleDouble',M,B='0');g.link('Location','Y','IsLeft','A');g.call('SideAlpha','SelectFloat',M);g.link('DoorAlphaLeft','DoorAlphaLeft','SideAlpha','A');g.link('DoorAlphaRight','DoorAlphaRight','SideAlpha','B');g.link('IsLeft','ReturnValue','SideAlpha','bPickA');g.call('CarSign','SelectFloat',M,A='65',B='-65');g.link('IsLeft','ReturnValue','CarSign','bPickA');g.call('Angle','Multiply_DoubleDouble',M);g.link('SideAlpha','ReturnValue','Angle','A');g.link('CarSign','ReturnValue','Angle','B');g.call('DoorRotation','MakeRotator',M);g.link('Angle','ReturnValue','DoorRotation','Yaw');g.call('Compose','ComposeRotators',M);g.link('Parts','Rotation','Compose','A');g.link('DoorRotation','ReturnValue','Compose','B');g.call('CarTransform','MakeTransform',M);g.link('Parts','Location','CarTransform','Location');g.link('Compose','ReturnValue','CarTransform','Rotation');g.link('Parts','Scale','CarTransform','Scale')
g.call('FirstDoor','EqualEqual_IntInt',M,B='0');g.link('EachDoor','Array Index','FirstDoor','A');g.call('SlideSign','SelectFloat',M,A='-50',B='50');g.link('FirstDoor','ReturnValue','SlideSign','bPickA');g.call('SlideX','Multiply_DoubleDouble',M);g.link('SlideSign','ReturnValue','SlideX','A');g.link('DoorAlphaLeft','DoorAlphaLeft','SlideX','B');g.call('SlideY','Multiply_DoubleDouble',M,B='-8');g.link('DoorAlphaLeft','DoorAlphaLeft','SlideY','A');g.call('Slide','MakeVector',M);g.link('SlideX','ReturnValue','Slide','X');g.link('SlideY','ReturnValue','Slide','Y');g.call('BusAt','Add_VectorVector',M);g.link('Parts','Location','BusAt','A');g.link('Slide','ReturnValue','BusAt','B');g.call('BusTransform','MakeTransform',M);g.link('BusAt','ReturnValue','BusTransform','Location');g.link('Parts','Rotation','BusTransform','Rotation');g.link('Parts','Scale','BusTransform','Scale');g.branch('PoseBus','Bus','Bus');g.link('EachDoor','LoopBody','PoseBus','execute')
for kind,edge in [('Bus','then'),('Car','else')]:
 g.call('Pose'+kind+'Door','SetBoneTransformByName',PO,BoneSpace='ComponentSpace');g.link('Body','Body','Pose'+kind+'Door','self');g.link('EachDoor','Array Element','Pose'+kind+'Door','BoneName');g.link(kind+'Transform','ReturnValue','Pose'+kind+'Door','InTransform');g.exec('PoseBus','Pose'+kind+'Door',edge)
g.setter('CleanPose','DoorPoseDirty',value='false');g.link('EachDoor','Completed','CleanPose','execute');g.exec('CleanPose','result');build(g,'UpdateDoorPose',[{'name':'Dt','category':'real'}])
g=d.Graph();last='entry'
for side in ['Left','Right']:
 g.call('Clamp'+side,'FClamp',M,Min='0',Max='1');g.link('entry',side,'Clamp'+side,'Value');g.setter('Set'+side,'DoorTarget'+side,'Clamp'+side);g.exec(last,'Set'+side);last='Set'+side
g.exec(last,'result');build(g,'RequestDoors',[{'name':'Left','category':'real'},{'name':'Right','category':'real'}])
g=d.Graph();g.call('Cache','CacheReferencePose',P);g.exec('entry','Cache');g.exec('Cache','result');g.build('ReceiveBeginPlay');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('PURE_TRAFFIC_DOOR_POSE_PASS')
