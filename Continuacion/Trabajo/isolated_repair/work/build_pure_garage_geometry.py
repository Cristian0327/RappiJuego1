import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/Delivery/BlueprintGameplay/UI';name='BP_BlueprintGaragePreview';f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(folder+'/'+name) or T.create_asset(name,folder,unreal.Blueprint,f);d.bp=bp
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;root=sub.k2_gather_subobject_data_for_blueprint(bp)[0];source=unreal.get_default_object(unreal.load_class(None,'/Script/BogotaVoxel.DeliveryVehiclePreview'));count=0
for old in source.get_components_by_class(unreal.StaticMeshComponent):
 n=old.get_name();existing=None
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  o=lib.get_object_for_blueprint(lib.get_data(h),bp)
  if o and o.get_name().removesuffix('_GEN_VARIABLE')==n:existing=o;break
 if not existing:
  h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(reason);assert sub.rename_subobject(h,unreal.Text(n));existing=lib.get_object_for_blueprint(lib.get_data(h),bp)
 for p in ['relative_location','relative_rotation','relative_scale3d','cast_shadow','visible_in_scene_capture_only']:existing.set_editor_property(p,old.get_editor_property(p))
 existing.set_static_mesh(old.get_editor_property('static_mesh'));existing.set_collision_profile_name('NoCollision')
 for i in range(old.get_num_materials()):existing.set_material(i,old.get_material(i))
 count+=1
# Scene capture and lighting are standard engine components. The finished garage is authored as Blueprint-owned geometry.
for n,cls,oldname,props in [('WorkshopCamera',unreal.SceneCaptureComponent2D,'WorkshopCamera',['relative_location','relative_rotation','projection_type','ortho_width','capture_source','capture_every_frame','capture_on_movement','primitive_render_mode','post_process_settings']),('WorkshopLight',unreal.PointLightComponent,'WorkshopLight',['relative_location','intensity','attenuation_radius','cast_shadows'])]:
 old=unreal.find_object(source,oldname);assert old,oldname;obj=None
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  o=lib.get_object_for_blueprint(lib.get_data(h),bp)
  if o and o.get_name().removesuffix('_GEN_VARIABLE')==n:obj=o;break
 if not obj:
  h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=cls,blueprint_context=bp));assert not str(reason);assert sub.rename_subobject(h,unreal.Text(n));obj=lib.get_object_for_blueprint(lib.get_data(h),bp)
 for p in props:obj.set_editor_property(p,old.get_editor_property(p))
known=[str(x) for x in E.list_member_variable_names(bp)]
if 'PreviewTexture' not in known:assert E.add_member_variable(bp,'PreviewTexture',E.get_object_reference_type(unreal.TextureRenderTarget2D.static_class()))
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['parent']=='/Script/Engine.Actor'
(r/'work/pure_garage_geometry.json').write_text(json.dumps({'status':'GEOMETRY_STAGING','static_mesh_components':count,'parent':audit['parent'],'pending':['Render target and model selection Blueprint functions','Phone image integration','Runtime visual verification']},indent=2));unreal.log('PURE_GARAGE_GEOMETRY_PASS blocks='+str(count))
