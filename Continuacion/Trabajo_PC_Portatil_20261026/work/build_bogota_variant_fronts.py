exec((__import__('pathlib').Path(__file__).parent/'build_cohesive_shops.py').read_text().split("for kind,label in enumerate")[0])
COL.update({'cobalt':(.015,.12,.60,1),'cyan':(.01,.64,.83,1),'brick':(.47,.19,.105,1),'bricklight':(.62,.26,.14,1),'graphite':(.11,.13,.15,1),'mortar':(.24,.22,.20,1),'tile':(.84,.84,.80,1),'glass':(.73,.88,.94,.12),'warm':(1,.65,.17,1)})
def export_review(name,label):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(V,[],F);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 for key,c in COL.items():
  mat=bpy.data.materials.new('ENV_'+key);mat.diffuse_color=c;mat.use_nodes=True;n=mat.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=c;n.inputs['Roughness'].default_value=.72
  if key=='glass':n.inputs['Transmission Weight'].default_value=1;n.inputs['IOR'].default_value=1.05;n.inputs['Roughness'].default_value=.03;n.inputs['Alpha'].default_value=.12
  if key in ['warm','cyan']:n.inputs['Emission Color'].default_value=c;n.inputs['Emission Strength'].default_value=.6
  mesh.materials.append(mat)
 for poly,i in zip(mesh.polygons,M):poly.material_index=i
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 sc=bpy.context.scene;sc['reference']='../References/Comercios_TresVistas_2026-10-05.png';sc['commercial_dimensions']='10x8x3.6m; centered clear door'
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 # Review assembly only: interior is exported independently, avoiding duplicate geometry in Unreal.
 with bpy.data.libraries.load(str(OUT/('SM_'+label+'Interior.blend')),link=False) as (a,b):b.objects=[n for n in a.objects if n.startswith('SM_'+label+'Interior')]
 for interior in b.objects:
  if interior:bpy.context.collection.objects.link(interior);interior.location.y+=4
 sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=-.7
 sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
 sc.world=bpy.data.worlds.new('Review');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.85,.89,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 bpy.ops.object.camera_add(location=(-13,-17,11));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=17;cam.rotation_euler=(Vector((0,3,1.7))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
 for pos,energy,size in [((-6,-5,10),1800,8),((7,-1,8),1400,7),((0,5,10),1600,6)]:
  bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=energy;l.data.size=size;l.rotation_euler=(Vector((0,3,1))-l.location).to_track_quat('-Z','Y').to_euler()
 sc.render.filepath=str(OUT/(name+'_ReferenceReview.png'));bpy.ops.render.render(write_still=True)
 import bmesh
 for item in [o for o in bpy.context.scene.objects if o.type=='MESH']:
  bm=bmesh.new();bm.from_mesh(item.data);faces=[]
  for face in bm.faces:
   center=item.matrix_world@face.calc_center_median()
   if center.z>3.43 or (center.x<-4.74 and center.y>.25):faces.append(face)
  bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(item.data);bm.free()
 sc.render.filepath=str(OUT/(name+'_InteriorCutaway.png'));bpy.ops.render.render(write_still=True);print('REFERENCE_STORE_DONE',label,flush=True)
for kind,label in [(0,'FreshMarket'),(1,'FastFood'),(2,'Components')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];M=[];library={}
 surface=['tile','brick','graphite','tile','sage'][kind];accent=['leaf','red','red','cobalt','leaf'][kind]
 # Walls: separate brick courses or staggered ceramic/panel tiles, matching the sheets.
 for side in [-1,1]:
  x=side*5
  box((x,4,1.8),(.14,8,3.6),'mortar' if kind==1 else surface)
  pitchz=.18 if kind==1 else .42;pitchy=.38 if kind==1 else .75
  for row in range(int(3.6/pitchz)):
   for col in range(int(8/pitchy)):
    y=col*pitchy+pitchy*.5+(pitchy*.5 if row%2 else 0)
    if y>7.95:continue
    box((x+side*.085,y,.08+row*pitchz),(.035,pitchy-.025,pitchz-.018),'bricklight' if kind==1 and (row*7+col)%9==0 else surface)
 box((0,8,1.8),(10,.15,3.6),surface)
 # Window spans have actual transparent glazing; doorway remains unobstructed.
 for x in [-3,3]:
  box((x,0,.22),(4,.20,.44),'steel');box((x,0,3.12),(4,.22,.96),surface)
  box((x,-.03,1.58),(3.62,.025,2.25),'glass')
  for dx in [-1.82,0,1.82]:box((x+dx,-.10,1.57),(.085,.12,2.30),'ink')
  for z in [.45,2.73]:box((x,-.10,z),(3.70,.12,.085),'ink')
  for row in range(3):
   for col in range(8):box((x-1.75+col*.5,-.13,2.92+row*.23),(.47,.045,.20),surface)
 for x in [-4.92,-1.06,1.06,4.92]:box((x,-.05,1.53),(.16,.24,3.06),'ink' if kind in [1,2] else surface)
 box((0,0,3.20),(2,.20,.8),surface)
 for x in [-1.06,1.06]:box((x,-.16,1.4),(.06,.09,2.8),'cyan' if kind==2 else 'ink')
 # Deep stepped awning, individual fascia blocks, roof parapets and contrasting trim.
 for i in range(20):box((-4.75+i*.5,-.46,2.95),(.49,1.05,.32),accent)
 box((0,-1.0,2.83),(10,.075,.08),'warm' if kind==1 else 'ivory')
 box((0,4,3.69),(10.2,8.2,.14),'graphite')
 for x in [-5,5]:box((x,4,3.86),(.18,8.2,.28),accent if kind==3 else 'graphite')
 box((0,8,3.86),(10.2,.18,.28),'graphite');box((0,0,3.84),(10.2,.22,.32),accent if kind==3 else 'graphite')
 if kind==0:
  for x in [-4.7+i*.22 for i in range(44)]:box((x,-.13,3.58),(.065,.10,.92),'graphite')
  for i in range(8):box((3.8+i*.14,-.18,3.78),(.06,.14,1.1),'honey')
 if kind==3:
  box((2.1,-.06,3.72),(3.3,.30,.73),'cobalt');box((2.1,-.23,3.33),(3.25,.035,.48),'tile')
  box((3.6,-.28,3.47),(.48,.08,.16),'cyan');box((3.6,-.28,3.63),(.16,.08,.16),'cyan');box((3.6,-.28,3.31),(.16,.08,.16),'cyan')
 if kind==2:
  for x in [-3.9,3.9]:
   box((x,-.20,3.38),(1.6,.12,.53),'ink')
   for i in range(5):box((x,-.29,3.19+i*.095),(1.42,.03,.03),'steel')
  box((0,-.22,3.67),(3.6,.40,1.2),'graphite')
 if kind==1:
  for x in [-4.72,4.72]:
   for row in range(22):box((x,-.14,.1+row*.17),(.40,.18,.155),'bricklight' if row%4==0 else 'brick')
  for x in [-2.8,2.8]:box((x,-.20,3.49),(2.2,.06,.12),'warm')
 # Wall lamps, modular planters, bollards, service access, AC grille and safety ladder.
 for x in [-4.35,4.35]:
  box((x,-.23,2.35),(.28,.16,.42),'graphite');box((x,-.33,2.35),(.19,.04,.26),'warm')
  box((x,-.65,.24),(.70,.70,.48),'steel')
  for i in range(12):
   a=i*2.4;box((x+math.cos(a)*.19,-.65+math.sin(a)*.19,.52+(i%4)*.10),(.20,.20,.22),'leaf' if i%3 else 'sage')
 for x in [-4.85,-1.50,1.50,4.85]:box((x,-1.15,.31),(.12,.12,.62),'steel');box((x,-1.15,.58),(.13,.13,.05),'ivory')
 box((-1.5,8.12,1.18),(1.25,.08,2.25),'steel');box((-1.0,8.18,1.15),(.06,.05,.13),'ivory')
 for x in [1.8,3.8]:
  box((x,5.5,4.05),(1.5,1,.65),'steel');box((x,4.97,4.05),(1.28,.035,.46),'graphite')
  for i in range(9):box((x-.58+i*.14,4.94,4.05),(.045,.035,.43),'steel')
 for x in [4.25,4.75]:box((x,8.15,2.25),(.07,.08,4.4),'steel')
 for i in range(14):box((4.5,8.15,.25+i*.30),(.55,.08,.05),'steel')
 export_review('SM_'+label+'Front',label)
