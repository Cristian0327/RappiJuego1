import bpy, math, json, random, os
from mathutils import Vector, Quaternion
from collections import defaultdict
from pathlib import Path

OUT = Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs')
OUT.mkdir(exist_ok=True, parents=True)
UNIT = 0.0225
random.seed(32)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 720
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = -0.35
scene.render.image_settings.file_format = 'PNG'
scene.world = bpy.data.worlds.new('Studio | charcoal')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.20,0.20,0.20,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4

COLORS = {
 'orange':'FF5915', 'orange_dark':'E64B0C', 'orange_light':'FF771D',
 'teal':'299F9F', 'teal_light':'39B7B5', 'teal_dark':'187A7B',
 'ice':'BAE9E5', 'ice_light':'D1F3EF', 'ice_shadow':'8ECFCF',
 'skin':'F3B083', 'skin_light':'FFC198', 'skin_dark':'D8936D',
 'hair':'39241D', 'hair_light':'493027', 'hair_dark':'291D19',
 'black':'252423', 'cloth':'302D2C', 'cloth_light':'393332',
 'sole':'57382E', 'white':'F1F4F1', 'eye':'30211D', 'stitch':'69473B',
}
rgb = {k: tuple(int(v[i:i+2],16)/255 for i in (0,2,4)) for k,v in COLORS.items()}
parts = {}
bone_for = {}
def part(name,bone):
    parts[name] = {}
    bone_for[name] = bone
    return name
def box(p, m, x0,x1,y0,y1,z0,z1):
    for x in range(math.floor(x0), math.ceil(x1)):
      for y in range(math.floor(y0), math.ceil(y1)):
       for z in range(math.floor(z0), math.ceil(z1)):
        parts[p][x,y,z] = m
def cut(p,x0,x1,y0,y1,z0,z1):
    for q in list(parts[p]):
        x,y,z=q
        if x0<=x<x1 and y0<=y<y1 and z0<=z<z1: del parts[p][q]
def ellipse(p,m,z0,z1,rx,ry,cy=0,cx=0):
    for x in range(math.floor(cx-rx),math.ceil(cx+rx)):
     for y in range(math.floor(cy-ry),math.ceil(cy+ry)):
      if ((x+.5-cx)/rx)**2+((y+.5-cy)/ry)**2 <= 1:
       box(p,m,x,x+1,y,y+1,z0,z1)

# The reference is approximately 80 half-voxel units tall. Front faces -Y.
p=part('01 | Face and ears','head')
box(p,'skin',-7,7,-7,6,58,68)
box(p,'skin_light',-8,8,-8,4,60,66)
box(p,'skin',-7,7,-8,4,58,60)
box(p,'skin',-6,6,-7,5,57,58)
box(p,'skin_dark',-4,4,-3,3,55,58)
for s in [-1,1]:
    a,b=sorted([s*9,s*11]); box(p,'skin',a,b,-3,1,61,65)
    a,b=sorted([s*9,s*10]); box(p,'skin_light',a,b,-4,-3,61,65)
    a,b=sorted([s*9,s*10]); box(p,'skin_dark',a,b,-3,0,60,61)

p=part('02 | Sculpted voxel hair','head')
ellipse(p,'hair',59,70,10,9,cy=1)
cut(p,-8,8,-9,4,59,67)
cut(p,-7,7,-8,5,58,60)
cut(p,-11,11,-4,1,61,65)
# Dense stepped back silhouette, with deliberate asymmetric tufts.
for z,rx,ry in [(56,4,4),(57,6,6),(58,7,7),(59,8,8),(60,9,8)]:
    ellipse(p,'hair',z,z+1,rx,ry,cy=2)
    cut(p,-8,8,-9,3,z,z+1)
for x0,x1,z,y in [(-10,-8,65,-7),(-8,-6,64,-8),(-6,-4,66,-9),(-4,-2,64,-9),(-2,0,63,-9),(0,2,65,-9),(2,3,67,-9),(5,7,66,-9),(7,9,63,-8),(9,10,61,-5)]:
    box(p,'hair',x0,x1,y,y+2,z,70)
