import bpy,numpy as np,json
from pathlib import Path
bpy.ops.wm.read_factory_settings(use_empty=True)
out={}
for name in ['SM_Mapa_000','SM_Mapa_067','SM_Mapa_Road_0']:
 bpy.ops.import_scene.fbx(filepath='C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/export/'+name+'.fbx');o=bpy.context.selected_objects[0];a=o.data.color_attributes.active_color;c=np.empty(len(a.data)*4,np.float32);a.data.foreach_get('color',c);u,ct=np.unique(np.round(c.reshape(-1,4),3),axis=0,return_counts=True);ix=np.argsort(ct)[-10:];out[name]={'unique':len(u),'colors':u[ix].tolist(),'count':ct[ix].tolist()};bpy.data.objects.remove(o,do_unlink=True)
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/fbx_palette.json').write_text(json.dumps(out,indent=2));print('PALETTE_READY')
