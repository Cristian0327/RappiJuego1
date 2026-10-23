from pathlib import Path
p=Path('work/rig_store_people.py');s=p.read_text();a=s.index(' # Rigid voxel panels');b=s.index(' mod=obj.modifiers',a)
s=s[:a]+''' # Coincident vertices share weights: greedy voxel faces must not split at joints.
 for v in obj.data.vertices:
  x,y,z=v.co;side='L' if x<0 else 'R'
  def blend(a,b,t):
   t=max(0.,min(1.,t))
   if t<1:groups[a].add([v.index],1-t,'REPLACE')
   if t>0:groups[b].add([v.index],t,'REPLACE')
  if z>shoulder+.02:blend('spine','head',(z-shoulder-.02)/.10)
  elif abs(x)>w*.51 and z>leg-.02:
   if z>shoulder-.32:blend('forearm_'+side,'upperarm_'+side,(z-(shoulder-.32))/.12)
   else:blend('hand_'+side,'forearm_'+side,(z-(shoulder-.54))/.12)
  elif z<leg+.05:
   if z<.30:blend('foot_'+side,'shin_'+side,(z-.18)/.12)
   elif z<.52:blend('shin_'+side,'thigh_'+side,(z-.40)/.12)
   else:blend('thigh_'+side,'pelvis',(z-leg+.06)/.11)
  else:blend('pelvis','spine',(z-leg-.02)/.20)
''' +s[b:];p.write_text(s)
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/BogotaCity.cpp');s=p.read_text();s=s.replace('Building(X+A*2600,Y+B*2200,','if(A==-1&&B==-1)continue; // This frontage belongs to the walk-in delivery shop.\n   Building(X+A*2600,Y+B*2200,');p.write_text(s)
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryVehicleArt.cpp');s=p.read_text();s=s.replace('for(float Radius:{160.f,230.f,320.f})','FVector ParkingOrigin=Delivery&&Delivery->InsideStore?Delivery->InsideStore->GetActorLocation()+FVector(0,-230,95):GetActorLocation();\n for(float Radius:{160.f,230.f,320.f,550.f,850.f})');s=s.replace('FVector Candidate=GetActorLocation()+FVector','FVector Candidate=ParkingOrigin+FVector');s=s.replace('FVector Floor=Ground.ImpactPoint+FVector(0,0,3);if(', 'FVector Floor=Ground.ImpactPoint+FVector(0,0,3);bool InShop=false;for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)if(It->ContainsVisitor(Floor+FVector(0,0,95))){InShop=true;break;}if(InShop)continue;if(')
if '#include "EngineUtils.h"' not in s:s='#include "EngineUtils.h"\n'+s
p.write_text(s)
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp');s=p.read_text();s=s.replace('if(true)for(int32 X','for(int32 X');s=s.replace('if(Delivery->State==EDeliveryState::Pickup||Delivery->State==EDeliveryState::Dropoff){FVector End=Delivery->GetOrderTarget();auto Route=', 'if(Delivery->State==EDeliveryState::Pickup||Delivery->State==EDeliveryState::Dropoff||Delivery->HasWaypoint){FVector End=Delivery->HasWaypoint&&Delivery->State!=EDeliveryState::Pickup&&Delivery->State!=EDeliveryState::Dropoff?Delivery->Waypoint:Delivery->GetOrderTarget();auto Route=');p.write_text(s)
