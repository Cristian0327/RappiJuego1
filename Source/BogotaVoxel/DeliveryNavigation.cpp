#include "DeliverySystem.h"
#include "BogotaGame.h"
TArray<FVector> UDeliveryComponent::NavigationRoute()const{
 TArray<FVector> Route;auto* P=Cast<ABogotaPlayer>(GetOwner());if(!P||!P->City)return Route;
 bool Active=State==EDeliveryState::Pickup||State==EDeliveryState::Dropoff;if(!Active&&!HasWaypoint)return Route;
 FVector Start=P->GetActorLocation(),End=Active?GetOrderTarget():Waypoint;Route.Add(Start);
 if(InsideStore){Route.Add(State==EDeliveryState::Dropoff?InsideStore->GetActorLocation()+FVector(0,-180,0):End);return Route;}
 auto Near=[](const TArray<float>& Roads,float Value){float Best=Roads[0];for(float R:Roads)if(FMath::Abs(R-Value)<FMath::Abs(Best-Value))Best=R;return Best;};
 float SX=Near(P->City->NorthRoads,Start.X),SY=Near(P->City->EastRoads,Start.Y),EX=Near(P->City->NorthRoads,End.X),EY=Near(P->City->EastRoads,End.Y);
 // Route over the street graph, including projections onto the current and destination streets.
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

 return Route;
}
FString UDeliveryComponent::NavigationInstruction()const{
 auto Route=NavigationRoute();if(Route.Num()<2)return TEXT("TAB: abre Pedidos y elige una ruta");
 auto* P=Cast<ABogotaPlayer>(GetOwner());FVector Delta=Route[1]-Route[0];float Distance=Delta.Size2D()/100;
 if(InsideStore&&State==EDeliveryState::Dropoff)return FString::Printf(TEXT("Pedido listo · Sal por la puerta · %.0f m"),Distance);
 if(InsideStore&&State==EDeliveryState::Pickup)return FString::Printf(TEXT("%s · %.0f m"),BasketCount<(Order.StoreKind==1?1:3)?TEXT("Recoge el artículo marcado"):TEXT("Acércate a la caja"),Distance);
 float Angle=FMath::FindDeltaAngleDegrees(P->GetActorRotation().Yaw,Delta.Rotation().Yaw);
 const TCHAR* Turn=FMath::Abs(Angle)>145?TEXT("Da la vuelta"):Angle>35?TEXT("Gira a la derecha"):Angle<-35?TEXT("Gira a la izquierda"):TEXT("Sigue recto");
 float Total=0;for(int32 I=1;I<Route.Num();I++)Total+=FVector::Dist2D(Route[I-1],Route[I]);
 FString Street=TEXT("Destino");
 if(Route.Num()>2){FVector Segment=Route[2]-Route[1];const bool OnCalle=FMath::Abs(Segment.Y)>FMath::Abs(Segment.X);const auto& Roads=OnCalle?P->City->NorthRoads:P->City->EastRoads;float Value=OnCalle?Route[1].X:Route[1].Y;int32 Closest=0;for(int32 I=1;I<Roads.Num();I++)if(FMath::Abs(Roads[I]-Value)<FMath::Abs(Roads[Closest]-Value))Closest=I;Street=OnCalle?FString::Printf(TEXT("Calle %d"),10+Closest*12):FString::Printf(TEXT("Carrera %d"),7+Closest*5);}
 const float Speed=FMath::Max(220.f,P->GetVelocity().Size2D());int32 Minutes=FMath::Max(1,FMath::CeilToInt(Total/Speed/60.f));
 return FString::Printf(TEXT("%s en %.0f m · %s · %.0f m / %d min"),Turn,Distance,*Street,Total/100,Minutes);
}
