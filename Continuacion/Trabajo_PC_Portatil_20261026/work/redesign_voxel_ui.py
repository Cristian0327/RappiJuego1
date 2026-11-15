from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp')
s=p.read_text(encoding='utf-8')
s=s.replace('namespace { const FLinearColor Ink(.012,.023,.039,1),Panel(.04,.067,.10,1),Mint(.025,.65,.86,1),Gold(1,.22,.025,1),Paper(.90,.80,.59,1); }',r'''namespace {
const FLinearColor Ink(.009,.019,.026,1),Panel(.035,.085,.105,1),Mint(.06,.85,.74,1),Gold(1,.36,.065,1),Paper(.94,.96,.87,1);
// A tiny, point-sampled relief tile. Nine-slice preserves its square steps at every size.
UTexture2D* VoxelTile(bool Pressed=false){
 static UTexture2D* Tiles[2]={};auto*& T=Tiles[Pressed?1:0];if(T)return T;
 T=UTexture2D::CreateTransient(16,16,PF_B8G8R8A8);T->AddToRoot();T->Filter=TF_Nearest;T->SRGB=true;T->NeverStream=true;
 auto& M=T->GetPlatformData()->Mips[0];auto* Pixels=static_cast<FColor*>(M.BulkData.Lock(LOCK_READ_WRITE));
 for(int Y=0;Y<16;Y++)for(int X=0;X<16;X++){
  const bool Cut=(X<2||X>=14)&&(Y<2||Y>=14);
  int V=230;if(X<2||Y<2)V=Pressed?75:255;else if(X>=14||Y>=14)V=Pressed?255:70;else if(X<4||Y<4)V=Pressed?130:245;else if(X>=12||Y>=12)V=Pressed?245:135;
  Pixels[Y*16+X]=FColor(V,V,V,Cut?0:255);
 }M.BulkData.Unlock();T->UpdateResource();return T;
}
FSlateBrush VoxelBrush(FLinearColor Color,bool Pressed=false){FSlateBrush B;B.SetResourceObject(VoxelTile(Pressed));B.DrawAs=ESlateBrushDrawType::Box;B.ImageSize=FVector2D(16,16);B.Margin=FMargin(.25f);B.TintColor=Color;return B;}
void VoxelButton(UButton* B,FLinearColor Color=Panel){auto S=B->GetStyle();S.Normal=VoxelBrush(Color);S.Hovered=VoxelBrush(FLinearColor(.10,.31,.33));S.Pressed=VoxelBrush(Gold,true);S.Disabled=VoxelBrush(FLinearColor(.045,.065,.075));S.NormalPadding=FMargin(6,3,6,5);S.PressedPadding=FMargin(6,5,6,3);B->SetStyle(S);B->SetToolTipText(FText::GetEmpty());}
}''')
# Existing authored layouts are retained: apply the same component system after loading them.
s=s.replace('if(!AuthoringPhoneTemplate)BuildPage(0);return Super::RebuildWidget();','''ApplyVoxelTheme();if(!AuthoringPhoneTemplate)BuildPage(0);return Super::RebuildWidget();''')
idx=s.index('void UDeliveryPhoneWidget::BuildPage(')
s=s[:idx]+r'''void UDeliveryPhoneWidget::ApplyVoxelTheme(){
 auto* Pixel=LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font"));
 TArray<UWidget*> All;WidgetTree->GetAllWidgets(All);
 for(auto* W:All){
  if(auto* B=Cast<UButton>(W))VoxelButton(B);
  if(auto* T=Cast<UTextBlock>(W)){auto F=T->GetFont();if(Pixel)F.FontObject=Pixel;T->SetFont(F);T->SetColorAndOpacity(Paper);T->SetShadowOffset(FVector2D(0,2));T->SetShadowColorAndOpacity(FLinearColor(0,0,0,.65));}
  if(auto* I=Cast<UImage>(W))if(auto* Texture=Cast<UTexture2D>(I->GetBrush().GetResourceObject()))Texture->Filter=TF_Nearest;
 }
 Header->SetColorAndOpacity(Mint);PageTitle->SetColorAndOpacity(Paper);
 PhoneShade->SetBrushColor(FLinearColor(.003,.01,.016,.8));
 if(auto* B=Cast<UBorder>(WidgetTree->FindWidget(TEXT("HomeStatusPanel")))){B->SetBrush(VoxelBrush(Panel));B->SetBrushColor(FLinearColor::White);}
 if(auto* T=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("HomeTagline"))))T->SetText(FText::FromString(TEXT("BOGOTÁ SE MUEVE CONTIGO")));
 for(auto* Bar:{EnergyBar,HoldBar}){FProgressBarStyle Style;Style.BackgroundImage=VoxelBrush(Ink);Style.FillImage=VoxelBrush(FLinearColor::White);Style.MarqueeImage=Style.FillImage;Bar->SetWidgetStyle(Style);}
 EnergyBar->SetFillColorAndOpacity(Mint);HoldBar->SetFillColorAndOpacity(Gold);
}
''' +s[idx:]
s=s.replace('BuildingLayout=false;RefreshText();','''BuildingLayout=false;
 for(auto* W:AppControls)if(auto* B=Cast<UButton>(W))VoxelButton(B);
 for(auto* B:{H,M,O,S}){const bool Current=(B==H&&Page==0)||(B==M&&Page==1)||(B==O&&(Page==2||Page==5))||(B==S&&(Page==3||Page==4||Page==6));if(Current){auto Style=B->GetStyle();Style.Normal.TintColor=Mint;B->SetStyle(Style);if(auto* T=Cast<UTextBlock>(B->GetContent())){T->SetColorAndOpacity(Ink);T->SetShadowOffset(FVector2D::ZeroVector);}}}
 RefreshText();''')
