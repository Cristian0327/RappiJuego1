from pathlib import Path
for p in [Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryStores.cpp'),Path('work/install_store_crowd.py')]:
 s=p.read_text();s=s.replace('StartY=FMath::Min(650.f,HalfDepth*2-500),EndY=StoreKind==1?FMath::Max(200.f,CounterDistanceMeters*100-180):HalfDepth*2-600','StartY=FMath::Min(850.f,HalfDepth*2-450),EndY=StoreKind==1?FMath::Max(200.f,CounterDistanceMeters*100-175):HalfDepth*2-500');p.write_text(s)
