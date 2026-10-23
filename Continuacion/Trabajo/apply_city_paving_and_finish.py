import unreal,json,sys,math,shutil,collections
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();plan=json.loads((W/'integration_plan.json').read_text());manifest=json.loads((W/'manifest.json').read_text());factor=manifest['spacing_expansion']
# Restore the existing widget-reference function; no native widget lookup dependency.
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone');d.bp=bp
g=d.Graph();g.get('Delivery');g.get('Page');g.get('PreviewMoto');g.get('MiniMap');g.get('App1_Bike_01');g.get('App1_Moto_01');g.call('Valid','IsValid','/Script/Engine.KismetSystemLibrary');g.link('Delivery','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');g.node('Open','getfield',owner='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C',var='PhoneOpen');g.link('Delivery','Delivery','Open','self');g.branch('Phone','Open','PhoneOpen');g.exec('Ready','Phone');g.node('Small','return');g.link('MiniMap','MiniMap','Small','ReturnValue');g.exec('Phone','Small','else');g.call('MapPage','EqualEqual_IntInt',d.M,B='1');g.link('Page','Page','MapPage','A');g.branch('IsMap','MapPage');g.exec('Phone','IsMap');g.exec('IsMap','result','else');g.branch('Mode','PreviewMoto','PreviewMoto');g.exec('IsMap','Mode')
for tag,widget,edge in [('Bike','App1_Bike_01','else'),('Moto','App1_Moto_01','then')]:g.node(tag,'return');g.link(widget,widget,tag,'ReturnValue');g.exec('Mode',tag,edge)
assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'GetActiveMapPanel',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'ReturnValue','category':'object','object':'/Script/UMG.Widget','out':True}],'pure':True,'const':True}));assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Terrain import, preserving the exact mesh and mountain vertex colors.
name='SM_Mapa_081';opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.import_animations=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;task=unreal.AssetImportTask();task.filename=str(W/'export'/(name+'.fbx'));task.destination_path='/Game/Maps/MapaCompleto/Geometry';task.destination_name=name;task.options=opt;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mesh=unreal.load_asset(task.destination_path+'/'+name);assert mesh
folder='/Game/Maps/MapaCompleto';mat=unreal.load_asset(folder+'/M_AndenesBogota') or T.create_asset('M_AndenesBogota',folder,unreal.Material,unreal.MaterialFactoryNew());ME=unreal.MaterialEditingLibrary;ME.delete_all_material_expressions(mat);vc=ME.create_material_expression(mat,unreal.MaterialExpressionVertexColor);pos=ME.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);custom=ME.create_material_expression(mat,unreal.MaterialExpressionCustom);custom.set_editor_property('inputs',[unreal.CustomInput(input_name='P'),unreal.CustomInput(input_name='C')]);custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);custom.set_editor_property('code','''if(P.z > 35 || P.z < -40) return C;
float zone=fmod(abs(floor(P.x/3600)+floor(P.y/3600)),3);
float row=floor(P.y/20); float2 tile=frac(float2(P.x/40+fmod(abs(row),2)*0.5,P.y/20));
float seam=(tile.x<0.045 || tile.y<0.08)?1:0;
float variation=frac(sin(dot(floor(float2(P.x/40+fmod(abs(row),2)*0.5,P.y/20)),float2(12.9898,78.233)))*43758.5453);
float3 brick=float3(.34,.27,.22)*(0.94+variation*.12);
float2 slab=frac(P.xy/120); float joint=(slab.x<.015 || slab.y<.015)?1:0;
float3 concrete=lerp(float3(.38,.39,.40),float3(.29,.30,.31),joint);
return zone<1?lerp(brick,float3(.24,.25,.26),seam):concrete;''');assert ME.connect_material_expressions(pos,'',custom,'P');assert ME.connect_material_expressions(vc,'',custom,'C');assert ME.connect_material_property(custom,'',unreal.MaterialProperty.MP_BASE_COLOR);rough=ME.create_material_expression(mat,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.93);ME.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);mat.set_editor_property('two_sided',True);ME.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);ME.recompile_material(mat);assert EL.save_loaded_asset(mat,only_if_is_dirty=False);mesh.set_material(0,mat);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert EL.save_loaded_asset(mesh,only_if_is_dirty=False)
# Add exact model instances, retaining original construction/legacy-clear graphs.
bp=unreal.load_asset(folder+'/BP_MapaCompletoGeometry');groups=collections.defaultdict(list)
for item in manifest['instances']:
 x,y,z=item['location'];rx,ry,rz=item['rotation'];groups[item['mesh']].append(unreal.Transform(location=unreal.Vector(x*100,-y*100,z*100),rotation=unreal.Rotator(pitch=-ry,yaw=-rz,roll=rx),scale=unreal.Vector(*item['scale'])))
ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp)
 if str(lib.get_variable_name(lib.get_data(h)))=='Part081':o.set_material(0,mat)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class())
for i,transforms in enumerate(groups.values()):c.set_editor_property('Transforms%03d'%i,transforms)
b=plan['building_footprints'];c.set_editor_property('BuildingCenters',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in b]);c.set_editor_property('BuildingExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in b]);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_MapaCompletoGeometry_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('Mapa Completo - andenes y adoquines')
# Resume the final stage after its former UI lookup failure.
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/apply_expanded_city_stage_b.py').read_text();exec(compile(s[s.index("unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')"):],'ExpandedCityFinalStage','exec'))
for n in ['manifest.json','integration_plan.json','Mapa_Completo_Andenes_Ampliado.blend','paving_report.json','urban_infill_report.json']:shutil.copy2(W/n,r/'outputs/MapRebuild'/n)
unreal.log('PAVING_AND_SAME_MODELS_READY')