for x0,x1,y0,y1,z0,z1 in [(-12,-10,-1,3,66,69),(10,12,-1,3,66,69),(-10,-8,3,7,62,68),(8,10,3,7,62,67),(-8,-6,7,9,59,65),(6,8,7,9,59,64),(-5,-2,9,10,60,64),(0,3,9,10,58,63),(3,6,8,10,60,66)]:
    box(p,'hair_light' if x0%3==0 else 'hair',x0,x1,y0,y1,z0,z1)

p=part('03 | Orange cap','head')
for z0,z1,rx,ry in [(68,70,10,9),(70,76,10,9),(76,78,8,8),(78,79,6,6)]:
    ellipse(p,'orange',z0,z1,rx,ry,cy=1)
# Flat raised forehead panel and the characteristic long stepped visor.
box(p,'orange',-8,8,-8,-5,70,77)
box(p,'orange',-6,6,-7,-4,77,79)
box(p,'orange',-10,-8,-6,-2,69,76)
box(p,'orange',8,10,-6,-2,69,76)
for x0,x1,front,z0 in [(-10,-8,-11,68),(-8,-6,-13,69),(-6,-4,-15,69),(-4,4,-16,70),(4,6,-15,69),(6,8,-13,69),(8,10,-11,68)]:
    box(p,'orange',x0,x1,front,-6,z0,z0+1)
    box(p,'orange_dark',x0,x1,front,-7,z0-1,z0)
# Rear opening and adjustment strap, visible from behind.
for z0,z1,w in [(68,71,4),(71,73,3),(73,74,2)]:
    cut(p,-w,w,6,12,z0,z1)
box(p,'hair_dark',-4,4,8,9,68,72)
box(p,'black',-8,8,9,10,66,68)
box(p,'hair_light',-7,7,10,11,66,67)
box(p,'black',-2,2,-1,3,79,80)
box(p,'black',-2,2,6,8,77,79)
box(p,'black',-1,1,8,10,77,79)

# Graphic eye and cap details are deliberately clean, unshaded pixel shapes.
details=[]
def detail(name,material,bounds,bone='head'):
    details.append((name,material,bounds,bone))
detail('Cap badge / pale frame','ice_light',(-4,4,-8.4,-8.02,72,78.5))
detail('Cap badge / dark inset','black',(-2,2,-8.56,-8.4,73,76.8))
detail('Cap badge / orange pixel','orange_light',(-.85,.85,-8.70,-8.56,74.1,75.8))
detail('Left eyebrow','hair_dark',(-6.3,-3.1,-8.19,-8.01,64.9,65.8))
detail('Right eyebrow','hair_dark',(3.0,6.8,-8.19,-8.01,64.9,65.8))
detail('Left eye / white','white',(-6.2,-3,-8.20,-8.01,61,64))
detail('Right eye / white','white',(3,6.2,-8.20,-8.01,61,64))
detail('Left eye / iris','eye',(-5.2,-3,-8.35,-8.20,61,64))
detail('Right eye / iris','eye',(3,5.2,-8.35,-8.20,61,64))
detail('Left eye / upper lid','hair_dark',(-6.3,-3,-8.4,-8.2,63.6,64.05))
detail('Right eye / upper lid','hair_dark',(3,6.3,-8.4,-8.2,63.6,64.05))
detail('Small square nose','skin_light',(-.8,1.2,-8.8,-8.0,59.8,61.4))
detail('Under-nose pixel','skin',(-.8,1.2,-8.83,-8.8,59.8,60.1))
detail('Neutral mouth','skin_dark',(-1.1,1.0,-8.1,-8.01,59.15,59.27))

