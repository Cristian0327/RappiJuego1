#include "DeliveryEditorLibrary.h"
#include "Modules/ModuleManager.h"
#include "Engine/Blueprint.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "EdGraphSchema_K2.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_CallFunction.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphPin.h"
#include "UObject/UnrealType.h"
#include "Engine/BlueprintGeneratedClass.h"
IMPLEMENT_MODULE(FDefaultModuleImpl,BogotaVoxelEditor)
bool UDeliveryEditorLibrary::SetGameplayComponent(UBlueprint* BP,UClass* GameplayClass){
 auto* Base=FindObject<UClass>(nullptr,TEXT("/Script/BogotaVoxel.DeliveryComponent"));if(!BP||!GameplayClass||!Base||!GameplayClass->IsChildOf(Base))return false;
 const FName ComponentName(TEXT("DeliveryGameplay"));BP->ComponentClassOverrides.RemoveAll([&](const FBPComponentClassOverride& O){return O.ComponentName==ComponentName;});BP->ComponentClassOverrides.Add(FBPComponentClassOverride(ComponentName,GameplayClass));FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return true;
}
bool UDeliveryEditorLibrary::AddActionGraph(UBlueprint* BP,FName Name,FName Function){
 if(!BP||!BP->ParentClass)return false;
 for(auto G:BP->FunctionGraphs)if(G->GetFName()==Name)return true;
 auto* Fn=BP->ParentClass->FindFunctionByName(Function);if(!Fn)return false;
 auto* Graph=FBlueprintEditorUtils::CreateNewGraph(BP,Name,UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());FBlueprintEditorUtils::AddFunctionGraph(BP,Graph,true,static_cast<UFunction*>(nullptr));
 UK2Node_FunctionEntry* Entry=nullptr;for(auto N:Graph->Nodes)if(auto* Found=Cast<UK2Node_FunctionEntry>(N))Entry=Found;if(!Entry)return false;
 auto* Call=NewObject<UK2Node_CallFunction>(Graph);Graph->AddNode(Call,false,false);Call->CreateNewGuid();Call->SetFromFunction(Fn);Call->AllocateDefaultPins();Call->NodePosX=300;
 auto* Exec=Entry->FindPin(UEdGraphSchema_K2::PN_Then);auto* Input=Call->FindPin(UEdGraphSchema_K2::PN_Execute);if(Exec&&Input)Graph->GetSchema()->TryCreateConnection(Exec,Input);
 for(TFieldIterator<FProperty> It(Fn);It;++It){auto* Property=*It;if(!Property->HasAnyPropertyFlags(CPF_Parm)||Property->HasAnyPropertyFlags(CPF_ReturnParm|CPF_OutParm))continue;FEdGraphPinType Type;if(GetDefault<UEdGraphSchema_K2>()->ConvertPropertyToPinType(Property,Type)){auto* Param=Entry->CreateUserDefinedPin(Property->GetFName(),Type,EGPD_Output);auto* Target=Call->FindPin(Property->GetFName());if(Param&&Target)Graph->GetSchema()->TryCreateConnection(Param,Target);}}
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return true;
}

#include "K2Node_FunctionResult.h"
#include "Kismet/KismetMathLibrary.h"
bool UDeliveryEditorLibrary::BuildRewardGraph(UBlueprint* BP){
 if(!BP||!BP->ParentClass)return false;
 FName Name(TEXT("RewardForDistance"));for(auto Existing:BP->FunctionGraphs)if(Existing->GetFName()==Name)return true;
 UFunction* Signature=BP->ParentClass->FindFunctionByName(Name);if(!Signature)return false;
 auto* G=FBlueprintEditorUtils::CreateNewGraph(BP,Name,UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());
 FBlueprintEditorUtils::AddFunctionGraph(BP,G,false,BP->ParentClass.Get());
 UK2Node_FunctionEntry* E=nullptr;UK2Node_FunctionResult* R=nullptr;
 for(auto N:G->Nodes){if(auto* X=Cast<UK2Node_FunctionEntry>(N))E=X;if(auto* X=Cast<UK2Node_FunctionResult>(N))R=X;}
 if(!E||!R)return false;
 auto Call=[&](const TCHAR* Fn,int X){auto* N=NewObject<UK2Node_CallFunction>(G);G->AddNode(N,false,false);N->CreateNewGuid();N->SetFromFunction(UKismetMathLibrary::StaticClass()->FindFunctionByName(Fn));N->AllocateDefaultPins();N->NodePosX=X;return N;};
 auto Link=[&](UEdGraphPin* A,UEdGraphPin* B){return A&&B&&G->GetSchema()->TryCreateConnection(A,B);};
 auto Value=[&](UK2Node_CallFunction* N,const TCHAR* Pin,const TCHAR* V){if(auto* P=N->FindPin(Pin))G->GetSchema()->TrySetDefaultValue(*P,V);};
 auto* Map=Call(TEXT("MapRangeClamped"),250);Value(Map,TEXT("InRangeA"),TEXT("100"));Value(Map,TEXT("InRangeB"),TEXT("900"));Value(Map,TEXT("OutRangeA"),TEXT("5000"));Value(Map,TEXT("OutRangeB"),TEXT("50000"));Link(E->FindPin(TEXT("Meters")),Map->FindPin(TEXT("Value")));
 auto* Mult=Call(TEXT("Multiply_DoubleDouble"),500);Link(Map->FindPin(UEdGraphSchema_K2::PN_ReturnValue),Mult->FindPin(TEXT("A")));Link(E->FindPin(TEXT("Multiplier")),Mult->FindPin(TEXT("B")));
 auto* Clamp=Call(TEXT("FClamp"),750);Value(Clamp,TEXT("Min"),TEXT("5000"));Value(Clamp,TEXT("Max"),TEXT("50000"));Link(Mult->FindPin(UEdGraphSchema_K2::PN_ReturnValue),Clamp->FindPin(TEXT("Value")));
 auto* Round=Call(TEXT("Round"),1000);Link(Clamp->FindPin(UEdGraphSchema_K2::PN_ReturnValue),Round->FindPin(TEXT("A")));Link(Round->FindPin(UEdGraphSchema_K2::PN_ReturnValue),R->FindPin(UEdGraphSchema_K2::PN_ReturnValue));Link(E->FindPin(UEdGraphSchema_K2::PN_Then),R->FindPin(UEdGraphSchema_K2::PN_Execute));R->NodePosX=1250;
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return BP->Status!=BS_Error;
}

