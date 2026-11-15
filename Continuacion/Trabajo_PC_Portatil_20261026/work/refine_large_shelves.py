import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/Shops';NEW=ROOT/'work/CommercialRefined';NEW.mkdir(exist_ok=True)
for label in ['Market','FreshMarket','Tech','Components','Pharmacy']:
 file=OUT/('SM_'+label+'Interior.blend');bpy.ops.wm.open_mainfile(filepath=str(file));obj=bpy.data.objects['SM_'+label+'Interior'];extras=[];materials={m.name.split('.')[0]:m for m in obj.data.materials}
 def box(p,s,color):
  bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(materials['ENV_'+color]);extras.append(o)
 def product(name,p,scale=.7):
  with bpy.data.libraries.load(str(ROOT/'outputs/DeliveryArt/HighFidelity'/('SM_'+name+'.blend')),link=False) as (a,b):b.meshes=['SM_'+name]
  o=bpy.data.objects.new('Stock_'+name,b.meshes[0]);bpy.context.collection.objects.link(o);o.location=p;o.scale=(scale,)*3;extras.append(o)
 fridge=[]
 for i in range(0,len(obj.data.vertices),8):
  group=list(obj.data.vertices[i:i+8]);lo=Vector([min(v.co[a] for v in group) for a in range(3)]);hi=Vector([max(v.co[a] for v in group) for a in range(3)]);c=(lo+hi)*.5;s=hi-lo
  if abs(s.x-1.2)<.001 and abs(s.y-2.6)<.001 and abs(s.z-2)<.001:
   for v in group:v.co.x=c.x+(v.co.x-c.x)*(.1/1.2)
   box((c.x,c.y,.09),(1.2,2.6,.18),'ivory')
  if abs(s.x-1.1)<.001 and abs(s.y-2.5)<.001 and abs(s.z-2.6)<.001:
   for v in group:v.co.y=c.y+1.2+(v.co.y-c.y)*(.08/2.5)
   fridge.append(tuple(c))
 for x,y,z in fridge:
  for dx in [-.52,.52]:box((x+dx,y,1.3),(.06,2.5,2.6),'steel')
  for zz in [.035,2.565]:box((x,y,zz),(1.1,2.5,.07),'steel')
  for k,zz in enumerate([.35,.95,1.55,2.15]):
   box((x,y,zz),(1.0,2.4,.045),'ivory')
   names=['Salad','Milk','Coffee','Bread'] if label=='FreshMarket' else ['Milk','Rice','Apples','Milk'] if label=='Market' else ['Medicine','Medicine','FirstAid','Medicine'] if label=='Pharmacy' else ['RAM','CircuitBoard','ToolKit','GPU'] if label=='Components' else ['PhoneBox','Headphones','Keyboard','PhoneBox']
   for dx in [-.24,.24]:product(names[k],(x+dx,y-1.04,zz+.035),.65)
 if label=='Components':
  for x in [-7.5,7.5]:
   for j,name in enumerate(['GPU','RAM','CircuitBoard','ToolKit']):product(name,(x,2+j*.65,1.05),.8)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
 for o in extras:o.select_set(True)
 bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.context.scene['open_shelf_refinement']=True
 bpy.ops.wm.save_as_mainfile(filepath=str(NEW/file.name));bpy.ops.export_scene.fbx(filepath=str((NEW/file.name).with_suffix('.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z');print('OPEN_SHELVES_REFINED',label,flush=True)