p=part('04 | Jacket torso','chest')
box(p,'teal',-7,7,-4,5,38,53)
box(p,'teal_light',-4,4,-5,-4,39,53)
box(p,'teal',-8,8,-3,4,39,50)
box(p,'orange',-7,-5,-5,5,51,55)
box(p,'orange',5,7,-5,5,51,55)
box(p,'orange',-8,-6,-4,4,49,52)
box(p,'orange',6,8,-4,4,49,52)
box(p,'ice',-4,-1,-5,-4,38,45)
box(p,'ice',1,4,-5,-4,38,45)
box(p,'ice_light',-4,-1,-6,-5,37,39)
box(p,'ice_light',1,4,-6,-5,37,39)
box(p,'teal_dark',-1,1,-5,-4,37,51)
box(p,'teal_light',-1,0,-6,-5,37,51)
for s in [-1,1]:
    a,b=sorted([5*s,8*s]); box(p,'teal_dark',a,b,-3,4,37,39)
    a,b=sorted([6*s,8*s]); box(p,'ice',a,b,-5,-3,37,39)
    a,b=sorted([5*s,7*s]); box(p,'orange',a,b,-6,-4,34,37)
    a,b=sorted([4*s,5*s]); box(p,'stitch',a,b,-5,-4,39,43)
detail('Zipper pull','ice_shadow',(-.45,.45,-6.08,-5.9,48.8,50),'chest')

p=part('05 | High turquoise collar','chest')
box(p,'teal',-5,5,-3,5,52,56)
box(p,'teal_light',-5,5,-5,-3,54,56)
box(p,'teal',-5,5,-6,-4,52,54)
box(p,'teal_dark',-4,4,-4,4,55,56)
box(p,'teal_light',-5,-4,-4,4,53,56)
box(p,'teal_light',4,5,-4,4,53,56)
box(p,'teal',-6,6,3,6,52,56)

p=part('06 | Harness and shoulder straps','chest')
for s in [-1,1]:
    a,b=sorted([6*s,10*s]); box(p,'black',a,b,-6,-4,41,52)
    a,b=sorted([6*s,9*s]); box(p,'cloth',a,b,-7,-5,43,51)
    a,b=sorted([7*s,10*s]); box(p,'black',a,b,-6,-4,40,43)
    a,b=sorted([7*s,9*s]); box(p,'black',a,b,-5,-3,39,41)
    a,b=sorted([7*s,10*s]); box(p,'black',a,b,-3,5,52,53)
    a,b=sorted([7*s,9*s]); box(p,'cloth',a,b,-1,3,53,54)
    a,b=sorted([5*s,6*s]); box(p,'stitch',a,b,-6,-5,44,47)
    a,b=sorted([5*s,7*s]); box(p,'black',a,b,-6,-5,46,48)

