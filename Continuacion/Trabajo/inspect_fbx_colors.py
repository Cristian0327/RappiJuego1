import bpy
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath='C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/export/SM_Mapa_067.fbx')
for o in bpy.data.objects:
 if o.type=='MESH':
  print('FBX_COLOR',o.name,len(o.data.color_attributes),[(a.name,a.domain) for a in o.data.color_attributes]);a=o.data.color_attributes.active_color;print('SAMPLES',[list(a.data[i].color) for i in range(min(12,len(a.data)))])
