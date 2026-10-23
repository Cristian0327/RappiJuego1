from pathlib import Path
p=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/work/rebuild_anatomical_mixamo.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("for label,file in [('Crowd',r/'outputs/DeliveryArt/Crowd/SK_Citizen12.blend'),('Hero',r/'outputs/unreal_v2/VoxelExplorer_GameRig.blend')]:", "for label,file in [(role,r/('outputs/DeliveryArt/People/SK_'+role+'.blend')) for role in ['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']]:")
s=s.replace("for clip in ['Walk','Idle','Jump']:","for clip in ['Walk','Idle']:")
needle="rests={n:target.data.bones[n].matrix_local.to_quaternion() for n in mapping};"
replacement="""mapping={n:v for n,v in mapping.items() if n in target.pose.bones};limbs={n:v for n,v in limbs.items() if n in target.pose.bones}
  if 'spine' in target.pose.bones:mapping['spine']='Spine2'
  if 'neck' in target.pose.bones:mapping['neck']='Neck'
  for suffix in ['L','R']:
   for n,sn,ch in [('upperarm','Arm','ForeArm'),('forearm','ForeArm','Hand'),('thigh','UpLeg','Leg'),('shin','Leg','Foot'),('foot','Foot','ToeBase')]:
    name=n+'_'+suffix
    if name in target.pose.bones:
     prefix='Left' if target.data.bones[name].head_local.x>0 else 'Right';mapping[name]=prefix+sn;limbs[name]=(prefix+sn,prefix+ch)
   name='hand_'+suffix
   if name in target.pose.bones:mapping[name]=('Left' if target.data.bones[name].head_local.x>0 else 'Right')+'Hand'
  rests={n:target.data.bones[n].matrix_local.to_quaternion() for n in mapping};"""
s=s.replace(needle,replacement);s=s.replace("for side_ in ['l','r']:","for side_ in (['l','r'] if 'thigh_l' in target.pose.bones else ['L','R']):").replace("target.pose.bones['calf_'+side_]","target.pose.bones[('calf_' if 'calf_'+side_ in target.pose.bones else 'shin_')+side_]")
p=r=p.with_name('rebuild_store_mixamo.py');p.write_text(s,encoding='utf-8')
