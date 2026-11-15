import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/DeliveryArt/Shops/SM_PizzaInterior.blend'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH');hits=[]
for p in o.data.polygons:
 vs=[o.data.vertices[i].co for i in p.vertices];lo=[min(v[j] for v in vs) for j in range(3)];hi=[max(v[j] for v in vs) for j in range(3)]
 if hi[0]<-4.55 or lo[0]>-4.05 or hi[1]<-5.5 or lo[1]>4.25 or hi[2]<.15 or lo[2]>1.75:continue
 hits.append({'center':list(p.center),'bounds':[lo,hi],'material':o.data.materials[p.material_index].name})
(root/'work/pizza_aisle_geometry.json').write_text(json.dumps(hits,indent=2))
