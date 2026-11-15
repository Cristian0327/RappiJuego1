import unreal
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'work'
for name,path in [('hero','/Game/VoxelExplorer/SK_VoxelExplorer'),('npc','/Game/Crowd/SK_Citizen00')]:
 m=unreal.load_asset(path);d=m.get_editor_property('asset_import_data');unreal.log('CROWD_FRONT '+name+' '+str(d.get_editor_property('force_front_x_axis')))
 t=unreal.AssetExportTask();t.object=m;t.filename=str(out/(name+'_ue_export.fbx'));t.automated=True;t.prompt=False;t.exporter=unreal.SkeletalMeshExporterFBX();t.options=unreal.FbxExportOption();assert unreal.Exporter.run_asset_export_task(t)
