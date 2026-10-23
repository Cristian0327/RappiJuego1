from pathlib import Path
import bpy,numpy as np
root=Path(__file__).resolve().parents[1]
exec((root/'work/sculpt_courier_style_staff.py').read_text().rsplit('\nnames=',1)[0])
names=['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']
spec=[(.68,1.15,.40),(.72,1.24,.52),(.77,1.26,.36),(.75,1.23,.36),(.73,1.20,.38),(.77,1.26,.39),(.75,1.23,.39),(.72,1.24,.39)]
customer=(root/'work/build_store_customers.py').read_text();body=customer[customer.index(' bpy.ops.wm.read_factory'):customer.index(" obj=mesh_grid")];body='\n'.join(line[1:] for line in body.splitlines())
for role,name in enumerate(names):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if role<5:character(role)
 else:
  source_role,cloth,accent,shoulder,leg=[(2,'rust','cream',1.26,.77),(3,'plum','white',1.23,.75),(1,'sage','gold',1.24,.72)][role-5];exec(body)
 leg,shoulder,w=spec[role];labels={}
 for ix,iy,iz in np.argwhere(grid):
  x,y,z=OR+(np.array([ix,iy,iz])+.5)*U;side='L' if x<0 else 'R'
  if z>shoulder+.075:n='head'
  elif abs(x)>w*.52 and z>shoulder-.64 and abs(y)<.18:
   n=('upperarm_' if z>shoulder-.27 else 'forearm_' if z>shoulder-.48 else 'hand_')+side
  elif z<leg-.035:n=('foot_' if z<.24 else 'shin_' if z<.46 else 'thigh_')+side
  else:n='spine' if z>leg+.14 else 'pelvis'
  if n not in labels:labels[n]=np.zeros_like(grid)
  labels[n][ix,iy,iz]=grid[ix,iy,iz]
 parts=[]
 for bone,g in labels.items():
  o=mesh_grid(bone,g);o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');parts.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();obj=bpy.context.object;obj.name='SM_'+name
 # Consolidate duplicate palette slots after joining independently closed pieces.
 old=list(obj.data.materials);indices=[KEYS.index(old[p.material_index].name.split('HF_')[-1].split('.')[0]) for p in obj.data.polygons]
 obj.data.materials.clear()
 for key in KEYS:obj.data.materials.append(next(m for m in old if m.name.split('HF_')[-1].split('.')[0]==key))
 for p,i in zip(obj.data.polygons,indices):p.material_index=i
 dest=root/'outputs/DeliveryArt/People/Segments';dest.mkdir(exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(dest/('SM_'+name+'.blend')))
print('CLOSED_RIGID_SEGMENTS_READY')
