import bpy,json,math,numpy as np
from pathlib import Path
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_corrections');O=U.parent/'urban_refresh';st=json.loads((U/'two_sided_stations.json').read_text());v=[];f=[];paths=[]
for cr in st['crossings']:
 s=st['stations'][cr['station_id']];sign=cr['station_end'];ang=math.radians(s['yaw']);t=np.array([math.cos(ang),math.sin(ang)]);rr=np.array([-t[1],t[0]]);q=np.array(s['position'][:2]);a=q+t*2400*sign;b=q+t*np.dot(np.array(cr['position'][:2])-q,t);pts=np.array([a-rr*110,a+rr*110,b+rr*110,b-rr*110]);pts=pts*[.01,-.01];area=sum(pts[i,0]*pts[(i+1)%4,1]-pts[(i+1)%4,0]*pts[i,1] for i in range(4))
 if area<0:pts=pts[::-1]
 i=len(v)
 for z in [-.04,.04]:v.extend([(float(x),float(y),z) for x,y in pts])
 f.extend([tuple(i+j for j in face) for face in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);paths.append(dict(station=cr['station_id'],end=sign,start=a.tolist(),finish=b.tolist()))
mat=bpy.data.materials.get('Bogota_Calles_Voxel')
def make(name,verts,faces,cols):
 old=bpy.data.objects.get(name)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mat);a=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');colors=[]
 for p,c in zip(me.polygons,cols):colors.extend([c]*len(p.loop_indices))
 a.data.foreach_set('color',np.asarray(colors,np.float32).ravel());me.color_attributes.active_color=a;o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(O/'export'/(name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=False,mesh_smooth_type='FACE',colors_type='LINEAR')
make('SM_Bogota_AccesosEstaciones',v,f,[[.55,.36,.18,1]]*len(f));mark=json.loads((U/'junction_marking_geometry.json').read_text());make(mark['name'],mark['verts'],mark['faces'],mark['colors']);signals=json.loads((U/'signal_approach_plan.json').read_text());names=['SM_Bogota_SemaforoPoste','SM_Bogota_SemaforoVerde','SM_Bogota_SemaforoRojo','SM_Bogota_SemaforoPeatonRojo']
with bpy.data.libraries.load(str(O/'Mobiliario_Bogota_Voxel.blend'),link=False) as (src,dst):dst.objects=list(names)
protos={name:o.data for name,o in zip(names,dst.objects)}
for row in signals['heads']:
 for name in ['SM_Bogota_SemaforoPoste','SM_Bogota_SemaforoVerde' if row['signal_group']==0 else 'SM_Bogota_SemaforoRojo','SM_Bogota_SemaforoPeatonRojo']:
  ob=bpy.data.objects.new(name+'_cruce',protos[name]);bpy.context.collection.objects.link(ob);ob.location=(row['position'][0]/100,-row['position'][1]/100,row['position'][2]/100);ob.rotation_euler.z=-math.radians(row['yaw']);ob['SignalGroup']=row['signal_group']
for ob in bpy.data.objects:
 if ob.type=='CURVE':ob.hide_set(True);ob.hide_render=True
bpy.context.scene['Principal']='Trazado y ancho originales conservados';bpy.context.scene['IntersectionDesign']='Calzada continua, aceras recortadas y fases excluyentes';bpy.context.scene['StationAccess']='Dos extremos y ambas aceras';(U/'station_access_paths.json').write_text(json.dumps(paths,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'Mapa_Bogota_Ambientado.blend'));print('TWO_SIDED_STATIONS_AND_STRATEGIC_SIGNALS_BLEND_READY',len(paths),len(signals['heads']))
