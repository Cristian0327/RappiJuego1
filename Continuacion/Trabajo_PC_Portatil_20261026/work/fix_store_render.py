import ast,json
from pathlib import Path
colors={}
for file,var,prefix in [('work/build_stores.py','colors','Store_'),('work/build_distinct_staff.py','palette','NPC_')]:
 tree=ast.parse(Path(file).read_text(encoding='utf-8-sig'))
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==var for t in node.targets):
   colors.update({prefix+k:v for k,v in ast.literal_eval(node.value).items()})
Path('outputs/DeliveryArt/Stores/materials.json').write_text(json.dumps(colors))
f=Path('work/import_stores.py');s=f.read_text(encoding='utf-8-sig');s=s[:s.index('tasks=[]')]+'''import json
colors=json.loads((root/'outputs/DeliveryArt/Stores/materials.json').read_text())
for name,c in colors.items():
 path='/Game/Delivery/Stores/'+name
 mat=unreal.load_asset(path)
 if not isinstance(mat,unreal.Material):mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Delivery/Stores',unreal.Material,unreal.MaterialFactoryNew())
 unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
 color=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0);color.set_editor_property('constant',unreal.LinearColor(*c));unreal.MaterialEditingLibrary.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
 glow=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,150);glow.set_editor_property('constant',unreal.LinearColor(c[0]*.45,c[1]*.45,c[2]*.45,1));unreal.MaterialEditingLibrary.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 unreal.MaterialEditingLibrary.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
for data in unreal.EditorAssetLibrary.list_assets('/Game/Delivery/Stores',recursive=False):
 mesh=unreal.load_asset(data)
 if isinstance(mesh,unreal.StaticMesh):
  for i,slot in enumerate(mesh.get_editor_property('static_materials')):
   name=str(slot.imported_material_slot_name)
   if name in colors:mesh.set_material(i,unreal.load_asset('/Game/Delivery/Stores/'+name))
  unreal.EditorAssetLibrary.save_loaded_asset(mesh)
unreal.log('STORE_COLORS_FIXED')
''';Path('work/fix_store_materials.py').write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel')
f=p/'DeliveryStores.cpp';s=f.read_text(encoding='utf-8').replace('C->SetRelativeLocation(Offset);','C->SetRelativeLocation(Offset);C->SetRelativeScale3D(FVector(1,-1,1));');needle=' const TCHAR* Staff[]=';s=s.replace(needle,''' auto* ExitDoor=NewObject<UStaticMeshComponent>(this);AddInstanceComponent(ExitDoor);ExitDoor->SetupAttachment(RootComponent);ExitDoor->SetRelativeLocation(FVector(0,-395,-14870));ExitDoor->SetRelativeScale3D(FVector(2,.12,2.6));ExitDoor->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));ExitDoor->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Delivery/Stores/Store_green.Store_green")));ExitDoor->SetCollisionProfileName(TEXT("BlockAll"));ExitDoor->RegisterComponent();
'''+needle);f.write_text(s,encoding='utf-8')
f=p/'BogotaPlayer.cpp';s=f.read_text(encoding='utf-8').replace(' CameraBoom->TargetArmLength=',' CameraBoom->bEnableCameraLag=!(Delivery&&Delivery->InsideStore);\n CameraBoom->TargetArmLength=');f.write_text(s,encoding='utf-8')
f=p/'DeliveryUI.cpp';s=f.read_text(encoding='utf-8').replace('#include "InputCoreTypes.h"','#include "InputCoreTypes.h"\n#include "EngineUtils.h"');needle=' if(Delivery->HasWaypoint)Dot';s=s.replace(needle,''' const FLinearColor ShopColors[]={FLinearColor(.2,.8,.3),Gold,Mint,FLinearColor(.9,.9,.8),FLinearColor(.9,.25,.6)};const TCHAR* Letters[]={TEXT("M"),TEXT("C"),TEXT("T"),TEXT("D"),TEXT("F")};
 for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It){FVector V=It->GetActorLocation();if(!FullMap&&(FMath::Abs(V.X-Center.X)>NX||FMath::Abs(V.Y-Center.Y)>EY))continue;Dot(V,ShopColors[It->StoreKind],FullMap?10:5);if(FullMap)FSlateDrawElement::MakeText(E,L+3,G.ToPaintGeometry(FVector2D(16,14),FSlateLayoutTransform(Point(V)+FVector2D(6,-6))),Letters[It->StoreKind],FCoreStyle::GetDefaultFontStyle(TEXT("Bold"),7),ESlateDrawEffect::None,Paper);}
'''+needle);s=s.replace('if(Delivery->State==EDeliveryState::Offered)S=','if(Delivery->State==EDeliveryState::Offered&&!Delivery->InsideStore)S=');f.write_text(s,encoding='utf-8')