for s,suf in [(1,'L'),(-1,'R')]:
    def sb(p,m,a,b,y0,y1,z0,z1):
        x0,x1=sorted((s*a,s*b)); box(p,m,x0,x1,y0,y1,z0,z1)
    p=part('07 | Upper sleeve.'+suf,'upper_arm.'+suf)
    sb(p,'orange',9,12,-3,4,47,52)
    sb(p,'orange',10,14,-4,4,45,50)
    sb(p,'orange_light',12,14,-3,3,47,50)
    sb(p,'teal_light',10,14,-4,4,43,45)
    sb(p,'orange',12,14,-3,3,45,47)
    p=part('08 | Ice sleeve.'+suf,'forearm.'+suf)
    sb(p,'ice',10,14,-4,4,38,45)
    sb(p,'ice',11,15,-5,4,36,43)
    sb(p,'ice_light',13,16,-5,3,34,39)
    sb(p,'ice_light',14,17,-5,3,34,37)
    sb(p,'teal',10,12,-4,4,37,41)
    sb(p,'ice_shadow',12,13,-5,4,37,41)
    sb(p,'black',10,16,-4,4,31,34)
    sb(p,'cloth',10,16,-5,-4,31,34)
    p=part('09 | Hand.'+suf,'hand.'+suf)
    sb(p,'skin',11,15,-3,2,28,31)
    sb(p,'skin_light',11,15,-3,1,27,29)
    sb(p,'skin',12,14,-4,-3,27,29)
    sb(p,'skin_dark',11,12,-3,0,27,28)
    sb(p,'skin_light',10,11,-4,-1,28,30)
    p=part('11 | Cargo thigh.'+suf,'thigh.'+suf)
    sb(p,'cloth',1,8,-3,5,18,30)
    sb(p,'cloth_light',2,7,-4,-3,18,29)
    sb(p,'black',1,2,-3,4,18,27)
    sb(p,'cloth_light',7,9,-2,4,20,26)
    sb(p,'cloth',6,9,-4,-2,20,26)
    sb(p,'orange',8,10,-2,3,20,24)
    sb(p,'stitch',6,8,-4,-3,26,28)
    p=part('12 | Shin and ankle.'+suf,'shin.'+suf)
    sb(p,'cloth',2,8,-3,5,10,18)
    sb(p,'cloth_light',1,9,-4,5,14,18)
    sb(p,'cloth',2,9,-4,5,10,12)
    sb(p,'black',3,8,-3,4,8,10)
    p=part('13 | Sneaker.'+suf,'foot.'+suf)
    sb(p,'sole',2,10,-8,5,0,1)
    sb(p,'sole',3,9,-9,-8,0,1)
    sb(p,'white',2,10,-8,5,1,3)
    sb(p,'white',3,9,-9,-8,1,3)
    sb(p,'teal',3,9,-7,4,3,6)
    sb(p,'black',4,8,-7,-4,4,6)
    sb(p,'ice',4,8,-3,4,6,10)
    sb(p,'ice_light',4,8,-4,-3,8,10)
    sb(p,'orange',3,9,-4,4,6,8)
    sb(p,'orange_light',2,4,-3,3,6,8)
    sb(p,'orange',8,10,-3,3,6,8)
    sb(p,'teal_light',3,5,-6,-4,3,5)
    sb(p,'teal_dark',7,9,-6,-4,3,5)
    sb(p,'ice',3,9,-7,-6,3,4)
    sb(p,'teal_light',4,8,4,5,6,8)
    sb(p,'black',4,8,4,5,3,6)

p=part('10 | Waist and pelvis','pelvis')
box(p,'cloth',-8,8,-4,5,30,37)
box(p,'black',-8,8,-4,5,30,31)
box(p,'cloth_light',-4,0,-5,-4,31,37)
box(p,'cloth_light',1,4,-5,-4,31,37)
box(p,'black',0,1,-5,-4,31,37)
box(p,'cloth',-2,2,-3,4,27,30)
box(p,'black',-8,-6,-4,4,31,34)
box(p,'black',6,8,-4,4,31,34)

p=part('14 | Backpack / removable','chest')
box(p,'black',-9,9,5,13,33,51)
box(p,'teal_dark',-9,9,7,14,36,49)
box(p,'teal',-7,7,13,15,35,49)
box(p,'orange',-7,7,13,15,33,35)
box(p,'orange',-7,7,13,15,47,49)
box(p,'orange',-7,7,12,14,50,51)
box(p,'teal_light',-7,7,11,14,51,52)
box(p,'black',-9,-7,12,16,33,51)
box(p,'black',7,9,12,16,33,51)
box(p,'black',-9,9,12,16,32,33)
box(p,'black',-10,10,13,16,49,51)
box(p,'black',-8,8,6,14,51,52)
box(p,'orange',-7,7,12,15,51,52)
for s in [-1,1]:
    a,b=sorted([s*8,s*9]); box(p,'orange',a,b,8,13,33,35)
    box(p,'teal',a,b,8,13,35,48)
    a,b=sorted([s*9,s*10]); box(p,'black',a,b,7,10,34,49)
    a,b=sorted([s*8,s*9]); box(p,'orange',a,b,9,13,48,50)
box(p,'black',-3,-1,7,10,52,54)
box(p,'black',1,3,7,10,52,54)
box(p,'orange',-2,2,8,10,54,55)
box(p,'orange',-3,3,10,12,53,54)
box(p,'orange_light',-2,2,12,14,52,53)

# Remove overlaps according to authored layer order; each anatomical object stays closed.
occupied={}
for p,vs in parts.items():
    for q,m in vs.items(): occupied[q]=(p,m)
for p in parts:
    parts[p]={q:m for q,m in parts[p].items() if occupied[q][0]==p}

