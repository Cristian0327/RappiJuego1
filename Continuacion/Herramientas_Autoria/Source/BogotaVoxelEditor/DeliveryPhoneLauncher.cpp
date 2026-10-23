#include "../BogotaVoxel/DeliverySystem.h"
#include "WidgetBlueprint.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Button.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Components/Border.h"
#include "Engine/Texture2D.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "K2Node_ComponentBoundEvent.h"
#include "K2Node_CallFunction.h"
#include "EdGraphSchema_K2.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "DeliveryEditorLibrary.h"

bool UDeliveryEditorLibrary::RemoveDeliveriesApp(UBlueprint* Blueprint){
 auto* BP=Cast<UWidgetBlueprint>(Blueprint);if(!BP||!BP->WidgetTree)return false;
 if(auto* Gameplay=LoadObject<UBlueprint>(nullptr,TEXT("/Game/Delivery/Core/BPC_DeliveryGameplay.BPC_DeliveryGameplay"))){for(auto Graph:Gameplay->FunctionGraphs)for(auto Node:Graph->Nodes)for(auto* Pin:Node->Pins)if(Pin->DefaultValue.Contains(TEXT("Mis entregas")))Pin->DefaultValue=Pin->DefaultValue.Replace(TEXT("Mis entregas"),TEXT("Pedidos aceptados"));FKismetEditorUtilities::CompileBlueprint(Gameplay);Gameplay->MarkPackageDirty();}
 for(auto Graph:BP->UbergraphPages){auto Nodes=Graph->Nodes;for(auto Node:Nodes)if(auto* Event=Cast<UK2Node_ComponentBoundEvent>(Node))if(Event->ComponentPropertyName==TEXT("HomeDeliveries")){Event->BreakAllNodeLinks();Graph->RemoveNode(Event);}}
 for(const TCHAR* Name:{TEXT("HomeDeliveries"),TEXT("HomeDeliveriesIcon"),TEXT("HomeDeliveriesLabel")})if(auto* W=BP->WidgetTree->FindWidget(Name)){BP->WidgetTree->RemoveWidget(W);W->Rename(nullptr,GetTransientPackage(),REN_DontCreateRedirectors|REN_NonTransactional);}
 for(const TCHAR* Name:{TEXT("HomeDeliveries"),TEXT("HomeDeliveriesIcon"),TEXT("HomeDeliveriesLabel")})BP->OnVariableRemoved(FName(Name));
 for(int32 I=0;I<2;I++){
  FString Name=I==0?TEXT("HomeCargo"):TEXT("HomeVehicles");const FVector2D P(76+I*116,370);
  for(auto Suffix:{FString(),FString(TEXT("Icon")),FString(TEXT("Label"))})if(auto* W=BP->WidgetTree->FindWidget(FName(Name+Suffix)))if(auto* Slot=Cast<UCanvasPanelSlot>(W->Slot))Slot->SetPosition(P+(Suffix==TEXT("Icon")?FVector2D(24,12):Suffix==TEXT("Label")?FVector2D(0,92):FVector2D::ZeroVector));
 }
 if(auto* T=Cast<UTextBlock>(BP->WidgetTree->FindWidget(TEXT("PhoneHints"))))T->SetText(FText::FromString(TEXT("E / A / X: aceptar · Cruceta: elegir · TAB: cerrar\n1 Mapa · 2 Pedidos · 3 Taller · 4 Maletas · 5 Garaje")));
 FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);FKismetEditorUtilities::CompileBlueprint(BP);BP->MarkPackageDirty();return BP->Status!=BS_Error;
}

