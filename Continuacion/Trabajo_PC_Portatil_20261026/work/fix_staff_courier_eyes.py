import bpy,json,shutil,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/People';report={}
backup=root/'work/Backups/CityVisuals_20261014/Staff';backup.mkdir(parents=True,exist_ok=True)
for path in sorted(out.glob('SK_*.blend')):
 if not (backup/path.name).exists():shutil.copy2(path,backup/path.name)
 bpy.ops.wm.open_mainfile(filepath=str(path));o=next(o for o in bpy.data.objects if o.type=='MESH');rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');old=o.data;image=next(n.image for n in old.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');px=list(image.pixels);w,h=image.size;uv=old.uv_layers.active
 colors={};poly_colors={};headidx=o.vertex_groups['head'].index
 for p in old.polygons:
  coord=uv.data[p.loop_indices[0]].uv;col=tuple(px[(min(h-1,int(coord.y*h))*w+min(w-1,int(coord.x*w)))*4:][:3]);poly_colors[p.index]=col
  if all(any(g.group==headidx and g.weight>.99 for g in old.vertices[vi].groups) for vi in p.vertices):
   entry=colors.setdefault(col,{'uv':tuple(coord),'polys':[]});entry['polys'].append(p.index)
 white=min(colors,key=lambda c:sum((c[a]-[.89,.87,.79][a])**2 for a in range(3)))
 iris=min(colors,key=lambda c:sum((c[a]-[.065,.027,.02][a])**2 for a in range(3)))
 skin=max((c for c in colors if c[0]>.35 and c[0]>c[1]*1.1 and c[1]>c[2]*1.2),key=lambda c:len(colors[c]['polys']))
 hair=min(colors,key=lambda c:sum((c[a]-[.13,.075,.052][a])**2 for a in range(3)))
 eye_polys=[old.polygons[i] for i in colors[iris]['polys']]
 eye_z0=min(old.vertices[vi].co.z for p in eye_polys for vi in p.vertices);eye_z1=max(old.vertices[vi].co.z for p in eye_polys for vi in p.vertices);centerz=(eye_z0+eye_z1)*.5
 group_names=[g.name for g in o.vertex_groups]
 verts=[tuple(v.co) for v in old.vertices];weights=[[(g.group,g.weight) for g in v.groups] for v in old.vertices];faces=[];uvs=[];removed=0
 for p in old.polygons:
  points=[old.vertices[i].co for i in p.vertices]
  remove=poly_colors[p.index] in [white,iris] and min(v.z for v in points)>=eye_z0-.001 and max(v.z for v in points)<=eye_z1+.001 and max(v.y for v in points)<-.18
  if remove:removed+=1;continue
  faces.append(tuple(p.vertices));uvs.append([tuple(uv.data[li].uv) for li in p.loop_indices])
 def box(col,bb):
  x0,x1,y0,y1,z0,z1=bb;first=len(verts);verts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]);weights.extend([[(headidx,1.0)]]*8)
  for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)]:faces.append(tuple(first+j for j in face));uvs.append([colors[col]['uv']]*4)
 for side in [-1,1]:
  centerx=side*.10125
  # Close the removed voxel sockets, then add the same thin layered graphics
  # as the main character: a 7.2 cm white and a 4.95 cm dark pupil.
  box(skin,(centerx-.05,centerx+.05,-.205,-.178,centerz-.044,centerz+.044))
  box(white,(centerx-.036,centerx+.036,-.209,-.205,centerz-.03375,centerz+.03375))
  pupilx=centerx-side*.01125
  box(iris,(pupilx-.02475,pupilx+.02475,-.2125,-.209,centerz-.03375,centerz+.03375))
  box(hair,(centerx-.037,centerx+.037,-.214,-.2115,centerz+.02475,centerz+.035))
 mesh=bpy.data.meshes.new(old.name+'_CourierEyes');mesh.from_pydata(verts,[],faces);mesh.update()
 for mat in old.materials:mesh.materials.append(mat)
 layer=mesh.uv_layers.new(name='Palette')
 for p,coords in zip(mesh.polygons,uvs):
  for li,coord in zip(p.loop_indices,coords):layer.data[li].uv=coord
 o.data=mesh
 o.vertex_groups.clear()
 for name in group_names:o.vertex_groups.new(name=name)
 for vi,groups in enumerate(weights):
  for gi,weight in groups:o.vertex_groups[gi].add([vi],weight,'REPLACE')
 o['courier_eye_revision']='2026-10-14';bpy.context.scene.frame_set(1)
 bpy.ops.wm.save_as_mainfile(filepath=str(path))
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(path.with_suffix('.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=.5,axis_forward='-Y',axis_up='Z')
 report[path.stem]={'removed_eye_faces':removed,'white_width_cm':7.2,'pupil_width_cm':4.95,'head_weight':1.0,'eye_center_z':centerz}
(root/'work/staff_courier_eyes.json').write_text(json.dumps(report,indent=2));print('STAFF_COURIER_EYES_ALL_8_PASS')
