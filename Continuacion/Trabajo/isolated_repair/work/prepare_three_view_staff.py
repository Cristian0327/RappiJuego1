from pathlib import Path
p=Path('work/build_reference_staff.py');s=p.read_text(encoding='utf-8-sig');at=s.index(' # Small color variation')
insert=''' # Three-view pass: silhouette, side volume and back construction follow the turnaround.
 # Replace the generic legs on Rosalba with a stepped skirt and short visible calves.
 if role==0:
  for q in list(v):
   if 9<=q[2]<27:del v[q]
  for z in range(10,29):oval('purple',z,z+1,12-(z-10)//7,7)
  for side in [-1,1]:box('skinLight',side*5-2,side*5+2,-2,3,5,11)
  # Bun now sits at the back rather than becoming a crest on top.
  for q in list(v):
   if q[2]>head+18:del v[q]
  for z,r in [(head+5,3),(head+6,4),(head+8,5),(head+11,4),(head+13,3)]:oval('gray',z,z+2,r,3,0,8)
  box('white',-10,10,6,8,waist+6,waist+8)
 if role in [0,1,4]:
  tie='white' if role==0 else 'red' if role==1 else 'green';z=waist+7
  box(tie,-width,width,6,8,z,z+2)
  for side in [-1,1]:
   box(tie,side*3-2,side*3+2,8,10,z-1,z+3)
   for j in range(7):box(tie,side*(1+j//3),side*(1+j//3)+2,8,9,z-j-1,z-j)
 if role==1:
  for side in [-1,1]:
   x=side*(width+2);box('denim',x-3,x+3,-4,4,shoulder-15,shoulder-8)
  # Back neck strap and stepped collar, pocket towel visible from profile.
  for j in range(8):box('red',-7+j,-5+j,6,8,shoulder-j//2,shoulder+2-j//2)
  box('white',width-2,width+1,-2,4,waist,waist+12)
 if role==2:
  # Navy overshirt has real thickness and cyan cuff/hem detail on sides and back.
  for q,c in list(v.items()):
   if c=='blue' and waist<q[2]<shoulder and q[1]>=-6:v[q]='denim'
  box('blue',-8,8,6,7,waist,waist+2)
  for side in [-1,1]:
   x=side*(width+2);box('blue',x-3,x+3,-4,5,shoulder-10,shoulder-8)
   box('ink',side*8-1,side*8+2,-2,3,waist-10,waist-3)
  box('denim',-7,7,5,7,shoulder-3,shoulder-1)
 if role==3:
  # Coat back yoke, belt and central split are visible in rear view.
  box('white',-9,9,5,7,22,shoulder-2);box('gray',-1,1,7,8,22,30)
  box('white',-8,8,7,8,waist+5,waist+7)
  for side in [-1,1]:box('blue',side*(width+2)-2,side*(width+2)+2,-4,4,shoulder-15,shoulder-13)
  # Complete square eyeglass frames including side temples.
  for x in [-6,2]:
   for xx in [x,x+4]:box('ink',xx,xx+1,-9,-8,head+8,head+12)
  for side in [-1,1]:box('ink',side*7,side*7+1,-8,1,head+11,head+12)
 if role==4:
  # Fabric scarf trails down back, with voxel floral pattern and knot.
  for z in range(head-2,head+15):box('white',3,7,8,9,z,z+1)
  for z in range(head,head+15,4):box('red',4,6,9,10,z,z+2);box('green',3,4,9,10,z-1,z+1)
  box('white',2,8,8,11,head+6,head+9)
  for side in [-1,1]:box('green',side*7-1,side*7+1,5,7,waist+6,shoulder)
 # Taper sleeve/hand silhouettes at the sides instead of rectangular straight arms.
 for side in [-1,1]:
  x=side*(width+2)
  for q in list(v):
   if shoulder-21<=q[2]<shoulder-14 and abs(q[0]-x)>1 and abs(q[0]-x)<=3 and q[1]>=3:del v[q]
'''
s=s[:at]+insert+s[at:];s=s.replace("../References/Encargados_Detallados.png","../References/Bogota_Encargados_TresVistas.png")
# Pack the actual image reference in every editable Blender file.
needle="o.select_set(True);bpy.context.view_layer.objects.active=o;"
s=s.replace(needle,"ref=bpy.data.images.load(str(out.parent/'References/Bogota_Encargados_TresVistas.png'),check_existing=True);ref.pack();guide=bpy.data.objects.new('REFERENCE - three views',None);bpy.context.collection.objects.link(guide);guide.empty_display_type='IMAGE';guide.data=ref;guide.hide_render=True;guide.hide_viewport=True;\n "+needle)
# Render actual modeled geometry from all three requested angles.
s=s.replace("scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)","""scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 (out/'Turnarounds').mkdir(exist_ok=True)
 for label,pos in [('Front',(0,-6,1)),('Side',(6,0,1)),('Back',(0,6,1))]:
  cam.location=pos;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/'Turnarounds'/(name+'_'+label+'.png'));bpy.ops.render.render(write_still=True)""")
Path('work/model_three_view_staff.py').write_text(s,encoding='utf-8')
