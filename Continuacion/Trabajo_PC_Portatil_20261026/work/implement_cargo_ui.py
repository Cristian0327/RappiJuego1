from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp');s=p.read_text(encoding='utf-8');s=s.replace('Caption(TEXT("ELIGE LA RUTA QUE TE CONVIENE"),FVector2D(8,78),FVector2D(356,20),10)->SetColorAndOpacity(Mint);','auto* Routes=AddButton(TEXT("MIS ENTREGAS / CAPACIDAD"),FVector2D(8,75),FVector2D(356,23));Routes->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenActiveOrders);')
s=s.replace('auto* Catalog=AddButton(Page==3?', 'auto* Cargo=AddButton(TEXT("MALETAS"),FVector2D(8,40),FVector2D(118,29));Cargo->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenCargo);\n  auto* Catalog=AddButton(Page==3?')
pos=s.index(' auto* H=AddButton(TEXT("CASA")');s=s[:pos]+''' if(Page==5){
  DSlot->SetPosition(FVector2D(8,80));DSlot->SetSize(FVector2D(356,70));
  for(int32 I=0;I<5;I++)AddChoice(TEXT(""),I,FVector2D(8,160+I*64),FVector2D(356,56));
  auto* More=AddButton(TEXT("BUSCAR OTRO PEDIDO"),FVector2D(8,495),FVector2D(356,40));More->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenOrders);
 }
 if(Page==6){
  DSlot->SetPosition(FVector2D(8,370));DSlot->SetSize(FVector2D(356,96));
  PreviewArt=AddArt(TEXT("T_CargoBackpack"),FVector2D(8,80),FVector2D(356,176));
  AddChoice(TEXT("MOCHILA +1"),10,FVector2D(8,266),FVector2D(172,42));
  AddChoice(TEXT("CANGURERA +1"),11,FVector2D(192,266),FVector2D(172,42));
  AddChoice(TEXT("MALETAS MOTO +2"),12,FVector2D(8,317),FVector2D(356,42));
  AcceptButton=AddButton(TEXT("COMPRAR Y EQUIPAR"),FVector2D(8,480),FVector2D(356,45));AcceptButton->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::BuySelected);
 }
'''+s[pos:]
s=s.replace('void UDeliveryPhoneWidget::OpenHome()', 'void UDeliveryPhoneWidget::OpenActiveOrders(){BuildPage(5);}\nvoid UDeliveryPhoneWidget::OpenCargo(){Selection=10;BuildPage(6);}\nvoid UDeliveryPhoneWidget::OpenHome()')
s=s.replace('void UDeliveryPhoneWidget::SelectPrevious(){SelectEntry(', 'void UDeliveryPhoneWidget::SelectPrevious(){if(Page==5){SelectEntry(FMath::Max(0,OrderSelection-1));return;}if(Page==6){SelectEntry(FMath::Max(10,Selection-1));return;}SelectEntry(')
s=s.replace('void UDeliveryPhoneWidget::SelectNext(){SelectEntry(', 'void UDeliveryPhoneWidget::SelectNext(){if(Page==5){SelectEntry(FMath::Min(Delivery->ActiveOrders.Num()-1,OrderSelection+1));return;}if(Page==6){SelectEntry(FMath::Min(12,Selection+1));return;}SelectEntry(')
s=s.replace('else if(Page==3){Selection=Index;}', 'else if(Page==5){if(Delivery&&Delivery->SelectActiveOrder(Index))OrderSelection=Index;}else if(Page==3||Page==6){Selection=Index;}')
s=s.replace('TEXT("LA VITRINA")};PageTitle->SetText(FText::FromString(Titles[FMath::Clamp(Page,0,4)]))', 'TEXT("LA VITRINA"),TEXT("MIS ENTREGAS"),TEXT("EQUIPO DE CARGA")};PageTitle->SetText(FText::FromString(Titles[FMath::Clamp(Page,0,6)]))')
s=s.replace('B->SetIsEnabled(!Active);', 'B->SetIsEnabled(Delivery->ActiveOrders.Num()<Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));')
s=s.replace('const bool Selected=O.ID==Delivery->Order.ID&&!Active;', 'const bool Selected=Delivery->SelectedIncoming()&&O.ID==Delivery->SelectedIncoming()->ID;')
s=s.replace('AcceptButton->SetIsEnabled(!Active&&Delivery->State==EDeliveryState::Offered&&Delivery->OfferSecondsLeft()>0);','''if(const auto* Incoming=Delivery->SelectedIncoming())T=FString::Printf(TEXT("$%s · %d/%d espacios ocupados\\nMantén E / A / X para aceptar."),*FText::AsNumber(Incoming->Reward).ToString(),Delivery->ActiveOrders.Num(),Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));
  AcceptButton->SetIsEnabled(Delivery->SelectedIncoming()&&Delivery->ActiveOrders.Num()<Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));''')
