"""Independent voxel sculpt: classic Beetle volumes, not the family-car template."""
import bpy,math,json,hashlib,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from voxel_greedy import emit
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/TrafficDetailed';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
Q=.04;VOX={};NAME='PrivateBeetle'
COL={'Paint':(.25,.53,.72,1),'PaintDark':(.235,.49,.675,1),'PaintLight':(.27,.56,.75,1),'Black':(.013,.017,.023,1),'Rubber':(.025,.032,.04,1),'Tread':(.040,.048,.056,1),'Glass':(.026,.044,.063,1),'GlassLight':(.065,.10,.13,1),'Chrome':(.60,.66,.69,1),'ChromeDark':(.27,.31,.34,1),'Lamp':(.92,.94,.94,1),'Amber':(.95,.29,.015,1),'Tail':(.72,.015,.015,1),'Plate':(.93,.60,.015,1)}
def paint(ix,iy,iz):
 h=(ix//3*17+iy//2*11+iz//2*7)%39
 return 'Paint'
def put(ix,iy,iz,c,b='root'):VOX[ix,iy,iz]=(c,b)
def box(p,s,c,b='root'):
 for ix in range(math.floor((p[0]-s[0]/2)/Q),math.ceil((p[0]+s[0]/2)/Q)):
  for iy in range(math.floor((p[1]-s[1]/2)/Q),math.ceil((p[1]+s[1]/2)/Q)):
   for iz in range(math.floor((p[2]-s[2]/2)/Q),math.ceil((p[2]+s[2]/2)/Q)):put(ix,iy,iz,c,b)
def line(a,b,t,c,bone='root'):
 a=Vector(a);b=Vector(b);n=max(1,int((b-a).length/Q*2))
 for i in range(n+1):box(a.lerp(b,i/n),(t,t,t),c,bone)
def ellipsoid(p,r,c,bone='root'):
 for ix in range(math.floor((p[0]-r[0])/Q),math.ceil((p[0]+r[0])/Q)):
  for iy in range(math.floor((p[1]-r[1])/Q),math.ceil((p[1]+r[1])/Q)):
   for iz in range(math.floor((p[2]-r[2])/Q),math.ceil((p[2]+r[2])/Q)):
    if sum((((i+.5)*Q-p[j])/r[j])**2 for j,i in enumerate((ix,iy,iz)))<=1:put(ix,iy,iz,c,bone)
AXLES=[1.20,-1.20];RADIUS=.31
def profile(x,points):
 for (a,v),(b,w) in zip(points,points[1:]):
  if a<=x<=b:return v+(w-v)*(x-a)/(b-a)
 return 0
ROOF=[(-1.77,.66),(-1.53,.98),(-1.28,1.27),(-1.00,1.49),(-.65,1.62),(-.25,1.66),(.10,1.62),(.33,1.51),(.53,1.24),(.68,1.03)]
HOOD=[(.38,1.035),(.70,1.02),(1.02,.96),(1.32,.85),(1.61,.67),(1.84,.48)]
for ix in range(math.floor(-2.075/Q),math.ceil(2.075/Q)):
 x=(ix+.5)*Q
 for iy in range(math.floor(-.875/Q),math.ceil(.875/Q)):
  y=(iy+.5)*Q
  for iz in range(math.floor(.25/Q),math.ceil(1.68/Q)):
   z=(iz+.5)*Q
   pan=-1.10<x<.53 and abs(y)<(.70-.025*((z-.65)/.4)**2) and .28<z<1.02
   ht=profile(x,HOOD);hw=profile(x,[(.38,.55),(.70,.53),(1.10,.465),(1.5,.36),(1.84,.20)])
   hood=ht>0 and abs(y)<hw and .39<z<ht-.15*(abs(y)/max(hw,.01))**2
   engine=((x+1.23)/.79)**2+(y/.53)**2+((z-.57)/.49)**2<1 and z>.40
   rt=profile(x,ROOF);cw=.63-.10*max(0,(z-1.02)/.64)
   cabin=rt>0 and z>.89 and abs(y)<cw and z<rt-.10*(abs(y)/max(cw,.01))**4
   cr=abs(y)/max(cw,.01)
   windplane=.68-.57*(z-1.03)
   fender=any(((x-a)/(.77 if a>0 else .74))**2+((abs(y)-.635)/.235)**2+((z-.36)/.58)**2<1 for a in AXLES) and abs(y)>.48
   if not(pan or hood or engine or cabin or fender):continue
   if abs(y)>.49 and any((x-a)**2+(z-RADIUS)**2<.355**2 for a in AXLES) and z<.69:continue
   c=paint(ix,iy,iz)
   if cabin:
    front=x>.18 and 1.08<z<1.485 and abs(y)<.43
    side=cr>.93 and -1.20<x<.40 and 1.075<z<min(1.49,rt-.095) and abs(x+.40)>.035
    rear=x<-1.20 and z>1.10 and z<1.34 and abs(y)<.37 and z>rt-.10
    if front or side or rear:c='Glass'
   if z<.32:c='Black'
   if abs(y)>.60 and .39<z<1.08 and (abs(x+.73)<.014 or abs(x-.36)<.014):c='ChromeDark'
   put(ix,iy,iz,c)
# Running boards, thin bumpers and the classic over-riders.
for side in [-1,1]:
 box((0,side*.735,.34),(1.36,.18,.095),'Black');box((0,side*.81,.365),(1.36,.022,.025),'Chrome')
 box((-.60,side*.722,.965),(.105,.027,.027),'Chrome')
 line((.22,side*.60,1.12),(.24,side*.815,1.17),.023,'Chrome')
 ellipsoid((.25,side*.827,1.19),(.084,.034,.062),'Chrome')
 line((-.99,side*.722,.83),(.33,side*.722,.83),.014,'Chrome')
for x in [-2.065,2.065]:
 box((x,0,.425),(.057,1.58,.060),'Chrome')
 for side in [-1,1]:box((x+.02 if x>0 else x-.02,side*.49,.48),(.065,.048,.245),'Chrome')
box((2.07,0,.53),(.032,.34,.125),'Plate');box((-2.04,0,.53),(.032,.34,.125),'Plate')
# Headlights are round pods joined to the curved front fenders.
for side in [-1,1]:
 cy=side*.62;cz=.79;ellipsoid((1.66,cy,cz),(.20,.17,.17),'Paint')
 for iy in range(math.floor((cy-.15)/Q),math.ceil((cy+.15)/Q)):
  y=(iy+.5)*Q
  for iz in range(math.floor((cz-.15)/Q),math.ceil((cz+.15)/Q)):
   z=(iz+.5)*Q;rr=math.hypot(y-cy,z-cz)
   if rr<=.145:box((1.835,y,z),(.026,Q,Q),'Chrome' if rr>.117 else 'Lamp')
 ellipsoid((1.14,side*.64,.913),(.070,.046,.037),'Amber')
 ellipsoid((-1.83,side*.64,.64),(.15,.105,.14),'Paint')
 box((-1.96,side*.64,.64),(.036,.095,.165),'Tail');box((-1.984,side*.64,.69),(.022,.09,.037),'Amber')
# The hood center seam and engine slots follow the sculpted surfaces exactly.
for i in range(45):
 x=.71+i*.024;z=profile(x,HOOD);box((x,0,z+.011),(.022,.012,.016),'Chrome')
for j in range(7):
 x=-1.64+j*.031
 for k in range(27):
  y=-.325+k*.025;value=1-((x+1.23)/.79)**2-(y/.56)**2
  if value>0:z=.57+.49*math.sqrt(value);box((x,y,z+.015),(.014,.026,.012),'Black')
def cabfront(y,z):return profile(z,[(1.03,.68),(1.24,.53),(1.51,.33)])
# No windshield wipers.
# Period-correct tires and smooth circular hubcaps, rather than modern spoke wheels.
bones={'root':((0,0,0),(0,0,.30),None)}
for i,x in enumerate(AXLES):
 for side in [-1,1]:
  cy=side*.70;bone=f'wheel_{i}_{"L" if side<0 else "R"}';bones[bone]=((x,cy,RADIUS),(x,cy+.20,RADIUS),'root')
  for ix in range(math.floor((x-RADIUS)/Q),math.ceil((x+RADIUS)/Q)):
   xx=(ix+.5)*Q-x
   for iz in range(0,math.ceil(2*RADIUS/Q)):
    zz=(iz+.5)*Q-RADIUS;rr=math.hypot(xx,zz);angle=math.atan2(zz,xx)
    for iy in range(math.floor((cy-.095)/Q),math.ceil((cy+.095)/Q)):
     yy=(iy+.5)*Q-cy
     if rr>RADIUS-max(0,abs(yy)-.052)*.4:continue
     mat='Tread' if rr>.25 and (int(angle*25/math.pi)+iy)%4==0 else 'Rubber'
     if side*yy>.05 and rr<.195:mat='ChromeDark' if rr>.175 else 'Chrome'
     if side*yy>.085 and rr<.125:mat='Chrome'
     put(ix,iy,iz,mat,bone)
  ellipsoid((x,cy+side*.108,RADIUS),(.145,.030,.145),'Chrome',bone)
directions=[((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),((-1,0,0),[(0,1,0),(0,0,0),(0,0,1),(0,1,1)]),((0,1,0),[(1,1,0),(0,1,0),(0,1,1),(1,1,1)]),((0,-1,0),[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)]),((0,0,-1),[(0,1,0),(1,1,0),(1,0,0),(0,0,0)])]
V,F,C,VB=emit(VOX,Q)
data=bpy.data.meshes.new('SK_'+NAME);data.from_pydata(V,[],F);data.update();obj=bpy.data.objects.new('SK_'+NAME,data);bpy.context.collection.objects.link(obj)
colors=data.color_attributes.new(name='TrafficColor',type='BYTE_COLOR',domain='CORNER')
for poly,key in zip(data.polygons,C):
 rough=.035 if key in ['Lamp','Tail'] else .35 if key.startswith('Glass') else .55 if key.startswith('Chrome') else .85
 for li in poly.loop_indices:colors.data[li].color=tuple(COL[key][:3])+(rough,)
mat=bpy.data.materials.new('TV_VoxelVertex');mat.use_nodes=True;vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='TrafficColor';bsdf=mat.node_tree.nodes['Principled BSDF'];mat.node_tree.links.new(vc.outputs['Color'],bsdf.inputs['Base Color']);mat.node_tree.links.new(vc.outputs['Alpha'],bsdf.inputs['Roughness']);data.materials.append(mat)
bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='Rig_'+NAME;bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
for name,(h,t,parent) in bones.items():
 eb=rig.data.edit_bones.new(name);eb.head=h;eb.tail=t
 if parent:eb.parent=rig.data.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');groups={b:obj.vertex_groups.new(name=b) for b in bones};ii={b:[] for b in bones}
for i,b in enumerate(VB):ii[b].append(i)
for b,indices in ii.items():groups[b].add(indices,1,'REPLACE')
modifier=obj.modifiers.new('RigidSkin','ARMATURE');modifier.object=rig;obj.parent=rig
for frame,a in [(1,0),(31,math.tau)]:
 for name in bones:
  if name.startswith('wheel_'):pb=rig.pose.bones[name];pb.rotation_mode='XYZ';pb.rotation_euler.y=a;pb.keyframe_insert('rotation_euler',frame=frame)
sc=bpy.context.scene;sc.frame_end=31;sc.frame_set(1);sc['reference_sheet']=str(ROOT/'outputs/DeliveryArt/References/Flota20_Clasicos_SinTexto.png');sc['modeling_method']='Reference constrained longitudinal profiles, narrow descending hood, separate fenders and arched rear roof.'
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(OUT/'SK_PrivateBeetle.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE')
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.view_settings.exposure=-.7
sc.world=bpy.data.worlds.new('Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.59,.64,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32
floor=bpy.data.materials.new('Floor');floor.use_nodes=True;floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.20,.21,.22,1)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.03));bpy.context.object.data.materials.append(floor)
aim=Vector((0,0,.76));bpy.ops.object.camera_add(location=(4.7,-6.0,2.9));cam=bpy.context.object;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.45;sc.camera=cam
for pos,energy,size in [((3,-4,6),500,5),((-4,-1,5),350,5),((0,4,6),500,5)]:
 bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=energy;light.data.size=size;light.rotation_euler=(aim-light.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(OUT/'PrivateBeetle_Review.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'SK_PrivateBeetle.blend'))
if '--no-render' not in sys.argv:bpy.ops.render.render(write_still=True)
manifest=json.loads((OUT/'manifest.json').read_text());manifest=[s for s in manifest if s['name']!=NAME];manifest.append({'name':NAME,'label':'Volkswagen Escarabajo','length_m':4.07,'width_m':1.64,'wheel_radius_m':RADIUS,'voxel_m':Q,'voxel_count':len(VOX),'vertices':len(V),'faces':len(F),'bones':list(bones),'reference':sc['reference_sheet'],'geometry_hash':hashlib.sha256(b''.join(struct.pack('<fff',*v) for v in V)).hexdigest(),'no_text':True,'independent_sculpt':True})
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print('INDEPENDENT_BEETLE_READY',len(V),flush=True)
