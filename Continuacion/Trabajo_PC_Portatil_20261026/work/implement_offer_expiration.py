from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.cpp');s=p.read_text(encoding='utf-8-sig');s=s.replace('void UDeliveryComponent::GenerateOffer_Implementation(){\n if(Offers.Num()', 'void UDeliveryComponent::GenerateOffer_Implementation(){\n CullExpiredOffers();if(Offers.Num()');needle='bool UDeliveryComponent::RouteAlreadyOffered';i=s.index(needle);s=s[:i]+'''void UDeliveryComponent::CullExpiredOffers_Implementation(){
 const float Now=GetWorld()->GetTimeSeconds();Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ExpiresAt<=Now;});
 if(State==EDeliveryState::Offered&&Order.ExpiresAt<=Now){EndAction();SelectedOffer.Invalidate();State=EDeliveryState::Idle;}
}
'''+s[i:];s=s.replace('Offers.RemoveAll([&](const FDeliveryOrder& O){return O.ExpiresAt<=Now;});\n if(State==EDeliveryState::Offered&&Order.ExpiresAt<=Now){EndAction();State=EDeliveryState::Idle;}', 'CullExpiredOffers();');p.write_text(s,encoding='utf-8')
p=Path('work/migrate_residential_market_blueprint.py');s=p.read_text(encoding='utf-8-sig').replace("g.exec('entry','Room')", "g.call('ExpireOld','CullExpiredOffers');g.exec('entry','ExpireOld');g.exec('ExpireOld','Room')");p.write_text(s,encoding='utf-8')