#include "K2Node_MacroInstance.h"
#include "K2Node_CallArrayFunction.h"
#include "K2Node_VariableGet.h"
#include "K2Node_VariableSet.h"
#include "K2Node_IfThenElse.h"
#include "K2Node_BreakStruct.h"
#include "K2Node_MakeStruct.h"
#include "K2Node_DynamicCast.h"
#include "K2Node_CallParentFunction.h"
#include "K2Node_GetDataTableRow.h"
#include "K2Node_CallDelegate.h"
#include "K2Node_MakeArray.h"
#include "K2Node_Message.h"
#include "Json.h"
bool UDeliveryEditorLibrary::BuildLogicGraph(UBlueprint* BP,FName Name,const FString& Specification){
 if(!BP||!BP->ParentClass)return false;
 TSharedPtr<FJsonObject> Spec;if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Specification),Spec))return false;
 // Editor authoring only: copy a signature into a user-defined graph, without retaining its native owner.
 UFunction* Signature=nullptr;FString SignatureOwner;
 if(Spec->TryGetStringField(TEXT("signature_owner"),SignatureOwner)){
  UClass* Source=LoadObject<UClass>(nullptr,*SignatureOwner);if(Source)Signature=Source->FindFunctionByName(Name);
  if(!Signature)return false;
 }
 UEdGraph* InterfaceGraph=nullptr;FString InterfaceOwner;
 if(Spec->TryGetStringField(TEXT("interface_owner"),InterfaceOwner)){UClass* Interface=LoadObject<UClass>(nullptr,*InterfaceOwner);if(!Interface||!Interface->HasAnyClassFlags(CLASS_Interface))return false;if(!BP->GeneratedClass->ImplementsInterface(Interface))if(!FBlueprintEditorUtils::ImplementNewInterface(BP,FTopLevelAssetPath(Interface)))return false;for(auto& Desc:BP->ImplementedInterfaces)if(Desc.Interface==Interface)for(auto Graph:Desc.Graphs)if(Graph->GetFName()==Name)InterfaceGraph=Graph;Signature=Interface->FindFunctionByName(Name);if(!Signature||!InterfaceGraph)return false;auto Existing=InterfaceGraph->Nodes;for(auto Node:Existing){Node->BreakAllNodeLinks();if(!Node->IsA<UK2Node_FunctionEntry>()&&!Node->IsA<UK2Node_FunctionResult>())InterfaceGraph->RemoveNode(Node);}}
 const bool CustomSignature=Spec->HasField(TEXT("parameters"));
 if(!Signature&&!BP->ParentClass->FindFunctionByName(Name)&&!CustomSignature)return false;
 for(int I=BP->FunctionGraphs.Num()-1;I>=0;--I)if(!InterfaceGraph&&BP->FunctionGraphs[I]->GetFName()==Name)FBlueprintEditorUtils::RemoveGraph(BP,BP->FunctionGraphs[I]);
 auto* G=InterfaceGraph?InterfaceGraph:FBlueprintEditorUtils::CreateNewGraph(BP,Name,UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());if(InterfaceGraph){}else if(Signature){FBlueprintEditorUtils::AddFunctionGraph(BP,G,true,Signature);GetDefault<UEdGraphSchema_K2>()->AddExtraFunctionFlags(G,Signature->FunctionFlags&(FUNC_BlueprintPure|FUNC_Const));}else if(CustomSignature){FBlueprintEditorUtils::AddFunctionGraph(BP,G,true,static_cast<UFunction*>(nullptr));bool Pure=false,Const=false;Spec->TryGetBoolField(TEXT("pure"),Pure);Spec->TryGetBoolField(TEXT("const"),Const);GetDefault<UEdGraphSchema_K2>()->AddExtraFunctionFlags(G,(Pure?FUNC_BlueprintPure:0)|(Const?FUNC_Const:0));}else FBlueprintEditorUtils::AddFunctionGraph(BP,G,false,BP->ParentClass.Get());
 // Remap copied parameter types to asset-authored enums/structs/classes before compiling.
 const TSharedPtr<FJsonObject>* TypeMap=nullptr;Spec->TryGetObjectField(TEXT("type_remap"),TypeMap);
 auto RemapObject=[&](UObject* Object)->UObject*{if(!Object||!TypeMap)return Object;FString Path;if((*TypeMap)->TryGetStringField(Object->GetPathName(),Path))return LoadObject<UObject>(nullptr,*Path);return Object;};
 auto RemapType=[&](FEdGraphPinType& Type){Type.PinSubCategoryObject=RemapObject(Type.PinSubCategoryObject.Get());Type.PinValueType.TerminalSubCategoryObject=RemapObject(Type.PinValueType.TerminalSubCategoryObject.Get());};
 if(TypeMap)for(auto Node:G->Nodes){for(auto* Pin:Node->Pins)RemapType(Pin->PinType);if(auto* Editable=Cast<UK2Node_EditablePinBase>(Node))for(auto Info:Editable->UserDefinedPins)RemapType(Info->PinType);}
 auto ResolvePin=[](UK2Node* Node,const FString& Name,EEdGraphPinDirection Direction=EGPD_MAX)->UEdGraphPin*{
  if(!Node)return nullptr;if(auto* Exact=Node->FindPin(*Name,Direction))return Exact;
  auto Normal=[](FString Value){Value.ReplaceInline(TEXT(" "),TEXT(""));Value.ReplaceInline(TEXT("_"),TEXT(""));return Value.ToLower();};
  const FString Wanted=Normal(Name);for(auto* Pin:Node->Pins){if(Direction!=EGPD_MAX&&Pin->Direction!=Direction)continue;if(Normal(Pin->PinFriendlyName.ToString())==Wanted)return Pin;}
  if(auto* Break=Cast<UK2Node_BreakStruct>(Node))if(Direction!=EGPD_Output)for(auto* Pin:Node->Pins)if(Pin->Direction==EGPD_Input&&Pin->PinType.PinCategory==UEdGraphSchema_K2::PC_Struct&&Break->StructType&&Pin->PinType.PinSubCategoryObject==Break->StructType)return Pin;
  if(auto* Make=Cast<UK2Node_MakeStruct>(Node))if(Direction!=EGPD_Input)for(auto* Pin:Node->Pins)if(Pin->Direction==EGPD_Output&&Pin->PinType.PinCategory==UEdGraphSchema_K2::PC_Struct&&Make->StructType&&Pin->PinType.PinSubCategoryObject==Make->StructType)return Pin;
  return nullptr;
 };
 TMap<FString,UK2Node*> Nodes;for(auto N:G->Nodes){if(auto* E=Cast<UK2Node_FunctionEntry>(N))Nodes.Add(TEXT("entry"),E);if(auto* R=Cast<UK2Node_FunctionResult>(N))Nodes.Add(TEXT("result"),R);}
 if(!Nodes.Contains(TEXT("result"))&&Nodes.Contains(TEXT("entry"))){auto* R=NewObject<UK2Node_FunctionResult>(G);R->FunctionReference=CastChecked<UK2Node_FunctionEntry>(Nodes[TEXT("entry")])->FunctionReference;G->AddNode(R,false,false);R->CreateNewGuid();R->AllocateDefaultPins();Nodes.Add(TEXT("result"),R);}
 if(CustomSignature)for(auto Value:Spec->GetArrayField(TEXT("parameters"))){auto Param=Value->AsObject();FEdGraphPinType Type;const FString Category=Param->GetStringField(TEXT("category"));Type.PinCategory=FName(*Category);if(Category==TEXT("real")){Type.PinSubCategory=UEdGraphSchema_K2::PC_Float;}FString ObjectPath;if(Param->TryGetStringField(TEXT("object"),ObjectPath))Type.PinSubCategoryObject=LoadObject<UObject>(nullptr,*ObjectPath);bool Array=false;Param->TryGetBoolField(TEXT("array"),Array);if(Array)Type.ContainerType=EPinContainerType::Array;bool Out=false;Param->TryGetBoolField(TEXT("out"),Out);auto* Editable=Cast<UK2Node_EditablePinBase>(Nodes[Out?TEXT("result"):TEXT("entry")]);Editable->CreateUserDefinedPin(FName(*Param->GetStringField(TEXT("name"))),Type,Out?EGPD_Input:EGPD_Output);}
 if(Nodes.Contains(TEXT("entry")))for(auto* Pin:Nodes[TEXT("entry")]->Pins)if(Pin->PinType.PinCategory==UEdGraphSchema_K2::PC_Exec)Pin->BreakAllPinLinks();
 const TArray<TSharedPtr<FJsonValue>>* Variables=nullptr;if(Spec->TryGetArrayField(TEXT("variables"),Variables))for(auto V:*Variables){auto O=V->AsObject();FEdGraphPinType Type;Type.PinCategory=UEdGraphSchema_K2::PC_Real;Type.PinSubCategory=UEdGraphSchema_K2::PC_Float;FString Kind;O->TryGetStringField(TEXT("type"),Kind);if(Kind==TEXT("bool")){Type.PinCategory=UEdGraphSchema_K2::PC_Boolean;Type.PinSubCategory=NAME_None;}FName Var(*O->GetStringField(TEXT("name")));bool Exists=false;for(auto Desc:BP->NewVariables)if(Desc.VarName==Var)Exists=true;if(!Exists)FBlueprintEditorUtils::AddMemberVariable(BP,Var,Type,O->GetStringField(TEXT("default")));}
 int Index=0;bool OK=true;
 for(auto V:Spec->GetArrayField(TEXT("nodes"))){auto O=V->AsObject();FString ID=O->GetStringField(TEXT("id")),Kind=O->GetStringField(TEXT("kind"));UK2Node* N=nullptr;
  if(Kind==TEXT("get")||Kind==TEXT("set")){FName Var(*O->GetStringField(TEXT("var")));if(Kind==TEXT("get")){auto* X=NewObject<UK2Node_VariableGet>(G);X->VariableReference.SetSelfMember(Var);N=X;}else{auto* X=NewObject<UK2Node_VariableSet>(G);X->VariableReference.SetSelfMember(Var);N=X;}}
  else if(Kind==TEXT("getfield")||Kind==TEXT("setfield")){UClass* Owner=LoadObject<UClass>(nullptr,*O->GetStringField(TEXT("owner")));if(!Owner)return false;FName Var(*O->GetStringField(TEXT("var")));if(Kind==TEXT("getfield")){auto* X=NewObject<UK2Node_VariableGet>(G);X->VariableReference.SetExternalMember(Var,Owner);N=X;}else{auto* X=NewObject<UK2Node_VariableSet>(G);X->VariableReference.SetExternalMember(Var,Owner);N=X;}}
  else if(Kind==TEXT("cast")){auto* X=NewObject<UK2Node_DynamicCast>(G);X->TargetType=LoadObject<UClass>(nullptr,*O->GetStringField(TEXT("type")));if(!X->TargetType)return false;X->SetPurity(true);N=X;}
  else if(Kind==TEXT("foreach")){auto* Macro=LoadObject<UBlueprint>(nullptr,TEXT("/Engine/EditorBlueprintResources/StandardMacros.StandardMacros"));UEdGraph* Loop=nullptr;if(Macro)for(auto Graph:Macro->MacroGraphs)if(Graph->GetName()==TEXT("ForEachLoop"))Loop=Graph;if(!Loop)return false;auto* X=NewObject<UK2Node_MacroInstance>(G);X->SetMacroGraph(Loop);N=X;}
  else if(Kind==TEXT("message")){UClass* Interface=LoadObject<UClass>(nullptr,*O->GetStringField(TEXT("owner")));UFunction* Fn=Interface?Interface->FindFunctionByName(*O->GetStringField(TEXT("fn"))):nullptr;if(!Fn)return false;auto* X=NewObject<UK2Node_Message>(G);X->SetFromFunction(Fn);N=X;}
  else if(Kind==TEXT("makearray"))N=NewObject<UK2Node_MakeArray>(G);
  else if(Kind==TEXT("delegate")){auto* X=NewObject<UK2Node_CallDelegate>(G);auto* Property=FindFProperty<FMulticastDelegateProperty>(BP->GeneratedClass,FName(*O->GetStringField(TEXT("var"))));if(!Property)return false;X->SetFromProperty(Property,true,BP->GeneratedClass);N=X;}
  else if(Kind==TEXT("datatable"))N=NewObject<UK2Node_GetDataTableRow>(G);
  else if(Kind==TEXT("branch"))N=NewObject<UK2Node_IfThenElse>(G);
  else if(Kind==TEXT("break")){auto* X=NewObject<UK2Node_BreakStruct>(G);X->StructType=LoadObject<UScriptStruct>(nullptr,*O->GetStringField(TEXT("type")));N=X;}
  else if(Kind==TEXT("make")){auto* X=NewObject<UK2Node_MakeStruct>(G);X->StructType=LoadObject<UScriptStruct>(nullptr,*O->GetStringField(TEXT("type")));N=X;}
  else if(Kind==TEXT("return")){auto* X=NewObject<UK2Node_FunctionResult>(G);X->FunctionReference=CastChecked<UK2Node_FunctionEntry>(Nodes[TEXT("entry")])->FunctionReference;N=X;}
  else if(Kind==TEXT("call")){FString Owner;O->TryGetStringField(TEXT("owner"),Owner);UClass* Class=Owner.IsEmpty()?BP->ParentClass.Get():LoadObject<UClass>(nullptr,*Owner);UFunction* Fn=Class?Class->FindFunctionByName(*O->GetStringField(TEXT("fn"))):nullptr;if(!Fn){UE_LOG(LogTemp,Error,TEXT("BP missing function %s"),*ID);return false;}UK2Node_CallFunction* X=Fn->HasMetaData(TEXT("ArrayParm"))?NewObject<UK2Node_CallArrayFunction>(G):NewObject<UK2Node_CallFunction>(G);X->SetFromFunction(Fn);N=X;}
  if(!N)return false;G->AddNode(N,false,false);N->CreateNewGuid();N->PostPlacedNewNode();N->AllocateDefaultPins();N->NodePosX=(Index%5)*300;N->NodePosY=(Index/5)*230;Index++;Nodes.Add(ID,N);
  const TSharedPtr<FJsonObject>* Defaults=nullptr;if(O->TryGetObjectField(TEXT("defaults"),Defaults))for(auto Pair:(*Defaults)->Values){auto* Pin=ResolvePin(N,FString(*Pair.Key));if(!Pin){UE_LOG(LogTemp,Error,TEXT("BP default pin missing %s.%s"),*ID,*Pair.Key);OK=false;continue;}if(Pin->PinType.PinCategory==UEdGraphSchema_K2::PC_Class)Pin->DefaultObject=LoadObject<UClass>(nullptr,*Pair.Value->AsString());else if(Kind==TEXT("datatable")&&Pair.Key==TEXT("DataTable")){Pin->DefaultObject=LoadObject<UDataTable>(nullptr,*Pair.Value->AsString());N->PinDefaultValueChanged(Pin);}else G->GetSchema()->TrySetDefaultValue(*Pin,Pair.Value->AsString());}
 }
 for(auto V:Spec->GetArrayField(TEXT("links"))){auto A=V->AsArray();FString S=A[0]->AsString(),SP=A[1]->AsString(),D=A[2]->AsString(),DP=A[3]->AsString();auto* SN=Nodes.FindRef(S);auto* DN=Nodes.FindRef(D);auto* Out=ResolvePin(SN,SP,EGPD_Output);auto* In=ResolvePin(DN,DP,EGPD_Input);
  if(!Out||!In||!G->GetSchema()->TryCreateConnection(Out,In)){UE_LOG(LogTemp,Error,TEXT("BP link failed %s.%s -> %s.%s"),*S,*SP,*D,*DP);OK=false;}
 }
 // Wildcard array pins acquire their type while links are connected; restore authored literals afterwards.
 for(auto Value:Spec->GetArrayField(TEXT("nodes"))){auto O=Value->AsObject();auto* Node=Nodes.FindRef(O->GetStringField(TEXT("id")));if(!Node)continue;const TSharedPtr<FJsonObject>* Defaults=nullptr;if(!O->TryGetObjectField(TEXT("defaults"),Defaults))continue;for(auto Pair:(*Defaults)->Values){if(O->GetStringField(TEXT("kind"))==TEXT("datatable")&&Pair.Key==TEXT("DataTable"))continue;auto* Pin=ResolvePin(Node,FString(*Pair.Key));if(!Pin)continue;if(Pin->PinType.PinCategory==UEdGraphSchema_K2::PC_Class)Pin->DefaultObject=LoadObject<UClass>(nullptr,*Pair.Value->AsString());else G->GetSchema()->TrySetDefaultValue(*Pin,Pair.Value->AsString());}}
 // AddFunctionGraph supplies parent-call nodes. Our overrides implement their own rules;
 // remove only impure parent calls that have no execution path, including older graphs.
 for(auto FunctionGraph:BP->FunctionGraphs){auto Existing=FunctionGraph->Nodes;for(auto Node:Existing)if(auto* Parent=Cast<UK2Node_CallParentFunction>(Node))if(auto* Exec=Parent->FindPin(UEdGraphSchema_K2::PN_Execute))if(Exec->LinkedTo.IsEmpty()){Parent->BreakAllNodeLinks();FunctionGraph->RemoveNode(Parent);}}
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return OK&&BP->Status!=BS_Error;
}
#include "../BogotaVoxel/DeliveryAnimInstance.h"
#include "Animation/AnimBlueprint.h"
#include "Animation/AnimSequence.h"
#include "Factories/AnimBlueprintFactory.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_SequencePlayer.h"
#include "AnimGraphNode_SequenceEvaluator.h"
#include "AnimGraphNode_BlendListByBool.h"
#include "AssetToolsModule.h"
UBlueprint* UDeliveryEditorLibrary::BuildLocomotionBlueprint(USkeleton* Skeleton,UAnimSequence* Idle,UAnimSequence* Walk,UAnimSequence* Bike,UAnimSequence* Moto,UAnimSequence* Jump){return BuildCharacterAnimationBlueprint(TEXT("ABP_DeliveryRider"),Skeleton,Idle,Walk,Bike,Moto,Jump);}
UBlueprint* UDeliveryEditorLibrary::BuildCharacterAnimationBlueprint(FName AssetName,USkeleton* Skeleton,UAnimSequence* Idle,UAnimSequence* Walk,UAnimSequence* Bike,UAnimSequence* Moto,UAnimSequence* Jump){
 if(!Skeleton||!Idle||!Walk||!Bike||!Moto||!Jump)return nullptr;
 const FString AssetPath=FString(TEXT("/Game/Delivery/Animation/"))+AssetName.ToString();auto* BP=LoadObject<UAnimBlueprint>(nullptr,*AssetPath);
 if(!BP){auto* Factory=NewObject<UAnimBlueprintFactory>();Factory->ParentClass=UDeliveryAnimInstance::StaticClass();Factory->TargetSkeleton=Skeleton;BP=Cast<UAnimBlueprint>(FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools")).Get().CreateAsset(AssetName.ToString(),TEXT("/Game/Delivery/Animation"),UAnimBlueprint::StaticClass(),Factory));}
 if(!BP)return nullptr;UEdGraph* G=nullptr;TArray<UEdGraph*> Graphs;BP->GetAllGraphs(Graphs);for(auto* Graph:Graphs)if(Graph->GetName()==TEXT("AnimGraph"))G=Graph;if(!G)return nullptr;
 UAnimGraphNode_Root* Root=nullptr;for(auto N:G->Nodes)if(auto* R=Cast<UAnimGraphNode_Root>(N))Root=R;if(!Root)return nullptr;
 auto OldNodes=G->Nodes;for(auto N:OldNodes)if(N!=Root)G->RemoveNode(N);Root->BreakAllNodeLinks();Root->NodePosX=1400;Root->NodePosY=200;
 auto Add=[&](UEdGraphNode* N,int32 X,int32 Y){G->AddNode(N,false,false);N->CreateNewGuid();N->NodePosX=X;N->NodePosY=Y;N->PostPlacedNewNode();N->AllocateDefaultPins();};
 bool OK=true;auto Link=[&](UEdGraphNode* A,const TCHAR* AP,UEdGraphNode* B,const TCHAR* BPin){auto* Out=A->FindPin(AP,EGPD_Output);auto* In=B->FindPin(BPin,EGPD_Input);if(!Out||!In||!G->GetSchema()->TryCreateConnection(Out,In)){UE_LOG(LogTemp,Error,TEXT("ANIM_LINK_FAILED %s.%s -> %s.%s"),*A->GetClass()->GetName(),AP,*B->GetClass()->GetName(),BPin);for(auto* Pin:B->Pins)UE_LOG(LogTemp,Display,TEXT("ANIM_PIN %s"),*Pin->PinName.ToString());OK=false;}};
 auto Expose=[&](UAnimGraphNode_Base* N,FName Name){for(auto& Pin:N->ShowPinForProperties)if(Pin.PropertyName==Name)Pin.bShowPin=true;N->ReconstructNode();};
 auto Value=[&](const TCHAR* Name,int32 X,int32 Y){auto* N=NewObject<UK2Node_VariableGet>(G);N->VariableReference.SetSelfMember(Name);Add(N,X,Y);return N;};
 auto Player=[&](UAnimSequence* Sequence,int32 Y){auto* N=NewObject<UAnimGraphNode_SequencePlayer>(G);N->Node.SetSequence(Sequence);Add(N,0,Y);return N;};
 auto Evaluator=[&](UAnimSequence* Sequence,const TCHAR* Time,int32 Y){auto* N=NewObject<UAnimGraphNode_SequenceEvaluator>(G);N->Node.SetSequence(Sequence);N->Node.SetTeleportToExplicitTime(true);Add(N,0,Y);Expose(N,TEXT("ExplicitTime"));auto* V=Value(Time,-250,Y+100);Link(V,Time,N,TEXT("ExplicitTime"));return N;};
 auto Blend=[&](const TCHAR* Variable,UEdGraphNode* True,UEdGraphNode* False,int32 X,int32 Y,float Seconds){auto* N=NewObject<UAnimGraphNode_BlendListByBool>(G);Add(N,X,Y);Expose(N,TEXT("bActiveValue"));for(const TCHAR* PinName:{TEXT("BlendTime_0"),TEXT("BlendTime_1")})if(auto* Pin=N->FindPin(PinName))G->GetSchema()->TrySetDefaultValue(*Pin,FString::SanitizeFloat(Seconds));Link(True,TEXT("Pose"),N,TEXT("BlendPose_0"));Link(False,TEXT("Pose"),N,TEXT("BlendPose_1"));auto* V=Value(Variable,X,Y+200);Link(V,Variable,N,TEXT("bActiveValue"));return N;};
 auto* IdleNode=Player(Idle,0);auto* WalkNode=Player(Walk,250);Expose(WalkNode,TEXT("PlayRate"));Link(Value(TEXT("WalkRate"),-250,350),TEXT("WalkRate"),WalkNode,TEXT("PlayRate"));
 auto* BikeNode=Evaluator(Bike,TEXT("PedalTime"),600);auto* MotoNode=Player(Moto,850);auto* JumpNode=Evaluator(Jump,TEXT("JumpTime"),1100);
 auto* Ground=Blend(TEXT("Walking"),WalkNode,IdleNode,350,150,.16f);auto* Vehicle=Blend(TEXT("Motorcycle"),MotoNode,BikeNode,350,700,.12f);auto* Air=Blend(TEXT("Jumping"),JumpNode,Ground,700,200,.09f);auto* Mounted=Blend(TEXT("Mounted"),Vehicle,Air,1050,200,.20f);Link(Mounted,TEXT("Pose"),Root,TEXT("Result"));
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return OK&&BP->Status!=BS_Error?BP:nullptr;
}




FString UDeliveryEditorLibrary::AuditBlueprint(UBlueprint* BP){
 TSharedRef<FJsonObject> Report=MakeShared<FJsonObject>();if(!BP)return TEXT("{}");
 Report->SetStringField(TEXT("asset"),BP->GetPathName());Report->SetStringField(TEXT("parent"),GetPathNameSafe(BP->ParentClass));
 TArray<TSharedPtr<FJsonValue>> Graphs;int32 Total=0;
 TArray<UEdGraph*> AuditGraphs=BP->FunctionGraphs;for(auto Graph:BP->UbergraphPages)AuditGraphs.AddUnique(Graph);for(const auto& Interface:BP->ImplementedInterfaces)for(auto Graph:Interface.Graphs)AuditGraphs.AddUnique(Graph);for(auto Graph:AuditGraphs){TSharedRef<FJsonObject> G=MakeShared<FJsonObject>();G->SetStringField(TEXT("name"),Graph->GetName());G->SetNumberField(TEXT("nodes"),Graph->Nodes.Num());if(auto* Function=BP->GeneratedClass->FindFunctionByName(Graph->GetFName())){G->SetStringField(TEXT("function_owner"),Function->GetOwnerClass()->GetPathName());G->SetNumberField(TEXT("bytecode"),Function->Script.Num());}TArray<TSharedPtr<FJsonValue>> Pins;for(auto N:Graph->Nodes)for(auto* Pin:N->Pins){FString Line=N->GetClass()->GetName()+TEXT(".")+Pin->GetName()+TEXT("=")+Pin->DefaultValue+FString::Printf(TEXT(" links:%d"),Pin->LinkedTo.Num());Pins.Add(MakeShared<FJsonValueString>(Line));}G->SetArrayField(TEXT("pins"),Pins);Total+=Graph->Nodes.Num();TArray<TSharedPtr<FJsonValue>> Calls;
 for(auto N:Graph->Nodes)if(auto* Call=Cast<UK2Node_CallFunction>(N))if(auto* F=Call->GetTargetFunction()){FString Owner=F->GetOwnerClass()->GetPathName();if(Owner.StartsWith(TEXT("/Script/BogotaVoxel")))Calls.Add(MakeShared<FJsonValueString>(F->GetName()));}
 G->SetArrayField(TEXT("native_calls"),Calls);Graphs.Add(MakeShared<FJsonValueObject>(G));}
 Report->SetArrayField(TEXT("graphs"),Graphs);Report->SetNumberField(TEXT("logic_nodes"),Total);Report->SetBoolField(TEXT("compiled"),BP->Status!=BS_Error);
 FString Result;auto Writer=TJsonWriterFactory<>::Create(&Result);FJsonSerializer::Serialize(Report,Writer);return Result;
}

#include "Editor.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "UObject/Script.h"
#include "../BogotaVoxel/BogotaGame.h"
#include "Components/PoseableMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
FString UDeliveryEditorLibrary::ValidateTrafficPaint(UClass* CityClass){
 FEditorScriptExecutionGuard Guard;UWorld* World=GEditor->GetEditorWorldContext().World();TSet<AActor*> Before;for(TActorIterator<AActor> It(World);It;++It)Before.Add(*It);
 auto* City=World->SpawnActor<ABogotaCity>(CityClass);if(!City)return TEXT("{}");City->ValidateTraffic(0);
 TMap<FString,TSet<FString>> ColorsByModel;TSet<FString> Colors;int32 InvalidMasks=0,PreservedLiveries=0,ColoredParked=0,InvalidMaterialParents=0;
 for(const auto& Car:City->Vehicles)if(Car.Visual.IsValid()){
  FString Model=GetNameSafe(Car.Visual->GetSkinnedAsset());auto* Material=Cast<UMaterialInstanceDynamic>(Car.Visual->GetMaterial(0));
  if(Model.StartsWith(TEXT("SK_Private"))&&Material){if(Cast<UMaterialInstanceDynamic>(Material->Parent))InvalidMaterialParents++;FString Color=Material->K2_GetVectorParameterValue(TEXT("BodyPaint")).ToString();ColorsByModel.FindOrAdd(Model).Add(Color);Colors.Add(Color);}
  else if(Car.Visual->GetMaterial(0))PreservedLiveries++;
 }
 for(const auto& Car:City->ParkedCars)if(Car.Visual.IsValid())if(auto* Material=Cast<UMaterialInstanceDynamic>(Car.Visual->GetMaterial(0)))if(Material->K2_GetScalarParameterValue(TEXT("PaintEnabled"))>.5f)ColoredParked++;
 int32 Minimum=1000;for(const auto& Entry:ColorsByModel){Minimum=FMath::Min(Minimum,Entry.Value.Num());auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*FString::Printf(TEXT("/Game/Traffic/Detailed/%s.%s"),*Entry.Key,*Entry.Key));auto* Data=Mesh?Mesh->GetResourceForRendering():nullptr;int32 Body=0,Detail=0;
  if(!Data||Data->LODRenderData.IsEmpty())InvalidMasks++;
  else{const auto& Buffer=Data->LODRenderData[0].StaticVertexBuffers.StaticMeshVertexBuffer;if(Buffer.GetNumTexCoords()<2)InvalidMasks++;else{for(uint32 V=0;V<Buffer.GetNumVertices();V++){auto UV=Buffer.GetVertexUV(V,1);if(UV.X>.5f)Body++;else Detail++;}if(Body==0||Detail==0)InvalidMasks++;}}
 }
 TSharedRef<FJsonObject> Report=MakeShared<FJsonObject>();Report->SetNumberField(TEXT("private_models"),ColorsByModel.Num());Report->SetNumberField(TEXT("private_colors"),Colors.Num());Report->SetNumberField(TEXT("minimum_colors_per_model"),Minimum);Report->SetNumberField(TEXT("invalid_paint_masks"),InvalidMasks);Report->SetNumberField(TEXT("invalid_material_parents"),InvalidMaterialParents);Report->SetNumberField(TEXT("preserved_taxis_and_buses"),PreservedLiveries);Report->SetNumberField(TEXT("colored_parked_cars"),ColoredParked);Report->SetBoolField(TEXT("blueprint_city"),City->GetClass()!=ABogotaCity::StaticClass());
 TArray<AActor*> Created;for(TActorIterator<AActor> It(World);It;++It)if(!Before.Contains(*It))Created.Add(*It);for(auto* Actor:Created)Actor->Destroy();
 FString Result;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Result));return Result;
}

