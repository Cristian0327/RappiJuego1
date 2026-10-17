#include "BogotaGame.h"
#include "DeliverySystem.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "CanvasItem.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"

void ABogotaHUD::Text(const FString& S,float X,float Y,FLinearColor C,float Scale){
 static UFont* Pixel=LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font"));
 auto* Font=Pixel?Pixel:GEngine->GetSmallFont();
 Scale*=1.5f;
 DrawText(S,FLinearColor(0,0,0,.8),FMath::RoundToFloat(X),FMath::RoundToFloat(Y)+2,Font,Scale,false);
 DrawText(S,C,FMath::RoundToFloat(X),FMath::RoundToFloat(Y),Font,Scale,false);
}

void ABogotaHUD::DrawHUD(){
 Super::DrawHUD();auto* P=Cast<ABogotaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));if(!P||!Canvas)return;float W=Canvas->SizeX,H=Canvas->SizeY;FLinearColor White(.92,.95,.93),Muted(.55,.7,.72),Accent(.15,.9,.79);
 // Square steps, full outline, top face and lower shadow share the phone's voxel vocabulary.
 auto VoxelPanel=[&](float X,float Y,float PW,float PH,FLinearColor Face){
  X=FMath::RoundToFloat(X);Y=FMath::RoundToFloat(Y);PW=FMath::RoundToFloat(PW);PH=FMath::RoundToFloat(PH);
  DrawRect(FLinearColor(.003,.008,.012,.85),X+4,Y+6,PW,PH);
  DrawRect(FLinearColor(.006,.014,.020,1),X+4,Y,PW-8,PH);DrawRect(FLinearColor(.006,.014,.020,1),X,Y+4,PW,PH-8);
  DrawRect(Face,X+4,Y+4,PW-8,PH-8);
  DrawRect(FLinearColor(.14,.30,.33),X+8,Y+4,PW-16,3);
  DrawRect(FLinearColor(.012,.025,.032),X+8,Y+PH-7,PW-16,3);
 };
 if(P->Delivery){
  if(!P->Delivery->PhoneOpen)VoxelPanel(12,12,FMath::Min(500.f,W-316),96,FLinearColor(.016,.044,.055));
  if(P->Delivery->DeveloperMode)Text(TEXT("DEV / LLUVIA / SOLEADO / CICLO / CARRO"),18,48,FLinearColor(1,.65,.1),.9);
  if(!P->Delivery->PhoneOpen){const float X=W-280;VoxelPanel(X,16,264,104,FLinearColor(.016,.044,.055));
   Text(TEXT("RUTA / BOGOTÁ"),X+16,29,Accent,1.0);
   Text(P->City?P->City->DistrictAt(P->GetActorLocation()):TEXT(""),X+16,54,White,.85);
   Text(FString::Printf(TEXT("$%s  |  %d km/h"),*FText::AsNumber(P->Delivery->Balance).ToString(),int32((P->City&&P->City->Vehicles.IsValidIndex(P->DeveloperCarIndex)?FMath::Abs(P->City->Vehicles[P->DeveloperCarIndex].Velocity):P->GetVelocity().Size2D())*.036f)),X+16,80,White,.9);
  }
  if(!P->Delivery->PhoneOpen)if(auto* PC=Cast<APlayerController>(P->GetController())){
   auto* Tasks=P->Delivery.Get();
   if(Tasks->ActiveOrders.Num()>1){
    const float S=FMath::Clamp(FMath::Min(W/1280.f,H/720.f),.5f,1.f),X=W-310*S-16,Y=130*S;
    VoxelPanel(X,Y,310*S,(42+58*Tasks->ActiveOrders.Num())*S,FLinearColor(.016,.044,.055));
    Text(FString::Printf(TEXT("MIS PEDIDOS  %d"),Tasks->ActiveOrders.Num()),X+12*S,Y+10*S,White,.95f*S);
    for(int32 I=0;I<Tasks->ActiveOrders.Num();I++){
     const auto& Job=Tasks->ActiveOrders[I];const bool Focus=Job.Order.ID==Tasks->Order.ID;
     const EDeliveryState State=Focus?Tasks->State:Job.State;const int32 Count=Focus?Tasks->BasketCount:Job.BasketCount;
     const int32 Total=Job.Order.StoreKind==1?1:3;const bool Collected=State==EDeliveryState::Dropoff;
     const FString Place=(Collected?Job.Order.DropoffName:Job.Order.PickupName).ToString();
     const float RowY=Y+(40+I*58)*S;
     DrawRect(Focus?Accent:Muted,X+12*S,RowY+4*S,6*S,6*S);
     Text(FString::Printf(TEXT("%d  %s%s"),I+1,*Place.Left(27),Place.Len()>27?TEXT("..."):TEXT("")),X+24*S,RowY,Focus?Accent:White,.86f*S);
     const FString Task=Collected?TEXT("Recogido  /  Entregar en casa"):Count>=Total?TEXT("Productos listos  /  Pasar por caja"):FString::Printf(TEXT("Buscar productos  %d/%d  /  Comprar"),Count,Total);
     Text(Task,X+24*S,RowY+22*S,White,.75f*S);
    }
   }
   auto Route=P->Delivery->NavigationRoute();for(int32 I=1;I<Route.Num();I++){FVector A=Route[I-1],B=Route[I];A.Z=B.Z=48;FVector Dir=(B-A).GetSafeNormal2D(),Side(-Dir.Y,Dir.X,0);float Length=FVector::Dist2D(A,B);
    for(float D=180;D<Length;D+=450){FVector Tip=A+Dir*D;if(FVector::Dist2D(Tip,P->GetActorLocation())>7000)continue;FVector2D T,L,R;if(PC->ProjectWorldLocationToScreen(Tip,T)&&PC->ProjectWorldLocationToScreen(Tip-Dir*65+Side*45,L)&&PC->ProjectWorldLocationToScreen(Tip-Dir*65-Side*45,R)){DrawLine(T.X,T.Y,L.X,L.Y,FLinearColor(1,.43,.035),3);DrawLine(T.X,T.Y,R.X,R.Y,FLinearColor(1,.43,.035),3);}}
   }
  }
  if(!P->Delivery->PhoneOpen){
  if(auto* PC=Cast<APlayerController>(P->GetController())){
   auto Badge=[&](FVector World,const FString& Key,const FString& Label){
    if(FVector::Dist2D(World,P->GetActorLocation())>1800)return;
    FVector2D S;if(!PC->ProjectWorldLocationToScreen(World,S)||S.X<40||S.X>W-40||S.Y<40||S.Y>H-155)return;
    VoxelPanel(S.X-20,S.Y-20,40,40,FLinearColor(.035,.10,.12));
    Text(Key,S.X-7,S.Y-12,White,1.4);Text(Label,S.X-100,S.Y+23,White,.8);
   };
   if(!P->Riding&&P->City)for(auto& Bike:P->City->BikeActors)if(Bike.IsValid()&&!Bike->IsHidden())Badge(Bike->GetActorLocation()+FVector(0,0,150),TEXT("F"),TEXT("Subir al vehículo"));
   auto* D=P->Delivery.Get();if(D->State==EDeliveryState::Pickup||D->State==EDeliveryState::Dropoff){
    FString Label=D->State==EDeliveryState::Dropoff?TEXT("Entregar pedido"):D->InsideStore?(D->BasketCount>=(D->Order.StoreKind==1?1:3)?TEXT("Confirmar compra en caja"):TEXT("Mantén E para recoger")):TEXT("Entra por la puerta");
    Badge(D->GetOrderTarget()+FVector(0,0,90),TEXT("E"),Label);
   }
  }
  const float HS=FMath::Clamp(W/1280.f,.8f,1.f),HW=FMath::Min(W-320.f,624.f*HS),HX=W-HW-16,HY=H-100;
  VoxelPanel(HX,HY,HW,84,FLinearColor(.016,.044,.055));
  Text(P->Delivery->NavigationInstruction(),HX+16,HY+12,Accent,.88f*HS);
  Text(TEXT("[TAB] Teléfono   [E] Acción   [F] Subir / bajar"),HX+16,HY+34,White,.85f*HS);
  Text(P->Riding?TEXT("[SHIFT] Impulso   [ESPACIO] Frenar   [ESC] Pausa"):TEXT("[WASD] Mover   [ESPACIO] Saltar   [ESC] Pausa"),HX+16,HY+55,White,.85f*HS);

  }
  if(P->Paused){DrawRect(FLinearColor(.003,.01,.016,.85),0,0,W,H);VoxelPanel(W*.5-180,H*.5-88,360,176,FLinearColor(.016,.044,.055));Text(TEXT("EN PAUSA"),W*.5-116,H*.5-55,Accent,1.8);Text(TEXT("[ESC] Volver a la ciudad"),W*.5-145,H*.5+10,White,1);Text(TEXT("Tu ruta te espera."),W*.5-112,H*.5+40,White,.9);}return;
 }
}