character=bpy.data.collections.new('CHARACTER | game export')
scene.collection.children.link(character)
studio=bpy.data.collections.new('STUDIO | preview only')
scene.collection.children.link(studio)
refs=bpy.data.collections.new('REFERENCE | original three views')
scene.collection.children.link(refs)

# Greedy surface extraction: a rectangle replaces coplanar voxel faces of equal color.
# Texture carries the subtle square-grid variation without wasting geometry.
surfaces=[]
for p,vox in parts.items():
    buckets=defaultdict(dict)
    for q,m in vox.items():
      for axis in range(3):
       a=(axis+1)%3; b=(axis+2)%3
       for sign in (-1,1):
        n=list(q);n[axis]+=sign
        if tuple(n) in vox: continue
        plane=q[axis]+(sign==1)
        buckets[axis,sign,plane][q[a],q[b]]=m
    for (axis,sign,plane),mask in buckets.items():
      while mask:
        u,v=min(mask,key=lambda q:(q[1],q[0])); m=mask[u,v]
        w=1
        while mask.get((u+w,v))==m: w+=1
        h=1
        while all(mask.get((u+i,v+h))==m for i in range(w)):h+=1
        for i in range(w):
         for j in range(h): del mask[u+i,v+j]
        surfaces.append({'p':p,'m':m,'axis':axis,'sign':sign,'plane':plane,'u':u,'v':v,'w':w,'h':h})
print('GREEDY_QUADS',len(surfaces),flush=True)

# Pack rectangular patches, 4 texels per half voxel, into a single power-of-two atlas.
TEXELS=4;PAD=2; atlas_size=1024
def pack(sz):
    x=y=PAD; rowh=0
    for f in sorted(surfaces,key=lambda f:f['h'],reverse=True):
        pw=f['w']*TEXELS+2*PAD;ph=f['h']*TEXELS+2*PAD
        if x+pw>sz: x=PAD;y+=rowh;rowh=0
        if y+ph>sz-16:return False
        f['tx']=x+PAD;f['ty']=y+PAD
        x+=pw;rowh=max(rowh,ph)
    return True
while not pack(atlas_size):atlas_size*=2
import numpy as np
pixels=np.ones((atlas_size,atlas_size,4),dtype=np.float32)
pixels[:,:,:3]=.2
for f in surfaces:
    col=np.array(rgb[f['m']])
    for j in range(-PAD,f['h']*TEXELS+PAD):
     for i in range(-PAD,f['w']*TEXELS+PAD):
        si=max(0,min(f['w']*TEXELS-1,i));sj=max(0,min(f['h']*TEXELS-1,j))
        wu=f['u']+si/TEXELS;wv=f['v']+sj/TEXELS
        uu=math.floor(wu/2);vv=math.floor(wv/2)
        noise=((uu*73856093 ^ vv*19349663 ^ f['plane']*83492791)&255)/255
        factor=0.988+noise*.024
        # Only a very fine dark seam; surfaces retain a unified voxel appearance.
        if (si+f['u']*TEXELS)%(2*TEXELS)==0 or (sj+f['v']*TEXELS)%(2*TEXELS)==0: factor*=.972
        pixels[f['ty']+j,f['tx']+i,:3]=np.clip(col*factor,0,1)
swatch={}
for ci,(m,col) in enumerate(rgb.items()):
    sx=ci*8;sy=atlas_size-8
    pixels[sy:sy+8,sx:sx+8,:3]=col
    swatch[m]=((sx+4)/atlas_size,(sy+4)/atlas_size)
tex=bpy.data.images.new('Character_Atlas_1024',width=atlas_size,height=atlas_size,alpha=True)
tex.pixels.foreach_set(pixels.ravel())
tex.filepath_raw=str(OUT/'character_atlas.png');tex.file_format='PNG';tex.save();tex.pack()
mat=bpy.data.materials.new('Character | one atlas material');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.87
bs.inputs['Specular IOR Level'].default_value=.18
im=mat.node_tree.nodes.new('ShaderNodeTexImage');im.image=tex;im.interpolation='Closest'
mat.node_tree.links.new(im.outputs['Color'],bs.inputs['Base Color'])