pos=s.index(' if((Page==3||Page==4)&&Delivery->VehicleCatalog)');s=s[:pos]+''' if(Page==5){
  Delivery->StoreFocusedOrder();T=FString::Printf(TEXT("%d / %d espacios · Pulsa una entrega para guiarte.\\nCada pedido conserva sus artículos y su pago."),Delivery->ActiveOrders.Num(),Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));
  for(auto* B:Choices){const int32 I=B->Choice;bool Valid=Delivery->ActiveOrders.IsValidIndex(I);B->SetVisibility(Delivery->PhoneOpen&&Valid?ESlateVisibility::Visible:ESlateVisibility::Collapsed);if(!Valid)continue;const auto& A=Delivery->ActiveOrders[I];auto Style=B->GetStyle();Style.Normal.TintColor=A.Order.ID==Delivery->Order.ID?Gold:Panel;B->SetStyle(Style);if(auto* L=Cast<UTextBlock>(B->GetContent())){auto F=L->GetFont();F.Size=10;L->SetFont(F);L->SetText(FText::FromString(FString::Printf(TEXT("%d · %s · $%s\\n%s"),I+1,A.State==EDeliveryState::Pickup?TEXT("RECOGER"):TEXT("ENTREGAR"),*FText::AsNumber(A.Order.Reward).ToString(),*(A.State==EDeliveryState::Pickup?A.Order.PickupName:A.Order.DropoffName).ToString())));}}
 }
 if(Page==6&&Delivery->Upgrades&&UpgradeIDs.IsValidIndex(Selection)){
  const FName ID=UpgradeIDs[Selection];const auto* R=Delivery->Upgrades->FindRow<FDeliveryUpgrade>(ID,TEXT("CargoUI"));if(R){bool Owned=Delivery->Owns(ID),Ready=(R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite))&&(ID!=TEXT("CargoPanniers")||Delivery->Owns(TEXT("Motorcycle")));
   const TCHAR* Desc=Selection==10?TEXT("Mochila expandible: 2 pedidos en total."):Selection==11?TEXT("Cangurera: 3 pedidos en total."):TEXT("Dos maletas laterales: 5 pedidos en moto.");
   T=FString::Printf(TEXT("%s · $%s\\n%s\\n%s\\nLa cicla usa solo mochila y cangurera."),*R->Title.ToString(),*FText::AsNumber(R->Price).ToString(),Desc,Owned?TEXT("EQUIPADA"):Ready?TEXT("Disponible"):TEXT("Requiere la mejora anterior; las maletas requieren moto."));AcceptButton->SetIsEnabled(!Owned&&Ready&&Delivery->Balance>=R->Price);
   const TCHAR* Art[]={TEXT("T_CargoBackpack"),TEXT("T_CargoWaist"),TEXT("T_CargoPanniers")};if(PreviewArt)PreviewArt->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr,*FString::Printf(TEXT("/Game/Delivery/Art/%s.%s"),Art[Selection-10],Art[Selection-10])));
  }
 }
'''+s[pos:]
s=s.replace('(Page==2||Page==3||Page==4)&&', '(Page==2||Page==3||Page==4||Page==5||Page==6)&&');s=s.replace('else if(Page==3)BuySelected()', 'else if(Page==3||Page==6)BuySelected()')
p.write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/DeliveryData/Upgrades.csv');s=p.read_text(encoding='utf-8');s+='CargoBackpack,"Mochila expandible",80000,None,Cargo,1,10\nCargoWaist,"Cangurera de reparto",160000,CargoBackpack,Cargo,1,11\nCargoPanniers,"Maletas laterales de moto",450000,CargoWaist,Cargo,2,12\n';p.write_text(s,encoding='utf-8')