int32 UDeliveryEditorLibrary::CleanBlueprint(UBlueprint* BP){
 if(!BP)return 0;int32 Removed=0;
 for(auto Graph:BP->FunctionGraphs){auto Nodes=Graph->Nodes;for(auto Node:Nodes)if(auto* Parent=Cast<UK2Node_CallParentFunction>(Node)){bool Used=false;for(auto* Pin:Parent->Pins)if(Pin->Direction==EGPD_Output&&!Pin->LinkedTo.IsEmpty())Used=true;if(!Used){Parent->BreakAllNodeLinks();Graph->RemoveNode(Parent);Removed++;}}}
 if(Removed){FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();}return Removed;
}

int32 UDeliveryEditorLibrary::CleanCityDuplicateBikes(){
 UWorld* World=GEditor->GetEditorWorldContext().World();int32 Removed=0;TArray<AActor*> Extras;
 for(TActorIterator<ABogotaCity> City(World);City;++City){TSet<AActor*> Linked;for(auto Bike:City->BikeActors)if(Bike.IsValid())Linked.Add(Bike.Get());
 for(TActorIterator<AStaticMeshActor> It(World);It;++It)if(!Linked.Contains(*It)&&GetNameSafe(It->GetStaticMeshComponent()->GetStaticMesh())==TEXT("SM_Bicycle")){for(auto* Bike:Linked)if(FVector::DistSquared(Bike->GetActorLocation(),It->GetActorLocation())<1){Extras.AddUnique(*It);break;}}}
 for(auto* Actor:Extras)if(GEditor->GetEditorWorldContext().World()->EditorDestroyActor(Actor,true))Removed++;return Removed;
}

