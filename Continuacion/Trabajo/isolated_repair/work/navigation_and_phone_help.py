from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryNavigation.cpp');s=p.read_text(encoding='utf-8');a=s.index(' FVector A=');b=s.index('\n return Route;',a);s=s[:a]+''' // Route over the street graph, including projections onto the current and destination streets.
 TArray<FVector> Nodes;Nodes.Add(FVector(Start.X,Start.Y,0));Nodes.Add(FVector(End.X,End.Y,0));
 for(float X:P->City->NorthRoads)for(float Y:P->City->EastRoads)Nodes.Add(FVector(X,Y,0));
 const int32 SA=Nodes.Add(FVector(SX,Start.Y,0)),SB=Nodes.Add(FVector(Start.X,SY,0)),EA=Nodes.Add(FVector(EX,End.Y,0)),EB=Nodes.Add(FVector(End.X,EY,0));
 TArray<float> Cost;Cost.Init(FLT_MAX,Nodes.Num());Cost[0]=0;TArray<int32> Previous;Previous.Init(-1,Nodes.Num());TSet<int32> Done;
 auto Road=[&](float V,const TArray<float>& Values){return Values.ContainsByPredicate([&](float R){return FMath::IsNearlyEqual(R,V,1.f);});};
 for(int32 Step=0;Step<Nodes.Num();Step++){
  int32 A=-1;for(int32 I=0;I<Nodes.Num();I++)if(!Done.Contains(I)&&(A<0||Cost[I]<Cost[A]))A=I;if(A<0||Cost[A]==FLT_MAX||A==1)break;Done.Add(A);
  for(int32 B=0;B<Nodes.Num();B++){if(B==A||Done.Contains(B))continue;
   bool Link=(A==0&&(B==SA||B==SB))||(B==1&&(A==EA||A==EB));
   if(A>1&&B>1)Link=(FMath::IsNearlyEqual(Nodes[A].X,Nodes[B].X,1.)&&Road(Nodes[A].X,P->City->NorthRoads))||(FMath::IsNearlyEqual(Nodes[A].Y,Nodes[B].Y,1.)&&Road(Nodes[A].Y,P->City->EastRoads));
   if(Link){float C=Cost[A]+FVector::Dist2D(Nodes[A],Nodes[B]);if(C<Cost[B]){Cost[B]=C;Previous[B]=A;}}
  }
 }
 Route.Empty();for(int32 I=1;I>=0;I=Previous[I]){Route.Insert(Nodes[I],0);if(I==0)break;}
 for(int32 I=Route.Num()-2;I>=0;I--)if(FVector::Dist2D(Route[I],Route[I+1])<80)Route.RemoveAt(I+1);
'''+s[b:];p.write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/BogotaHUD.cpp');s=p.read_text(encoding='utf-8');s=s.replace('#include "Kismet/GameplayStatics.h"','#include "Kismet/GameplayStatics.h"\n#include "GameFramework/PlayerController.h"');pos=s.index('  const float HS=');s=s[:pos]+'''  if(!P->Delivery->PhoneOpen)if(auto* PC=Cast<APlayerController>(P->GetController())){
   auto Route=P->Delivery->NavigationRoute();for(int32 I=1;I<Route.Num();I++){FVector A=Route[I-1],B=Route[I];A.Z=B.Z=48;FVector Dir=(B-A).GetSafeNormal2D(),Side(-Dir.Y,Dir.X,0);float Length=FVector::Dist2D(A,B);
    for(float D=180;D<Length;D+=450){FVector Tip=A+Dir*D;if(FVector::Dist2D(Tip,P->GetActorLocation())>7000)continue;FVector2D T,L,R;if(PC->ProjectWorldLocationToScreen(Tip,T)&&PC->ProjectWorldLocationToScreen(Tip-Dir*65+Side*45,L)&&PC->ProjectWorldLocationToScreen(Tip-Dir*65-Side*45,R)){DrawLine(T.X,T.Y,L.X,L.Y,FLinearColor(1,.43,.035),3);DrawLine(T.X,T.Y,R.X,R.Y,FLinearColor(1,.43,.035),3);}}
   }
  }
  if(!P->Delivery->PhoneOpen){
'''+s[pos:];s=s.replace('  if(P->Paused){DrawRect','  }\n  if(P->Paused){DrawRect',1);p.write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.h');s=p.read_text(encoding='utf-8').replace('UPROPERTY() UTextBlock* Notice=nullptr;', 'UPROPERTY() UTextBlock* Notice=nullptr;\n UPROPERTY() UTextBlock* PhoneHints=nullptr;');p.write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp');s=p.read_text(encoding='utf-8');pos=s.index(' EnergyText=WidgetTree->');s=s[:pos]+''' PhoneHints=WidgetTree->ConstructWidget<UTextBlock>();PhoneHints->SetColorAndOpacity(Paper);PhoneHints->SetAutoWrapText(true);auto HintFont=PhoneHints->GetFont();HintFont.Size=11;PhoneHints->SetFont(HintFont);PhoneHints->SetJustification(ETextJustify::Center);PhoneHints->SetText(FText::FromString(TEXT("E / A / X: aceptar · Cruceta: elegir · TAB / Select: cerrar\\n1 Mapa · 2 Pedidos · 3 Taller · 4 Entregas · 5 Maletas")));auto* HintSlot=Root->AddChildToCanvas(PhoneHints);HintSlot->SetAnchors(FAnchors(0,1,1,1));HintSlot->SetOffsets(FMargin(12,-62,12,58));HintSlot->SetZOrder(99);
'''+s[pos:];s=s.replace('(View.Y-48)/680.f','(View.Y-114)/680.f');s=s.replace('(View-FVector2D(420*Scale,680*Scale))*.5','(View-FVector2D(420*Scale,680*Scale+64))*.5');s=s.replace('PhoneShade->SetVisibility(Open?', 'PhoneHints->SetVisibility(Open?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);PhoneShade->SetVisibility(Open?');s=s.replace('if(K==EKeys::One)', 'if(K==EKeys::Four){OpenActiveOrders();return FReply::Handled();}if(K==EKeys::Five){OpenCargo();return FReply::Handled();}\n if(K==EKeys::One)');p.write_text(s,encoding='utf-8')
