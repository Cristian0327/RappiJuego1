import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone');phone=unreal.get_default_object(bp.generated_class());checks=[]
for label,p,c,full,x,y in [('full_center',(0,0,0),(0,0,0),True,.5,.5),('full_northwest',(45000,-30000,0),(0,0,0),True,0,0),('full_southeast',(-45000,30000,0),(0,0,0),True,1,1),('full_east',(0,15000,0),(0,0,0),True,.75,.5),('mini_center',(1000,-2200,90),(1000,-2200,100),False,.5,.5),('mini_northwest',(9000,-7700,90),(1000,-2200,100),False,0,0),('mini_southeast',(-7000,3300,90),(1000,-2200,100),False,1,1)]:
 out=phone.call_method('MapNormalizedPoint',args=(unreal.Vector(*p),unreal.Vector(*c),full));assert math.isclose(out.x,x,abs_tol=.0001) and math.isclose(out.y,y,abs_tol=.0001),(label,out);checks.append(label)
for path in ['/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone','/Game/Delivery/BlueprintGameplay/UI/BP_BlueprintGaragePreview','/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider']:
 audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(unreal.load_asset(path)));assert not any(g['native_calls'] for g in audit['graphs']),path;checks.append(path+' NoNativeCalls')
(r/'work/pure_phone_map_vm_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'count':len(checks),'main_promoted':False},indent=2));unreal.log('PURE_PHONE_MAP_VM_PASS checks='+str(len(checks)))
