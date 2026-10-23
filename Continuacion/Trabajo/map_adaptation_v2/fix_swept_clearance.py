from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
b=use(V);g=d.Graph()
for n in ['PreviousPosition','PreviousYaw','HalfLength','HalfWidth']:g.get(n)
for n in ['PreviousPosition','PreviousYaw','HalfLength','HalfWidth']:field(g,'Other'+n,n,('entry','Other'),V)
g.call('Rotation','MakeRotator',M);g.link('PreviousYaw','PreviousYaw','Rotation','Yaw');g.call('OtherRotation','MakeRotator',M);g.link('OtherPreviousYaw','PreviousYaw','OtherRotation','Yaw')
for prefix,rotation in [('', 'Rotation'),('Other','OtherRotation')]:
 for axis,fn in [('Forward','GetForwardVector'),('Right','GetRightVector')]:g.call(prefix+axis,fn,M);g.link(rotation,'ReturnValue',prefix+axis,'InRot')
op(g,'Delta','Subtract_VectorVector',('OtherPreviousPosition','PreviousPosition'),('PreviousPosition','PreviousPosition'));earliest=None;latest=None;valid=None
for i,axis in enumerate(['Forward','Right','OtherForward','OtherRight']):
 tag='Axis'+str(i);op(g,tag+'Offset','Dot_VectorVector',('Delta','ReturnValue'),(axis,'ReturnValue'));op(g,tag+'Rate','Dot_VectorVector',('Forward','ReturnValue'),(axis,'ReturnValue'));op(g,tag+'AbsRate','Abs',(tag+'Rate','ReturnValue'));op(g,tag+'Parallel','Less_DoubleDouble',(tag+'AbsRate','ReturnValue'),B='.00001');g.call(tag+'SafeRate','SelectFloat',M,A='1');g.link(tag+'Rate','ReturnValue',tag+'SafeRate','B');g.link(tag+'Parallel','ReturnValue',tag+'SafeRate','bPickA');extents=[]
 for prefix in ['','Other']:
  for dimension,direction,margin in [('Length','Forward','60'),('Width','Right','10')]:
   n=tag+prefix+dimension;op(g,n+'Cos','Dot_VectorVector',(prefix+direction,'ReturnValue'),(axis,'ReturnValue'));op(g,n+'Abs','Abs',(n+'Cos','ReturnValue'));op(g,n+'Size','Add_DoubleDouble',((prefix+'Half'+dimension) if prefix else 'Half'+dimension,'Half'+dimension),B=margin);op(g,n,'Multiply_DoubleDouble',(n+'Size','ReturnValue'),(n+'Abs','ReturnValue'));extents.append(n)
 r=extents[0]
 for j,n in enumerate(extents[1:]):op(g,tag+'Sum'+str(j),'Add_DoubleDouble',(r,'ReturnValue'),(n,'ReturnValue'));r=tag+'Sum'+str(j)
 op(g,tag+'LoNumerator','Subtract_DoubleDouble',(tag+'Offset','ReturnValue'),(r,'ReturnValue'));op(g,tag+'HiNumerator','Add_DoubleDouble',(tag+'Offset','ReturnValue'),(r,'ReturnValue'))
 for side in ['Lo','Hi']:op(g,tag+side,'Divide_DoubleDouble',(tag+side+'Numerator','ReturnValue'),(tag+'SafeRate','ReturnValue'))
 op(g,tag+'Minimum','FMin',(tag+'Lo','ReturnValue'),(tag+'Hi','ReturnValue'));op(g,tag+'Maximum','FMax',(tag+'Lo','ReturnValue'),(tag+'Hi','ReturnValue'))
 for suffix,source,value in [('Entry','Minimum','-100000000'),('Exit','Maximum','100000000')]:g.call(tag+suffix,'SelectFloat',M,A=value);g.link(tag+source,'ReturnValue',tag+suffix,'B');g.link(tag+'Parallel','ReturnValue',tag+suffix,'bPickA')
 op(g,tag+'Separation','Abs',(tag+'Offset','ReturnValue'));op(g,tag+'Separated','Greater_DoubleDouble',(tag+'Separation','ReturnValue'),(r,'ReturnValue'));op(g,tag+'NeverHits','BooleanAND',(tag+'Parallel','ReturnValue'),(tag+'Separated','ReturnValue'));op(g,tag+'Possible','Not_PreBool',(tag+'NeverHits','ReturnValue'))
 if earliest:op(g,tag+'Earliest','FMax',(earliest,'ReturnValue'),(tag+'Entry','ReturnValue'));op(g,tag+'Latest','FMin',(latest,'ReturnValue'),(tag+'Exit','ReturnValue'));op(g,tag+'AllPossible','BooleanAND',(valid,'ReturnValue'),(tag+'Possible','ReturnValue'));earliest=tag+'Earliest';latest=tag+'Latest';valid=tag+'AllPossible'
 else:earliest=tag+'Entry';latest=tag+'Exit';valid=tag+'Possible'
op(g,'Future','FMax',(earliest,'ReturnValue'),B='0');op(g,'Overlaps','GreaterEqual_DoubleDouble',(latest,'ReturnValue'),('Future','ReturnValue'));op(g,'Near','Less_DoubleDouble',('Future','ReturnValue'),B='5000');op(g,'Possible','BooleanAND',(valid,'ReturnValue'),('Overlaps','ReturnValue'));op(g,'Relevant','BooleanAND',('Possible','ReturnValue'),('Near','ReturnValue'));op(g,'Margin','Subtract_DoubleDouble',('Future','ReturnValue'),B='25');op(g,'Gap','FMax',('Margin','ReturnValue'),B='0');g.call('Answer','SelectFloat',M,B='100000000');g.link('Gap','ReturnValue','Answer','A');g.link('Relevant','ReturnValue','Answer','bPickA');g.link('Answer','ReturnValue','result','ReturnValue');g.exec('entry','result');build(b,g,'EnvelopeClearanceFromVehicle',[dict(name='Other',category='object',object=V),dict(name='ReturnValue',category='real',out=True)],True);save(b);unreal.log('V2_SWEPT_OBB_CLEARANCE_COMPILED')
