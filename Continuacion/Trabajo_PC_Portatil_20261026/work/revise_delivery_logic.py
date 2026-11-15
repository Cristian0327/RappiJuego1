from pathlib import Path
p=Path(__file__).resolve().parents[1]/'outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.cpp'
s=p.read_text(encoding='utf-8-sig')
s=s.replace('LoadProfile();RebuildStats();Energy=Capacity;EnterIdle();','LoadProfile();RebuildStats();Energy=Capacity;EnterIdle();\n if(!bValidation)GetWorld()->GetTimerManager().SetTimer(NextOfferTimer,this,&UDeliveryComponent::GenerateOffer,1.f,false);')
s=s.replace('if(State!=EDeliveryState::Idle)return;','if(Offers.Num()>=6)return;',1)
a=s.index('const auto Pair=Pairs[FMath::RandHelper(Pairs.Num())]')
b=s.index('\n}\nfloat UDeliveryComponent::OfferSecondsLeft',a)
s=s[:a]+'''while(Offers.Num()<6&&!Pairs.IsEmpty()){
 const int32 PairIndex=FMath::RandHelper(Pairs.Num());const auto Pair=Pairs[PairIndex];Pairs.RemoveAtSwap(PairIndex);
 FDeliveryOrder New;New.ID=FGuid::NewGuid();New.Pickup=Points[Pair.X].P;New.Dropoff=Points[Pair.Y].P;New.PickupName=FText::FromString(Points[Pair.X].Name);New.DropoffName=FText::FromString(Points[Pair.Y].Name);New.DistanceMeters=FVector::Dist2D(New.Pickup,New.Dropoff)/100;
 New.Reward=CalculatePay(New.DistanceMeters,Advanced?.9f:Owns(TEXT("BikeFrame"))?.95f:1.f);New.ExpiresAt=GetWorld()->GetTimeSeconds()+OfferLifetime+FMath::RandRange(0.f,8.f);Offers.Add(New);
 }
 if(State==EDeliveryState::Idle&&!Offers.IsEmpty()){Order=Offers[0];State=EDeliveryState::Offered;}
 StatusMessage=FText::FromString(TEXT("Hay pedidos cerca. Abre la app para elegir tu ruta."));Changed();'''+s[b:]
s=s.replace('void UDeliveryComponent::ExpireOffer(){if(State==EDeliveryState::Offered){StatusMessage=FText::FromString(TEXT("Oferta vencida. Próxima oferta en 3 minutos."));EnterIdle();}}','void UDeliveryComponent::ExpireOffer(){if(State==EDeliveryState::Offered){Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ID==Order.ID;});StatusMessage=FText::FromString(TEXT("Oferta vencida. Consulta las otras rutas."));EnterIdle();}}')
s=s.replace('StatusMessage=FText::FromString(TEXT("Pedido ignorado."));EnterIdle();','Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ID==Order.ID;});StatusMessage=FText::FromString(TEXT("Pedido ignorado. Puedes elegir otro."));EnterIdle();')
s=s.replace('State=EDeliveryState::Pickup;EndAction();','Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ID==ID;});State=EDeliveryState::Pickup;EndAction();',1)
s=s.replace('||PhoneOpen||GetOwner()->GetVelocity().Size2D()>100','||GetOwner()->GetVelocity().Size2D()>100')
s=s.replace('S->Vehicle=Vehicle;bool OK','S->Vehicle=Vehicle;S->BikeColor=BikeColor;S->MotoColor=MotoColor;bool OK')
s=s.replace('Balance=FMath::Max(0,S->Balance);','Balance=FMath::Max(0,S->Balance);BikeColor=FMath::Clamp(S->BikeColor,0,5);MotoColor=FMath::Clamp(S->MotoColor,0,5);')
s=s.replace('Super::TickComponent(Dt,Tick,Fn);UpdateBoost(Dt);','''Super::TickComponent(Dt,Tick,Fn);UpdateBoost(Dt);
 if(!bValidation){
 const float Now=GetWorld()->GetTimeSeconds();Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ExpiresAt<=Now;});
 if(State==EDeliveryState::Offered&&Order.ExpiresAt<=Now){EndAction();State=EDeliveryState::Idle;}
 if(State==EDeliveryState::Idle&&!Offers.IsEmpty()){Order=Offers[0];State=EDeliveryState::Offered;Changed();}
 static_cast<void>(Now);
 if(!GetWorld()->GetTimerManager().IsTimerActive(NextOfferTimer))GetWorld()->GetTimerManager().SetTimer(NextOfferTimer,this,&UDeliveryComponent::GenerateOffer,FMath::Max(2.f,OfferInterval),false);
 }
 if(auto* Rider=Cast<ABogotaPlayer>(GetOwner()))Rider->RefreshVehicleArt();''')
pos=s.index('\nfloat UDeliveryComponent::OfferSecondsLeft')
s=s[:pos]+'''
bool UDeliveryComponent::SelectOffer(int32 Index){
 if((State!=EDeliveryState::Idle&&State!=EDeliveryState::Offered)||!Offers.IsValidIndex(Index)||Offers[Index].ExpiresAt<=GetWorld()->GetTimeSeconds())return false;
 EndAction();Order=Offers[Index];State=EDeliveryState::Offered;Changed();return true;
}
bool UDeliveryComponent::PaintVehicle(bool Moto,int32 Color){
 if(Color<0||Color>5||(Moto&&!Owns(TEXT("Motorcycle"))))return false;
 int32& Current=Moto?MotoColor:BikeColor;if(Current==Color)return true;
 if(Balance<2000){StatusMessage=FText::FromString(TEXT("Pintura: necesitas $2.000."));return false;}
 Balance-=2000;Current=Color;SaveProfile();Changed();return true;
}
'''+s[pos:]
# Make lifetime exactly 30 seconds for each independent offer.
s=s.replace('OfferLifetime+FMath::RandRange(0.f,8.f)','OfferLifetime')
p.write_text(s,encoding='utf-8')