objects=[]
def new_mesh(name,verts,faces,uvs,bone):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='AtlasUV')
    for poly,pts in zip(mesh.polygons,uvs):
        for li,pt in zip(poly.loop_indices,pts):uv.data[li].uv=pt
    ob=bpy.data.objects.new(name,mesh);character.objects.link(ob);ob.data.materials.append(mat)
    vg=ob.vertex_groups.new(name=bone);vg.add(list(range(len(verts))),1,'REPLACE')
    ob['rigid_bone']=bone;objects.append(ob)
    return ob
for p in parts:
    verts=[];faces=[];uvs=[];vid={}
    for f in [f for f in surfaces if f['p']==p]:
        axis=f['axis'];a=(axis+1)%3;b=(axis+2)%3
        rect=[(0,0),(f['w'],0),(f['w'],f['h']),(0,f['h'])]
        if f['sign']<0: rect.reverse()
        ids=[];tu=[]
        for du,dv in rect:
            q=[0,0,0];q[axis]=f['plane'];q[a]=f['u']+du;q[b]=f['v']+dv;q=tuple(q)
            if q not in vid:vid[q]=len(verts);verts.append(tuple(v*UNIT for v in q))
            ids.append(vid[q]);tu.append(((f['tx']+du*TEXELS)/atlas_size,(f['ty']+dv*TEXELS)/atlas_size))
        faces.append(ids);uvs.append(tu)
    new_mesh(p,verts,faces,uvs,bone_for[p])

# All small face and emblem details share an existing color swatch in the atlas.
detail_by_bone=defaultdict(list)
for d in details:detail_by_bone[d[3]].append(d)
for bone,ds in detail_by_bone.items():
    verts=[];faces=[];uvs=[]
    for name,m,(x0,x1,y0,y1,z0,z1),_ in ds:
        start=len(verts)
        verts.extend([(x*UNIT,y*UNIT,z*UNIT) for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]])
        for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            faces.append([start+i for i in face]);uvs.append([swatch[m]]*4)
    new_mesh('15 | Pixel details / '+bone,verts,faces,uvs,bone)

# Rigid skinning: each vertex follows one bone, preserving square corners.
arm=bpy.data.armatures.new('Voxel skeleton');rig=bpy.data.objects.new('RIG | rigid voxel humanoid',arm);character.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
bones={}
def bone(name,head,tail,parent=None):
    eb=arm.edit_bones.new(name);eb.head=Vector(head)*UNIT;eb.tail=Vector(tail)*UNIT
    if parent:eb.parent=bones[parent]
    eb.use_deform=name!='root';bones[name]=eb
bone('root',(0,0,0),(0,0,8))
bone('pelvis',(0,0,29),(0,0,37),'root')
bone('chest',(0,0,37),(0,0,54),'pelvis')
bone('head',(0,0,55),(0,0,71),'chest')
for s,suf in [(1,'L'),(-1,'R')]:
    bone('upper_arm.'+suf,(s*10,0,51),(s*12,0,44),'chest')
    bone('forearm.'+suf,(s*12,0,44),(s*13,0,31),'upper_arm.'+suf)
    bone('hand.'+suf,(s*13,0,31),(s*13,0,27),'forearm.'+suf)
    bone('thigh.'+suf,(s*5,0,30),(s*5,0,18),'pelvis')
    bone('shin.'+suf,(s*5,0,18),(s*5,0,9),'thigh.'+suf)
    bone('foot.'+suf,(s*5,0,9),(s*5,-6,3),'shin.'+suf)
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True;arm.display_type='STICK'
for ob in objects:
    ob.parent=rig
    mod=ob.modifiers.new('Rigid voxel deformation','ARMATURE');mod.object=rig
    ob['game_asset']=True
rig['notes']='Rigid skinning: one bone per vertex. Neutral pose matches reference. No animation clips included.'
rig['height_m']=80*UNIT
rig['forward_axis']='-Y in Blender; GLB export uses Y up'

