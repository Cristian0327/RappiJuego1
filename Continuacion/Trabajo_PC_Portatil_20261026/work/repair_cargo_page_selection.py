from pathlib import Path
r=Path('outputs/BogotaVoxel/Source/BogotaVoxel');p=r/'DeliveryUI.cpp';s=p.read_text(encoding='utf-8-sig')
s=s.replace('if(Delivery)Delivery->EndAction();Page=NewPage;', '''if(Delivery)Delivery->EndAction();Page=FMath::Clamp(NewPage,0,6);
 if(Page==6)Selection=FMath::Clamp(Selection,10,12);
 if(Page==3)Selection=FMath::Clamp(Selection,PreviewMoto?4:0,PreviewMoto?9:3);
 if(Page==4)CatalogSelection=FMath::Clamp(CatalogSelection,PreviewMoto?3:0,PreviewMoto?5:2);
 ''')
s=s.replace('if(Page==6&&Delivery->Upgrades&&UpgradeIDs.IsValidIndex(Selection))','if(Page==6&&Selection>=10&&Selection<=12&&Delivery->Upgrades&&UpgradeIDs.IsValidIndex(Selection))')
s=s.replace('auto HintFont=PhoneHints->GetFont();HintFont.Size=FMath::CeilToInt(12.f/ViewportScale);PhoneHints->SetFont(HintFont);','auto HintFont=PhoneHints->GetFont();const int32 HintSize=FMath::CeilToInt(12.f/ViewportScale);if(HintFont.Size!=HintSize){HintFont.Size=HintSize;PhoneHints->SetFont(HintFont);}')
old=' PhoneHints->SetText(FText::FromString(TEXT("Flechas / Cruceta: elegir · E / Enter: mantener · TAB / ESC: cerrar\\n1 Mapa · 2 Pedidos · 3 Taller · 4 Maletas · 5 Garaje")));'
assert old in s;s=s.replace(old,'')
pos=s.index(' if(Delivery&&Delivery->Upgrades){UpgradeIDs=')
s=s[:pos]+' PhoneHints->SetText(FText::FromString(TEXT("Flechas/Cruceta: elegir · E/Enter/A-X: mantener · TAB/ESC/Select: cerrar\\n1 Mapa · 2 Pedidos · 3 Taller · 4 Maletas · 5 Garaje")));\n'+s[pos:]
p.write_text(s,encoding='utf-8')
p=r/'DeliveryUsability.cpp';s=p.read_text(encoding='utf-8-sig').replace('#include "Components/ProgressBar.h"','#include "Components/ProgressBar.h"\n#include "Components/Image.h"')
s=s.replace('for(int32 Page=0;Page<=6;Page++)UI->BuildPage(Page);TArray<UWidget*> All;', 'for(int32 Page=0;Page<=6;Page++)UI->BuildPage(Page);Check(UI->Selection>=10&&UI->Selection<=12,TEXT("cargo_page_selection_is_sanitized"));Check(UI->PreviewArt&&UI->PreviewArt->GetBrush().GetResourceObject()!=nullptr,TEXT("cargo_preview_loaded_after_page_changes"));TArray<UWidget*> All;')
p.write_text(s,encoding='utf-8')
# Make a package command that includes the newly introduced native test file.
p=Path('work/package_current_game.ps1');s=p.read_text(encoding='utf-8-sig').replace('-NoUBA -MaxParallelActions=2','-NoUBA -NoUBTMakefiles -MaxParallelActions=2');Path('work/package_usability_game.ps1').write_text(s,encoding='utf-8')
print('Cargo selection bounds repaired; hints retain keyboard and gamepad controls.')
