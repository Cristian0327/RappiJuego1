#include "DeliveryEditorLibrary.h"
#include "../BogotaVoxel/DeliverySystem.h"
#include "WidgetBlueprint.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Widget.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Button.h"
#include "Components/ButtonSlot.h"
#include "Components/TextBlock.h"
#include "Engine/Font.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
void PopulatePhoneLauncher(UWidgetBlueprint* BP);
bool BindPhoneLauncher(UWidgetBlueprint* BP);

bool UDeliveryEditorLibrary::StylePhoneTypography(UBlueprint* Blueprint,UFont* Font){
 auto* BP=Cast<UWidgetBlueprint>(Blueprint);if(!BP||!BP->WidgetTree||!Font)return false;
 BP->WidgetTree->ForEachWidget([Font](UWidget* Widget){if(auto* Text=Cast<UTextBlock>(Widget)){
  auto Style=Text->GetFont();Style.FontObject=Font;Style.TypefaceFontName=NAME_None;Text->SetFont(Style);
  if(Text->GetName().StartsWith(TEXT("Home"))){Text->SetShadowOffset(FVector2D(1,2));Text->SetShadowColorAndOpacity(FLinearColor(0.01f,.025f,.035f,1));}
 }});
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return BP->Status!=BS_Error;
}

bool UDeliveryEditorLibrary::BuildPhoneAppLayouts(UBlueprint* Blueprint){
 auto* BP=Cast<UWidgetBlueprint>(Blueprint);if(!BP||!BP->WidgetTree)return false;
 auto* Screen=Cast<UCanvasPanel>(BP->WidgetTree->FindWidget(TEXT("Screen")));if(!Screen)return false;
 auto* Template=NewObject<UDeliveryPhoneWidget>(GetTransientPackage());Template->AuthoringPhoneTemplate=true;Template->Initialize();Template->TakeWidget();Template->AuthorAppLayouts();
 auto* Source=CastChecked<UCanvasPanel>(Template->WidgetTree->FindWidget(TEXT("Screen")));
 for(auto* W:Source->GetAllChildren()){
  if(!W->GetName().StartsWith(TEXT("App"))||BP->WidgetTree->FindWidget(W->GetFName()))continue;
  auto* Copy=DuplicateObject<UWidget>(W,BP->WidgetTree,W->GetFName());
  Copy->Slot=nullptr;
  if(auto* SourceButton=Cast<UButton>(W))if(auto* Content=SourceButton->GetContent()){
   auto* Original=CastChecked<UButtonSlot>(Content->Slot);const FMargin Padding=Original->GetPadding();const auto Horizontal=Original->GetHorizontalAlignment();const auto Vertical=Original->GetVerticalAlignment();
   auto* Button=CastChecked<UButton>(Copy);Button->ClearChildren();
   auto* Label=DuplicateObject<UWidget>(Content,BP->WidgetTree,FName(*(W->GetName()+TEXT("Label"))));Label->Slot=nullptr;Label->ClearFlags(RF_Transient|RF_DuplicateTransient);Label->bIsVariable=false;
   auto* Slot=CastChecked<UButtonSlot>(Button->AddChild(Label));Slot->SetPadding(Padding);Slot->SetHorizontalAlignment(Horizontal);Slot->SetVerticalAlignment(Vertical);
  }
  auto* From=CastChecked<UCanvasPanelSlot>(W->Slot);auto* To=Screen->AddChildToCanvas(Copy);To->SetLayout(From->GetLayout());To->SetZOrder(From->GetZOrder());Copy->SetVisibility(ESlateVisibility::Collapsed);
  TArray<UObject*> Objects;GetObjectsWithOuter(Copy,Objects,true);Objects.Add(Copy);
  for(auto* Object:Objects){Object->ClearFlags(RF_Transient|RF_DuplicateTransient);if(auto* Widget=Cast<UWidget>(Object))Widget->bIsVariable=false;if(auto* Button=Cast<UButton>(Object)){Button->OnClicked.Clear();Button->OnPressed.Clear();Button->OnReleased.Clear();}if(auto* Choice=Cast<UDeliveryChoiceButton>(Object))Choice->Phone=nullptr;}
 }
 BP->WidgetTree->ForEachWidget([BP](UWidget* Widget){if(!BP->WidgetVariableNameToGuidMap.Contains(Widget->GetFName()))BP->OnVariableAdded(Widget->GetFName());});
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return BP->Status!=BS_Error;
}

bool UDeliveryEditorLibrary::BuildPhoneDesigner(UBlueprint* Blueprint)
{
 auto* PhoneBP=Cast<UWidgetBlueprint>(Blueprint);
 if(!PhoneBP||!PhoneBP->ParentClass->IsChildOf(UDeliveryPhoneWidget::StaticClass()))return false;
 // Preserve any existing designer work on subsequent runs.
 if(PhoneBP->WidgetTree&&PhoneBP->WidgetTree->FindWidget(TEXT("DesignerHome")))return true;
 auto* Template=NewObject<UDeliveryPhoneWidget>(GetTransientPackage());
 Template->AuthoringPhoneTemplate=true;
 Template->Initialize();
 Template->TakeWidget();
 if(!Template->WidgetTree||!Template->WidgetTree->RootWidget)return false;
 if(PhoneBP->WidgetTree)PhoneBP->WidgetTree->Rename(nullptr,GetTransientPackage(),REN_DontCreateRedirectors|REN_NonTransactional);
 PhoneBP->WidgetTree=DuplicateObject<UWidgetTree>(Template->WidgetTree,PhoneBP,TEXT("WidgetTree"));
 PhoneBP->WidgetTree->ClearFlags(RF_Transient|RF_DuplicateTransient);
 PhoneBP->WidgetTree->SetFlags(RF_DefaultSubObject);
 TArray<UObject*> Children;GetObjectsWithOuter(PhoneBP->WidgetTree,Children,true);
 for(auto* Child:Children)Child->ClearFlags(RF_Transient|RF_DuplicateTransient);
 PhoneBP->WidgetTree->SetFlags(RF_Transactional);
 PhoneBP->WidgetTree->ForEachWidget([](UWidget* Widget){Widget->bIsVariable=false;});
 PopulatePhoneLauncher(PhoneBP);
 PhoneBP->WidgetTree->ForEachWidget([PhoneBP](UWidget* Widget){if(!PhoneBP->WidgetVariableNameToGuidMap.Contains(Widget->GetFName()))PhoneBP->OnVariableAdded(Widget->GetFName());});
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(PhoneBP);
 FKismetEditorUtilities::CompileBlueprint(PhoneBP);
 if(PhoneBP->Status==BS_Error||!BindPhoneLauncher(PhoneBP))return false;
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(PhoneBP);
 FKismetEditorUtilities::CompileBlueprint(PhoneBP);
 PhoneBP->MarkPackageDirty();
 return PhoneBP->Status!=BS_Error;
}
