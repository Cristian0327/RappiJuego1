import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=[root/'outputs/DeliveryArt/Crowd/SK_Citizen00.blend',root/'outputs/DeliveryArt/People/SK_Cashier.blend',root/'outputs/DeliveryArt/Shops/SM_MarketFront.blend',root/'outputs/DeliveryArt/Cargo/VoxelExplorer_CargoLoadout.blend',root/'outputs/unreal_v2/VoxelExplorer_GameRig.blend']
result=[]
for p in files:
 bpy.ops.wm.open_mainfile(filepath=str(p))
 result.append({'file':str(p.relative_to(root)),'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'vertices':len(o.data.vertices) if o.type=='MESH' else 0,'dimensions':list(o.dimensions)} for o in bpy.data.objects]})
(root/'work/asset_source_inventory.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('ASSET_SOURCE_INVENTORY_READY')
