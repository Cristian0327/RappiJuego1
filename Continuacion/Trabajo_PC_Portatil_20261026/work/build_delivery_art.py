import bpy, math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'outputs'/'DeliveryArt'
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for name,color in {'Ink':(0.025,0.04,0.05,1),'Mint':(0.06,0.68,0.46,1),'Screen':(0.035,0.085,0.08,1),'Paper':(0.83,0.91,0.82,1),'Gold':(0.98,0.64,0.06,1),'Steel':(0.35,0.43,0.46,1),'Red':(0.75,0.10,0.06,1)}.items():
    m=bpy.data.materials.new('Voxel_'+name);m.diffuse_color=color;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;materials[name]=m
def block(name,pos,size,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(materials[mat]);return o
def export(name):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.join();bpy.context.object.name=name
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
    bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Physical phone is 16 x 8 x 1.2 cm, front along -Y. Square cells, stepped corners.
block('PhoneBody',(0,0,.08),(.08,.012,.15),'Ink')
block('PhoneFrame',(0,-.007,.08),(.072,.004,.142),'Mint')
block('PixelScreen',(0,-.010,.083),(.062,.003,.120),'Screen')
for x in [-.024,0,.024]:
    block('App',(x,-.012,.09),(.014,.002,.014),'Gold' if x==0 else 'Mint')
    block('AppLabel',(x,-.012,.075),(.012,.002,.003),'Paper')
for z in [.036,.048,.118,.13]:block('PixelLine',(0,-.012,z),(.046,.002,.003),'Paper')
block('Speaker',(0,-.012,.146),(.025,.002,.003),'Ink')
block('Home',(0,-.012,.017),(.009,.002,.005),'Gold')
export('SM_PhoneVoxel')
# Bike-compatible motorcycle body: wheels are separate in the playable rider.
block('Engine',(0,0,.60),(.58,.32,.30),'Ink')
block('Tank',(.24,0,.87),(.36,.35,.25),'Mint')
block('Seat',(-.28,0,.90),(.54,.36,.12),'Ink')
block('Tail',(-.53,0,.84),(.15,.36,.22),'Mint')
block('TailLamp',(-.62,0,.89),(.035,.20,.08),'Red')
block('Front',(.49,0,.94),(.16,.35,.36),'Mint')
block('Headlamp',(.585,0,1.02),(.025,.22,.13),'Paper')
block('Handlebar',(.39,0,1.11),(.10,.67,.07),'Steel')
for y in [-.36,.36]:block('Grip',(.40,y,1.11),(.12,.12,.08),'Ink')
for y in [-.19,.19]:block('FootPeg',(-.04,y,.35),(.23,.16,.06),'Steel')
block('Exhaust',(-.35,-.22,.38),(.58,.11,.11),'Steel')
export('SM_MotorcycleBodyVoxel')
print('DELIVERY_VOXEL_ART_READY',str(out),flush=True)
