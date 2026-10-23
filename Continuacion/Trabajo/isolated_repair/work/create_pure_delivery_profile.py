import unreal,json,uuid,re
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/Delivery/BlueprintSchema';name='BP_DeliveryProfile';path=folder+'/'+name;f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.SaveGame);bp=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else T.create_asset(name,folder,unreal.Blueprint,f);known=[str(x) for x in E.list_member_variable_names(bp)];integer=E.get_basic_type_by_name('int');named=E.get_basic_type_by_name('name');types={n:integer for n in ['Version','Balance','BikeColor','MotoColor']};types.update({n:E.get_array_type(named) for n in ['Purchased','OwnedModels']});types.update({n:named for n in ['BikeModel','MotoModel']});types['Vehicle']=E.get_basic_type_by_name('byte');types['ModelColors']=E.get_map_type(named,integer)
for n,t in types.items():
 if n not in known:E.add_member_variable(bp,n,t)
 E.set_blueprint_variable_instance_editable(bp,n,True)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());c.set_editor_property('Version',2);c.set_editor_property('BikeModel',unreal.Name('BikeCity'));c.set_editor_property('MotoModel',unreal.Name('MotoStreet'));assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
save=unreal.GameplayStatics.create_save_game_object(bp.generated_class());values={'Version':2,'Balance':123456,'Vehicle':1,'BikeColor':3,'MotoColor':5,'Purchased':[unreal.Name('CargoPanniers'),unreal.Name('Motorcycle')],'OwnedModels':[unreal.Name('BikeCity'),unreal.Name('MotoSport')],'BikeModel':unreal.Name('BikeCity'),'MotoModel':unreal.Name('MotoSport'),'ModelColors':{unreal.Name('MotoSport'):5,unreal.Name('BikeCity'):3}}
for n,v in values.items():save.set_editor_property(n,v)
slot='BlueprintProfileQA_'+uuid.uuid4().hex;assert not unreal.GameplayStatics.does_save_game_exist(slot,0);assert unreal.GameplayStatics.save_game_to_slot(save,slot,0);loaded=unreal.GameplayStatics.load_game_from_slot(slot,0);assert loaded and loaded.get_class()==bp.generated_class()
for n,v in values.items():
 actual=loaded.get_editor_property(n)
 if n in ['Purchased','OwnedModels']:assert list(actual)==v,n
 elif n=='ModelColors':assert dict(actual)==v,n
 else:assert actual==v,(n,actual,v)
assert unreal.GameplayStatics.delete_game_in_slot(slot,0);assert not unreal.GameplayStatics.does_save_game_exist(slot,0);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['parent']=='/Script/Engine.SaveGame';(r/'work/pure_profile_validation.json').write_text(json.dumps({'status':'STAGING_NOT_PROMOTED','asset':path,'serialized_fields':list(values),'roundtrip':'PASS','real_player_profiles_modified':False,'audit':audit},indent=2));unreal.log('PURE_BLUEPRINT_SAVE_PROFILE_ROUNDTRIP_PASS fields=10')
# Compare every table field after conversion, allowing localization IDs to change while text stays identical.
def norm(v):
 if isinstance(v,dict):return {k:norm(x) for k,x in v.items()}
 if isinstance(v,list):return [norm(x) for x in v]
 if isinstance(v,str) and v.startswith(('NSLOCTEXT(','INVTEXT(')):
  strings=re.findall(r'"(?:[^"\\]|\\.)*"',v)
  return json.loads(strings[-1]) if strings else v
 return v
rows=0
for name in ['DT_Upgrades','DT_StoreThemes','DT_Vehicles']:
 a=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/Delivery/Data/'+name)));b=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/Delivery/BlueprintSchema/Tables/'+name)));assert norm(a)==norm(b),(name,norm(a),norm(b));rows+=len(a)
(r/'work/blueprint_table_full_parity.json').write_text(json.dumps({'status':'PASS','tables':3,'rows':rows,'all_fields_compared':True}));unreal.log('BLUEPRINT_TABLE_FULL_FIELD_PARITY_PASS rows='+str(rows))