FString UDeliveryEditorLibrary::ValidateMapRoutes(float Seconds){
 FEditorScriptExecutionGuard Guard;UWorld* World=GEditor->GetEditorWorldContext().World();
 for(TActorIterator<ABogotaCity> It(World);It;++It)return It->ValidateMapRoutes(Seconds);
 return TEXT("{}");
}

#include "Factories/StructureFactory.h"
#include "Factories/EnumFactory.h"
#include "Kismet2/StructureEditorUtils.h"
#include "Kismet2/EnumEditorUtils.h"
#include "UserDefinedStructure/UserDefinedStructEditorData.h"
#include "UObject/StructOnScope.h"

FString UDeliveryEditorLibrary::CreateBlueprintGameplaySchema(const FString& DestinationFolder){
 if(!DestinationFolder.StartsWith(TEXT("/Game/")))return TEXT("{\"error\":\"invalid_destination\"}");
 auto& Assets=FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools")).Get();
 TMap<UObject*,UObject*> Types;TArray<TSharedPtr<FJsonValue>> EnumRows,StructRows;
 auto Failure=[](const FString& Error){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("error"),Error);FString Out;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&Out));return Out;};
 for(const TCHAR* TypeName:{TEXT("EDeliveryState"),TEXT("EDeliveryVehicle"),TEXT("EUpgradeEffect")}){
  UEnum* Source=LoadObject<UEnum>(nullptr,*(FString(TEXT("/Script/BogotaVoxel."))+TypeName));if(!Source)return Failure(TypeName);
  FString Name=FString(TEXT("E_"))+FString(TypeName).RightChop(1),Path=DestinationFolder/TEXT("")/Name;
  UUserDefinedEnum* Target=LoadObject<UUserDefinedEnum>(nullptr,*Path);
  if(!Target){Target=Cast<UUserDefinedEnum>(Assets.CreateAsset(Name,DestinationFolder,UUserDefinedEnum::StaticClass(),NewObject<UEnumFactory>()));if(!Target)return Failure(Name);
   int32 Count=Source->NumEnums()-1;
   while(Target->NumEnums()-1<Count)FEnumEditorUtils::AddNewEnumeratorForUserDefinedEnum(Target);
   while(Target->NumEnums()-1>Count)FEnumEditorUtils::RemoveEnumeratorFromUserDefinedEnum(Target,Target->NumEnums()-2);
   for(int32 I=0;I<Count;I++)if(!FEnumEditorUtils::SetEnumeratorDisplayName(Target,I,FText::FromString(Source->GetNameStringByIndex(I))))return Failure(Name+TEXT(" display"));
  }
  Types.Add(Source,Target);Target->MarkPackageDirty();auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("source"),Source->GetPathName());Row->SetStringField(TEXT("asset"),Target->GetPathName());Row->SetNumberField(TEXT("values"),Target->NumEnums()-1);EnumRows.Add(MakeShared<FJsonValueObject>(Row));
 }
 for(const TCHAR* TypeName:{TEXT("DeliveryUpgrade"),TEXT("DeliveryShopTheme"),TEXT("DeliveryOrder"),TEXT("ActiveDelivery"),TEXT("DeliveryVehicleSpec"),TEXT("MapFootprint")}){
  UScriptStruct* Source=LoadObject<UScriptStruct>(nullptr,*(FString(TEXT("/Script/BogotaVoxel."))+TypeName));if(!Source)return Failure(TypeName);
  FString Name=FString(TEXT("ST_"))+TypeName,Path=DestinationFolder/TEXT("")/Name;UUserDefinedStruct* Target=LoadObject<UUserDefinedStruct>(nullptr,*Path);bool Created=!Target;
  if(Created)Target=Cast<UUserDefinedStruct>(Assets.CreateAsset(Name,DestinationFolder,UUserDefinedStruct::StaticClass(),NewObject<UStructureFactory>()));if(!Target)return Failure(Name);
  Types.Add(Source,Target);TArray<TSharedPtr<FJsonValue>> Fields;
  if(Created){TArray<FGuid> Placeholders;for(auto& Var:FStructureEditorUtils::GetVarDesc(Target))Placeholders.Add(Var.VarGuid);FStructOnScope Defaults(Source);
   for(TFieldIterator<FProperty> It(Source);It;++It){FProperty* Property=*It;FEdGraphPinType Type;if(!GetDefault<UEdGraphSchema_K2>()->ConvertPropertyToPinType(Property,Type))return Failure(Property->GetName());
    UObject* Original=Type.PinSubCategoryObject.Get();if(auto Replacement=Types.Find(Original))Type.PinSubCategoryObject=*Replacement;else if(Original&&Original->GetOutermost()->GetName()==TEXT("/Script/BogotaVoxel"))return Failure(TEXT("unmapped ")+Original->GetName());
    if(!FStructureEditorUtils::AddVariable(Target,Type))return Failure(Name+TEXT(" add ")+Property->GetName());FGuid Guid=FStructureEditorUtils::GetVarDesc(Target).Last().VarGuid;
    if(!FStructureEditorUtils::RenameVariable(Target,Guid,Property->GetName()))return Failure(Name+TEXT(" rename ")+Property->GetName());
    FString Default;Property->ExportTextItem_Direct(Default,Property->ContainerPtrToValuePtr<void>(Defaults.GetStructMemory()),nullptr,nullptr,PPF_None);
    if(UUserDefinedEnum* Enum=Cast<UUserDefinedEnum>(Type.PinSubCategoryObject.Get())){int64 Value=0;if(auto* EP=CastField<FEnumProperty>(Property))Value=EP->GetUnderlyingProperty()->GetSignedIntPropertyValue(Property->ContainerPtrToValuePtr<void>(Defaults.GetStructMemory()));else if(auto* BP=CastField<FByteProperty>(Property))Value=BP->GetPropertyValue(Property->ContainerPtrToValuePtr<void>(Defaults.GetStructMemory()));Default=Enum->GetNameStringByValue(Value);}
    if(!Default.IsEmpty()&&!(Cast<UUserDefinedStruct>(Type.PinSubCategoryObject.Get())))FStructureEditorUtils::ChangeVariableDefaultValue(Target,Guid,Default);
   }
   for(FGuid Guid:Placeholders)FStructureEditorUtils::RemoveVariable(Target,Guid);
  }
  for(auto& Var:FStructureEditorUtils::GetVarDesc(Target)){auto Field=MakeShared<FJsonObject>();Field->SetStringField(TEXT("friendly_name"),Var.FriendlyName);Field->SetStringField(TEXT("property_name"),Var.VarName.ToString());Field->SetStringField(TEXT("default"),Var.DefaultValue);Fields.Add(MakeShared<FJsonValueObject>(Field));}
  Target->MarkPackageDirty();auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("source"),Source->GetPathName());Row->SetStringField(TEXT("asset"),Target->GetPathName());Row->SetArrayField(TEXT("fields"),Fields);StructRows.Add(MakeShared<FJsonValueObject>(Row));
 }
 auto Report=MakeShared<FJsonObject>();Report->SetArrayField(TEXT("enums"),EnumRows);Report->SetArrayField(TEXT("structs"),StructRows);FString Out;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Out));return Out;
}

