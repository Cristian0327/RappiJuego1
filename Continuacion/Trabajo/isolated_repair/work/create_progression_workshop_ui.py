from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp');s=p.read_text(encoding='utf-8')
# Always update cached button layout when switching between the phone and wide garage.
s=s.replace('if(auto* Existing=Cast<UButton>(WidgetTree->FindWidget(LayoutName))){if(auto* Label=', 'if(auto* Existing=Cast<UButton>(WidgetTree->FindWidget(LayoutName))){if(auto* LayoutSlot=Cast<UCanvasPanelSlot>(Existing->Slot)){LayoutSlot->SetPosition(P);LayoutSlot->SetSize(S);}if(auto* Label=')
s=s.replace('const bool GaragePage=Page==3||Page==4;', 'const bool GaragePage=Page==3||Page==4;const float ContentWidth=GaragePage?712.f:372.f;')
s=s.replace('TitleFont.Size=GaragePage?17:26','TitleFont.Size=GaragePage?24:26').replace('FVector2D(GaragePage?164:350,42)','FVector2D(350,42)')
s=s.replace('FVector2D(338,0),FVector2D(32,28)','FVector2D(ContentWidth-34,0),FVector2D(32,28)')
s=s.replace('FVector2D(178,40),FVector2D(80,29)','FVector2D(460,40),FVector2D(104,32)').replace('FVector2D(264,40),FVector2D(100,29)','FVector2D(572,40),FVector2D(132,32)')
s=s.replace('TEXT("PIEZAS")','TEXT("MEJORAS")')
s=s.replace('FVector2D(8,79),FVector2D(174,29)','FVector2D(8,80),FVector2D(344,32)').replace('FVector2D(190,79),FVector2D(174,29)','FVector2D(360,80),FVector2D(344,32)')
s=s.replace('FVector2D(8,112),FVector2D(356,176)','FVector2D(8,128),FVector2D(356,250)').replace('FVector2D(8,290),FVector2D(356,25)','FVector2D(8,386),FVector2D(356,25)')
old='''   for(int32 I=Start;I<End;I++){int32 J=I-Start;AddChoice(Names[I],I,FVector2D(8+(J%3)*120,320+(J/3)*43),FVector2D(112,36));}
   DSlot->SetPosition(FVector2D(8,410));DSlot->SetSize(FVector2D(356,51));'''
new=r'''   Caption(TEXT("PROGRESIÓN DE MEJORAS"),FVector2D(380,120),FVector2D(324,24),14)->SetColorAndOpacity(Mint);
   const FVector2D NodePos[]={FVector2D(380,156),FVector2D(552,156),FVector2D(552,280),FVector2D(380,280),FVector2D(380,404),FVector2D(552,404)};
   auto Wire=[&](FVector2D Pos,FVector2D Size){const FName N=NextLayoutName();auto* W=Cast<UBorder>(WidgetTree->FindWidget(N));if(!W){W=WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(),N);Screen->AddChildToCanvas(W);}W->SetBrushColor(FLinearColor(.12,.30,.32));auto* WS=Cast<UCanvasPanelSlot>(W->Slot);WS->SetPosition(Pos);WS->SetSize(Size);AppControls.Add(W);};
   for(int32 J=0;J<End-Start-1;J++){const auto A=NodePos[J],B=NodePos[J+1];if(A.Y==B.Y){Wire(FVector2D(536,A.Y+42),FVector2D(16,8));Caption(J==2?TEXT("<"):TEXT(">"),FVector2D(538,A.Y+22),FVector2D(14,16),10);}else{Wire(FVector2D(A.X+74,A.Y+92),FVector2D(8,32));Caption(TEXT("v"),FVector2D(A.X+70,A.Y+101),FVector2D(16,16),11);}}
   for(int32 I=Start;I<End;I++)AddChoice(Names[I],I,NodePos[I-Start],FVector2D(156,92));
   if(!PreviewMoto){auto* Next=AddButton(TEXT("SIGUIENTE RAMA: MOTOS >"),FVector2D(380,440),FVector2D(324,52));Next->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::GarageMoto);Caption(TEXT("Instala el motor de cicla para desbloquearla."),FVector2D(380,502),FVector2D(324,36),11);}
   DSlot->SetPosition(FVector2D(8,416));DSlot->SetSize(FVector2D(356,70));'''
