from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliverySystem.cpp');s=p.read_text(encoding='utf-8-sig');a=s.index('void UDeliveryComponent::GenerateOffer(){');b=s.index('bool UDeliveryComponent::SelectOffer_Implementation',a)
s=s[:a]+'''TArray<FDeliveryOrder> UDeliveryComponent::GetAvailableResidentialRoutes()const{
 TArray<FDeliveryOrder> Routes;auto* P=Cast<ABogotaPlayer>(GetOwner());if(!P||!P->City)return Routes;
 TArray<ADeliveryPoint*> Shops;for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It)Shops.Add(*It);
 TArray<FVector> Homes;FCollisionQueryParams Params;Params.AddIgnoredActor(P);
 for(const auto& Building:P->City->MapFootprints){
  if(Building.Extent.X>4500||Building.Extent.Y>4500)continue;
  FVector Door=Building.Center+FVector(0,-Building.Extent.Y-150,0);bool Commercial=false;
  for(auto* Shop:Shops){FVector Local=Door-Shop->GetActorLocation();if(FMath::Abs(Local.X)<Shop->HalfWidth+180&&Local.Y>-180&&Local.Y<Shop->HalfDepth*2+180){Commercial=true;break;}}
  if(Commercial)continue;FHitResult Floor;
  if(!GetWorld()->LineTraceSingleByChannel(Floor,Door+FVector(0,0,500),Door-FVector(0,0,500),ECC_Visibility,Params)||Floor.ImpactNormal.Z<.8f)continue;
  Door.Z=Floor.ImpactPoint.Z+5;if(GetWorld()->OverlapBlockingTestByChannel(Door+FVector(0,0,95),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(70,88),Params))continue;
  if(!Homes.ContainsByPredicate([&](const FVector& H){return FVector::Dist2D(H,Door)<200;}))Homes.Add(Door);
 }
 const TCHAR* Customers[]={TEXT("Valeria"),TEXT("Don Luis"),TEXT("Camila"),TEXT("Andrea"),TEXT("Marta"),TEXT("Nicolas"),TEXT("Sara"),TEXT("Don Pedro")};
 for(auto* Shop:Shops){FVector Pickup=Shop->GetActorLocation();FHitResult Floor;
  if(!GetWorld()->LineTraceSingleByChannel(Floor,Pickup+FVector(0,0,500),Pickup-FVector(0,0,500),ECC_Visibility,Params))continue;
  Pickup.Z=Floor.ImpactPoint.Z+5;if(GetWorld()->OverlapBlockingTestByChannel(Pickup+FVector(0,0,95),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(70,88),Params))continue;
  for(int32 I=0;I<Homes.Num();I++){FDeliveryOrder Route;Route.StoreID=Shop->PointID;Route.Grocery=Shop->Grocery;Route.StoreKind=Shop->StoreKind;Route.GoodsCost=Shop->PurchaseBudget;Route.Pickup=Pickup;Route.Dropoff=Homes[I];Route.PickupName=Shop->PlaceName;Route.DropoffName=FText::FromString(FString::Printf(TEXT("Casa de %s - %s"),Customers[I%8],*P->City->DistrictAt(Homes[I])));Route.DistanceMeters=FVector::Dist2D(Pickup,Homes[I])/100;Routes.Add(Route);}
 }
 return Routes;
}
bool UDeliveryComponent::RouteAlreadyOffered(FVector Pickup,FVector Dropoff)const{
 for(const auto& O:Offers)if(O.Pickup.Equals(Pickup,1)&&O.Dropoff.Equals(Dropoff,1))return true;
 for(const auto& O:ActiveOrders)if(O.Order.Pickup.Equals(Pickup,1)&&O.Order.Dropoff.Equals(Dropoff,1))return true;
 return false;
}
void UDeliveryComponent::GenerateOffer_Implementation(){
 if(Offers.Num()>=6)return;auto Routes=GetAvailableResidentialRoutes();const bool Advanced=Owns(TEXT("BikeMotor"))||Owns(TEXT("Motorcycle"));const float Min=Advanced?350:100,Max=Owns(TEXT("BikeFrame"))?900:450;
 while(Offers.Num()<6&&!Routes.IsEmpty()){int32 I=FMath::RandHelper(Routes.Num());auto O=Routes[I];Routes.RemoveAtSwap(I);if(O.DistanceMeters<Min||O.DistanceMeters>Max||RouteAlreadyOffered(O.Pickup,O.Dropoff))continue;O.ID=FGuid::NewGuid();O.Reward=RewardForDistance(O.DistanceMeters,Advanced?.9f:Owns(TEXT("BikeFrame"))?.95f:1.f);O.ExpiresAt=GetWorld()->GetTimeSeconds()+OfferLifetime;Offers.Add(O);}
 if(State==EDeliveryState::Idle&&!Offers.IsEmpty())SelectOffer(0);Changed();
}
''' +s[b:];s=s.replace('const bool Saved=SaveProfile();StatusMessage=', 'const bool Saved=SaveProfile();GenerateOffer();StatusMessage=');p.write_text(s,encoding='utf-8')