// Editor-only authoring: generated assets use Unreal's standard Blueprint input bindings.
#include "K2Node_InputAxisEvent.h"
#include "K2Node_InputAction.h"
bool UDeliveryEditorLibrary::BuildBlueprintInputGraph(UBlueprint* BP,const FString& Specification){
 if(!BP)return false;
 TArray<TSharedPtr<FJsonValue>> Items;
 if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Specification),Items))return false;
 BP->Modify();UEdGraph* Graph=nullptr;
 for(auto G:BP->UbergraphPages)if(G&&G->GetFName()==TEXT("PlayerInput")){Graph=G;break;}
 if(!Graph){Graph=FBlueprintEditorUtils::CreateNewGraph(BP,TEXT("PlayerInput"),UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());FBlueprintEditorUtils::AddUbergraphPage(BP,Graph);}
 else {TArray<UEdGraphNode*> Old;for(auto Node:Graph->Nodes)Old.Add(Node);for(auto Node:Old)Graph->RemoveNode(Node);}
 const auto* Schema=GetDefault<UEdGraphSchema_K2>();int32 Row=0;
 auto Add=[&](UEdGraphNode* Node,int32 X,int32 Y){Graph->AddNode(Node,false,false);Node->CreateNewGuid();Node->PostPlacedNewNode();Node->NodePosX=X;Node->NodePosY=Y;Node->AllocateDefaultPins();};
 auto Call=[&](const FString& Name,int32 Y)->UK2Node_CallFunction*{UFunction* Fn=BP->GeneratedClass?BP->GeneratedClass->FindFunctionByName(FName(*Name)):nullptr;if(!Fn)return nullptr;auto* Node=NewObject<UK2Node_CallFunction>(Graph);Node->SetFromFunction(Fn);Add(Node,400,Y);return Node;};
 for(auto Value:Items){const auto O=Value->AsObject();if(!O.IsValid())return false;const FString Kind=O->GetStringField(TEXT("kind"));const FName Name(*O->GetStringField(TEXT("name")));const int32 Y=Row++*300;
  if(Kind==TEXT("axis")){auto* Event=NewObject<UK2Node_InputAxisEvent>(Graph);Event->Initialize(Name);Event->bConsumeInput=false;Add(Event,0,Y);auto* Target=Call(O->GetStringField(TEXT("function")),Y);if(!Target)return false;FString Parameter=TEXT("V");O->TryGetStringField(TEXT("parameter"),Parameter);if(!Schema->TryCreateConnection(Event->FindPin(UEdGraphSchema_K2::PN_Then),Target->GetExecPin())||!Schema->TryCreateConnection(Event->FindPin(TEXT("AxisValue")),Target->FindPin(*Parameter)))return false;}
  else if(Kind==TEXT("action")){auto* Event=NewObject<UK2Node_InputAction>(Graph);Event->InputActionName=Name;Event->bConsumeInput=false;Event->bExecuteWhenPaused=false;Add(Event,0,Y);
   for(const TCHAR* Edge:{TEXT("pressed"),TEXT("released")}){FString Function;if(!O->TryGetStringField(Edge,Function)||Function.IsEmpty())continue;auto* Target=Call(Function,Y+(FCString::Strcmp(Edge,TEXT("released"))==0?120:0));if(!Target)return false;UEdGraphPin* Pin=FCString::Strcmp(Edge,TEXT("pressed"))==0?Event->GetPressedPin():Event->GetReleasedPin();if(!Schema->TryCreateConnection(Pin,Target->GetExecPin()))return false;}
  }else return false;
 }
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return BP->Status!=BS_Error;
}

