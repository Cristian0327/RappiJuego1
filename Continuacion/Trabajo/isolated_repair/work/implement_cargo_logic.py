from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.h');s=p.read_text(encoding='utf-8');s=s.replace('MotoInfinite };','MotoInfinite, Cargo };');pos=s.index('USTRUCT(BlueprintType) struct FDeliveryVehicleSpec')
s=s[:pos]+'''USTRUCT(BlueprintType) struct FActiveDelivery {
 GENERATED_BODY()
 UPROPERTY(BlueprintReadOnly) FDeliveryOrder Order;
 UPROPERTY(BlueprintReadOnly) EDeliveryState State=EDeliveryState::Pickup;
 UPROPERTY(BlueprintReadOnly) int32 BasketCount=0;
 UPROPERTY(BlueprintReadOnly) bool Paid=false;
 UPROPERTY(BlueprintReadOnly) int32 Budget=0;
 UPROPERTY(BlueprintReadOnly) int32 GoodsPaid=0;
};
'''+s[pos:]
s=s.replace('UPROPERTY(BlueprintReadOnly,Category="Delivery") TArray<FDeliveryOrder> Offers;', '''UPROPERTY(BlueprintReadOnly,Category="Delivery") TArray<FDeliveryOrder> Offers;
 UPROPERTY(BlueprintReadOnly,Category="Delivery") TArray<FActiveDelivery> ActiveOrders;
 UPROPERTY(BlueprintReadOnly,Category="Delivery") FGuid SelectedOffer;
 UFUNCTION(BlueprintPure) int32 CargoCapacity(bool Motorcycle) const;
 UFUNCTION(BlueprintCallable) bool SelectActiveOrder(int32 Index);
 const FDeliveryOrder* SelectedIncoming() const;
 void StoreFocusedOrder();
 void RestoreOrderMarkers();''')
