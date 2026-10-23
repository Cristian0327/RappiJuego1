from pathlib import Path
p=Path('work/rig_store_people.py');s=p.read_text();needle=' # One palette atlas/material'
pos=s.index(needle);s=s[:pos]+''' # Split greedy rectangles on the original voxel lattice before skinning.
 # This removes T-junction cracks while retaining the authored silhouette and colors.
 verts=[];faces=[];mats=[];old=obj.data
 for poly in old.polygons:
  corners=[old.vertices[i].co.copy() for i in poly.vertices]
  if len(corners)!=4:
   start=len(verts);verts.extend(corners);faces.append(tuple(range(start,len(verts))));mats.append(poly.material_index);continue
  a,b,c,d=corners;nu=max(1,round((b-a).length/.0225));nv=max(1,round((d-a).length/.0225))
  start=len(verts)
  for j in range(nv+1):
   for i in range(nu+1):verts.append(a+(b-a)*(i/nu)+(d-a)*(j/nv))
  for j in range(nv):
   for i in range(nu):
    k=start+j*(nu+1)+i;faces.append((k,k+1,k+nu+2,k+nu+1));mats.append(poly.material_index)
 mesh=bpy.data.meshes.new('SkinTopology');mesh.from_pydata(verts,[],faces)
 for m in old.materials:mesh.materials.append(m)
 for p,mi in zip(mesh.polygons,mats):p.material_index=mi
 obj.data=mesh
''' +s[pos:];p.write_text(s)