#include "UObject/UObjectHash.h"
FString UDeliveryEditorLibrary::AuditBlueprintInputBindings(UBlueprint* BP){
 TSharedRef<FJsonObject> Report=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Bindings;int32 Axes=0,Actions=0;
 if(BP&&BP->GeneratedClass){TArray<UObject*> Objects;GetObjectsWithOuter(BP->GeneratedClass,Objects,false);
  for(auto* Object:Objects){const FString Name=Object->GetClass()->GetName();if(Name!=TEXT("InputAxisDelegateBinding")&&Name!=TEXT("InputActionDelegateBinding"))continue;TSharedRef<FJsonObject> Item=MakeShared<FJsonObject>();Item->SetStringField(TEXT("class"),Object->GetClass()->GetPathName());
   for(FName Field:{FName(TEXT("InputAxisDelegateBindings")),FName(TEXT("InputActionDelegateBindings"))})if(auto* Property=FindFProperty<FArrayProperty>(Object->GetClass(),Field)){FScriptArrayHelper Values(Property,Property->ContainerPtrToValuePtr<void>(Object));const int32 Count=Values.Num();Item->SetNumberField(Field.ToString(),Count);if(Field==TEXT("InputAxisDelegateBindings"))Axes+=Count;else Actions+=Count;}
   Bindings.Add(MakeShared<FJsonValueObject>(Item));
  }
 }
 Report->SetNumberField(TEXT("axes"),Axes);Report->SetNumberField(TEXT("action_edges"),Actions);Report->SetArrayField(TEXT("bindings"),Bindings);FString Out;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Out));return Out;
}
