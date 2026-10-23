import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/TrafficDetailed'
bpy.ops.wm.open_mainfile(filepath=str(out/'SK_TransMilenio.blend'))
o=bpy.data.objects['SK_TransMilenio'];o.name='SK_TransMilenioG66';o.data.name=o.name;rig=bpy.data.objects['Rig_TransMilenio'];rig.name='Rig_TransMilenioG66'
for c in o.data.color_attributes['TrafficColor'].data:
 r,g,b,a=c.color
 if r>.35 and g<.09 and b<.10:c.color=(.20,.045,.43,a)
 elif r>.7 and g>.30 and b<.06:c.color=(.48,.20,.68,a)
bpy.context.scene['reference']='G66 leyenda bogotana: morado, sin textos, entre 02:00 y 03:00; base TransMilenio_Rojo_Detallado_SinTexto.png'
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(out/'SK_TransMilenioG66.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'SK_TransMilenioG66.blend'))
manifest=json.loads((out/'manifest.json').read_text());s=dict(next(x for x in manifest if x['name']=='TransMilenio'));s.update(name='TransMilenioG66',label='G66 morado',rare_event=True,no_text=True);manifest=[x for x in manifest if x['name']!='TransMilenioG66']+[s];(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
