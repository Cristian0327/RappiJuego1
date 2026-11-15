import unreal
from pathlib import Path
path='/Game/World/BlueprintWorld/M_BlueprintSky';sky=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset('/Game/World/M_Sky',path); mel=unreal.MaterialEditingLibrary
assert sky
mel.delete_all_material_expressions(sky)
sky.set_editor_property('two_sided',True);sky.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
sky.set_editor_property('is_sky',True)
c=mel.create_material_expression(sky,unreal.MaterialExpressionCustom,0,0)
c.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
c.set_editor_property('description','Ciclo: cielo, nubes voxel, sol, luna y estrellas')
code='''
float3 d=normalize(-ViewDir);
float h=saturate(d.z);
float3 color=lerp(Horizon,Zenith,pow(h,.55));
float glow=pow(saturate(dot(d,normalize(SunDir))),12)*Twilight;
color+=float3(1,.18,.025)*glow*.65;
float sun=smoothstep(.99915,.99955,dot(d,normalize(SunDir)))*Daylight;
float moon=smoothstep(.99935,.99965,dot(d,normalize(MoonDir)))*Night;
float2 cloudUV=floor((d.xy/max(.18,d.z+.16)*3+float2(CloudTime*.004,CloudTime*.0015))*12)/12;
float2 cell=floor(cloudUV),f=frac(cloudUV);f=f*f*(3-2*f);
float n00=frac(sin(dot(cell,float2(127.1,311.7)))*43758.5453);
float n10=frac(sin(dot(cell+float2(1,0),float2(127.1,311.7)))*43758.5453);
float n01=frac(sin(dot(cell+float2(0,1),float2(127.1,311.7)))*43758.5453);
float n11=frac(sin(dot(cell+float2(1,1),float2(127.1,311.7)))*43758.5453);
float noise=lerp(lerp(n00,n10,f.x),lerp(n01,n11,f.x),f.y);
float cloud=step(lerp(.63,.38,saturate(WeatherRain)),noise)*smoothstep(.03,.16,d.z);
float shade=saturate((noise-.63)*3.5);
float3 cloudDay=lerp(float3(.56,.67,.8),float3(.95,.97,1),shade);
cloudDay=lerp(cloudDay,lerp(float3(.07,.09,.13),float3(.21,.24,.29),shade),saturate(WeatherRain));
color=lerp(color,lerp(float3(.025,.035,.075),cloudDay,Daylight),cloud*.92);
float2 starCell=floor(d.xy/max(.15,abs(d.z)+.1)*260);
float starHash=frac(sin(dot(starCell,float2(12.9898,78.233)))*43758.5453);
float stars=step(.9985,starHash)*smoothstep(.08,.3,d.z)*Night*(1-cloud);
color+=stars*float3(.7,.82,1)*1.4;
color+=sun*float3(5,3.8,2.2)*(1-saturate(WeatherRain)*.95)+moon*float3(.7,.85,1.1)*(1-saturate(WeatherRain)*.8);
return color;
'''
c.set_editor_property('code',code)
params=[('Horizon',(.25,.54,.9)),('Zenith',(.035,.22,.62)),('SunDir',(.4,.2,.8)),('MoonDir',(-.4,-.2,-.8)),('Daylight',1),('Twilight',0),('Night',0),('CloudTime',0),('WeatherRain',0)]
inputs=[]
for name in ['ViewDir']+[p[0] for p in params]:
 inp=unreal.CustomInput();inp.set_editor_property('input_name',name);inputs.append(inp)
c.set_editor_property('inputs',inputs)
v=mel.create_material_expression(sky,unreal.MaterialExpressionCameraVectorWS,-400,-150);assert mel.connect_material_expressions(v,'',c,'ViewDir')
for i,(name,value) in enumerate(params):
 cls=unreal.MaterialExpressionVectorParameter if isinstance(value,tuple) else unreal.MaterialExpressionScalarParameter
 p=mel.create_material_expression(sky,cls,-450,i*100);p.set_editor_property('parameter_name',name)
 p.set_editor_property('default_value',unreal.LinearColor(*value,1) if isinstance(value,tuple) else value)
 assert mel.connect_material_expressions(p,'',c,name),name
assert mel.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(sky);unreal.EditorAssetLibrary.save_asset(path,False)
unreal.log('PURE_DYNAMIC_SKY_MATERIAL_PASS')
