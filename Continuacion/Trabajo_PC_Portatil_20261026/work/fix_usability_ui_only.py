from pathlib import Path
r=Path("outputs/BogotaVoxel/Source/BogotaVoxel")
p=r/'DeliveryUI.cpp';s=p.read_text(encoding="utf-8-sig");s=s.replace('AcceptButton=nullptr;ModelBuyButton=nullptr;','AcceptButton=nullptr;ModelBuyButton=nullptr;ModelEquipButton=nullptr;')
s=s.replace('L->SetPosition(FVector2D(8,136));L->SetSize(FVector2D(356,350));','L->SetPosition(FVector2D(8,152));L->SetSize(FVector2D(356,334));')
s=s.replace('}auto* Clear=AddButton(TEXT("QUITAR MI MARCA")','}auto* MapSlot=Cast<UCanvasPanelSlot>(MainMap->Slot);MapSlot->SetPosition(FVector2D(8,152));MapSlot->SetSize(FVector2D(356,334));auto* Clear=AddButton(TEXT("QUITAR MI MARCA")')
s=s.replace('auto* Equip=AddButton(TEXT("EQUIPAR"),FVector2D(240,515),FVector2D(124,30));Equip->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::EquipModel);','ModelEquipButton=AddButton(TEXT("EQUIPAR"),FVector2D(240,515),FVector2D(124,30));ModelEquipButton->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::EquipModel);')
a='if(const auto* Incoming=Delivery->SelectedIncoming())T=FString::Printf(TEXT("$%s · %d/%d espacios ocupados\\nMantén E / A / X para aceptar."),*FText::AsNumber(Incoming->Reward).ToString(),Delivery->ActiveOrders.Num(),Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));'
b='if(const auto* Incoming=Delivery->SelectedIncoming())T=FString::Printf(TEXT("Recoge: %s\\nEntrega: %s\\n$%s · Cupo %d/%d · Mantén E/Enter 2 s"),*Incoming->PickupName.ToString(),*Incoming->DropoffName.ToString().Replace(TEXT("Casa de "),TEXT("")),*FText::AsNumber(Incoming->Reward).ToString(),Delivery->ActiveOrders.Num(),Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));'
assert a in s;s=s.replace(a,b)
s=s.replace('if(ModelBuyButton)ModelBuyButton->SetIsEnabled(CanBuy);','if(ModelBuyButton)ModelBuyButton->SetIsEnabled(CanBuy);if(ModelEquipButton)ModelEquipButton->SetIsEnabled(Delivery->OwnsVehicle(Model)&&Delivery->ActiveOrders.Num()<=Delivery->CargoCapacity(Spec->Motorcycle));')
a='OpenAlpha=FMath::FInterpConstantTo(OpenAlpha,Open?1.f:0.f,Dt,4.f);const float A=FMath::SmoothStep(0.f,1.f,OpenAlpha);const FVector2D View=UWidgetLayoutLibrary::GetViewportSize(this)/FMath::Max(.1f,UWidgetLayoutLibrary::GetViewportScale(this));'
b='''OpenAlpha=FMath::FInterpConstantTo(OpenAlpha,Open?1.f:0.f,Dt,4.f);const float A=FMath::SmoothStep(0.f,1.f,OpenAlpha);const float ViewportScale=FMath::Max(.1f,UWidgetLayoutLibrary::GetViewportScale(this));const FVector2D View=UWidgetLayoutLibrary::GetViewportSize(this)/ViewportScale;
 auto HintFont=PhoneHints->GetFont();HintFont.Size=FMath::CeilToInt(12.f/ViewportScale);PhoneHints->SetFont(HintFont);
 PhoneHints->SetText(FText::FromString(TEXT("Flechas / Cruceta: elegir · E / Enter: mantener · TAB / ESC: cerrar\\n1 Mapa · 2 Pedidos · 3 Taller · 4 Maletas · 5 Garaje")));
 auto* ProgressSlot=Cast<UCanvasPanelSlot>(HoldBar->Slot);ProgressSlot->SetZOrder(100);
 if(Open&&Page==2&&AcceptButton){const auto& ButtonGeometry=AcceptButton->GetCachedGeometry();const FVector2D ButtonSize=ButtonGeometry.GetLocalSize();
  if(ButtonSize.X>0){FVector2D Start=G.AbsoluteToLocal(ButtonGeometry.LocalToAbsolute(FVector2D(0,ButtonSize.Y-5))),End=G.AbsoluteToLocal(ButtonGeometry.LocalToAbsolute(ButtonSize));ProgressSlot->SetPosition(Start);ProgressSlot->SetSize(FVector2D(End.X-Start.X,FMath::Max(3.f/ViewportScale,End.Y-Start.Y)));}
 }else {ProgressSlot->SetPosition(FVector2D(28,187));ProgressSlot->SetSize(FVector2D(220,8));}'''
assert a in s;s=s.replace(a,b)
a='if(!Delivery||!Delivery->PhoneOpen)return Super::NativeOnPreviewKeyDown(G,E);auto K=E.GetKey();if(E.IsRepeat())return Super::NativeOnPreviewKeyDown(G,E);'
b='''if(!Delivery||!Delivery->PhoneOpen)return Super::NativeOnPreviewKeyDown(G,E);auto K=E.GetKey();
 const bool Confirm=K==EKeys::E||K==EKeys::Enter||K==EKeys::Gamepad_FaceButton_Bottom;
 if(E.IsRepeat()&&Confirm)return FReply::Handled();''';assert a in s;s=s.replace(a,b)
s=s.replace('(K==EKeys::Gamepad_DPad_Down||K==EKeys::Gamepad_DPad_Right)){SelectNext();','(K==EKeys::Down||K==EKeys::Right||K==EKeys::Gamepad_DPad_Down||K==EKeys::Gamepad_DPad_Right)){if(Page==2&&!Delivery->SelectedIncoming())SelectEntry(0);else SelectNext();')
s=s.replace('(K==EKeys::Gamepad_DPad_Up||K==EKeys::Gamepad_DPad_Left)){SelectPrevious();','(K==EKeys::Up||K==EKeys::Left||K==EKeys::Gamepad_DPad_Up||K==EKeys::Gamepad_DPad_Left)){if(Page==2&&!Delivery->SelectedIncoming())SelectEntry(0);else SelectPrevious();')
s=s.replace('if(K==EKeys::E||K==EKeys::Gamepad_FaceButton_Bottom){if(Page==2)','if(Confirm){if(Page==2)')
s=s.replace('(E.GetKey()==EKeys::E||E.GetKey()==EKeys::Gamepad_FaceButton_Bottom)','(E.GetKey()==EKeys::E||E.GetKey()==EKeys::Enter||E.GetKey()==EKeys::Gamepad_FaceButton_Bottom)')
p.write_text(s,encoding="utf-8")
print('Applied the 7 confirmed usability repairs.')
