#include "DeliverySystem.h"
#include "BogotaGame.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/ProgressBar.h"
#include "Components/Image.h"
#include "Blueprint/WidgetTree.h"
#include "Blueprint/WidgetLayoutLibrary.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Framework/Application/SlateApplication.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Json.h"
#include "UnrealClient.h"
#include "Engine/World.h"

void UDeliveryComponent::UpdateUsabilityValidation(float Dt){
 ValidationTime+=Dt;auto* P=Cast<ABogotaPlayer>(GetOwner());auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget);if(!P||!P->City||!UI)return;
 static TArray<TSharedPtr<FJsonValue>> Checks;static int32 StableWidgets=0;static FGuid HeldID;
 auto Check=[&](bool OK,const TCHAR* ID){auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("id"),ID);R->SetBoolField(TEXT("passed"),OK);Checks.Add(MakeShared<FJsonValueObject>(R));if(!OK)ValidationErrors.Add(ID);UE_LOG(LogTemp,Display,TEXT("USABILITY_CHECK %s %s"),ID,OK?TEXT("PASS"):TEXT("FAIL"));};
 auto Key=[&](FKey K,bool Repeat=false){return UI->NativeOnPreviewKeyDown(UI->GetCachedGeometry(),FKeyEvent(K,FModifierKeysState(),0,Repeat,0,0));};
 auto Release=[&](FKey K){return UI->NativeOnKeyUp(UI->GetCachedGeometry(),FKeyEvent(K,FModifierKeysState(),0,false,0,0));};
 auto Capture=[&](const TCHAR* Name){FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/")+Name,true,false);};
 auto Next=[&](){ValidationStage++;ValidationTime=0;};
 auto Button=[&](const TCHAR* Label)->UButton*{for(auto* W:UI->AppControls)if(auto* B=Cast<UButton>(W))if(auto* T=Cast<UTextBlock>(B->GetContent()))if(T->GetText().ToString()==Label)return B;return nullptr;};
 static int32 ShotStage=-1;
 if(ValidationTime>.5f&&ShotStage!=ValidationStage){if(ValidationStage==1)Capture(TEXT("QA_Home.png"));if(ValidationStage==2)Capture(TEXT("QA_Map.png"));if(ValidationStage==7)Capture(TEXT("QA_Workshop_Bike.png"));if(ValidationStage==8)Capture(TEXT("QA_Garage_Locked.png"));if(ValidationStage==13)Capture(TEXT("QA_HUD.png"));ShotStage=ValidationStage;}
 if(FParse::Param(FCommandLine::Get(),TEXT("UsabilityResumeTest"))){
  if(ValidationTime<3||ValidationStage>0)return;
  auto* Saved=Cast<UDeliverySave>(UGameplayStatics::LoadGameFromSlot(ProfileSlot(),0));
  Check(!bValidation&&Saved,TEXT("normal_startup_reads_qa_profile"));
  Check(Saved&&Balance==Saved->Balance,TEXT("restart_restores_wallet"));
  Check(Saved&&Purchased.Num()==Saved->Purchased.Num()&&!Saved->Purchased.ContainsByPredicate([&](FName ID){return !Owns(ID);}),TEXT("restart_restores_purchased_upgrades"));
  Check(Saved&&Vehicle==Saved->Vehicle&&BikeModel==Saved->BikeModel&&MotoModel==Saved->MotoModel,TEXT("restart_restores_equipped_vehicle"));
  Check(CargoCapacity(true)==5&&Owns(TEXT("CargoPanniers")),TEXT("restart_restores_cargo_capacity"));
  Check(ActiveOrders.IsEmpty()&&!SelectedIncoming()&&!bHolding,TEXT("restart_does_not_invent_active_orders"));
  Capture(TEXT("QA_Profile_Restart.png"));
  auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("status"),ValidationErrors.IsEmpty()?TEXT("PASS"):TEXT("FAIL"));R->SetArrayField(TEXT("checks"),Checks);R->SetNumberField(TEXT("total"),Checks.Num());TArray<TSharedPtr<FJsonValue>> Errors;for(const auto& E:ValidationErrors)Errors.Add(MakeShared<FJsonValueString>(E));R->SetArrayField(TEXT("failures"),Errors);R->SetNumberField(TEXT("viewport_width"),UWidgetLayoutLibrary::GetViewportSize(this).X);R->SetNumberField(TEXT("viewport_height"),UWidgetLayoutLibrary::GetViewportSize(this).Y);
  FString JSON;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&JSON));FFileHelper::SaveStringToFile(JSON,*(FPaths::ProjectSavedDir()/TEXT("usability_validation.json")));UE_LOG(LogTemp,Display,TEXT("USABILITY_RESUME_RESULT %s"),*JSON);ValidationStage++;
  GetWorld()->GetTimerManager().SetTimerForNextTick([](){FPlatformMisc::RequestExit(false);});return;
 }
 if(ValidationStage==0&&ValidationTime>3){
  Check(Balance==0&&Purchased.IsEmpty(),TEXT("fresh_profile_isolated"));Check(!PhoneOpen&&CargoCapacity(false)==1,TEXT("new_player_starts_with_one_slot"));
  OfferLifetime=120;EnterIdle();Offers.Empty();GenerateOffer();Check(Offers.Num()==6&&!SelectedIncoming(),TEXT("market_requires_explicit_selection"));
  TogglePhone();UI->OpenHome();Check(PhoneOpen&&UI->Page==0,TEXT("phone_opens_home"));Next();
 }else if(ValidationStage==1&&ValidationTime>1){
  P->MoveForward(1);P->MoveRight(1);P->StartSprint();P->JumpOrBrake();Check(P->ForwardInput==0&&P->SideInput==0&&!P->Sprint&&!P->bPressedJump,TEXT("phone_blocks_walk_boost_and_jump"));P->StopJump();
  Key(EKeys::One);Check(UI->Page==1,TEXT("keyboard_shortcut_opens_map"));Next();
 }else if(ValidationStage==2&&ValidationTime>1){
  auto* MapSlot=UI->MainMap?Cast<UCanvasPanelSlot>(UI->MainMap->Slot):nullptr;auto* TextSlot=Cast<UCanvasPanelSlot>(UI->Details->Slot);
  Check(MapSlot&&TextSlot&&MapSlot->GetPosition().Y>=TextSlot->GetPosition().Y+TextSlot->GetSize().Y+8,TEXT("map_does_not_cover_its_instructions"));
  if(UI->MainMap){auto G=UI->MainMap->GetCachedGeometry();auto Point=G.LocalToAbsolute(G.GetLocalSize()*FVector2D(.65,.35));FPointerEvent Click(0,Point,Point,TSet<FKey>{EKeys::LeftMouseButton},EKeys::LeftMouseButton,0,FModifierKeysState());UI->MainMap->NativeOnMouseButtonDown(G,Click);}
  Check(HasWaypoint&&FMath::Abs(Waypoint.X)<=42000&&FMath::Abs(Waypoint.Y)<=26500,TEXT("map_click_sets_bounded_waypoint"));
  if(auto* B=Button(TEXT("QUITAR MI MARCA")))B->OnClicked.Broadcast();Check(!HasWaypoint,TEXT("map_clear_button_works"));
  Key(EKeys::Two);SelectedOffer.Invalidate();Next();
 }else if(ValidationStage==3&&ValidationTime>1){
  Check(Key(EKeys::Down).IsEventHandled()&&SelectedIncoming()&&SelectedIncoming()->ID==Offers[0].ID,TEXT("keyboard_down_selects_first_offer"));
  UI->SelectEntry(3);Check(Key(EKeys::Up).IsEventHandled()&&SelectedIncoming()&&SelectedIncoming()->ID==Offers[2].ID,TEXT("keyboard_up_selects_previous_offer"));
  Offers[0].PickupName=FText::FromString(TEXT("Mercado Don Luis - La Candelaria"));Offers[0].DropoffName=FText::FromString(TEXT("Casa de Marta - Centro / La Candelaria"));UI->SelectEntry(0);UI->RefreshText();Check(SelectedIncoming()&&UI->Details->GetText().ToString().Contains(SelectedIncoming()->PickupName.ToString())&&UI->Details->GetText().ToString().Contains(SelectedIncoming()->DropoffName.ToString().Replace(TEXT("Casa de "),TEXT(""))),TEXT("selected_offer_shows_full_origin_and_destination"));
  auto Contrast=[](FLinearColor A,FLinearColor B){auto Lum=[](FLinearColor C){return .2126*C.R+.7152*C.G+.0722*C.B;};return (FMath::Max(Lum(A),Lum(B))+.05)/(FMath::Min(Lum(A),Lum(B))+.05);};
  bool NormalReadable=true,HoverReadable=true;for(auto* B:UI->Choices)if(auto* T=Cast<UTextBlock>(B->GetContent())){auto C=T->GetColorAndOpacity().GetSpecifiedColor();NormalReadable&=Contrast(C,B->GetStyle().Normal.TintColor.GetSpecifiedColor())>=4.5;HoverReadable&=Contrast(C,B->GetStyle().Hovered.TintColor.GetSpecifiedColor())>=4.5;}
  Check(NormalReadable,TEXT("offer_text_contrast_normal_at_least_4_5"));Check(HoverReadable,TEXT("offer_text_contrast_hover_at_least_4_5"));
  UI->AcceptPressed();Check(bHolding,TEXT("accept_button_begins_hold"));Next();
 }else if(ValidationStage==4&&ValidationTime>.75){
  auto Bar=UI->HoldBar->GetCachedGeometry(),Accept=UI->AcceptButton->GetCachedGeometry();auto B=Bar.GetAbsolutePosition(),A=Accept.GetAbsolutePosition(),S=Accept.GetAbsoluteSize();
  Check(HoldProgress>.15f&&B.X>=A.X-2&&B.X<=A.X+S.X&&B.Y>=A.Y-2&&B.Y<=A.Y+S.Y+12,TEXT("hold_progress_is_at_accept_button"));Check(UI->Details->GetDesiredSize().Y<=UI->Details->GetCachedGeometry().GetLocalSize().Y+1,TEXT("long_route_details_fit_without_hiding_reward"));Capture(TEXT("QA_Accept_Hold.png"));Next();
 }else if(ValidationStage==5&&ValidationTime>.25){
  UI->AcceptReleased();HoldStart=GetWorld()->GetTimeSeconds()-3;AdvanceHeldAction();Check(!bHolding&&HoldProgress==0&&ActiveOrders.IsEmpty(),TEXT("release_cancels_without_accepting"));
  UI->SelectEntry(0);UI->AcceptPressed();UI->OpenMap();Check(!bHolding&&ActiveOrders.IsEmpty(),TEXT("changing_page_cancels_hold"));
  UI->OpenOrders();UI->SelectEntry(0);UI->AcceptPressed();UI->SelectEntry(1);Check(!bHolding&&HoldProgress==0,TEXT("changing_selection_cancels_hold"));
  UI->SelectEntry(0);UI->AcceptPressed();FSlateApplication::Get().OnApplicationActivationStateChanged().Broadcast(false);Check(!bHolding&&HoldProgress==0,TEXT("alt_tab_cancels_pending_acceptance"));EndAction();Next();
 }else if(ValidationStage==6&&ValidationTime>.4){
  UI->SelectEntry(0);auto Enter=Key(EKeys::Enter);Check(Enter.IsEventHandled()&&bHolding,TEXT("enter_supports_hold_to_accept"));HeldID=HeldOrder;Key(EKeys::Enter,true);Check(!bHolding||HeldOrder==HeldID,TEXT("key_repeat_does_not_switch_order"));Release(EKeys::Enter);Check(!bHolding&&ActiveOrders.IsEmpty(),TEXT("enter_release_cancels_hold"));
  SelectedOffer.Invalidate();Key(EKeys::E);HoldStart=GetWorld()->GetTimeSeconds()-3;AdvanceHeldAction();Check(ActiveOrders.IsEmpty()&&!bHolding,TEXT("confirm_without_selection_cannot_accept"));
  UI->SelectEntry(0);UI->AcceptPressed();Offers[0].ExpiresAt=GetWorld()->GetTimeSeconds()-1;AdvanceHeldAction();Check(ActiveOrders.IsEmpty()&&!bHolding,TEXT("expired_offer_cancels_pending_acceptance"));
  Offers.Empty();EnterIdle();GenerateOffer();UI->OpenShop();Next();
 }else if(ValidationStage==7&&ValidationTime>1){
  Check(UI->AcceptButton&&!UI->AcceptButton->GetIsEnabled(),TEXT("unaffordable_upgrade_disabled"));int32 Before=Balance;Check(!PurchaseUpgrade(TEXT("BikePedals"))&&Balance==Before,TEXT("unaffordable_purchase_preserves_money"));Check(!SwitchVehicle(),TEXT("locked_motorcycle_cannot_switch"));
  bool NodesFit=true;int32 Nodes=0;for(auto* B:UI->Choices)if(B->Choice<100){Nodes++;NodesFit&=B->GetContent()->GetDesiredSize().Y<=36;}
  Check(Nodes==4&&NodesFit,TEXT("bike_progression_four_readable_nodes"));
  UI->SelectEntry(0);Key(EKeys::Right);Check(UI->Selection==1,TEXT("progression_arrow_right_follows_spatial_node"));Key(EKeys::Down);Check(UI->Selection==2,TEXT("progression_arrow_down_follows_spatial_node"));Key(EKeys::Left);Check(UI->Selection==3,TEXT("progression_arrow_left_follows_spatial_node"));
  UI->OpenCatalog();UI->GarageMoto();UI->SelectEntry(5);Next();
 }else if(ValidationStage==8&&ValidationTime>1){
  auto* FrameSlot=Cast<UCanvasPanelSlot>(UI->Frame->Slot);Check(FrameSlot&&FrameSlot->GetSize().Equals(FVector2D(420,680),.1),TEXT("garage_preserves_original_phone_dimensions"));Check(UI->Details->GetText().ToString().Contains(TEXT("Sistema de inyección")),TEXT("garage_explains_exact_upgrade_requirement"));
  auto* Equip=Button(TEXT("EQUIPAR"));Check(Equip&&!Equip->GetIsEnabled(),TEXT("unowned_vehicle_cannot_offer_equip_action"));
  Check(UI->ModelBuyButton&&!UI->ModelBuyButton->GetIsEnabled(),TEXT("locked_catalog_purchase_disabled"));Check(!EquipVehicle(TEXT("MotoSport")),TEXT("unowned_vehicle_equip_rejected"));
  UI->OpenActiveOrders();Check(UI->Details->GetText().ToString().Contains(TEXT("primera ruta"))&&Button(TEXT("BUSCAR OTRO PEDIDO")),TEXT("empty_active_orders_explains_next_action"));
  UI->OpenHome();Next();
 }else if(ValidationStage==9&&ValidationTime>1){
  auto Hints=UI->PhoneHints->GetFont();float DPIScale=UWidgetLayoutLibrary::GetViewportScale(this);Check(Hints.Size*DPIScale>=11.5f,TEXT("keyboard_hints_have_readable_physical_size"));
  for(int32 Page=0;Page<=6;Page++)UI->BuildPage(Page);Check(UI->Selection>=10&&UI->Selection<=12,TEXT("cargo_page_selection_is_sanitized"));Check(UI->PreviewArt&&UI->PreviewArt->GetBrush().GetResourceObject()!=nullptr,TEXT("cargo_preview_loaded_after_page_changes"));TArray<UWidget*> All;UI->WidgetTree->GetAllWidgets(All);StableWidgets=All.Num();
  for(int32 N=0;N<6;N++)for(int32 Page=0;Page<=6;Page++)UI->BuildPage(Page);All.Empty();UI->WidgetTree->GetAllWidgets(All);Check(All.Num()==StableWidgets,TEXT("reopening_pages_does_not_leak_widgets"));
  UI->OpenOrders();UI->SelectEntry(0);UI->AcceptPressed();if(PhoneOpen)TogglePhone();Check(!bHolding,TEXT("closing_phone_cancels_hold"));
  UI->SelectEntry(0);BeginAction();P->TogglePause();Check(UGameplayStatics::IsGamePaused(this)&&!bHolding,TEXT("pause_cancels_held_action"));P->TogglePause();Check(!UGameplayStatics::IsGamePaused(this),TEXT("pause_can_resume"));
  Balance=1000000;int32 Before=Balance;bool Bought=PurchaseUpgrade(TEXT("BikePedals"));Check(Bought&&Balance<Before&&Owns(TEXT("BikePedals")),TEXT("valid_purchase_charges_once"));Before=Balance;Check(!PurchaseUpgrade(TEXT("BikePedals"))&&Balance==Before,TEXT("duplicate_purchase_cannot_charge_twice"));
  Check(SaveProfile(),TEXT("qa_profile_saves"));auto* Saved=Cast<UDeliverySave>(UGameplayStatics::LoadGameFromSlot(ProfileSlot(),0));Check(Saved&&Saved->Balance==Balance&&Saved->Purchased.Contains(TEXT("BikePedals")),TEXT("saved_progress_matches_purchase"));
  for(FName ID:{FName(TEXT("CargoBackpack")),FName(TEXT("CargoWaist")),FName(TEXT("Motorcycle")),FName(TEXT("CargoPanniers"))})Purchased.AddUnique(ID);RebuildStats();Check(EquipVehicle(TEXT("MotoStreet"))&&CargoCapacity(true)==5,TEXT("cargo_capacity_five_after_unlocks"));Next();
 }else if(ValidationStage==10&&ValidationTime>.6){
  ExitStore();P->GetCharacterMovement()->StopMovementImmediately();P->SetActorLocation(FVector(-6400,14100,100));Offers.Empty();EnterIdle();GenerateOffer();
  for(int32 N=0;N<5;N++){if(Offers.IsEmpty())GenerateOffer();if(!Offers.IsEmpty())Check(AcceptOffer(Offers[0].ID),TEXT("accept_order_with_free_cargo_slot"));}
  Check(ActiveOrders.Num()==5,TEXT("five_orders_can_coexist"));GenerateOffer();int32 Count=ActiveOrders.Num();Check(!Offers.IsEmpty()&&!AcceptOffer(Offers[0].ID)&&ActiveOrders.Num()==Count,TEXT("sixth_order_rejected_at_capacity"));
  Check(!EquipVehicle(TEXT("BikeCity"))&&Vehicle==EDeliveryVehicle::Motorcycle,TEXT("overloaded_vehicle_change_rejected"));
  if(!PhoneOpen)TogglePhone();UI->OpenActiveOrders();Next();
 }else if(ValidationStage==11&&ValidationTime>1){
  int32 Visible=0;for(auto* B:UI->Choices)if(B->GetVisibility()==ESlateVisibility::Visible)Visible++;Check(Visible==5,TEXT("all_five_active_orders_visible"));
  UI->SelectEntry(4);int32 Budget=OrderBudget;int32 Basket=BasketCount;FGuid ID=Order.ID;UI->SelectEntry(0);UI->SelectEntry(4);Check(Order.ID==ID&&OrderBudget==Budget&&BasketCount==Basket,TEXT("active_order_selection_preserves_shopping_state"));
  Capture(TEXT("QA_Five_Orders.png"));Next();
 }else if(ValidationStage==12&&ValidationTime>.8){
  if(PhoneOpen)TogglePhone();EndAction();DestroyMarkers();ActiveOrders.Empty();Offers.Empty();EnterIdle();GenerateOffer();
  Next();
 }else if(ValidationStage==13&&ValidationTime>.8f){
  for(auto* W:UI->AppControls)if(W)Check(W->GetVisibility()==ESlateVisibility::Collapsed,TEXT("closed_phone_hides_app_controls"));
  auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("status"),ValidationErrors.IsEmpty()?TEXT("PASS"):TEXT("FAIL"));R->SetArrayField(TEXT("checks"),Checks);R->SetNumberField(TEXT("total"),Checks.Num());TArray<TSharedPtr<FJsonValue>> Errors;for(const auto& E:ValidationErrors)Errors.Add(MakeShared<FJsonValueString>(E));R->SetArrayField(TEXT("failures"),Errors);R->SetNumberField(TEXT("viewport_width"),UWidgetLayoutLibrary::GetViewportSize(this).X);R->SetNumberField(TEXT("viewport_height"),UWidgetLayoutLibrary::GetViewportSize(this).Y);
  FString JSON;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&JSON));FFileHelper::SaveStringToFile(JSON,*(FPaths::ProjectSavedDir()/TEXT("usability_validation.json")));UE_LOG(LogTemp,Display,TEXT("USABILITY_RESULT %s"),*JSON);ValidationStage++;FPlatformMisc::RequestExit(false);
 }
}