s=s.replace('Style.Normal.TintColor=Selected?Gold:Paper;Style.Disabled=Style.Normal;Style.Hovered.TintColor=FLinearColor(1,.72,.38);','Style.Normal.TintColor=Selected?Gold:Panel;Style.Hovered.TintColor=Selected?FLinearColor(1,.54,.13):FLinearColor(.10,.31,.33);')
s=s.replace('L->SetColorAndOpacity(Ink);L->SetText','L->SetColorAndOpacity(Selected?Ink:Paper);L->SetShadowOffset(Selected?FVector2D::ZeroVector:FVector2D(0,1));L->SetText')
# Logical errors become actionable, before the purchase rather than silent disabled controls.
s=s.replace('AcceptButton->SetIsEnabled(Delivery->SelectedIncoming()&&Delivery->ActiveOrders.Num()<Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));','''const bool Full=Delivery->ActiveOrders.Num()>=Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle);
  AcceptButton->SetIsEnabled(Delivery->SelectedIncoming()&&!Full);
  if(Full)T=TEXT("Carga completa. Entrega un pedido para liberar espacio.\nTus pedidos están en VER PEDIDOS ACEPTADOS.");
  if(auto* L=Cast<UTextBlock>(AcceptButton->GetContent()))L->SetText(FText::FromString(Full?TEXT("SIN ESPACIO DE CARGA"):Delivery->bHolding?TEXT("ACEPTANDO... SUELTA PARA CANCELAR"):TEXT("MANTÉN E / ENTER  2 s PARA ACEPTAR")));''')
