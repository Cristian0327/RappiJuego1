"""Keep accessible ramp collision while making road paint nonphysical."""
from pathlib import Path
import unreal,json,sys
root=Path(__file__).resolve().parent.parent
p=root/'scripts/traffic_gameplay_repair/implement.py';exec(compile(p.read_text().split('# Recovery never')[0],str(p),'exec'))
asset='/Game/World/BogotaUrban/Geometry/SM_Bogota_CruceAccesible';mesh=unreal.load_asset(asset)
backup='/Game/QA/Backups/SM_Bogota_CruceAccesible_PreTrafficFix'
if not unreal.EditorAssetLibrary.does_asset_exist(backup):assert unreal.EditorAssetLibrary.duplicate_asset(asset,backup)
before=mesh.get_bounds();before_size=list(before.box_extent.to_tuple());before_center=list(before.origin.to_tuple())
full=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,full,unreal.GeometryScriptCopyMeshFromAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL))
def geometry(dm):
    _,vs,_=unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dm,False);vertices=unreal.GeometryScript_List.convert_vector_list_to_array(vs)
    _,ts,_=unreal.GeometryScript_MeshQueries.get_all_triangle_indices(dm,False);triangles=unreal.GeometryScript_List.convert_triangle_list_to_array(ts)
    return vertices,triangles
vertices,triangles=geometry(full)
limits=dict(min=[min(getattr(v,k) for v in vertices) for k in ['x','y','z']],max=[max(getattr(v,k) for v in vertices) for k in ['x','y','z']])
assert 15<limits['max'][2]<25 and 1400<limits['max'][1]<1700,limits
assert max(abs((limits['max'][i]-limits['min'][i])/2-before_size[i]) for i in range(3))<.1,(limits,before_size)
paint=[]
for t in triangles:
    if min(t.x,t.y,t.z)<0:continue
    q=[vertices[t.x],vertices[t.y],vertices[t.z]]
    if min(v.z for v in q)>6 and max(v.z for v in q)<7:
        center=tuple(sum(getattr(v,k) for v in q)/3 for k in ['x','y','z'])
        if abs(center[0])<400 and abs(center[1])<1000:paint.append(center)
assert paint
paint_point=min(paint,key=lambda q:q[0]*q[0]+q[1]*q[1])
# Bake the legacy import scale into the same visual geometry, in centimeters.
unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(full,mesh,unreal.GeometryScriptCopyMeshToAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshWriteLOD())
after=mesh.get_bounds();assert max(abs(a-b) for a,b in zip(before_size,after.box_extent.to_tuple()))<.1
collision=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,collision,unreal.GeometryScriptCopyMeshFromAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL))
cv,ct=geometry(collision);remove=[i for i,t in enumerate(ct) if min(t.x,t.y,t.z)>=0 and max(cv[j].z for j in [t.x,t.y,t.z])<7]
unreal.GeometryScript_MeshEdits.delete_triangles_from_mesh(collision,unreal.GeometryScript_List.convert_array_to_index_list(remove))
remaining=collision.get_triangle_count();assert 12<=remaining<=32,remaining
body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX)
options=unreal.GeometryScriptCollisionFromMeshOptions(method=unreal.GeometryScriptCollisionGenerationMethod.CONVEX_HULLS,auto_detect_spheres=False,auto_detect_boxes=False,auto_detect_capsules=False,simplify_hulls=False)
unreal.GeometryScript_Collision.set_static_mesh_collision_from_mesh(collision,mesh,options)
simple=unreal.GeometryScript_Collision.get_simple_collision_from_static_mesh(mesh);shapes=unreal.GeometryScript_Collision.get_simple_collision_shape_count(simple);assert shapes==2,shapes
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)

# Query simple and complex collision independently in an empty editor world.
factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor)
b=unreal.load_asset('/Game/QA/BP_CrosswalkCollisionProbe') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_CrosswalkCollisionProbe','/Game/QA',unreal.Blueprint,factory)
g=d.Graph();g.call('Ray','LineTraceSingle',K,TraceChannel='TraceTypeQuery1',DrawDebugType='None',bIgnoreSelf='true');g.link('entry','Start','Ray','Start');g.link('entry','End','Ray','End');g.link('entry','Complex','Ray','bTraceComplex');g.exec('entry','Ray');g.call('Hit','BreakHitResult',G);g.link('Ray','OutHit','Hit','Hit');g.link('Ray','ReturnValue','result','Blocked');g.link('Hit','ImpactPoint','result','Impact');g.exec('Ray','result')
params=[dict(name=n,category='struct',object='/Script/CoreUObject.Vector') for n in ['Start','End']]+[dict(name='Complex',category='bool'),dict(name='Blocked',category='bool',out=True),dict(name='Impact',category='struct',object='/Script/CoreUObject.Vector',out=True)]
build(b,g,'QueryCrosswalk',params);save(b)
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
floor=aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());component=floor.static_mesh_component;component.set_static_mesh(mesh);component.set_collision_profile_name('BlockAll')
probe=aa.spawn_actor_from_class(b.generated_class(),unreal.Vector(5000,5000,0));checks=[]
for name,x,y,complex_trace,expected in [('paint_simple',paint_point[0],paint_point[1],False,False),('paint_visual',paint_point[0],paint_point[1],True,True),('ramp_north',0,1408,False,True),('ramp_south',0,-1408,False,True)]:
    blocked,impact=probe.call_method('QueryCrosswalk',(unreal.Vector(x,y,100),unreal.Vector(x,y,-50),complex_trace))
    row=dict(name=name,blocked=bool(blocked),expected=expected,impact=list(impact.to_tuple()));checks.append(row);assert bool(blocked)==expected,row
report=dict(asset=asset,backup=backup,visual_bounds_before=before_size,visual_bounds_after=list(after.box_extent.to_tuple()),source_limits=limits,removed_paint_collision_triangles=len(remove),remaining_ramp_triangles=remaining,simple_shapes=shapes,checks=checks)
(root/'crosswalk_collision_verification.json').write_text(json.dumps(report,indent=2));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('CROSSWALK_COLLISION_VERIFIED')
