import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
IMPORT_ONLY_NAMES=[p.stem for p in (root/'outputs/DeliveryArt/TrafficDetailed').glob('SK_Private*.fbx')]
exec(compile((root/'work/fix_traffic_material.py').read_text(encoding='utf-8-sig'),str(root/'work/fix_traffic_material.py'),'exec'))
m=unreal.load_asset('/Game/Traffic/Detailed/M_TrafficVoxelVertex');mel=unreal.MaterialEditingLibrary
sample=mel.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR)
def node(cls,x,y,**props):
 n=mel.create_material_expression(m,cls,x,y)
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def link(a,ap,b,bp):
 for outpin in ([ap,''] if ap=='RGB' else [ap]):
  for inpin in ([bp,''] if bp=='Input' else [bp]):
   if mel.connect_material_expressions(a,outpin,b,inpin):return
 raise AssertionError((a,ap,b,bp))
uv=node(unreal.MaterialExpressionTextureCoordinate,-1100,-700,coordinate_index=1)
mask=node(unreal.MaterialExpressionComponentMask,-850,-700,r=True,g=False,b=False,a=False);link(uv,'',mask,'Input')
enable=node(unreal.MaterialExpressionScalarParameter,-1100,-500,parameter_name='PaintEnabled',default_value=0)
alpha=node(unreal.MaterialExpressionMultiply,-600,-600);link(mask,'',alpha,'A');link(enable,'',alpha,'B')
paint=node(unreal.MaterialExpressionVectorParameter,-850,-1050,parameter_name='BodyPaint',default_value=unreal.LinearColor(1,1,1,1))
sample_luma=node(unreal.MaterialExpressionDesaturation,-850,-150);link(sample,'RGB',sample_luma,'Input')
v=node(unreal.MaterialExpressionVertexColor,-1300,-150)
vertex_luma=node(unreal.MaterialExpressionDesaturation,-1100,0);link(v,'RGB',vertex_luma,'Input')
safe=node(unreal.MaterialExpressionMax,-850,50,const_b=.001);link(vertex_luma,'',safe,'A')
texture_shade=node(unreal.MaterialExpressionDivide,-600,-100);link(sample_luma,'',texture_shade,'A');link(safe,'',texture_shade,'B')
shaded_paint=node(unreal.MaterialExpressionMultiply,-300,-700);link(paint,'RGB',shaded_paint,'A');link(texture_shade,'',shaded_paint,'B')
result=node(unreal.MaterialExpressionLinearInterpolate,0,-500);link(sample,'RGB',result,'A');link(shaded_paint,'',result,'B');link(alpha,'',result,'Alpha')
assert mel.connect_material_property(result,'',unreal.MaterialProperty.MP_BASE_COLOR)
mel.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
for name in IMPORT_ONLY_NAMES:
 mesh=unreal.load_asset('/Game/Traffic/Detailed/'+name)
 assert mesh and len(mesh.get_editor_property('materials'))==1,name
unreal.log('TRAFFIC_BODY_PAINT_PASS '+str(len(IMPORT_ONLY_NAMES)))
