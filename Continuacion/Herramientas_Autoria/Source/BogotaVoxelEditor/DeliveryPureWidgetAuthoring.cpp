#include "DeliveryEditorLibrary.h"
#include "WidgetBlueprint.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Widget.h"
#include "Components/PanelWidget.h"
#include "Components/PanelSlot.h"
#include "Components/CanvasPanel.h"
#include "Components/Button.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "K2Node_ComponentBoundEvent.h"
#include "K2Node_CallFunction.h"
#include "EdGraphSchema_K2.h"
#include "UObject/UnrealType.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
// Editor-only authoring. No source-project widget class is retained by the new tree.
static void CopyDesignerValues(UObject* Source,UObject* Destination){
 const TCHAR* Names[]={TEXT("WidgetStyle"),TEXT("Brush"),TEXT("ColorAndOpacity"),TEXT("BrushColor"),TEXT("BackgroundColor"),TEXT("ContentColorAndOpacity"),TEXT("Padding"),TEXT("HorizontalAlignment"),TEXT("VerticalAlignment"),TEXT("ShadowOffset"),TEXT("ShadowColorAndOpacity"),TEXT("Justification"),TEXT("AutoWrapText"),TEXT("bAutoWrapText"),TEXT("WrapTextAt"),TEXT("Font"),TEXT("Text"),TEXT("RenderOpacity"),TEXT("Visibility"),TEXT("RenderTransform"),TEXT("RenderTransformPivot"),TEXT("Clipping"),TEXT("bIsEnabled"),TEXT("bShowEffectWhenDisabled"),TEXT("FillColorAndOpacity"),TEXT("Percent"),TEXT("BarFillType"),TEXT("bIsMarquee"),TEXT("bIsFocusable"),TEXT("LayoutData"),TEXT("ZOrder"),TEXT("bAutoSize"),TEXT("MinDesiredWidth"),TEXT("TextOverflowPolicy")};
 for(const TCHAR* Name:Names){auto* From=FindFProperty<FProperty>(Source->GetClass(),Name);auto* To=FindFProperty<FProperty>(Destination->GetClass(),Name);if(From&&To&&From->SameType(To))To->CopyCompleteValue(To->ContainerPtrToValuePtr<void>(Destination),From->ContainerPtrToValuePtr<void>(Source));}
}
bool UDeliveryEditorLibrary::CloneEngineWidgetDesigner(UBlueprint* SourceBlueprint,UBlueprint* DestinationBlueprint){
 auto* Source=Cast<UWidgetBlueprint>(SourceBlueprint);auto* Destination=Cast<UWidgetBlueprint>(DestinationBlueprint);
 if(!Source||!Destination||Source==Destination||!Source->WidgetTree||!Source->WidgetTree->RootWidget||Destination->ParentClass!=UUserWidget::StaticClass())return false;
 Destination->Modify();if(Destination->WidgetTree)Destination->WidgetTree->Rename(nullptr,GetTransientPackage(),REN_DontCreateRedirectors|REN_NonTransactional);
 Destination->WidgetTree=NewObject<UWidgetTree>(Destination,TEXT("WidgetTree"),RF_Transactional|RF_DefaultSubObject);Destination->WidgetVariableNameToGuidMap.Reset();bool Valid=true;
 TFunction<UWidget*(UWidget*)> Clone=[&](UWidget* Old)->UWidget*{UClass* Class=Old->GetClass();const FString Type=Class->GetPathName();if(Type==TEXT("/Script/BogotaVoxel.DeliveryChoiceButton"))Class=UButton::StaticClass();else if(Type==TEXT("/Script/BogotaVoxel.DeliveryMapWidget"))Class=UCanvasPanel::StaticClass();else if(Type.StartsWith(TEXT("/Script/BogotaVoxel"))){Valid=false;return nullptr;}
  auto* New=Destination->WidgetTree->ConstructWidget<UWidget>(Class,Old->GetFName());CopyDesignerValues(Old,New);New->bIsVariable=true;Destination->OnVariableAdded(New->GetFName());
  if(auto* Panel=Cast<UPanelWidget>(Old)){auto* NewPanel=Cast<UPanelWidget>(New);if(!NewPanel){Valid=false;return New;}for(auto* Child:Panel->GetAllChildren()){auto* NewChild=Clone(Child);if(!NewChild)continue;auto* Slot=NewPanel->AddChild(NewChild);if(Child->Slot&&Slot)CopyDesignerValues(Child->Slot,Slot);}}
  return New;
 };
 Destination->WidgetTree->RootWidget=Clone(Source->WidgetTree->RootWidget);if(!Valid)return false;
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Destination);FKismetEditorUtilities::CompileBlueprint(Destination);Destination->MarkPackageDirty();return Destination->Status!=BS_Error;
}
bool UDeliveryEditorLibrary::BindWidgetDelegateGraph(UBlueprint* Blueprint,const FString& Specification){
 auto* BP=Cast<UWidgetBlueprint>(Blueprint);if(!BP||!BP->WidgetTree)return false;TArray<TSharedPtr<FJsonValue>> Items;if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Specification),Items))return false;UEdGraph* Graph=nullptr;
 for(auto Existing:BP->UbergraphPages)if(Existing&&Existing->GetFName()==TEXT("PhoneActions")){Graph=Existing;break;}
 if(!Graph){Graph=FBlueprintEditorUtils::CreateNewGraph(BP,TEXT("PhoneActions"),UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());FBlueprintEditorUtils::AddUbergraphPage(BP,Graph);}else{TArray<UEdGraphNode*> Old;for(auto Node:Graph->Nodes)Old.Add(Node);for(auto Node:Old)Graph->RemoveNode(Node);}
 const auto* Schema=GetDefault<UEdGraphSchema_K2>();int32 Row=0;
 for(auto Value:Items){const auto O=Value->AsObject();if(!O.IsValid())return false;const FName Widget(*O->GetStringField(TEXT("widget")));const FName DelegateName(*O->GetStringField(TEXT("delegate")));const FName FunctionName(*O->GetStringField(TEXT("function")));auto* Property=FindFProperty<FObjectProperty>(BP->SkeletonGeneratedClass,Widget);if(!Property)return false;auto* Delegate=FindFProperty<FMulticastDelegateProperty>(Property->PropertyClass,DelegateName);auto* Function=BP->GeneratedClass->FindFunctionByName(FunctionName);if(!Delegate||!Function)return false;
  auto* Event=NewObject<UK2Node_ComponentBoundEvent>(Graph);Graph->AddNode(Event,false,false);Event->CreateNewGuid();Event->InitializeComponentBoundEventParams(Property,Delegate);Event->AllocateDefaultPins();Event->NodePosY=Row*200;
  auto* Call=NewObject<UK2Node_CallFunction>(Graph);Graph->AddNode(Call,false,false);Call->CreateNewGuid();Call->SetFromFunction(Function);Call->AllocateDefaultPins();Call->NodePosX=440;Call->NodePosY=Row++*200;
  const TSharedPtr<FJsonObject>* Defaults=nullptr;if(O->TryGetObjectField(TEXT("defaults"),Defaults))for(const auto& Pair:(*Defaults)->Values)if(auto* Pin=Call->FindPin(FName(*FString(*Pair.Key))))Schema->TrySetDefaultValue(*Pin,Pair.Value->AsString());
  if(!Schema->TryCreateConnection(Event->FindPin(UEdGraphSchema_K2::PN_Then),Call->FindPin(UEdGraphSchema_K2::PN_Execute)))return false;
 }
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return BP->Status!=BS_Error;
}