# The supplied reference stays packed in the native project, excluded from export.
refpath=r'C:/Users/CRISTIAN/AppData/Local/Temp/codex-clipboard-d72ca8d3-40c0-4a7a-89d9-3aad6731f4e4.png'
refim=bpy.data.images.load(refpath);refim.pack()
ref=bpy.data.objects.new('Original reference | three views',None);refs.objects.link(ref)
ref.empty_display_type='IMAGE';ref.data=refim;ref.empty_display_size=3
ref.rotation_euler=(math.pi/2,0,0);ref.location=(3,1,1)
ref.hide_render=True;refs.hide_viewport=True

def material(name,c):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95
    return m
floor_mat=material('Studio floor',(.025,.024,.024))
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.008));floor=bpy.context.object
for co in list(floor.users_collection):co.objects.unlink(floor)
studio.objects.link(floor);floor.name='Studio floor';floor.data.materials.append(floor_mat)
def area(name,location,power,size,color):
    d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);studio.objects.link(o)
    o.location=location;d.energy=power;d.shape='DISK';d.size=size;d.color=color
    o.rotation_euler=(Vector((0,0,.95))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key / softbox',(-3,-4,5),450,4,(1,.88,.77))
area('Fill / softbox',(3,-2,2.5),270,3,(.78,.92,1))
area('Rim / softbox',(1,3,4),550,3,(1,.93,.86))
def camera(name,pos,target,ortho):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);studio.objects.link(o)
    o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.type='ORTHO';d.ortho_scale=ortho;d.lens=60
    return o
cameras={
 'front':camera('Camera | FRONT',(0,-7,.93),(0,0,.93),2.05),
 'side':camera('Camera | SIDE',(7,0,.93),(0,0,.93),2.05),
 'back':camera('Camera | BACK',(0,7,.93),(0,0,.93),2.05),
 'hero':camera('Camera | HERO',(3,-6,2.35),(0,0,.95),2.12),
}
scene.camera=cameras['hero']

# Neutral file opens ready to inspect, with stage hidden in viewport only.
for ob in list(bpy.context.selected_objects):ob.select_set(False)
bpy.context.view_layer.objects.active=objects[0]
for ob in studio.objects:ob.hide_set(True)
rig.hide_set(True)
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
    a.spaces.active.shading.type='MATERIAL'
    a.spaces.active.overlay.show_floor=False
    a.spaces.active.overlay.show_axis_x=False
    a.spaces.active.overlay.show_axis_y=False
    a.spaces.active.region_3d.view_distance=2.6
    a.spaces.active.region_3d.view_location=(0,0,.93)
    a.spaces.active.region_3d.view_rotation=cameras['hero'].rotation_euler.to_quaternion()
    a.spaces.active.region_3d.view_perspective='ORTHO'

tris=sum(len(o.data.polygons)*2 for o in objects)
stats={'height_m':1.8,'editable_mesh_objects':len(objects),'export_mesh_objects':1,'triangles':tris,'vertices':sum(len(o.data.vertices) for o in objects),'materials':1,'atlas_size':[atlas_size,atlas_size],'bones':len(arm.bones),'animation_clips':0,'voxel_unit_m':UNIT,'forward':'-Y','rig':'rigid, one bone per vertex'}
(OUT/'asset_info.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print('ASSET_STATS',stats,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'voxel_explorer.blend'))
rig.hide_set(False)
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.join()
joined=bpy.context.object
joined.name='Voxel Explorer | optimized skinned mesh'
objects=[joined]
rig.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'voxel_explorer.glb'),export_format='GLB',use_selection=True,export_animations=False,export_yup=True,export_apply=False,export_skins=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
for ob in objects+[rig]:ob.select_set(False)
rig.hide_set(True)
# File is already saved. Rendering affects only this background process.
for key in ['front','side','back','hero']:
    scene.camera=cameras[key]
    scene.render.filepath=str(OUT/f'view_{key}.png')
    bpy.ops.render.render(write_still=True)
    print('RENDER_DONE',key,flush=True)
print('BUILD_COMPLETE',flush=True)
