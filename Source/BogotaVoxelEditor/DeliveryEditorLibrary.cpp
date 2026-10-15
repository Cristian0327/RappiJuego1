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
#include "Json.h"
bool UDeliveryEditorLibrary::BuildLogicGraph(UBlueprint* BP,FName Name,const FString& Specification){
 if(!BP||!BP->ParentClass||!BP->ParentClass->FindFunctionByName(Name))return false;
 TSharedPtr<FJsonObject> Spec;if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Specification),Spec))return false;
 for(int I=BP->FunctionGraphs.Num()-1;I>=0;--I)if(BP->FunctionGraphs[I]->GetFName()==Name)FBlueprintEditorUtils::RemoveGraph(BP,BP->FunctionGraphs[I]);
 auto* G=FBlueprintEditorUtils::CreateNewGraph(BP,Name,UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());FBlueprintEditorUtils::AddFunctionGraph(BP,G,false,BP->ParentClass.Get());
 TMap<FString,UK2Node*> Nodes;for(auto N:G->Nodes){if(auto* E=Cast<UK2Node_FunctionEntry>(N))Nodes.Add(TEXT("entry"),E);if(auto* R=Cast<UK2Node_FunctionResult>(N))Nodes.Add(TEXT("result"),R);}
 if(!Nodes.Contains(TEXT("result"))&&Nodes.Contains(TEXT("entry"))){auto* R=NewObject<UK2Node_FunctionResult>(G);R->FunctionReference=CastChecked<UK2Node_FunctionEntry>(Nodes[TEXT("entry")])->FunctionReference;G->AddNode(R,false,false);R->CreateNewGuid();R->AllocateDefaultPins();Nodes.Add(TEXT("result"),R);}
 if(Nodes.Contains(TEXT("entry")))for(auto* Pin:Nodes[TEXT("entry")]->Pins)if(Pin->PinType.PinCategory==UEdGraphSchema_K2::PC_Exec)Pin->BreakAllPinLinks();
 const TArray<TSharedPtr<FJsonValue>>* Variables=nullptr;if(Spec->TryGetArrayField(TEXT("variables"),Variables))for(auto V:*Variables){auto O=V->AsObject();FEdGraphPinType Type;Type.PinCategory=UEdGraphSchema_K2::PC_Real;Type.PinSubCategory=UEdGraphSchema_K2::PC_Float;FString Kind;O->TryGetStringField(TEXT("type"),Kind);if(Kind==TEXT("bool")){Type.PinCategory=UEdGraphSchema_K2::PC_Boolean;Type.PinSubCategory=NAME_None;}FName Var(*O->GetStringField(TEXT("name")));bool Exists=false;for(auto Desc:BP->NewVariables)if(Desc.VarName==Var)Exists=true;if(!Exists)FBlueprintEditorUtils::AddMemberVariable(BP,Var,Type,O->GetStringField(TEXT("default")));}
 int Index=0;bool OK=true;
 for(auto V:Spec->GetArrayField(TEXT("nodes"))){auto O=V->AsObject();FString ID=O->GetStringField(TEXT("id")),Kind=O->GetStringField(TEXT("kind"));UK2Node* N=nullptr;
  if(Kind==TEXT("get")||Kind==TEXT("set")){FName Var(*O->GetStringField(TEXT("var")));if(Kind==TEXT("get")){auto* X=NewObject<UK2Node_VariableGet>(G);X->VariableReference.SetSelfMember(Var);N=X;}else{auto* X=NewObject<UK2Node_VariableSet>(G);X->VariableReference.SetSelfMember(Var);N=X;}}
  else if(Kind==TEXT("getfield")||Kind==TEXT("setfield")){UClass* Owner=LoadObject<UClass>(nullptr,*O->GetStringField(TEXT("owner")));if(!Owner)return false;FName Var(*O->GetStringField(TEXT("var")));if(Kind==TEXT("getfield")){auto* X=NewObject<UK2Node_VariableGet>(G);X->VariableReference.SetExternalMember(Var,Owner);N=X;}else{auto* X=NewObject<UK2Node_VariableSet>(G);X->VariableReference.SetExternalMember(Var,Owner);N=X;}}
  else if(Kind==TEXT("cast")){auto* X=NewObject<UK2Node_DynamicCast>(G);X->TargetType=LoadObject<UClass>(nullptr,*O->GetStringField(TEXT("type")));if(!X->TargetType)return false;X->SetPurity(true);N=X;}
  else if(Kind==TEXT("foreach")){auto* Macro=LoadObject<UBlueprint>(nullptr,TEXT("/Engine/EditorBlueprintResources/StandardMacros.StandardMacros"));UEdGraph* Loop=nullptr;if(Macro)for(auto Graph:Macro->MacroGraphs)if(Graph->GetName()==TEXT("ForEachLoop"))Loop=Graph;if(!Loop)return false;auto* X=NewObject<UK2Node_MacroInstance>(G);X->SetMacroGraph(Loop);N=X;}
  else if(Kind==TEXT("branch"))N=NewObject<UK2Node_IfThenElse>(G);
  else if(Kind==TEXT("break")){auto* X=NewObject<UK2Node_BreakStruct>(G);X->StructType=FindObject<UScriptStruct>(nullptr,*O->GetStringField(TEXT("type")));N=X;}
  else if(Kind==TEXT("make")){auto* X=NewObject<UK2Node_MakeStruct>(G);X->StructType=FindObject<UScriptStruct>(nullptr,*O->GetStringField(TEXT("type")));N=X;}
  else if(Kind==TEXT("return")){auto* X=NewObject<UK2Node_FunctionResult>(G);X->FunctionReference=CastChecked<UK2Node_FunctionEntry>(Nodes[TEXT("entry")])->FunctionReference;N=X;}
  else if(Kind==TEXT("call")){FString Owner;O->TryGetStringField(TEXT("owner"),Owner);UClass* Class=Owner.IsEmpty()?BP->ParentClass.Get():LoadObject<UClass>(nullptr,*Owner);UFunction* Fn=Class?Class->FindFunctionByName(*O->GetStringField(TEXT("fn"))):nullptr;if(!Fn){UE_LOG(LogTemp,Error,TEXT("BP missing function %s"),*ID);return false;}UK2Node_CallFunction* X=Fn->HasMetaData(TEXT("ArrayParm"))?NewObject<UK2Node_CallArrayFunction>(G):NewObject<UK2Node_CallFunction>(G);X->SetFromFunction(Fn);N=X;}
  if(!N)return false;G->AddNode(N,false,false);N->CreateNewGuid();N->PostPlacedNewNode();N->AllocateDefaultPins();N->NodePosX=(Index%5)*300;N->NodePosY=(Index/5)*230;Index++;Nodes.Add(ID,N);
  const TSharedPtr<FJsonObject>* Defaults=nullptr;if(O->TryGetObjectField(TEXT("defaults"),Defaults))for(auto Pair:(*Defaults)->Values){auto* Pin=N->FindPin(*Pair.Key);if(!Pin){OK=false;continue;}if(Pin->PinType.PinCategory==UEdGraphSchema_K2::PC_Class)Pin->DefaultObject=LoadObject<UClass>(nullptr,*Pair.Value->AsString());else G->GetSchema()->TrySetDefaultValue(*Pin,Pair.Value->AsString());}
 }
 for(auto V:Spec->GetArrayField(TEXT("links"))){auto A=V->AsArray();FString S=A[0]->AsString(),SP=A[1]->AsString(),D=A[2]->AsString(),DP=A[3]->AsString();auto* SN=Nodes.FindRef(S);auto* DN=Nodes.FindRef(D);auto* Out=SN?SN->FindPin(*SP,EGPD_Output):nullptr;auto* In=DN?DN->FindPin(*DP,EGPD_Input):nullptr;
  if(!Out||!In||!G->GetSchema()->TryCreateConnection(Out,In)){UE_LOG(LogTemp,Error,TEXT("BP link failed %s.%s -> %s.%s"),*S,*SP,*D,*DP);OK=false;}
 }
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



