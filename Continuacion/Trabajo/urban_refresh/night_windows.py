import unreal
ME=unreal.MaterialEditingLibrary;EL=unreal.EditorAssetLibrary
mat=unreal.load_asset('/Game/Maps/MapaCompleto/M_MapaVoxel');mpc=unreal.load_asset('/Game/World/BogotaUrban/MPC_BogotaWeather')
vc=ME.create_material_expression(mat,unreal.MaterialExpressionVertexColor);pos=ME.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);normal=ME.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS);night=ME.create_material_expression(mat,unreal.MaterialExpressionCollectionParameter);night.set_editor_property('collection',mpc);night.set_editor_property('parameter_name','Night')
f=ME.create_material_expression(mat,unreal.MaterialExpressionCustom);f.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
inputs=[]
for name in ['C','P','N','Night']:
 q=unreal.CustomInput();q.set_editor_property('input_name',name);inputs.append(q)
f.set_editor_property('inputs',inputs)
f.set_editor_property('code','''float blue=step(C.r*1.35+0.015,C.b)*step(C.g*.95,C.b)*step(.045,C.b)*step(C.b,.35)*step(C.r,.12)*step(C.g,.25);float cream=step(.8,C.r)*step(.72,C.g)*step(.4,C.b)*step(C.b,C.g*.88);float facade=1-smoothstep(.15,.45,abs(N.z));float3 cell=floor(P/float3(240,240,280));float hash=frac(sin(dot(cell,float3(12.9898,78.233,37.719)))*43758.5453);float on=step(.47,hash);float warmth=frac(hash*17.31);return lerp(float3(1,.47,.16),float3(1,.79,.39),warmth)*1.8*saturate(Night)*facade*blue*on;''')
for a,p,n in [(vc,'','C'),(pos,'','P'),(normal,'','N'),(night,'','Night')]:assert ME.connect_material_expressions(a,p,f,n)
assert ME.connect_material_property(f,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);ME.recompile_material(mat);assert EL.save_loaded_asset(mat,only_if_is_dirty=False)
unreal.log('VARIED_NIGHT_WINDOWS_READY')
