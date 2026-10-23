from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp');s=p.read_text(encoding='utf-8')
s=s.replace('FVector2D(8,102+I*51),FVector2D(356,46)','FVector2D(8,102+I*46),FVector2D(356,42)')
s=s.replace('FVector2D(10,105+I*51),FVector2D(35,39)','FVector2D(12,106+I*46),FVector2D(32,32)')
# Cached authored widgets must receive the new layout too.
s=s.replace('Existing->Phone=this;Existing->Choice=Index;','if(auto* LayoutSlot=Cast<UCanvasPanelSlot>(Existing->Slot)){LayoutSlot->SetPosition(P);LayoutSlot->SetSize(S);}Existing->Phone=this;Existing->Choice=Index;')
s=s.replace('if(auto* Existing=Cast<UImage>(WidgetTree->FindWidget(LayoutName))){AppControls.Add(Existing);return Existing;}','if(auto* Existing=Cast<UImage>(WidgetTree->FindWidget(LayoutName))){if(auto* LayoutSlot=Cast<UCanvasPanelSlot>(Existing->Slot)){LayoutSlot->SetPosition(P);LayoutSlot->SetSize(S);}AppControls.Add(Existing);return Existing;}')
p.write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUsability.cpp');s=p.read_text(encoding='utf-8')
s=s.replace('UI->SelectEntry(0);UI->RefreshText();Check(SelectedIncoming()', 'Offers[0].PickupName=FText::FromString(TEXT("Mercado Don Luis - La Candelaria"));Offers[0].DropoffName=FText::FromString(TEXT("Casa de Marta - Centro / La Candelaria"));UI->SelectEntry(0);UI->RefreshText();Check(SelectedIncoming()',1)
s=s.replace('Capture(TEXT("QA_Accept_Hold.png"));Next();','Check(UI->Details->GetDesiredSize().Y<=UI->Details->GetCachedGeometry().GetLocalSize().Y+1,TEXT("long_route_details_fit_without_hiding_reward"));Capture(TEXT("QA_Accept_Hold.png"));Next();',1)
p.write_text(s,encoding='utf-8')