assert old in s;s=s.replace(old,new)
s=s.replace('FVector2D(8,467),FVector2D(222,32)','FVector2D(8,488),FVector2D(222,32)').replace('FVector2D(238,467),FVector2D(126,32)','FVector2D(238,488),FVector2D(126,32)')
s=s.replace('FVector2D(8+I*35,510),FVector2D(29,26)','FVector2D(8+I*35,526),FVector2D(29,22)').replace('FVector2D(224,510),FVector2D(140,26)','FVector2D(224,526),FVector2D(140,22)')
s=s.replace('DSlot->SetPosition(FVector2D(8,481));DSlot->SetSize(FVector2D(356,29));','DSlot->SetPosition(FVector2D(8,420));DSlot->SetSize(FVector2D(356,80));\n   Caption(TEXT("ELIGE UN MODELO"),FVector2D(380,120),FVector2D(324,24),14)->SetColorAndOpacity(Mint);')
s=s.replace('FVector2D(8,320+J*51),FVector2D(356,44)','FVector2D(380,156+J*124),FVector2D(324,96)')
# Footer spans the wider surface while all other apps retain their existing layout.
s=s.replace('FVector2D(8,552),FVector2D(82,33)','FVector2D(8,552),FVector2D(GaragePage?164:82,33)')
s=s.replace('FVector2D(99,552),FVector2D(82,33)','FVector2D(GaragePage?184:99,552),FVector2D(GaragePage?164:82,33)')
s=s.replace('FVector2D(190,552),FVector2D(82,33)','FVector2D(GaragePage?360:190,552),FVector2D(GaragePage?164:82,33)')
s=s.replace('FVector2D(281,552),FVector2D(83,33)','FVector2D(GaragePage?536:281,552),FVector2D(GaragePage?168:83,33)')
s=s.replace('TEXT("EL TALLER"),TEXT("LA VITRINA")','TEXT("MIS MEJORAS"),TEXT("MI GARAJE")')
# Upgrade labels expose actual progression state and price from the data table.
needle='bool Selected=B->Choice==Selection;Style.Normal.TintColor=Selected?Gold:Delivery->Owns(UpgradeIDs[B->Choice])?FLinearColor(.02,.13,.14):Panel;'
replace=r'''bool Selected=B->Choice==Selection;const auto* R=Delivery->Upgrades->FindRow<FDeliveryUpgrade>(UpgradeIDs[B->Choice],TEXT("ProgressNode"));const bool Owned=Delivery->Owns(UpgradeIDs[B->Choice]);const bool Ready=R&&(R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite));Style.Normal.TintColor=Selected?Gold:Owned?FLinearColor(.02,.13,.14):Panel;if(R)if(auto* L=Cast<UTextBlock>(B->GetContent())){auto F=L->GetFont();F.Size=12;L->SetFont(F);L->SetJustification(ETextJustify::Center);L->SetText(FText::FromString(FString::Printf(TEXT("%02d  %s\n%s\n%s"),B->Choice-(PreviewMoto?4:0)+1,*R->Title.ToString(),Owned?TEXT("[+] INSTALADA"):Ready?TEXT("DISPONIBLE"):TEXT("[X] BLOQUEADA"),Owned?TEXT("LISTA PARA USAR"):*FString::Printf(TEXT("$%s"),*FText::AsNumber(R->Price).ToString()))));}'''
assert needle in s;s=s.replace(needle,replace)
s=s.replace('FString::Printf(TEXT("%s   /   %s"),*R->Title.ToString(),Delivery->OwnsVehicle(ID)?TEXT("EN TU GARAJE"):*FString::Printf(TEXT("$%s"),*FText::AsNumber(R->Price).ToString()))','FString::Printf(TEXT("%s\n%s\n%s"),*R->Title.ToString(),Delivery->OwnsVehicle(ID)?TEXT("[+] EN TU GARAJE"):*FString::Printf(TEXT("$%s"),*FText::AsNumber(R->Price).ToString()),Delivery->OwnsVehicle(ID)?TEXT("SELECCIONA Y EQUIPA"):R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite)?TEXT("DISPONIBLE"):TEXT("[X] REQUIERE MEJORAS"))')
s=s.replace('TEXT("Bloqueado: instala primero la mejora de moto.")','TEXT("Bloqueado: completa antes la mejora requerida en MIS MEJORAS.")')
s=s.replace('FVector2D(640,360)','FVector2D(640,448)')
# The garage expands into a landscape workbench, rather than shrinking everything into a phone.
s=s.replace('const float Scale=FMath::Min((View.Y-98)/680.f,(View.X-48)/420.f);','const float OpenWidth=(Page==3||Page==4)?760.f:420.f;const float Scale=FMath::Min((View.Y-98)/680.f,(View.X-48)/OpenWidth);')
s=s.replace('FVector2D(420*Scale,680*Scale)','FVector2D(OpenWidth*Scale,680*Scale)').replace('FVector2D(420*Scale,680*Scale+64)','FVector2D(OpenWidth*Scale,680*Scale+64)').replace('Open?FVector2D(420,680)','Open?FVector2D(OpenWidth,680)')
p.write_text(s,encoding='utf-8')
