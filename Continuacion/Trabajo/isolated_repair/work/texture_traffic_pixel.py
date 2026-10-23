import bpy,math,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/TrafficDetailed'
files=sorted(out.glob('SK_*.blend'));palette={}
for f in files:
 bpy.ops.wm.open_mainfile(filepath=str(f));m=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SK_'))
 a=m.data.color_attributes['TrafficColor']
 for p in m.data.polygons:
  k=tuple(round(v,3) for v in a.data[p.loop_start].color)
  if k not in palette:palette[k]=len(palette)
assert len(palette)<=256,len(palette)
size=512;tile=32;pixels=[0.0]*(size*size*4)
for k,idx in palette.items():
 r,g,b,rough=k;tx=idx%16;ty=idx//16
 for y in range(tile):
  for x in range(tile):
   # Broad pixel shading like clothing panels; no random surface grain.
   factor=.90+.13*y/(tile-1)
   if y<2:factor*=.91
   if x<1 or x>30:factor*=.97
   rgb=[min(1,c*factor) for c in (r,g,b)]
   if .25<rough<.43 and max(r,g,b)<.3:
    reflection=(7<x-y<10 or 16<x-y<18)
    if reflection:rgb=[min(1,c*.65+.13) for c in (r,g,b)]
   if rough<.08:rgb=[min(1,c*(.85 if x<2 or y<2 else 1)) for c in (r,g,b)]
   pos=((ty*tile+y)*size+tx*tile+x)*4;pixels[pos:pos+4]=rgb+[1.0]
image=bpy.data.images.new('TrafficPixelAtlas',width=size,height=size,alpha=True);image.pixels=pixels;image.filepath_raw=str(out/'T_TrafficPixelAtlas.png');image.file_format='PNG';image.save()
for f in files:
 bpy.ops.wm.open_mainfile(filepath=str(f));m=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SK_'));rig=m.find_armature();bpy.context.scene.frame_set(1)
 a=m.data.color_attributes['TrafficColor'];uv=m.data.uv_layers.get('TrafficUV') or m.data.uv_layers.new(name='TrafficUV')
 for p in m.data.polygons:
  k=tuple(round(v,3) for v in a.data[p.loop_start].color);idx=palette[k];tx=idx%16;ty=idx//16
  # Tiny stair faces sample one texel, so contours do not become noisy.
  axes=sorted(range(3),key=lambda i:abs(p.normal[i]))[:2]
  bounds=[(min(m.data.vertices[m.data.loops[li].vertex_index].co[axis] for li in p.loop_indices),max(m.data.vertices[m.data.loops[li].vertex_index].co[axis] for li in p.loop_indices)) for axis in axes]
  for li in p.loop_indices:
   co=m.data.vertices[m.data.loops[li].vertex_index].co
   xy=[.1+.8*(co[axis]-mn)/max(.00001,mx-mn) for axis,(mn,mx) in zip(axes,bounds)] if p.area>.015 else [.5,.5]
   uv.data[li].uv=((tx+xy[0])/16,(ty+xy[1])/16)
 m.data.uv_layers.active=uv
 img=bpy.data.images.load(str(out/'T_TrafficPixelAtlas.png'),check_existing=True);img.pack()
 mat=m.data.materials[0];nodes=mat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Closest';mat.node_tree.links.new(tex.outputs['Color'],nodes['Principled BSDF'].inputs['Base Color'])
 bpy.ops.object.select_all(action='DESELECT');m.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=m
 bpy.ops.export_scene.fbx(filepath=str(out/(f.stem+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE')
 bpy.context.scene['surface_style']='Shared 512px pixel atlas with clothing-like broad shades, nearest filtering, no noise, no wipers.'
 bpy.ops.wm.save_as_mainfile(filepath=str(f))
(out/'texture_atlas_report.json').write_text(json.dumps({'size':size,'palette_tiles':len(palette),'models':len(files),'filter':'nearest','no_random_grain':True},indent=2))
print('PIXEL_TEXTURES_READY',len(files),flush=True)
