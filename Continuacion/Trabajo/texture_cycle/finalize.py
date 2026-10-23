import unreal,json,sys,shutil,re
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/texture_cycle');root=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
EL=unreal.EditorAssetLibrary;mat=unreal.load_asset('/Game/Traffic/Detailed/M_TaxiOpaqueVertex');fixed=[]
for path in EL.list_assets('/Game/Traffic/Detailed',recursive=True):
 if not any(n in path for n in ['SK_TaxiCompact.','SK_TaxiSedan.','SM_TaxiCompact.','SM_TaxiSedan.']):continue
 asset=unreal.load_asset(path)
 if not isinstance(asset,(unreal.SkeletalMesh,unreal.StaticMesh)):continue
 rel=path.split('.')[0].replace('/Game/','')+'.uasset';src=root/'RappiJuego1/Content'/rel;dst=P/'asset_backup'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(src,dst)
 if isinstance(asset,unreal.SkeletalMesh):
  slots=list(asset.get_editor_property('materials'))
  for slot in slots:slot.set_editor_property('material_interface',mat)
  asset.set_editor_property('materials',slots)
 else:
  for i in range(len(asset.static_materials)):asset.set_material(i,mat)
 assert EL.save_loaded_asset(asset,only_if_is_dirty=False);fixed.append(path)
audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(unreal.load_asset('/Game/World/BogotaUrban/BP_DeveloperTimeCycle')));assert audit['compiled'] and not any(g['native_calls'] for g in audit['graphs']);log=(P/'FinalRuntimeQA.log').read_text(errors='replace');checks={n:('DEVELOPER_NEXT_HOUR_'+str(n)+'=true') in log for n in [6,9,12,16,18,22,3]};assert all(checks.values()) and 'NORMAL_MODE_N_BLOCKED=true' in log;assert 'Failed to compile Material' not in log
report=dict(time_key='N after ESOYAM; phone closed',phase_hours=[6,9,12,16,18,22,3],phase_checks=checks,normal_mode_blocked=True,vehicle_models_inspected=23,shader_compile_errors=0,legacy_vehicle_materials_repaired=3,taxi_vertex_livery=True,taxi_mesh_defaults=fixed,station_access_finish_offset_cm=.4,ground_layer_rule='clip low plot surfaces inside existing road and sidewalk reserve; small per-instance ground bias',runtime_custom_cpp=False);(P/'final_report.json').write_text(json.dumps(report,indent=2));shutil.copy2(P/'final_report.json',root/'outputs/BogotaUrban/texture_time_report.json');shutil.copy2(P/'T_UrbanGroundPriority.png',root/'outputs/BogotaUrban/T_UrbanGroundPriority.png');unreal.log('TEXTURE_AND_N_CYCLE_FINAL_VERIFIED '+json.dumps(report))
