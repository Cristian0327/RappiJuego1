from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];src=root/'outputs/BogotaVoxel/Source/BogotaVoxel'
for name in ['DeliverySystem.cpp','DeliveryCargo.cpp','DeliveryUI.cpp']:
 target=root/'work/Backups/CityVisuals_20261014'/name
 if not target.exists():shutil.copy2(src/name,target)
p=src/'DeliverySystem.cpp';s=p.read_text()
s=s.replace('State=EDeliveryState::Idle;Order=FDeliveryOrder();EndAction();','State=EDeliveryState::Idle;Order=FDeliveryOrder();SelectedOffer.Invalidate();EndAction();')
s=s.replace(' if(State==EDeliveryState::Idle&&!Offers.IsEmpty())SelectOffer(0);\n','')
s=s.replace(' if(State==EDeliveryState::Idle&&!Offers.IsEmpty())SelectOffer(0);Changed();',' Changed();')
s=s.replace('GenerateOffer();AcceptOffer(Order.ID);','GenerateOffer();SelectOffer(0);AcceptOffer(Order.ID);')
s=s.replace('GenerateOffer();Order.ExpiresAt=', 'GenerateOffer();SelectOffer(0);Order.ExpiresAt=')
s=s.replace('Check(ActiveOrders.IsEmpty()&&State==EDeliveryState::Offered&&Balance==Expected,TEXT("delivery_pays"))','Check(ActiveOrders.IsEmpty()&&State==EDeliveryState::Idle&&Balance==Expected,TEXT("delivery_pays"))')
s=s.replace('GenerateOffer();Check(State==EDeliveryState::Offered,TEXT("offer_generation"));', '''GenerateOffer();Check(State==EDeliveryState::Idle,TEXT("offer_generation_waits_for_selection"));
  BeginAction();Check(!bHolding&&!SelectedIncoming(),TEXT("holding_action_without_selection_does_not_accept"));HoldStart=GetWorld()->GetTimeSeconds()-HoldDuration-1;AdvanceHeldAction();Check(ActiveOrders.IsEmpty(),TEXT("unselected_hold_cannot_create_order"));
  UpdateMarketplace(OfferInterval+1);BeginAction();AdvanceHeldAction();Check(!bHolding&&ActiveOrders.IsEmpty()&&!SelectedIncoming(),TEXT("market_refresh_does_not_select_or_accept"));Check(SelectOffer(0),TEXT("explicit_first_offer_selection"));''')
p.write_text(s)
p=src/'DeliveryCargo.cpp';s=p.read_text()
s=s.replace(' if(State==EDeliveryState::Offered)return Offers.FindByPredicate([&](const FDeliveryOrder& V){return V.ID==Order.ID;});\n','')
p.write_text(s)
p=src/'DeliveryUI.cpp';s=p.read_text(encoding='utf-8-sig').replace('else T=TEXT("Buscando nuevas rutas por el barrio…");','else T=Delivery->Offers.IsEmpty()?TEXT("Buscando nuevas rutas por el barrio…"):TEXT("Selecciona una ruta antes de aceptar el pedido.");')
p.write_text(s,encoding='utf-8')
p=root/'work/migrate_lifecycle_blueprints.py';s=p.read_text()
s=s.replace("g.setter('ClearOrder','Order','EmptyOrder','DeliveryOrder');g.call('CancelHold','EndAction')", "g.setter('ClearOrder','Order','EmptyOrder','DeliveryOrder');g.get('SelectedOffer');g.call('ClearSelection','Invalidate_Guid',G);g.link('SelectedOffer','SelectedOffer','ClearSelection','InGuid');g.call('CancelHold','EndAction')")
s=s.replace("'ClearOrder','CancelHold'", "'ClearOrder','ClearSelection','CancelHold'")
start=s.index("g.call('IsIdle','EqualEqual_ByteByte'")
end=s.index("g.call('SafeDelta'",start)
s=s[:start]+"g.call('Count','Array_Length',A);g.link('Offers','Offers','Count','TargetArray')\n"+s[end:]
s=s.replace("g.exec('Select','AdvanceClock');g.exec('Preview','AdvanceClock','else')","g.exec('Expire','AdvanceClock')")
p.write_text(s)
p=root/'work/migrate_residential_market_blueprint.py';s=p.read_text()
start=s.index("g.call('Idle','EqualEqual_ByteByte'")
end=s.index("report=g.build('GenerateOffer')",start)
s=s[:start]+"g.call('Notify','Changed');g.link('Loop','Completed','Notify','execute');g.exec('Notify','result');"+s[end:]
p.write_text(s)
