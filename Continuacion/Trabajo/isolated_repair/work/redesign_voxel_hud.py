from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/BogotaHUD.cpp');s=p.read_text(encoding='utf-8')
s=s.replace('#include "Engine/Engine.h"','#include "Engine/Engine.h"\n#include "Engine/Font.h"')
s=s.replace('void ABogotaHUD::Text(const FString& S,float X,float Y,FLinearColor C,float Scale){DrawText(S,C,X,Y,GEngine->GetSmallFont(),Scale,false);}', '''void ABogotaHUD::Text(const FString& S,float X,float Y,FLinearColor C,float Scale){
 static UFont* Pixel=LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font"));
 auto* Font=Pixel?Pixel:GEngine->GetSmallFont();
 DrawText(S,FLinearColor(0,0,0,.8),FMath::RoundToFloat(X),FMath::RoundToFloat(Y)+2,Font,Scale,false);
 DrawText(S,C,FMath::RoundToFloat(X),FMath::RoundToFloat(Y),Font,Scale,false);
}''')
needle='if(P->Delivery){\n'
s=s.replace(needle,'''// Square steps, full outline, top face and lower shadow share the phone's voxel vocabulary.
 auto VoxelPanel=[&](float X,float Y,float PW,float PH,FLinearColor Face){
  X=FMath::RoundToFloat(X);Y=FMath::RoundToFloat(Y);PW=FMath::RoundToFloat(PW);PH=FMath::RoundToFloat(PH);
  DrawRect(FLinearColor(.003,.008,.012,.85),X+4,Y+6,PW,PH);
  DrawRect(FLinearColor(.006,.014,.020,1),X+4,Y,PW-8,PH);DrawRect(FLinearColor(.006,.014,.020,1),X,Y+4,PW,PH-8);
  DrawRect(Face,X+4,Y+4,PW-8,PH-8);
  DrawRect(FLinearColor(.14,.30,.33),X+8,Y+4,PW-16,3);
  DrawRect(FLinearColor(.012,.025,.032),X+8,Y+PH-7,PW-16,3);
 };
 if(P->Delivery){
''',1)
old='if(!P->Delivery->PhoneOpen){Text(TEXT("RUTA  /  BOGOTÁ VOXEL"),W-300,28,Accent,1.1);Text(P->City?P->City->DistrictAt(P->GetActorLocation()):TEXT(""),W-300,54,White,.85);Text(FString::Printf(TEXT("%d km/h    $%d"),int32(P->GetVelocity().Size2D()*.036f),P->Delivery->Balance),W-300,78,White,.9);}'
new='''if(!P->Delivery->PhoneOpen){const float X=W-280;VoxelPanel(X,16,264,104,FLinearColor(.016,.044,.055));
   Text(TEXT("RUTA / BOGOTÁ"),X+16,29,Accent,1.0);
   Text(P->City?P->City->DistrictAt(P->GetActorLocation()):TEXT(""),X+16,54,White,.85);
   Text(FString::Printf(TEXT("$%s  |  %d km/h"),*FText::AsNumber(P->Delivery->Balance).ToString(),int32(P->GetVelocity().Size2D()*.036f)),X+16,80,White,.9);
  }'''
assert old in s;s=s.replace(old,new)
s=s.replace('Y=110*S','Y=130*S').replace('DrawRect(FLinearColor(.012f,.023f,.039f,.94f),X,Y,310*S,(42+58*Tasks->ActiveOrders.Num())*S);','VoxelPanel(X,Y,310*S,(42+58*Tasks->ActiveOrders.Num())*S,FLinearColor(.016,.044,.055));')
s=s.replace('DrawRect(Focus?Accent:Muted,X+12*S,RowY+4*S,4*S,40*S);','DrawRect(Focus?Accent:Muted,X+12*S,RowY+4*S,6*S,6*S);')
s=s.replace('DrawRect(FLinearColor(.015,.025,.04,.95),S.X-18,S.Y-18,36,36);DrawRect(Accent,S.X-18,S.Y+16,36,3);','VoxelPanel(S.X-20,S.Y-20,40,40,FLinearColor(.035,.10,.12));')
start=s.index('  const float HS=FMath::Clamp(W/1280.f')
end=s.index('\n  }\n  if(P->Paused)',start)
s=s[:start]+'''  const float HS=FMath::Clamp(W/1280.f,.8f,1.f),HW=FMath::Min(W-320.f,624.f*HS),HX=W-HW-16,HY=H-100;
  VoxelPanel(HX,HY,HW,84,FLinearColor(.016,.044,.055));
  Text(P->Delivery->NavigationInstruction(),HX+16,HY+12,Accent,.88f*HS);
  Text(TEXT("[TAB] Teléfono   [E] Acción   [F] Subir / bajar"),HX+16,HY+34,White,.85f*HS);
  Text(P->Riding?TEXT("[SHIFT] Impulso   [ESPACIO] Frenar   [ESC] Pausa"):TEXT("[WASD] Mover   [ESPACIO] Saltar   [ESC] Pausa"),HX+16,HY+55,White,.85f*HS);
''' +s[end:]
s=s.replace('if(P->Paused){DrawRect(FLinearColor(0,0,0,.55),0,0,W,H);Text(TEXT("PAUSA"),W*.5-65,H*.5-25,White,2);}return;', '''if(P->Paused){DrawRect(FLinearColor(.003,.01,.016,.85),0,0,W,H);VoxelPanel(W*.5-180,H*.5-88,360,176,FLinearColor(.016,.044,.055));Text(TEXT("EN PAUSA"),W*.5-116,H*.5-55,Accent,1.8);Text(TEXT("[ESC] Volver a la ciudad"),W*.5-145,H*.5+10,White,1);Text(TEXT("Tu ruta te espera."),W*.5-112,H*.5+40,White,.9);}return;''')
p.write_text(s,encoding='utf-8')
