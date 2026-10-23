import bpy,json
from pathlib import Path
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");out=r/'outputs/DeliveryArt/Services';manifest=json.loads((out/'manifest.json').read_text())
for entry in manifest['models']:
 path=out/(entry['name']+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path));mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.name==entry['name']);image=bpy.data.images.load(str(out/'T_ServicePixelAtlas.png'),check_existing=True);image.colorspace_settings.name='sRGB';image.filepath='//T_ServicePixelAtlas.png'
 for mat in mesh.data.materials:
  if not mat or mat.name.startswith('ServiceWindow'):continue
  bsdf=mat.node_tree.nodes.get('Principled BSDF')
  if not bsdf:bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;node.interpolation='Closest';mat.node_tree.links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
 bpy.ops.wm.save_as_mainfile(filepath=str(path));print('BLENDER_MATERIAL_MATCH',entry['name'],flush=True)
print('ALL_SERVICE_BLENDER_MATERIALS_MATCH_PASS',flush=True)