void PopulatePhoneLauncher(UWidgetBlueprint* BP)
{
 auto* Tree=BP->WidgetTree.Get();
 if(Tree->FindWidget(TEXT("DesignerHome")))return;
 auto* Screen=CastChecked<UCanvasPanel>(Tree->FindWidget(TEXT("Screen")));
 auto* Home=Tree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(),TEXT("DesignerHome"));
 auto* HS=Screen->AddChildToCanvas(Home);HS->SetPosition(FVector2D(0,35));HS->SetSize(FVector2D(372,506));Home->SetClipping(EWidgetClipping::ClipToBounds);
 auto Place=[&](UWidget* W,FVector2D P,FVector2D S){auto* Slot=Home->AddChildToCanvas(W);Slot->SetPosition(P);Slot->SetSize(S);};
 auto Art=[&](FName Name,const TCHAR* Asset,FVector2D P,FVector2D S){auto* W=Tree->ConstructWidget<UImage>(UImage::StaticClass(),Name);W->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr,*(FString(TEXT("/Game/Delivery/Art/"))+Asset)));W->SetVisibility(ESlateVisibility::HitTestInvisible);Place(W,P,S);return W;};
 auto Text=[&](FName Name,const TCHAR* Value,FVector2D P,FVector2D S,int32 Size,FLinearColor Color){auto* W=Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(),Name);W->SetText(FText::FromString(Value));auto Font=W->GetFont();Font.Size=Size;Font.TypefaceFontName=TEXT("Bold");W->SetFont(Font);W->SetColorAndOpacity(Color);W->SetVisibility(ESlateVisibility::HitTestInvisible);W->SetClipping(EWidgetClipping::ClipToBounds);Place(W,P,S);return W;};
 Art(TEXT("HomeWallpaper"),TEXT("T_BogotaWallpaper"),FVector2D(0,0),FVector2D(372,506));
 Art(TEXT("HomeBrand"),TEXT("T_RutaBog"),FVector2D(18,18),FVector2D(184,92));
 Text(TEXT("HomeTagline"),TEXT("TU BARRIO. TU RUTA."),FVector2D(20,120),FVector2D(332,24),12,FLinearColor(.9f,.93f,.88f));
 auto* StatusPanel=Tree->ConstructWidget<UBorder>(UBorder::StaticClass(),TEXT("HomeStatusPanel"));StatusPanel->SetBrushColor(FLinearColor(.025f,.065f,.085f,.94f));StatusPanel->SetVisibility(ESlateVisibility::HitTestInvisible);Place(StatusPanel,FVector2D(16,160),FVector2D(340,60));
 Text(TEXT("HomeStatus"),TEXT("Elige tu próxima ruta"),FVector2D(28,170),FVector2D(316,40),12,FLinearColor(.87f,.94f,.93f));
 const TCHAR* Names[]={TEXT("HomeMap"),TEXT("HomeOrders"),TEXT("HomeWorkshop"),TEXT("HomeCargo"),TEXT("HomeVehicles")};
 const TCHAR* Labels[]={TEXT("Mapa"),TEXT("Pedidos"),TEXT("Taller"),TEXT("Maletas"),TEXT("Garaje")};
 const TCHAR* Icons[]={TEXT("T_AppMap"),TEXT("T_AppOrders"),TEXT("T_AppWorkshop"),TEXT("T_CargoBackpack"),TEXT("T_SM_BikeStage0")};
 const FLinearColor Colors[]={FLinearColor(.025f,.25f,.24f),FLinearColor(.36f,.14f,.045f),FLinearColor(.12f,.15f,.28f),FLinearColor(.25f,.11f,.22f),FLinearColor(.09f,.21f,.29f)};
 for(int32 I=0;I<5;I++){
  const FVector2D P(I<3?18+I*116:76+(I-3)*116,244+(I/3)*126);
  auto* Button=Tree->ConstructWidget<UButton>(UButton::StaticClass(),FName(Names[I]));Button->bIsVariable=true;
  auto Style=Button->GetStyle();for(auto* B:{&Style.Normal,&Style.Hovered,&Style.Pressed}){B->DrawAs=ESlateBrushDrawType::Box;B->Margin=FMargin(0);B->TintColor=Colors[I];}Style.Hovered.TintColor=Colors[I]*1.4f;Style.Pressed.TintColor=FLinearColor(.95f,.35f,.06f);Button->SetStyle(Style);Place(Button,P,FVector2D(104,88));
  Art(FName(FString(Names[I])+TEXT("Icon")),Icons[I],P+FVector2D(24,12),FVector2D(56,60));
  auto* Label=Text(FName(FString(Names[I])+TEXT("Label")),Labels[I],P+FVector2D(0,92),FVector2D(104,22),12,FLinearColor(.92f,.93f,.88f));Label->SetJustification(ETextJustify::Center);
 }
}

bool BindPhoneLauncher(UWidgetBlueprint* BP)
{
 auto* G=FBlueprintEditorUtils::CreateNewGraph(BP,TEXT("LauncherApps"),UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());FBlueprintEditorUtils::AddUbergraphPage(BP,G);
 const TCHAR* Names[]={TEXT("HomeMap"),TEXT("HomeOrders"),TEXT("HomeWorkshop"),TEXT("HomeCargo"),TEXT("HomeVehicles")};
 const TCHAR* Functions[]={TEXT("OpenMap"),TEXT("OpenOrders"),TEXT("OpenShop"),TEXT("OpenCargo"),TEXT("OpenCatalog")};
 const auto* Delegate=FindFProperty<FMulticastDelegateProperty>(UButton::StaticClass(),TEXT("OnClicked"));
 for(int32 I=0;I<5;I++){
  auto* Property=FindFProperty<FObjectProperty>(BP->SkeletonGeneratedClass,FName(Names[I]));if(!Property||!Delegate)return false;
  auto* Event=NewObject<UK2Node_ComponentBoundEvent>(G);G->AddNode(Event,false,false);Event->CreateNewGuid();Event->InitializeComponentBoundEventParams(Property,Delegate);Event->AllocateDefaultPins();Event->NodePosY=I*200;
  auto* Call=NewObject<UK2Node_CallFunction>(G);G->AddNode(Call,false,false);Call->CreateNewGuid();Call->SetFromFunction(UDeliveryPhoneWidget::StaticClass()->FindFunctionByName(Functions[I]));Call->AllocateDefaultPins();Call->NodePosX=440;Call->NodePosY=I*200;
  if(!G->GetSchema()->TryCreateConnection(Event->FindPin(UEdGraphSchema_K2::PN_Then),Call->FindPin(UEdGraphSchema_K2::PN_Execute)))return false;
 }
 return true;
}
