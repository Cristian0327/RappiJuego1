from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp')
s=p.read_text(encoding='utf-8')
start=s.index(' Root=WidgetTree->ConstructWidget<UCanvasPanel>();')
end=s.index(' if(Delivery&&Delivery->Upgrades)',start)
block=s[start:end]
widgets={'Root':'UCanvasPanel','PhoneShade':'UBorder','PhoneArt':'UImage','Frame':'UBorder','Screen':'UCanvasPanel','MiniMap':'UDeliveryMapWidget','Notice':'UTextBlock','PhoneHints':'UTextBlock','EnergyText':'UTextBlock','EnergyBar':'UProgressBar','HoldBar':'UProgressBar'}
for name,typ in widgets.items():
 old=f'{name}=WidgetTree->ConstructWidget<{typ}>();'
 assert old in block,old
 block=block.replace(old,f'{name}=WidgetTree->ConstructWidget<{typ}>({typ}::StaticClass(),TEXT("{name}"));')
for name in ['Header','Details','PageTitle']:
 line=next(l for l in block.splitlines() if l.strip().startswith(name+'=AddText'))
 block=block.replace(line,line+f'\n {name}->Rename(TEXT("{name}"),WidgetTree);')
lookup=' Root=Cast<UCanvasPanel>(WidgetTree->FindWidget(TEXT("Root")));\n if(Root){\n'
for name,typ in {**widgets,**{n:'UTextBlock' for n in ['Header','Details','PageTitle']}}.items():
 if name!='Root':lookup+=f'  {name}=Cast<{typ}>(WidgetTree->FindWidget(TEXT("{name}")));\n'
lookup+='  if(MiniMap)MiniMap->Delivery=Delivery;\n }\n if(!Root||!Frame||!Screen||!MiniMap||!Header||!Details||!PageTitle||!PhoneArt||!PhoneShade||!Notice||!PhoneHints||!EnergyText||!EnergyBar||!HoldBar){\n'
block+=' auto* InitialFrame=Cast<UCanvasPanelSlot>(Frame->Slot);InitialFrame->SetPosition(FVector2D(20,20));InitialFrame->SetSize(FVector2D(420,680));\n auto* InitialArt=Cast<UCanvasPanelSlot>(PhoneArt->Slot);InitialArt->SetPosition(FVector2D(20,20));InitialArt->SetSize(FVector2D(420,680));\n }\n'
s=s[:start]+lookup+block+s[end:]
s=s.replace(' BuildPage(0);return Super::RebuildWidget();',' if(!AuthoringPhoneTemplate)BuildPage(0);return Super::RebuildWidget();')
p.write_text(s,encoding='utf-8')
