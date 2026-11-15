from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.cpp')
s=p.read_text(encoding='utf-8')
s=s.replace('#include "DeliverySystem.h"','#include "DeliverySystem.h"\n#include "Components/Button.h"\n#include "Components/TextBlock.h"',1)
old='  if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget))UI->OpenHome();CaptureUI(TEXT("UrbanHome.png"));ValidationStage++;ValidationTime=0;'
new='''  if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget)){
   const TCHAR* Buttons[]={TEXT("HomeMap"),TEXT("HomeOrders"),TEXT("HomeWorkshop"),TEXT("HomeDeliveries"),TEXT("HomeCargo"),TEXT("HomeVehicles")};
   const TCHAR* Titles[]={TEXT("MIS CALLES"),TEXT("PEDIDOS"),TEXT("EL TALLER"),TEXT("MIS ENTREGAS"),TEXT("EQUIPO DE CARGA"),TEXT("LA VITRINA")};
   Check(UI->GetWidgetFromName(TEXT("DesignerHome"))!=nullptr,TEXT("designer_home_loaded"));
   for(int32 I=0;I<6;I++){
    auto* Button=Cast<UButton>(UI->GetWidgetFromName(Buttons[I]));Check(Button!=nullptr,Buttons[I]);
    if(Button){Button->OnClicked.Broadcast();auto* Title=Cast<UTextBlock>(UI->GetWidgetFromName(TEXT("PageTitle")));Check(Title&&Title->GetText().ToString()==Titles[I],TEXT("blueprint_launcher_opens_expected_app"));}
   }
   UI->OpenHome();
  }CaptureUI(TEXT("UrbanHome.png"));ValidationStage++;ValidationTime=0;'''
assert old in s
p.write_text(s.replace(old,new),encoding='utf-8')
