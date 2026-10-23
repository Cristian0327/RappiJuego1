from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp')
s=p.read_text(encoding='utf-8')
marker='UTextBlock* UDeliveryPhoneWidget::AddText'
pos=s.index(marker)
s=s[:pos]+'''FName UDeliveryPhoneWidget::NextLayoutName(){return BuildingLayout?FName(*FString::Printf(TEXT("App%d_%s_%02d"),Page,PreviewMoto?TEXT("Moto"):TEXT("Bike"),LayoutIndex++)):NAME_None;}
void UDeliveryPhoneWidget::AuthorAppLayouts(){
 for(int32 Mode=0;Mode<2;Mode++){PreviewMoto=Mode==1;for(int32 App=1;App<=6;App++)BuildPage(App);}
 for(auto* W:AppControls)if(W)W->SetVisibility(ESlateVisibility::Collapsed);
 if(MainMap)MainMap->SetVisibility(ESlateVisibility::Collapsed);
}
'''+s[pos:]
prefixes={
'UTextBlock* UDeliveryPhoneWidget::AddText': ' const FName LayoutName=NextLayoutName();if(auto* Existing=Cast<UTextBlock>(WidgetTree->FindWidget(LayoutName)))return Existing;\n',
'UButton* UDeliveryPhoneWidget::AddButton':' const FName LayoutName=NextLayoutName();if(auto* Existing=Cast<UButton>(WidgetTree->FindWidget(LayoutName))){Existing->OnClicked.Clear();Existing->OnPressed.Clear();Existing->OnReleased.Clear();AppControls.Add(Existing);return Existing;}\n',
'UDeliveryChoiceButton* UDeliveryPhoneWidget::AddChoice':' const FName LayoutName=NextLayoutName();if(auto* Existing=Cast<UDeliveryChoiceButton>(WidgetTree->FindWidget(LayoutName))){Existing->Phone=this;Existing->Choice=Index;Existing->OnClicked.Clear();Existing->OnClicked.AddDynamic(Existing,&UDeliveryChoiceButton::Choose);AppControls.Add(Existing);Choices.Add(Existing);return Existing;}\n',
'UImage* UDeliveryPhoneWidget::AddArt':' const FName LayoutName=NextLayoutName();if(auto* Existing=Cast<UImage>(WidgetTree->FindWidget(LayoutName))){AppControls.Add(Existing);return Existing;}\n'}
for signature,prefix in prefixes.items():
 start=s.index(signature);a=s.index('{\n',start)+2;b=s.index('\n}',a)
 block=s[a:b]
 for typ in ['UTextBlock','UButton','UDeliveryChoiceButton','UImage']:
  # Only the first constructed widget is the page element. Button labels remain unnamed.
  old=f'WidgetTree->ConstructWidget<{typ}>()'
  if old in block:
   block=block.replace(old,f'WidgetTree->ConstructWidget<{typ}>({typ}::StaticClass(),LayoutName)',1);break
 # Button labels must not share the parent name.
 if 'AddButton' in signature or 'AddChoice' in signature:
  block=s[a:b]
  typ='UDeliveryChoiceButton' if 'AddChoice' in signature else 'UButton'
  block=block.replace(f'WidgetTree->ConstructWidget<{typ}>()',f'WidgetTree->ConstructWidget<{typ}>({typ}::StaticClass(),LayoutName)',1)
 s=s[:a]+prefix+block+s[b:]
s=s.replace('if(W)W->RemoveFromParent();AppControls.Empty();','if(W)W->SetVisibility(ESlateVisibility::Collapsed);AppControls.Empty();')
s=s.replace('if(MainMap){MainMap->RemoveFromParent();MainMap=nullptr;}','if(MainMap){MainMap->SetVisibility(ESlateVisibility::Collapsed);MainMap=nullptr;}\n LayoutIndex=0;BuildingLayout=true;')
s=s.replace('  MainMap=WidgetTree->ConstructWidget<UDeliveryMapWidget>();','  const FName MapName=NextLayoutName();MainMap=Cast<UDeliveryMapWidget>(WidgetTree->FindWidget(MapName));const bool NewMap=!MainMap;if(NewMap)MainMap=WidgetTree->ConstructWidget<UDeliveryMapWidget>(UDeliveryMapWidget::StaticClass(),MapName);')
s=s.replace('auto* L=Screen->AddChildToCanvas(MainMap);L->SetPosition(FVector2D(8,136));L->SetSize(FVector2D(356,350));','if(NewMap){auto* L=Screen->AddChildToCanvas(MainMap);L->SetPosition(FVector2D(8,136));L->SetSize(FVector2D(356,350));}')
s=s.replace(' RefreshText();\n}\nvoid UDeliveryPhoneWidget::OpenActiveOrders',' BuildingLayout=false;RefreshText();\n}\nvoid UDeliveryPhoneWidget::OpenActiveOrders')
p.write_text(s,encoding='utf-8')