s=s.replace('if(Page==1)T=TEXT("Mercado · Comida · Tecnología\\nDroguería · Flores\\nClic: marcar destino · Turquesa: tu ruta");','if(Page==1)T=TEXT("Mercado · Comida · Tecnología\\nDroguería · Flores\\nClic: marcar destino · Turquesa: tu ruta");')
s=s.replace('Details->SetText(FText::FromString(T));Details->SetVisibility',r'''// Finish every selection with the same readable selected/owned/disabled vocabulary.
 for(auto* B:Choices){bool Selected=Page==2?(Delivery->SelectedIncoming()&&Delivery->Offers.IsValidIndex(B->Choice)&&Delivery->Offers[B->Choice].ID==Delivery->SelectedIncoming()->ID):Page==5?(Delivery->ActiveOrders.IsValidIndex(B->Choice)&&Delivery->ActiveOrders[B->Choice].Order.ID==Delivery->Order.ID):Page==4?B->Choice==CatalogSelection:B->Choice==Selection;
  if(Page==6){auto Style=B->GetStyle();Style.Normal.TintColor=Selected?Gold:Panel;B->SetStyle(Style);}
  if(auto* Label=Cast<UTextBlock>(B->GetContent())){Label->SetColorAndOpacity(Selected?Ink:Paper);Label->SetShadowOffset(Selected?FVector2D::ZeroVector:FVector2D(0,1));}
 }
 if(Page==4&&ModelIDs.IsValidIndex(CatalogSelection)){
  const auto* Spec=Delivery->VehicleCatalog->FindRow<FDeliveryVehicleSpec>(ModelIDs[CatalogSelection],TEXT("Explain"));
  if(Spec){if(Delivery->OwnsVehicle(ModelIDs[CatalogSelection]))T=TEXT("En tu garaje. Elige EQUIPAR para usarlo.");else if(!Spec->Prerequisite.IsNone()&&!Delivery->Owns(Spec->Prerequisite))T=TEXT("Bloqueado: instala primero la mejora de moto.");else if(Delivery->Balance<Spec->Price)T=FString::Printf(TEXT("Te faltan $%s para comprarlo."),*FText::AsNumber(Spec->Price-Delivery->Balance).ToString());}
 }
 if((Page==3||Page==6)&&AcceptButton&&!AcceptButton->GetIsEnabled()&&UpgradeIDs.IsValidIndex(Selection)){
  const auto* R=Delivery->Upgrades->FindRow<FDeliveryUpgrade>(UpgradeIDs[Selection],TEXT("Explain"));if(R&&!Delivery->Owns(UpgradeIDs[Selection])&&(R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite))&&Delivery->Balance<R->Price)T+=FString::Printf(TEXT("\nTe faltan $%s."),*FText::AsNumber(R->Price-Delivery->Balance).ToString());
 }
 for(auto* B:{AcceptButton,ModelBuyButton,ModelEquipButton})if(B){auto Style=B->GetStyle();Style.Normal.TintColor=Mint;Style.Hovered.TintColor=FLinearColor(.25,1,.85);B->SetStyle(Style);if(auto* L=Cast<UTextBlock>(B->GetContent())){L->SetColorAndOpacity(B->GetIsEnabled()?Ink:FLinearColor(.58,.67,.68));L->SetShadowOffset(FVector2D::ZeroVector);}}
 Details->SetText(FText::FromString(T));Details->SetVisibility''')
# Keep the layout still and crisp; remove the temporary tilt that resampled the entire UI.
s=s.replace('SetRenderTransformAngle(FMath::Sin(A*PI)*-4)','SetRenderTransformAngle(0)')
s=s.replace('const float Scale=FMath::Min((View.Y-114)/680.f,(View.X-48)/420.f);','const float Scale=FMath::Min((View.Y-98)/680.f,(View.X-48)/420.f);')
# Pixel map: no antialiasing of roads; consistent pixel font for all map labels.
s=s.replace('ESlateDrawEffect::None,C,true,Thick','ESlateDrawEffect::None,C,false,Thick')
s=s.replace('FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),8)','FSlateFontInfo(LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font")),8)')
s=s.replace('FCoreStyle::GetDefaultFontStyle(TEXT("Bold"),9)','FSlateFontInfo(LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font")),9)')
p.write_text(s,encoding='utf-8')
h=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.h');s=h.read_text(encoding='utf-8');s=s.replace(' FName NextLayoutName();',' void ApplyVoxelTheme();\n FName NextLayoutName();');h.write_text(s,encoding='utf-8')
