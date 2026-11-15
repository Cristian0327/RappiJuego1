import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];report={}
catalog=json.loads((root/'outputs/DeliveryArt/Crowd/catalog.json').read_text());staff=json.loads((root/'work/staff_courier_eyes.json').read_text())
files=list(sorted((root/'outputs/DeliveryArt/Crowd').glob('SK_Citizen*.blend')))+list(sorted((root/'outputs/DeliveryArt/People').glob('SK_*.blend')))
for path in files:
 bpy.ops.wm.open_mainfile(filepath=str(path));o=next(o for o in bpy.data.objects if o.type=='MESH');rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');head=rig.data.bones['head'];img=next(n.image for n in o.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');px=list(img.pixels);w,h=img.size;uv=o.data.uv_layers.active
 crowd='Citizen' in path.stem
 if crowd:
  width=catalog[int(path.stem[-2:])]['width'];samples=[(-5.7*2.25*width,-8.2*2.25,62*2.25,True),(5.7*2.25*width,-8.2*2.25,62*2.25,True),(-4*2.25*width,-8.35*2.25,62*2.25,False),(4*2.25*width,-8.35*2.25,62*2.25,False)]
 else:
  z=staff[path.stem]['eye_center_z'];samples=[(-.13125,-.209,z,True),(.13125,-.209,z,True),(-.09,-.2125,z,False),(.09,-.2125,z,False)]
 checks=[]
 for frame in [1,8,16,24]:
  bpy.context.scene.frame_set(frame);ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons],all_triangles=False);deform=rig.pose.bones['head'].matrix@head.matrix_local.inverted()
  for low in [False,True]:
   direction=(deform.to_3x3()@Vector((0,1,.3 if low else 0))).normalized()
   for x,y,z,white in samples:
    point=deform@Vector((x,y,z));hit,normal,index,distance=tree.ray_cast(point-direction*(200 if crowd else 2),direction)
    assert index is not None,(path.stem,frame,'hole')
    p=mesh.polygons[index];coord=mesh.uv_layers.active.data[p.loop_indices[0]].uv;col=px[(min(h-1,int(coord.y*h))*w+min(w-1,int(coord.x*w)))*4:][:3]
    expected=(catalog[int(path.stem[-2:])]['colors']['white' if white else 'eye'] if crowd else ([.89,.87,.79] if white else [.065,.027,.02]))
    passed=max(abs(a-b) for a,b in zip(col,expected))<.012
    checks.append({'frame':frame,'low_angle':low,'white':white,'color':[round(a,3) for a in col],'pass':passed})
  ev.to_mesh_clear()
 report[path.stem]={'checks':checks,'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL'}
fail=[n for n,v in report.items() if v['status']=='FAIL'];report['status']='FAIL' if fail else 'PASS';report['failed_models']=fail
(root/'work/courier_eyes_validation.json').write_text(json.dumps(report,indent=2));print('COURIER_EYES_RESULT',len(files),'models; failed:',fail,flush=True)
assert not fail
