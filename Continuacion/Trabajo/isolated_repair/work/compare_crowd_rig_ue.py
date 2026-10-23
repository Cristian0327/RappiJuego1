import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];r={}
for key,f in [('hero',root/'work/hero_ue_export.fbx'),('npc',root/'work/npc_ue_export.fbx')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(f));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');r[key]={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones};print(key,rig.matrix_world)
(root/'work/crowd_rig_compare.json').write_text(json.dumps(r))
for b in r['hero']:
 if b in r['npc']:print(b,max(abs(r['hero'][b][i][j]-r['npc'][b][i][j]) for i in range(4) for j in range(4)))

