import unreal,json,sys,shutil
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/texture_cycle');root=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();ME=unreal.MaterialEditingLibrary;ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;AS=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=d.M;A='/Script/Engine.Actor';G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';folder='/Game/World/BogotaUrban';W='/Game/World/BlueprintWorld/BP_WorldState.BP_WorldState_C';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';backup=P/'asset_backup';backup.mkdir(exist_ok=True)
def back(path):
 rel=path.replace('/Game/','')+('.umap' if path.endswith('MapaCompleto_Integration') else '.uasset');src=root/'RappiJuego1/Content'/rel;dst=backup/rel
 if src.exists() and not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for path in ['/Game/Maps/MapaCompleto_Integration','/Game/Maps/MapaCompleto/M_MapaVoxel',folder+'/BP_CallesSecundarias']+['/Game/Traffic/Detailed/'+n for n in ['M_TrafficVoxel','M_TrafficVoxelVertex','M_TrafficOpaqueSafe_20261021','T_TrafficPixelAtlas']]:back(path)
# Repair legacy and current vehicle references, so parked/spawned variants share a valid shader.
tex=unreal.load_asset('/Game/Traffic/Detailed/T_TrafficPixelAtlas');tex.set_editor_property('never_stream',True);tex.set_editor_property('lod_bias',0);assert EL.save_loaded_asset(tex,only_if_is_dirty=False)
for name in ['M_TrafficVoxel','M_TrafficVoxelVertex','M_TrafficOpaqueSafe_20261021']:
 mat=unreal.load_asset('/Game/Traffic/Detailed/'+name)
 if not mat:continue
 ME.delete_all_material_expressions(mat);sample=ME.create_material_expression(mat,unreal.MaterialExpressionTextureSample);sample.set_editor_property('texture',tex);uv=ME.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate);uv.set_editor_property('coordinate_index',1);paint=ME.create_material_expression(mat,unreal.MaterialExpressionVectorParameter);paint.set_editor_property('parameter_name','BodyPaint');paint.set_editor_property('default_value',unreal.LinearColor(.55,.6,.65,1));enabled=ME.create_material_expression(mat,unreal.MaterialExpressionScalarParameter);enabled.set_editor_property('parameter_name','PaintEnabled');night=ME.create_material_expression(mat,unreal.MaterialExpressionScalarParameter);night.set_editor_property('parameter_name','NightLights');vc=ME.create_material_expression(mat,unreal.MaterialExpressionVertexColor)
 def custom(code):
  v=ME.create_material_expression(mat,unreal.MaterialExpressionCustom);v.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);ins=[]
  for n in ['Atlas','UV','Paint','Enabled','Alpha','Night']:
   i=unreal.CustomInput();i.set_editor_property('input_name',n);ins.append(i)
  v.set_editor_property('inputs',ins);v.set_editor_property('code',code)
  for src,out,n in [(sample,'RGB','Atlas'),(uv,'','UV'),(paint,'','Paint'),(enabled,'','Enabled'),(vc,'A','Alpha'),(night,'','Night')]:assert ME.connect_material_expressions(src,out,v,n)
  return v
 code='float shade=clamp(UV.y,.75,1.25); float3 color=dot(Paint.rgb,float3(.299,.587,.114))<.045?float3(.065,.08,.10):Paint.rgb; float3 base=lerp(Atlas,color*shade,saturate(UV.x)*saturate(Enabled)); '
 base=custom(code+'return max(base,0);');em=custom(code+'return base*.015 + Atlas*2*saturate(Night)*(1-step(.08,Alpha));');assert ME.connect_material_property(base,'',unreal.MaterialProperty.MP_BASE_COLOR);assert ME.connect_material_property(em,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 for prop,value in [(unreal.MaterialProperty.MP_ROUGHNESS,.75),(unreal.MaterialProperty.MP_METALLIC,.08),(unreal.MaterialProperty.MP_SPECULAR,.25)]:
  n=ME.create_material_expression(mat,unreal.MaterialExpressionConstant);n.set_editor_property('r',value);assert ME.connect_material_property(n,'',prop)
 mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_OPAQUE);mat.set_editor_property('two_sided',True);ME.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);ME.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);ME.recompile_material(mat);assert EL.save_loaded_asset(mat,only_if_is_dirty=False)
# Only low architectural ground is clipped beneath the already-existing road/sidewalk surfaces.
task=unreal.AssetImportTask();task.filename=str(P/'T_UrbanGroundPriority.png');task.destination_path=folder;task.destination_name='T_UrbanGroundPriority';task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mask=unreal.load_asset(folder+'/T_UrbanGroundPriority');mask.set_editor_property('srgb',False);mask.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS);mask.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);mask.set_editor_property('never_stream',True);mask.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);EL.save_loaded_asset(mask,only_if_is_dirty=False)
mat=unreal.load_asset('/Game/Maps/MapaCompleto/M_MapaVoxel');world=ME.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);obj=ME.create_material_expression(mat,unreal.MaterialExpressionTextureObject);obj.set_editor_property('texture',mask);obj.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS);random=ME.create_material_expression(mat,unreal.MaterialExpressionPerInstanceRandom)
def ground_custom(code,names,output):
 v=ME.create_material_expression(mat,unreal.MaterialExpressionCustom);v.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3 if output==unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET else unreal.CustomMaterialOutputType.CMOT_FLOAT1);ins=[]
 for name in names.values():
  i=unreal.CustomInput();i.set_editor_property('input_name',name);ins.append(i)
 v.set_editor_property('inputs',ins);v.set_editor_property('code',code)
 for src,name in names.items():assert ME.connect_material_expressions(src,'',v,name)
 assert ME.connect_material_property(v,'',output)
# Map keys are nodes, values are the HLSL input identifiers.
ground_custom('float2 uv=float2((P.x+40000)/80000,(P.y+50000)/100000); bool inside=all(uv>=0)&&all(uv<=1); float road=Texture2DSampleLevel(Road,RoadSampler,uv,0).r; return (inside && P.z<24 && P.z>-100)?1-step(.5,road):1;', {world:'P',obj:'Road'},unreal.MaterialProperty.MP_OPACITY_MASK)
ground_custom('return float3(0,0,(P.z<24 && P.z>-100)?-(.4+.8*R):0);', {world:'P',random:'R'},unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET);mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);mat.set_editor_property('opacity_mask_clip_value',.333);ME.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);ME.recompile_material(mat);assert EL.save_loaded_asset(mat,only_if_is_dirty=False)
# Station walkway tops were at the exact asphalt height: put the finish above it and below the zebra paint.
bp=unreal.load_asset(folder+'/BP_CallesSecundarias')
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 if str(lib.get_variable_name(lib.get_data(h)))=='StationAccess':lib.get_object_for_blueprint(lib.get_data(h),bp).set_relative_location(unreal.Vector(0,0,.4),False,False)
assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False)
exec(compile((P/'build_time_cycle.py').read_text(),'DeveloperTimeCycleBlueprint','exec'),{})
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
for a in list(AS.get_all_level_actors()):
 if a.get_class().get_name() in ['BP_CallesSecundarias_C','BP_DeveloperTimeCycle_C']:AS.destroy_actor(a)
for path in [folder+'/BP_CallesSecundarias',folder+'/BP_DeveloperTimeCycle']:AS.spawn_actor_from_class(unreal.load_asset(path).generated_class(),unreal.Vector())
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('TEXTURE_LAYERS_VEHICLE_MATERIALS_AND_N_CYCLE_SAVED')
