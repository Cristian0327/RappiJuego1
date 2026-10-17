#include "DeliverySystem.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"


const FDeliveryOrder* UDeliveryComponent::SelectedIncoming()const{
 if(const auto* O=Offers.FindByPredicate([&](const FDeliveryOrder& V){return V.ID==SelectedOffer;}))return O;
 return nullptr;
}


void UDeliveryComponent::RestoreOrderMarkers(){
 if(State==EDeliveryState::Pickup){
  if(auto* Shop=OrderStore())Shop->PresentOrder(Order.ID,BasketCount);
  auto* Mark=GetWorld()->SpawnActor<AStaticMeshActor>(GetOrderTarget()+FVector(0,0,130),FRotator::ZeroRotator);
  if(Mark){Mark->SetMobility(EComponentMobility::Movable);auto* Mesh=Mark->GetStaticMeshComponent();Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));Mesh->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/World/M_Teal.M_Teal")));Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Mark->SetActorScale3D(FVector(.18,.18,.28));PickupMarker=Mark;}
 }else if(State==EDeliveryState::Dropoff){
  FActorSpawnParameters Params;Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
  Recipient=GetWorld()->SpawnActor<ADeliveryRecipient>(RecipientClass,Order.Dropoff,FRotator(0,180,0),Params);
  if(Recipient){Recipient->OrderID=Order.ID;Recipient->Delivery=this;const FName Roles[]={TEXT("CustomerStudent"),TEXT("CustomerOffice"),TEXT("CustomerNeighbor")};Recipient->InitializeAppearance(Roles[Order.ID.A%3]);}
 }
}
