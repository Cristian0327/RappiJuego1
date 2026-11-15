from pathlib import Path
source=Path(__file__).parent/'sculpt_courier_style_staff.py'
exec(source.read_text().rsplit("\nnames=",1)[0])
for source_role,name,cloth,accent,shoulder,leg in [(2,'CustomerStudent','rust','cream',1.26,.77),(3,'CustomerOffice','plum','white',1.23,.75),(1,'CustomerNeighbor','sage','gold',1.24,.72)]:
 bpy.ops.wm.read_factory_settings(use_empty=True);character(source_role)
 grid[:,:,:int((shoulder+.075)/U)]=0
 box('darkSkin' if source_role==2 else 'skinLight',(0,0,shoulder+.055),(.15,.17,.18))
 for side in [-1,1]:
  x=side*.105;box('charcoal',(x,0,.46),(.16,.20,.52));box('ink',(x,0,.24),(.19,.24,.08));boot(x,0,2 if source_role==2 else 0)
 box(cloth,(0,0,(leg+shoulder)/2),(.39,.32,shoulder-leg));box(accent,(0,-.174,shoulder-.035),(.22,.04,.085))
 for side in [-1,1]:
  x=side*.25;box(cloth,(x,0,shoulder-.18),(.14,.20,.29));box(cloth,(side*.28,-.01,shoulder-.39),(.14,.18,.18));box(accent,(side*.28,-.01,shoulder-.47),(.16,.20,.045));box('darkSkin' if source_role==2 else 'skinLight',(side*.28,-.025,shoulder-.55),(.115,.13,.12))
 box('charcoal',(0,0,leg),(.38,.30,.12))
 if source_role==2:
  box('navy',(0,.22,leg+.25),(.32,.19,.40));box('navyLight',(0,.325,leg+.20),(.27,.045,.18))
  for side in [-1,1]:box('navy',(side*.13,-.18,shoulder-.18),(.055,.045,.33))
 elif source_role==3:
  for side in [-1,1]:box('plumLight',(side*.09,-.19,shoulder-.12),(.07,.035,.22))
  box('brown',(.29,.02,leg+.03),(.14,.20,.23));box('gold',(.29,-.09,leg+.07),(.055,.02,.045))
 else:
  box('cream',(0,-.19,shoulder-.14),(.14,.035,.25))
  for z in [leg+.13,leg+.22,leg+.31]:box('brown',(0,-.22,z),(.0225,.025,.0225))
 obj=mesh_grid('SM_'+name,grid);obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('SM_'+name+'.blend')))
print('THREE_CASUAL_CUSTOMERS_MODELED')
