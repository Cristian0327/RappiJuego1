import bpy,numpy as np

bpy.ops.wm.read_factory_settings(use_empty=True);paths=['C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/export/SM_Mapa_000.fbx','C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/unreal_export.fbx'];rows=[]
for p in paths:
 bpy.ops.import_scene.fbx(filepath=p);o=bpy.context.selected_objects[0];a=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);rows.append(a);bpy.data.objects.remove(o,do_unlink=True);print('BOUNDS',p,a.min(axis=0),a.max(axis=0))
np.save('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/roundtrip_a.npy',rows[0]);np.save('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/roundtrip_b.npy',rows[1])