s=s.replace('UFUNCTION() void OpenCatalog();','UFUNCTION() void OpenCatalog();\n UFUNCTION() void OpenActiveOrders();\n UFUNCTION() void OpenCargo();');p.write_text(s,encoding='utf-8')
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.cpp');s=p.read_text(encoding='utf-8');a=s.index('bool UDeliveryComponent::SelectOffer(');b=s.index('bool UDeliveryComponent::PaintVehicle',a);s=s[:a]+'''bool UDeliveryComponent::SelectOffer(int32 Index){
 if(!Offers.IsValidIndex(Index)||Offers[Index].ExpiresAt<=GetWorld()->GetTimeSeconds())return false;
 EndAction();SelectedOffer=Offers[Index].ID;
 if(ActiveOrders.IsEmpty()){Order=Offers[Index];State=EDeliveryState::Offered;}
 Changed();return true;
}
'''+s[b:]
s=s.replace('if(State==EDeliveryState::Idle&&!Offers.IsEmpty()){Order=Offers[0];State=EDeliveryState::Offered;}','if(State==EDeliveryState::Idle&&!Offers.IsEmpty()){Order=Offers[0];SelectedOffer=Order.ID;State=EDeliveryState::Offered;}')
s=s.replace('if(Row->Motorcycle){MotoModel=', 'if(ActiveOrders.Num()>CargoCapacity(Row->Motorcycle)){StatusMessage=FText::FromString(TEXT("Entrega pedidos antes de cambiar a un vehículo con menos capacidad."));return false;}\n if(Row->Motorcycle){MotoModel=')
a=s.index('bool UDeliveryComponent::AcceptOffer(');b=s.index('FVector UDeliveryComponent::GetOrderTarget()',a);s=s[:a]+'''bool UDeliveryComponent::AcceptOffer(FGuid ID){
 const auto* Incoming=Offers.FindByPredicate([&](const FDeliveryOrder& O){return O.ID==ID;});
 if(!Incoming||Incoming->ExpiresAt<=GetWorld()->GetTimeSeconds())return false;
 if(InsideStore){StatusMessage=FText::FromString(TEXT("Sal del local antes de aceptar otra ruta."));return false;}
 if(ActiveOrders.Num()>=CargoCapacity(Vehicle==EDeliveryVehicle::Motorcycle)){StatusMessage=FText::FromString(TEXT("Sin espacio. Mejora tus maletas o termina una entrega."));return false;}
 if(ActiveOrders.IsEmpty())if(auto* P=Cast<ABogotaPlayer>(GetOwner()))if(!P->PlaceDeliveryVehicle()){StatusMessage=FText::FromString(TEXT("Busca un espacio libre para sacar tu vehículo."));return false;}
 StoreFocusedOrder();FDeliveryOrder Accepted=*Incoming;DestroyMarkers();Order=Accepted;
 BasketCount=0;OrderPaid=false;OrderBudget=Order.GoodsCost;GoodsPaid=0;State=EDeliveryState::Pickup;
 FActiveDelivery Entry;Entry.Order=Order;Entry.Budget=OrderBudget;ActiveOrders.Add(Entry);
 Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ID==ID;});SelectedOffer.Invalidate();EndAction();
 if(PhoneOpen)TogglePhone();RestoreOrderMarkers();
 StatusMessage=FText::FromString(TEXT("Pedido aceptado. Mis entregas permite elegir qué ruta seguir."));Changed();return true;
}
'''+s[b:]
s=s.replace('if(bHolding)return;','''if(bHolding)return;
 if(!PickupButton&&(State==EDeliveryState::Offered||PhoneOpen))if(const auto* Incoming=SelectedIncoming()){
  if(ActiveOrders.Num()>=CargoCapacity(Vehicle==EDeliveryVehicle::Motorcycle))return;
  bHolding=true;bPickupButton=false;HeldOrder=Incoming->ID;HeldState=EDeliveryState::Offered;HoldStart=GetWorld()->GetTimeSeconds();HoldProgress=0;return;
 }''',1)
s=s.replace('if(ShopCollect())return true;', 'if(ShopCollect()){StoreFocusedOrder();return true;}')
s=s.replace('State=EDeliveryState::Dropoff;EndAction();StatusMessage=', 'State=EDeliveryState::Dropoff;StoreFocusedOrder();EndAction();StatusMessage=')
a=s.index(' const int32 Pay=Order.Reward;');b=s.index('\n}',a);s=s[:a]+''' const int32 Pay=Order.Reward;ActiveOrders.RemoveAll([&](const FActiveDelivery& O){return O.Order.ID==ID;});
 State=EDeliveryState::Idle;Balance+=Pay;DestroyMarkers();EndAction();
 if(ActiveOrders.IsEmpty())EnterIdle();else SelectActiveOrder(0);
 const bool Saved=SaveProfile();StatusMessage=FText::FromString(FString::Printf(TEXT("¡Entrega completada! +$%d · Quedan %d pedidos%s"),Pay,ActiveOrders.Num(),Saved?TEXT(""):TEXT(" · Error al guardar")));Changed();return true;'''+s[b:]
s=s.replace('EndAction();BoostActive=false;Vehicle=Vehicle==','if(ActiveOrders.Num()>CargoCapacity(Vehicle!=EDeliveryVehicle::Motorcycle)){StatusMessage=FText::FromString(TEXT("La cicla no admite las maletas de moto. Termina entregas antes de cambiar."));return false;}\n EndAction();BoostActive=false;Vehicle=Vehicle==')
s=s.replace('if(!Row||Owns(ID)||Row->Price<=0', 'if((ID==TEXT("CargoPanniers")&&!Owns(TEXT("Motorcycle")))||!Row||Owns(ID)||Row->Price<=0')
s=s.replace('EndAction();BoostActive=false;DestroyMarkers();Offers.Empty();EnterIdle();','EndAction();BoostActive=false;DestroyMarkers();ActiveOrders.Empty();Offers.Empty();EnterIdle();')
a=s.index(' if(bHolding){if(State!=HeldState');b=s.index('\n if(bValidation)',a)
s=s[:a]+''' if(bHolding){
  const auto* Incoming=Offers.FindByPredicate([&](const FDeliveryOrder& O){return O.ID==HeldOrder;});
  bool Valid=HeldState==EDeliveryState::Offered?(Incoming&&Incoming->ExpiresAt>GetWorld()->GetTimeSeconds()&&SelectedIncoming()&&SelectedIncoming()->ID==HeldOrder):(State==HeldState&&Order.ID==HeldOrder&&IsAtTarget()&&!PhoneOpen);
  if(!Valid)EndAction();else{HoldProgress=FMath::Clamp((GetWorld()->GetTimeSeconds()-HoldStart)/FMath::Max(.1f,HoldDuration),0.f,1.f);if(HoldProgress>=1){FGuid ID=HeldOrder;auto Old=HeldState;EndAction();if(Old==EDeliveryState::Offered)AcceptOffer(ID);else CollectOrder(ID);}}
 }
'''+s[b:]
s=s.replace('GetRowNames().Num()==10,TEXT("upgrade_table")','GetRowNames().Num()==13,TEXT("upgrade_table")')
p.write_text(s,encoding='utf-8')
