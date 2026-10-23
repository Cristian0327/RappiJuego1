from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.cpp');s=p.read_text(encoding='utf-8');s=s.replace('Order.ExpiresAt=GetWorld()->GetTimeSeconds()-.1f;Check(', 'Order.ExpiresAt=GetWorld()->GetTimeSeconds()-.1f;for(auto& O:Offers)if(O.ID==Order.ID)O.ExpiresAt=Order.ExpiresAt;Check(');s=s.replace('Offers.Empty();State=EDeliveryState::Idle;GenerateOffer();Check(Offers.Num()==6', 'DestroyMarkers();ActiveOrders.Empty();Offers.Empty();State=EDeliveryState::Idle;GenerateOffer();Check(Offers.Num()==6')
pos=s.index(' }else if(ValidationStage==28&&ValidationTime>1.2){');s=s[:pos]+''' }else if(ValidationStage==28&&ValidationTime>1.2){
  ExitStore();DestroyMarkers();ActiveOrders.Empty();State=EDeliveryState::Idle;Offers.Empty();P->SetActorLocation(FVector(-6500,14000,130));P->GetCharacterMovement()->StopMovementImmediately();Balance=5000000;
  Check(CargoCapacity(false)==1&&CargoCapacity(true)==1,TEXT("base_one_order_capacity"));Check(PurchaseUpgrade(TEXT("CargoBackpack"))&&CargoCapacity(false)==2,TEXT("backpack_adds_order_slot"));
  GenerateOffer();Check(AcceptOffer(Offers[0].ID),TEXT("accept_first_batch_order"));FGuid First=Order.ID;int32 BudgetOne=OrderBudget;
  Check(SelectOffer(0)&&AcceptOffer(Offers[0].ID),TEXT("accept_second_batch_order"));FGuid Second=Order.ID;Check(ActiveOrders.Num()==2&&Order.ID!=First,TEXT("two_independent_order_ids"));Check(!AcceptOffer(Offers[0].ID),TEXT("reject_order_when_capacity_full"));
  BasketCount=1;StoreFocusedOrder();Check(SelectActiveOrder(0)&&Order.ID==First&&BasketCount==0&&OrderBudget==BudgetOne,TEXT("switch_preserves_separate_budgets"));Check(SelectActiveOrder(1)&&Order.ID==Second&&BasketCount==1,TEXT("switch_preserves_partial_basket"));
  Check(PurchaseUpgrade(TEXT("CargoWaist"))&&CargoCapacity(false)==3,TEXT("waist_adds_third_slot"));Check(PurchaseUpgrade(TEXT("CargoPanniers"))&&CargoCapacity(true)==5&&CargoCapacity(false)==3,TEXT("panniers_moto_only"));Vehicle=EDeliveryVehicle::Motorcycle;
  for(int32 I=0;I<3;I++)Check(AcceptOffer(Offers[0].ID),TEXT("fill_moto_cargo_slots"));Check(ActiveOrders.Num()==5&&!AcceptOffer(Offers[0].ID),TEXT("moto_limit_five"));Check(!SwitchVehicle()&&!EquipVehicle(TEXT("BikeCity")),TEXT("cannot_switch_to_overloaded_bicycle"));
  // Complete every independently accepted order through collection, checkout and handover.
  int32 ExpectedWallet=Balance;while(!ActiveOrders.IsEmpty()){
   SelectActiveOrder(0);auto* Shop=OrderStore();Check(Shop!=nullptr,TEXT("batch_store_exists"));if(!Shop)break;InsideStore=Shop;
   for(int32 I=BasketCount;I<Shop->ItemCount();I++){P->SetActorLocation(Shop->ProductPosition(I)+FVector(0,-80,0));Check(CollectOrder(Order.ID),TEXT("batch_collect_independent_products"));}
   P->SetActorLocation(Shop->CheckoutPosition()+FVector(0,0,90));Check(CollectOrder(Order.ID)&&OrderBudget==0&&OrderPaid,TEXT("batch_checkout_independent_budget"));
   ExitStore();FGuid Done=Order.ID;ExpectedWallet+=Order.Reward;int32 Remaining=ActiveOrders.Num()-1;P->SetActorLocation(Order.Dropoff+FVector(0,0,95));Check(CompleteOrder(Done)&&Balance==ExpectedWallet&&ActiveOrders.Num()==Remaining,TEXT("batch_delivery_pays_only_its_reward"));Check(!CompleteOrder(Done),TEXT("batch_duplicate_delivery_rejected"));if(Remaining)Check(State==EDeliveryState::Pickup||State==EDeliveryState::Dropoff,TEXT("batch_keeps_other_orders_active"));
  }
  Check(ActiveOrders.IsEmpty()&&!P->Riding,TEXT("last_batch_delivery_removes_vehicle"));P->RefreshVehicleArt();Check(P->CargoBackpack&&P->CargoBackpack->GetSkeletalMeshAsset()&&P->CargoWaist&&P->CargoWaist->GetSkeletalMeshAsset()&&P->CargoPanniers&&P->CargoPanniers->GetStaticMesh(),TEXT("cargo_models_loaded"));Check(P->JumpClip&&P->Walk&&P->Walk->GetName()==TEXT("AN_MixamoWalk"),TEXT("main_mixamo_walk_jump_loaded"));
  SaveProfile();auto* SavedCargo=Cast<UDeliverySave>(UGameplayStatics::LoadGameFromSlot(TEXT("VoxelDelivery_Automation"),0));Check(SavedCargo&&SavedCargo->Purchased.Contains(TEXT("CargoPanniers")),TEXT("cargo_upgrades_saved"));
  TogglePhone();if(auto* UI=Cast<UDeliveryPhoneWidget>(PhoneWidget))UI->OpenCargo();CaptureUI(TEXT("CargoShop.png"));ValidationStage++;ValidationTime=0;
 }else if(ValidationStage==29&&ValidationTime>1.2){
'''+s[pos+len(' }else if(ValidationStage==28&&ValidationTime>1.2){'):];p.write_text(s,encoding='utf-8')
