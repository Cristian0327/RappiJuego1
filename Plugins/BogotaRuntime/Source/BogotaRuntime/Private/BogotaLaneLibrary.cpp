#include "GameFramework/Character.h"
#include "ProfilingDebugging/CsvProfiler.h"
#include "BogotaLaneLibrary.h"
#include "Components/SplineComponent.h"
#include "Modules/ModuleManager.h"
#include "Algo/Sort.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Kismet/GameplayStatics.h"
namespace {
struct FActorQueryCache {
 uint64 Frame=MAX_uint64;
 FDelegateHandle Spawned,Destroyed;
 TMap<TWeakObjectPtr<UClass>,TArray<TWeakObjectPtr<AActor>>> Entries;
};
TMap<TWeakObjectPtr<UWorld>,FActorQueryCache> ActorQueries;
void ClearActorQueries() {
 for(auto& Pair:ActorQueries) if(auto* World=Pair.Key.Get()) {
  World->RemoveOnActorSpawnedHandler(Pair.Value.Spawned);
  World->RemoveOnActorDestroyedHandler(Pair.Value.Destroyed);
 }
 ActorQueries.Empty();
}
}
namespace {
struct FNode { FBox Bounds{ForceInit}; int32 Left=-1,Right=-1,Begin=0,End=0; };
struct FIndex {
 TArray<FNode> Nodes;
 TArray<FBox> Boxes;
 TArray<int32> Order;
 TMap<FVector,float> ExactKeys;
 FDelegateHandle Changed,Updated;
 bool Dirty=true;
 int32 Build(int32 Begin,int32 End) {
  const int32 Id=Nodes.AddDefaulted();
  FBox Bounds(ForceInit); for(int32 I=Begin;I<End;++I) Bounds+=Boxes[Order[I]];
  Nodes[Id].Bounds=Bounds; Nodes[Id].Begin=Begin; Nodes[Id].End=End;
  if(End-Begin>8) {
   const FVector Extent=Bounds.GetSize(); const int32 Axis=Extent.X>Extent.Y?(Extent.X>Extent.Z?0:2):(Extent.Y>Extent.Z?1:2);
   MakeArrayView(Order.GetData()+Begin,End-Begin).Sort([&](int32 A,int32 B){return Boxes[A].GetCenter()[Axis]<Boxes[B].GetCenter()[Axis];});
   const int32 Mid=(Begin+End)/2;
   const int32 L=Build(Begin,Mid),R=Build(Mid,End); Nodes[Id].Left=L; Nodes[Id].Right=R;
  }
  return Id;
 }
 void Rebuild(const FInterpCurveVector& Curve) {
  Nodes.Reset(); Boxes.Reset(); Order.Reset(); ExactKeys.Reset();
  const int32 N=Curve.Points.Num(), Count=Curve.bIsLooped?N:N-1;
  for(int32 I=0;I<Count;++I) {
   const int32 J=(I+1)%N; const auto& A=Curve.Points[I]; const auto& B=Curve.Points[J];
   const float Dt=J==0?Curve.LoopKeyOffset:B.InVal-A.InVal;
   FBox Box(ForceInit); Box+=A.OutVal; Box+=B.OutVal;
   if(A.InterpMode!=CIM_Linear && A.InterpMode!=CIM_Constant) {
    Box+=A.OutVal+A.LeaveTangent*(Dt/3.0f); Box+=B.OutVal-B.ArriveTangent*(Dt/3.0f);
   }
   Boxes.Add(Box.ExpandBy(0.1)); Order.Add(I);
  }
  if(Count>0) Build(0,Count); Dirty=false;
 }
};
TMap<TWeakObjectPtr<USplineComponent>,TSharedPtr<FIndex>> LaneIndices;
void ClearIndices() {
 for(auto& Pair:LaneIndices) if(auto* S=Pair.Key.Get()) {
  S->GetOnSplineChanged().Remove(Pair.Value->Changed);
  S->GetOnSplineUpdated().Remove(Pair.Value->Updated);
 }
 LaneIndices.Empty();
}
float Query(USplineComponent* Route,const FVector& Position) {
 if(!IsValid(Route)) return 0.f;
 if(!IsInGameThread()) return Route->FindInputKeyClosestToWorldLocation(Position);
 auto& Ptr=LaneIndices.FindOrAdd(Route);
 if(!Ptr) {
  Ptr=MakeShared<FIndex>(); TWeakPtr<FIndex> Weak=Ptr;
  auto Invalidate=[Weak](){if(auto P=Weak.Pin()) P->Dirty=true;};
  Ptr->Changed=Route->GetOnSplineChanged().AddLambda(Invalidate);
  Ptr->Updated=Route->GetOnSplineUpdated().AddLambda(Invalidate);
  for(auto It=LaneIndices.CreateIterator();It;++It) if(!It.Key().IsValid()) It.RemoveCurrent();
 }
 FIndex& Index=*Ptr;
 const auto& Curve=static_cast<const USplineComponent*>(Route)->GetSplinePointsPosition();
 if(Index.Dirty) Index.Rebuild(Curve);
 if(Index.Nodes.IsEmpty()) return Route->FindInputKeyClosestToWorldLocation(Position);
 const FVector Local=Route->GetComponentTransform().InverseTransformPosition(Position);
 if(const float* Cached=Index.ExactKeys.Find(Local)) return *Cached;
 float BestDistance=0.f; float BestKey=Curve.FindNearestOnSegment(Local,0,BestDistance); int32 BestSegment=0;
 TArray<int32,TInlineAllocator<64>> Stack; Stack.Add(0);
 while(!Stack.IsEmpty()) {
  const FNode& Node=Index.Nodes[Stack.Pop(EAllowShrinking::No)];
  // Float conversion mirrors the engine's distance comparison, retaining equal-distance candidates.
  if(static_cast<float>(Node.Bounds.ComputeSquaredDistanceToPoint(Local))>BestDistance) continue;
  if(Node.Left<0) {
   for(int32 I=Node.Begin;I<Node.End;++I) {
    const int32 Segment=Index.Order[I]; if(Segment==0) continue;
    float Distance; const float Key=Curve.FindNearestOnSegment(Local,Segment,Distance);
    if(Distance<BestDistance || (Distance==BestDistance && Segment<BestSegment)) {BestDistance=Distance; BestKey=Key; BestSegment=Segment;}
   }
  } else {
   const double L=Index.Nodes[Node.Left].Bounds.ComputeSquaredDistanceToPoint(Local),R=Index.Nodes[Node.Right].Bounds.ComputeSquaredDistanceToPoint(Local);
   Stack.Add(L<R?Node.Right:Node.Left); Stack.Add(L<R?Node.Left:Node.Right);
  }
 }
 if(Index.ExactKeys.Num()>=1024) Index.ExactKeys.Reset();
 Index.ExactKeys.Add(Local,BestKey); return BestKey;
}
}
float UBogotaLaneLibrary::ClosestInputKey(USplineComponent* Route,FVector Position) { return Query(Route,Position); }
float UBogotaLaneLibrary::ClosestDistance(USplineComponent* Route,FVector Position) { return IsValid(Route)?Route->GetDistanceAlongSplineAtSplineInputKey(Query(Route,Position)):0.f; }
class FBogotaRuntimeModule : public IModuleInterface { public: virtual void ShutdownModule() override { ClearActorQueries(); ClearIndices(); } };
IMPLEMENT_MODULE(FBogotaRuntimeModule,BogotaRuntime)

int32 UBogotaLaneLibrary::NearestPoint(const TArray<FVector>& Points,FVector Position) {
 double Best=100000000000.0; int32 BestIndex=0;
 for(int32 I=0;I<Points.Num();++I) {
  const FVector D=Points[I]-Position; const double Distance=FMath::Sqrt(D.X*D.X+D.Y*D.Y);
  if(Distance<Best) { Best=Distance; BestIndex=I; }
 }
 return BestIndex;
}
FVector2D UBogotaLaneLibrary::ProjectMapPoint(FVector Position,FVector Center,bool FullMap,double FullSpanX,double FullSpanY,double MiniSpanX,double MiniSpanY) {
 const double SpanX=FullMap?FullSpanX:MiniSpanX,SpanY=FullMap?FullSpanY:MiniSpanY;
 return FVector2D(0.5+(Position.Y-Center.Y)/SpanY,0.5-(Position.X-Center.X)/SpanX);
}

void UBogotaLaneLibrary::GetActorsOfClassCached(const UObject* WorldContextObject,TSubclassOf<AActor> ActorClass,TArray<AActor*>& OutActors) {
 OutActors.Reset();
 UWorld* World=GEngine?GEngine->GetWorldFromContextObject(WorldContextObject,EGetWorldErrorMode::ReturnNull):nullptr;
 if(!World || !ActorClass) return;
 if(!IsInGameThread()) {UGameplayStatics::GetAllActorsOfClass(WorldContextObject,ActorClass,OutActors);return;}
 const TWeakObjectPtr<UWorld> Key=World;
 if(!ActorQueries.Contains(Key)) {
  for(auto It=ActorQueries.CreateIterator();It;++It) if(!It.Key().IsValid()) It.RemoveCurrent();
  FActorQueryCache& NewCache=ActorQueries.Add(Key);
  auto Invalidate=[Key](AActor*){if(auto* Cache=ActorQueries.Find(Key)) Cache->Entries.Reset();};
  NewCache.Spawned=World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateLambda(Invalidate));
  NewCache.Destroyed=World->AddOnActorDestroyedHandler(FOnActorDestroyed::FDelegate::CreateLambda(Invalidate));
 }
 FActorQueryCache& Cache=ActorQueries.FindChecked(Key);
 if(Cache.Frame!=GFrameCounter) {Cache.Entries.Reset();Cache.Frame=GFrameCounter;}
 TArray<TWeakObjectPtr<AActor>>* Found=Cache.Entries.Find(ActorClass.Get());
 if(!Found) {
  UGameplayStatics::GetAllActorsOfClass(WorldContextObject,ActorClass,OutActors);
  TArray<TWeakObjectPtr<AActor>>& Entry=Cache.Entries.Add(ActorClass.Get());Entry.Reserve(OutActors.Num());
  for(AActor* Actor:OutActors) Entry.Add(Actor);
 } else {
  OutActors.Reserve(Found->Num());for(const auto& Weak:*Found) if(AActor* Actor=Weak.Get()) OutActors.Add(Actor);
 }
}
void UBogotaLaneLibrary::StaggerActorTick(AActor* Actor,float Interval,int32 Index,int32 Count) {
 if(!IsValid(Actor) || !IsInGameThread()) return;
 if(Interval<=0.f || Count<=1) {Actor->SetActorTickInterval(Interval);return;}
 // Change only the next due time; subsequent ticks retain their original interval.
 FActorTickFunction& Tick=Actor->PrimaryActorTick;
 const float Phase=FMath::Clamp((static_cast<float>(Index)+0.5f)/static_cast<float>(Count),0.001f,1.f);
 Tick.UpdateTickIntervalAndCoolDown(Interval*Phase);
 Tick.TickInterval=Interval;
}
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "GameFramework/Pawn.h"
#include <limits>
#include "Engine/World.h"
int32 UBogotaLaneLibrary::UpdatePrecipitationDrops(UInstancedStaticMeshComponent* Mesh,TArray<FVector>& Points,TArray<double>& Floors,double Dt,FVector Eye,bool Relocate,int32 VisibleCount,bool Hail) {
 if(!IsValid(Mesh)||!Mesh->GetWorld()||!IsInGameThread())return 0;
 const int32 Total=Mesh->GetInstanceCount(),Active=FMath::Clamp(VisibleCount,0,Total);
 Points.SetNum(Total);Floors.SetNum(Total);
 TArray<FTransform> Transforms;Transforms.SetNum(Total);
 FCollisionQueryParams Query(SCENE_QUERY_STAT(BogotaRainRoof),false,Mesh->GetOwner());
 if(APawn* Pawn=UGameplayStatics::GetPlayerPawn(Mesh,0))Query.AddIgnoredActor(Pawn);
 const double Top=Eye.Z+(Hail?2500.0:2300.0),Bottom=Eye.Z-3500.0,Margin=Hail?10.0:25.0;
 const FVector Velocity=Hail?FVector(-190,70,-2700):FVector(-110,45,-1600);
 const FVector Size=Hail?FVector(.055,.055,.055):FVector(.025,.025,.45);
 const FQuat Rotation=Hail?FQuat::Identity:FRotator(0,0,-4).Quaternion();
 const double Step=FMath::Clamp(Dt,0.0,.1);int32 Traces=0;const int32 Budget=Hail?16:64;
 for(int32 I=0;I<Total;++I){
  if(I>=Active){Transforms[I]=FTransform(FQuat::Identity,Points[I],FVector::ZeroVector);continue;}
  FVector& Point=Points[I];double& Floor=Floors[I];
  const bool Respawn=Relocate||!FMath::IsFinite(Floor)||Point.Z<Floor+Margin||FMath::Abs(Point.X-Eye.X)>2200.0||FMath::Abs(Point.Y-Eye.Y)>2200.0;
  if(Respawn){
   // Pending drops stay hidden until their roof query fits the frame's budget.
   if(Traces>=Budget){Floor=std::numeric_limits<double>::infinity();Transforms[I]=FTransform(FQuat::Identity,Point,FVector::ZeroVector);continue;}
   Point=Eye+FVector(FMath::FRandRange(-2100.f,2100.f),FMath::FRandRange(-2100.f,2100.f),FMath::FRandRange(300.f,Hail?2300.f:2100.f));
   FHitResult Hit;++Traces;
   Floor=Mesh->GetWorld()->LineTraceSingleByChannel(Hit,FVector(Point.X,Point.Y,Top),FVector(Point.X,Point.Y,Bottom),ECC_Visibility,Query)?Hit.ImpactPoint.Z:0.0;
   if(Relocate||!FMath::IsFinite(Floor))Point.Z=FMath::FRandRange(FMath::Min(Floor+50.0,Top),Top);
  }
  Point+=Velocity*Step;
  Transforms[I]=FTransform(Rotation,Point,Point.Z>Floor+Margin?Size:FVector::ZeroVector);
 }
 if(Total>0)Mesh->BatchUpdateInstancesTransforms(0,Transforms,false,true,true);
 return Traces;
}
void UBogotaLaneLibrary::DrawProjectedRoads(FPaintContext& Context,const TArray<FVector>& Starts,const TArray<FVector>& Ends,FVector Center,bool FullMap,FVector2D Origin,FVector2D Size,double FullSpanX,double FullSpanY,double MiniSpanX,double MiniSpanY) {
 auto Inside=[](FVector2D P){return P.X>=0.0 && P.X<=1.0 && P.Y>=0.0 && P.Y<=1.0;};
 auto Pixel=[&](FVector2D P){return Origin+FVector2D(FMath::Clamp(P.X,0.015,0.985)*Size.X,FMath::Clamp(P.Y,0.015,0.985)*Size.Y);};
 const FLinearColor Color(0.38f,0.49f,0.53f,1.f);
 for(int32 I=0;I<FMath::Min(Starts.Num(),Ends.Num());++I) {
  FVector2D A=ProjectMapPoint(Starts[I],Center,FullMap,FullSpanX,FullSpanY,MiniSpanX,MiniSpanY);
  FVector2D B=ProjectMapPoint(Ends[I],Center,FullMap,FullSpanX,FullSpanY,MiniSpanX,MiniSpanY);
  if(Inside(A)||Inside(B)) UWidgetBlueprintLibrary::DrawLine(Context,Pixel(A),Pixel(B),Color,false,5.f);
 }
}


#include "Engine/LevelStreaming.h"
#include "HAL/PlatformMemory.h"
int32 UBogotaLaneLibrary::MaintainSectorCache(const UObject* WorldContextObject,const TArray<FName>& SectorNames,int32 MaximumCached){
 if(!IsInGameThread()||!GEngine)return 0;UWorld* World=GEngine->GetWorldFromContextObject(WorldContextObject,EGetWorldErrorMode::ReturnNull);if(!World||!World->IsGameWorld())return 0;
 static TMap<TWeakObjectPtr<UWorld>,TMap<FName,double>> Histories;for(auto It=Histories.CreateIterator();It;++It)if(!It.Key().IsValid())It.RemoveCurrent();auto& History=Histories.FindOrAdd(World);const double Now=FPlatformTime::Seconds();
 const uint64 Available=FPlatformMemory::GetStats().AvailablePhysical;int32 Budget=FMath::Clamp(MaximumCached,0,6);if(Available<2ull*1024*1024*1024)Budget=0;else if(Available<4ull*1024*1024*1024)Budget=FMath::Min(Budget,2);
 struct FCandidate{ULevelStreaming* Level;double Last;};TArray<FCandidate> Candidates;
 for(FName Name:SectorNames)if(ULevelStreaming* Level=UGameplayStatics::GetStreamingLevel(World,Name)){
  if(Level->GetShouldBeVisibleFlag()){History.Add(Name,Now);continue;}
  if(Level->GetLoadedLevel()){if(const double* Last=History.Find(Name))Candidates.Add({Level,*Last});}
 }
 Candidates.Sort([](const FCandidate& A,const FCandidate& B){return A.Last>B.Last;});int32 Kept=0;
 for(const FCandidate& C:Candidates){const bool Keep=Kept<Budget;C.Level->SetShouldBeLoaded(Keep);if(Keep)++Kept;}
 return Kept;
}

void UBogotaLaneLibrary::CopyVectorRange(const TArray<FVector>& Source,int32 Start,int32 Count,TArray<FVector>& Destination){
 Destination.Reset(); if(Start<0 || Count<0 || Start>Source.Num() || Count>Source.Num()-Start)return; Destination.Append(Source.GetData()+Start,Count);
}
double UBogotaLaneLibrary::RouteSignalLimit(const TArray<int32>& GateLanes,const TArray<double>& GateDistances,const TArray<int32>& GateCounts,const TArray<bool>& Green,int32 Group,double Distance,double Length,double HalfLength,double AvailableRoom,bool CheckExit){
 if(Length<=0 || GateLanes.Num()!=GateDistances.Num() || GateCounts.Num()!=GateLanes.Num() || Green.Num()!=GateLanes.Num())return 0.;
 double Limit=1.e8;
 for(int32 I=0;I<GateLanes.Num();++I){if(GateLanes[I]!=Group)continue;const double Ahead=FMath::Fmod(GateDistances[I]-Distance+Length,Length);const double Gap=Ahead-HalfLength-450.;if(Gap>=-30. && !Green[I])Limit=FMath::Min(Limit,Gap);}
 if(CheckExit){AvailableRoom=FMath::Min(AvailableRoom,Limit);for(int32 I=0;I<GateLanes.Num();++I){if(GateLanes[I]!=Group || GateCounts[I]<-1)continue;const double Gap=FMath::Fmod(GateDistances[I]-Distance+Length,Length)-HalfLength-450.;if(Gap>=-30. && Gap<Limit && AvailableRoom<Gap+2.*HalfLength+700.)Limit=Gap;}}
 return FMath::Max(0.,Limit);
}
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"
namespace {
struct FVehicleFields {
 FStructProperty *Previous,*Next;
 FDoubleProperty *Yaw,*NextYaw,*HalfLength,*HalfWidth,*Speed;
 FBoolProperty *Player,*Parked;
 FVehicleFields(UClass* C){Previous=FindFProperty<FStructProperty>(C,TEXT("PreviousPosition"));Next=FindFProperty<FStructProperty>(C,TEXT("NextPosition"));Yaw=FindFProperty<FDoubleProperty>(C,TEXT("PreviousYaw"));NextYaw=FindFProperty<FDoubleProperty>(C,TEXT("NextYaw"));HalfLength=FindFProperty<FDoubleProperty>(C,TEXT("HalfLength"));HalfWidth=FindFProperty<FDoubleProperty>(C,TEXT("HalfWidth"));Speed=FindFProperty<FDoubleProperty>(C,TEXT("Speed"));Player=FindFProperty<FBoolProperty>(C,TEXT("PlayerControlled"));Parked=FindFProperty<FBoolProperty>(C,TEXT("Parked"));}
 bool Valid()const{return Previous&&Next&&Yaw&&NextYaw&&HalfLength&&HalfWidth&&Speed&&Player&&Parked;}
};
FVehicleFields& Fields(AActor* A){static TMap<UClass*,TUniquePtr<FVehicleFields>> Cache;auto& P=Cache.FindOrAdd(A->GetClass());if(!P)P=MakeUnique<FVehicleFields>(A->GetClass());return *P;}
double D(FDoubleProperty* P,AActor* A){return P->GetPropertyValue_InContainer(A);}
FVector V(FStructProperty* P,AActor* A){return *P->ContainerPtrToValuePtr<FVector>(A);}
FVector Axis(double Yaw){double R=FMath::DegreesToRadians(Yaw);return FVector(FMath::Cos(R),FMath::Sin(R),0);}
}
double UBogotaLaneLibrary::ClampRouteStep(AActor* Visitor,double RequestedStep){
 CSV_SCOPED_TIMING_STAT_EXCLUSIVE(BogotaRouteCollision);
 if(!IsValid(Visitor)||RequestedStep<=0.)return 0.;auto& A=Fields(Visitor);if(!A.Valid())return 0.;
 auto Object=[](UObject* X,const TCHAR* N)->UObject*{auto P=FindFProperty<FObjectPropertyBase>(X->GetClass(),N);return P?P->GetObjectPropertyValue_InContainer(X):nullptr;};
 UObject* Lane=Object(Visitor,TEXT("Lane"));if(!IsValid(Lane))return 0.;USplineComponent* Route=Cast<USplineComponent>(Object(Lane,TEXT("Route")));if(!Route)return 0.;
 auto DistanceProperty=FindFProperty<FDoubleProperty>(Visitor->GetClass(),TEXT("Distance"));if(!DistanceProperty)return 0.;double Distance=DistanceProperty->GetPropertyValue_InContainer(Visitor),Length=Route->GetSplineLength();if(Length<=0.)return 0.;
 struct FBody {FVector P,F,R;double L,W,EX,EY;FBody(FVector InP,FVector InF,double InL,double InW):P(InP),F(InF),R(-InF.Y,InF.X,0),L(InL),W(InW),EX(FMath::Abs(InF.X)*InL+FMath::Abs(InF.Y)*InW),EY(FMath::Abs(InF.Y)*InL+FMath::Abs(InF.X)*InW){}};
 struct FReservation {double Time=0.,Start=0.,Horizon=0.;TWeakObjectPtr<UObject> Lane;uint32 Generation=0;TArray<FBody> Bodies;};
 struct FGridBody {TWeakObjectPtr<AActor> Owner;uint32 Generation;FBody Shape;};
 struct FHeadway {uint64 Frame=MAX_uint64;double Distance=0.,Value=0.,Time=-100.;};
 static TWeakObjectPtr<UWorld> World;static uint64 Frame=MAX_uint64;static TMap<TWeakObjectPtr<AActor>,FReservation> Reservations;static TArray<FGridBody> Bodies;static TMap<FIntPoint,TArray<int32>> Grid;static TMap<TWeakObjectPtr<AActor>,FHeadway> Headways;
 if(World.Get()!=Visitor->GetWorld()){World=Visitor->GetWorld();Reservations.Reset();Headways.Reset();Frame=MAX_uint64;}
 double Now=Visitor->GetWorld()->GetTimeSeconds();
 bool IsHeadway=RequestedStep==5000.;if(IsHeadway){auto* Cached=Headways.Find(Visitor);if(Cached&&Now-Cached->Time<.4){double Advance=FMath::Fmod(Distance-Cached->Distance+Length,Length);if(Advance<600.)return FMath::Max(0.,Cached->Value-Advance);}}
 auto AddGrid=[&](AActor* Owner,const FReservation& Reservation){for(const FBody& B:Reservation.Bodies){int32 Index=Bodies.Add({Owner,Reservation.Generation,B});double X=FMath::Abs(B.F.X)*B.L+FMath::Abs(B.F.Y)*B.W,Y=FMath::Abs(B.F.Y)*B.L+FMath::Abs(B.F.X)*B.W;for(int32 I=FMath::FloorToInt((B.P.X-X)/1000.);I<=FMath::FloorToInt((B.P.X+X)/1000.);++I)for(int32 J=FMath::FloorToInt((B.P.Y-Y)/1000.);J<=FMath::FloorToInt((B.P.Y+Y)/1000.);++J)Grid.FindOrAdd(FIntPoint(I,J)).Add(Index);}};
 if(Frame!=GFrameCounter){Frame=GFrameCounter;Bodies.Reset();Grid.Reset();for(auto It=Reservations.CreateIterator();It;++It){AActor* Owner=It.Key().Get();if(!IsValid(Owner)||Now-It.Value().Time>1.5){It.RemoveCurrent();continue;}AddGrid(Owner,It.Value());}}
 static UClass* Base=nullptr;if(!Base)Base=LoadClass<AActor>(nullptr,TEXT("/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C"));TArray<AActor*> All;GetActorsOfClassCached(Visitor,Base,All);
 FVector Start=V(A.Next,Visitor),Forward=Axis(D(A.NextYaw,Visitor));double Horizon=2.*D(A.HalfLength,Visitor)+800.,Radius=D(A.HalfLength,Visitor)+D(A.HalfWidth,Visitor)+FMath::Max(RequestedStep,Horizon)+100.;
 TArray<AActor*,TInlineAllocator<24>> Near;
 for(AActor* Other:All){if(!IsValid(Other)||Other==Visitor)continue;auto& B=Fields(Other);if(B.Valid()&&FVector::DistSquaredXY(Start,V(B.Next,Other))<FMath::Square(Radius+D(B.HalfLength,Other)+D(B.HalfWidth,Other)))Near.Add(Other);}
 auto Compatible=[&](AActor* Other){UObject* OtherLane=Object(Other,TEXT("Lane"));if(!IsValid(OtherLane))return false;auto* Group=FindFProperty<FIntProperty>(Lane->GetClass(),TEXT("RouteGroup"));auto* OtherGroup=FindFProperty<FIntProperty>(OtherLane->GetClass(),TEXT("RouteGroup"));if(!Group||!OtherGroup)return false;bool SameGroup=Group->GetPropertyValue_InContainer(Lane)==OtherGroup->GetPropertyValue_InContainer(OtherLane);if(SameGroup)return true;auto& B=Fields(Other);FVector Delta=V(B.Next,Other)-Start;return (FVector::DotProduct(Delta,Forward)<-50.)&&FVector::DotProduct(Forward,Axis(D(B.NextYaw,Other)))>.95&&FMath::Abs(Delta.X*Forward.Y-Delta.Y*Forward.X)<100.;};
 struct FObstacle {FBody Next,Previous;bool Compatible;};TArray<FObstacle,TInlineAllocator<24>> Obstacles;
 for(AActor* Other:Near){auto& B=Fields(Other);Obstacles.Add({{V(B.Next,Other),Axis(D(B.NextYaw,Other)),D(B.HalfLength,Other)+8.,D(B.HalfWidth,Other)+5.},{V(B.Previous,Other),Axis(D(B.Yaw,Other)),D(B.HalfLength,Other)+8.,D(B.HalfWidth,Other)+5.},Compatible(Other)});}
 TMap<TWeakObjectPtr<AActor>,bool> OwnerAllowed;
 auto Overlap=[](const FBody& A,const FBody& B){FVector Delta=B.P-A.P;if(FMath::Abs(Delta.X)>=A.EX+B.EX||FMath::Abs(Delta.Y)>=A.EY+B.EY)return false;auto Dot=[](FVector A,FVector B){return A.X*B.X+A.Y*B.Y;};for(FVector Axis:{A.F,A.R,B.F,B.R}){double E=A.L*FMath::Abs(Dot(A.F,Axis))+A.W*FMath::Abs(Dot(A.R,Axis))+B.L*FMath::Abs(Dot(B.F,Axis))+B.W*FMath::Abs(Dot(B.R,Axis));if(FMath::Abs(Dot(Delta,Axis))>=E)return false;}return true;};
 auto At=[&](double Step,double ExtraLength,double ExtraWidth){double Dst=FMath::Fmod(Distance+Step,Length);return FBody{Route->GetLocationAtDistanceAlongSpline(Dst,ESplineCoordinateSpace::World),Route->GetDirectionAtDistanceAlongSpline(Dst,ESplineCoordinateSpace::World).GetSafeNormal2D(),D(A.HalfLength,Visitor)+ExtraLength,D(A.HalfWidth,Visitor)+ExtraWidth};};
 auto Solve=[&](double Request,bool ConflictOnly){int32 Steps=FMath::Max(1,FMath::CeilToInt(Request/(Request>600.?100.:35.)));double Safe=0.;for(int32 I=1;I<=Steps;++I){double Step=Request*I/Steps;FBody Candidate=At(Step,8.,5.);bool Blocked=false;
  for(const FObstacle& B:Obstacles){if(ConflictOnly&&B.Compatible)continue;if(Overlap(Candidate,B.Next)||Overlap(Candidate,B.Previous)){Blocked=true;break;}}
  double X=FMath::Abs(Candidate.F.X)*Candidate.L+FMath::Abs(Candidate.F.Y)*Candidate.W,Y=FMath::Abs(Candidate.F.Y)*Candidate.L+FMath::Abs(Candidate.F.X)*Candidate.W;
  for(int32 U=FMath::FloorToInt((Candidate.P.X-X)/1000.);!Blocked&&U<=FMath::FloorToInt((Candidate.P.X+X)/1000.);++U)for(int32 W=FMath::FloorToInt((Candidate.P.Y-Y)/1000.);!Blocked&&W<=FMath::FloorToInt((Candidate.P.Y+Y)/1000.);++W){auto* Bucket=Grid.Find(FIntPoint(U,W));if(!Bucket)continue;for(int32 Index:*Bucket){const auto& Body=Bodies[Index];AActor* Owner=Body.Owner.Get();if(!IsValid(Owner)||Owner==Visitor||!Overlap(Candidate,Body.Shape))continue;auto* Held=Reservations.Find(Body.Owner);if(!Held||Held->Generation!=Body.Generation||Now-Held->Time>1.5)continue;bool* Allowed=OwnerAllowed.Find(Body.Owner);if(!Allowed)Allowed=&OwnerAllowed.Add(Body.Owner,!Compatible(Owner));if(*Allowed){Blocked=true;break;}}}
  if(Blocked)break;Safe=Step;
 }return Safe;};
 double Safe=Solve(RequestedStep,false);
 if(RequestedStep<=600.&&Safe>0.){
  if(auto* Held=Reservations.Find(Visitor)){double Advance=FMath::Fmod(Distance-Held->Start+Length,Length);if(Held->Lane.Get()==Lane&&Now-Held->Time<=1.5&&Advance+Safe<Held->Horizon-250.){Held->Time=Now;return Safe;}}
  if(Solve(Horizon,true)<Horizon-.01)return 0.;
  auto& R=Reservations.FindOrAdd(Visitor);R.Time=Now;R.Start=Distance;R.Horizon=Horizon;R.Lane=Lane;++R.Generation;R.Bodies.Reset();int32 Count=FMath::CeilToInt(Horizon/250.);for(int32 I=0;I<=Count;++I)R.Bodies.Add(At(Horizon*I/Count,45.,15.));AddGrid(Visitor,R);
 }
 if(IsHeadway)Headways.Add(Visitor,{GFrameCounter,Distance,Safe,Now});return Safe;
}

double UBogotaLaneLibrary::VehicleClearance(AActor* Visitor,AActor* Other){
 if(!IsValid(Visitor)||!IsValid(Other)||Visitor==Other)return 1.e8;
 auto& A=Fields(Visitor);auto& B=Fields(Other);if(!A.Valid()||!B.Valid())return 0.;
 auto Object=[](UObject* X,const TCHAR* N)->UObject*{auto P=FindFProperty<FObjectPropertyBase>(X->GetClass(),N);return P?P->GetObjectPropertyValue_InContainer(X):nullptr;};
 auto Number=[](UObject* X,const TCHAR* N)->double{auto P=FindFProperty<FDoubleProperty>(X->GetClass(),N);return P?P->GetPropertyValue_InContainer(X):0.;};
 auto Integer=[](UObject* X,const TCHAR* N)->int32{auto P=FindFProperty<FIntProperty>(X->GetClass(),N);return P?P->GetPropertyValue_InContainer(X):0;};
 if(B.Player->GetPropertyValue_InContainer(Other)||B.Parked->GetPropertyValue_InContainer(Other))return EnvelopeClearance(Visitor,Other);
 UObject* Lane=Object(Visitor,TEXT("Lane"));UObject* OtherLane=Object(Other,TEXT("Lane"));if(!IsValid(Lane)||!IsValid(OtherLane))return EnvelopeClearance(Visitor,Other);
 USplineComponent* Route=Cast<USplineComponent>(Object(Lane,TEXT("Route")));if(!Route)return EnvelopeClearance(Visitor,Other);
 const double Length=Route->GetSplineLength();if(Length<=0)return 0.;
 FVector OtherPosition=V(B.Previous,Other);const float Mapped=ClosestDistance(Route,OtherPosition);FVector Point=Route->GetLocationAtDistanceAlongSpline(Mapped,ESplineCoordinateSpace::World),Heading=Route->GetDirectionAtDistanceAlongSpline(Mapped,ESplineCoordinateSpace::World),OtherForward=Axis(D(B.Yaw,Other));
 const bool Shared=FVector::DistSquaredXY(OtherPosition,Point)<14400.&&FVector::DotProduct(Heading,OtherForward)>.98;
 if(Shared){
  const bool Same=Integer(Lane,TEXT("RouteGroup"))==Integer(OtherLane,TEXT("RouteGroup"));double Position=Same?Number(Other,TEXT("PreviousDistance")):Mapped;
  double Ahead=FMath::Fmod(Position-Number(Visitor,TEXT("Distance"))+Length,Length);if(Same&&Ahead<.01)return 1.e8;
  double TotalLength=D(A.HalfLength,Visitor)+D(B.HalfLength,Other);double Gap=FMath::Max(0.,Ahead-TotalLength-190.);
  if(FVector::DistXY(OtherPosition,V(A.Previous,Visitor))<TotalLength+1000.&&FVector::DotProduct(Axis(D(A.Yaw,Visitor)),OtherForward)>.85)Gap=FMath::Min(Gap,EnvelopeClearance(Visitor,Other));return Gap;
 }
 UObject* Junction=Object(Visitor,TEXT("ArcJunctionRef"));if(IsValid(Junction)&&Junction==Object(Other,TEXT("ArcJunctionRef"))){
  UFunction* Fn=Junction->FindFunction(TEXT("ArcCompatibleMovements"));if(Fn){FStructOnScope Params(Fn);auto First=FindFProperty<FIntProperty>(Fn,TEXT("First"));auto Second=FindFProperty<FIntProperty>(Fn,TEXT("Second"));auto Result=FindFProperty<FBoolProperty>(Fn,TEXT("ReturnValue"));if(First&&Second&&Result){First->SetPropertyValue_InContainer(Params.GetStructMemory(),Integer(Visitor,TEXT("ArcMovement")));Second->SetPropertyValue_InContainer(Params.GetStructMemory(),Integer(Other,TEXT("ArcMovement")));Junction->ProcessEvent(Fn,Params.GetStructMemory());if(Result->GetPropertyValue_InContainer(Params.GetStructMemory()))return 1.e8;}}
 }
 return EnvelopeClearance(Visitor,Other);
}
bool UBogotaLaneLibrary::PedestrianCorridorClear(const TArray<AActor*>& Vehicles,FVector Start,FVector Finish){
 FVector Half=(Finish-Start)*.5,Mid=(Finish+Start)*.5,Normal=FVector::CrossProduct(Half,FVector::UpVector).GetSafeNormal2D();
 for(AActor* Car:Vehicles){if(!IsValid(Car))continue;auto& P=Fields(Car);if(!P.Valid())return false;FVector F=Axis(D(P.NextYaw,Car)),R=FVector::CrossProduct(F,FVector::UpVector),Offset=Mid-V(P.Next,Car);double L=D(P.HalfLength,Car),W=D(P.HalfWidth,Car),Margin=59.+D(P.Speed,Car)*.15;
 if(FMath::Abs(FVector::DotProduct(Offset,F))>=L+FMath::Abs(FVector::DotProduct(Half,F))+Margin)continue;
 if(FMath::Abs(FVector::DotProduct(Offset,R))>=W+FMath::Abs(FVector::DotProduct(Half,R))+Margin)continue;
 if(FMath::Abs(FVector::DotProduct(Offset,Normal))>=FMath::Abs(FVector::DotProduct(F,Normal))*L+FMath::Abs(FVector::DotProduct(R,Normal))*W+Margin)continue;
 return false;}
 return true;
}
double UBogotaLaneLibrary::EnvelopeClearance(AActor* Visitor,AActor* Other){
 if(!IsValid(Visitor)||!IsValid(Other))return 1.e8;auto& A=Fields(Visitor);auto& B=Fields(Other);if(!A.Valid()||!B.Valid())return 0.;
 FVector F=Axis(D(A.Yaw,Visitor)),R(-F.Y,F.X,0),G=Axis(D(B.Yaw,Other)),S(-G.Y,G.X,0),Delta=V(B.Previous,Other)-V(A.Previous,Visitor);
 double Entry=-1.e8,Exit=1.e8;bool Possible=true;
 for(FVector Direction:{F,R,G,S}){
  double Offset=FVector::DotProduct(Delta,Direction),Rate=FVector::DotProduct(F,Direction);
  double Extent=(D(A.HalfLength,Visitor)+60)*FMath::Abs(FVector::DotProduct(F,Direction))+(D(A.HalfWidth,Visitor)+10)*FMath::Abs(FVector::DotProduct(R,Direction))+(D(B.HalfLength,Other)+60)*FMath::Abs(FVector::DotProduct(G,Direction))+(D(B.HalfWidth,Other)+10)*FMath::Abs(FVector::DotProduct(S,Direction));
  if(FMath::Abs(Rate)<.00001){if(FMath::Abs(Offset)>Extent)Possible=false;continue;}
  double Lo=(Offset-Extent)/Rate,Hi=(Offset+Extent)/Rate;Entry=FMath::Max(Entry,FMath::Min(Lo,Hi));Exit=FMath::Min(Exit,FMath::Max(Lo,Hi));
 }
 double Future=FMath::Max(Entry,0.);return Possible&&Exit>=Future&&Future<5000?FMath::Max(Future-25.,0.):1.e8;
}




void UBogotaLaneLibrary::SimulateVehicleStep(AActor* Visitor,double DeltaTime,double Clearance,double DesiredSpeed){
 CSV_SCOPED_TIMING_STAT_EXCLUSIVE(BogotaVehicleStep);
 if(!IsValid(Visitor)||DeltaTime<=0.)return;auto& F=Fields(Visitor);if(!F.Valid()||F.Player->GetPropertyValue_InContainer(Visitor)||F.Parked->GetPropertyValue_InContainer(Visitor))return;
 struct FStepFields{FDoubleProperty *Distance,*PreviousDistance,*Cruise,*Left,*Right,*Wheel,*PreviousWheel,*Radius,*Steer,*Step;FObjectPropertyBase* Lane;FStepFields(UClass* C){
 Distance=FindFProperty<FDoubleProperty>(C,TEXT("Distance"));PreviousDistance=FindFProperty<FDoubleProperty>(C,TEXT("PreviousDistance"));Cruise=FindFProperty<FDoubleProperty>(C,TEXT("CruiseSpeed"));Left=FindFProperty<FDoubleProperty>(C,TEXT("DoorAlphaLeft"));Right=FindFProperty<FDoubleProperty>(C,TEXT("DoorAlphaRight"));Wheel=FindFProperty<FDoubleProperty>(C,TEXT("WheelAngle"));PreviousWheel=FindFProperty<FDoubleProperty>(C,TEXT("PreviousWheelAngle"));Radius=FindFProperty<FDoubleProperty>(C,TEXT("WheelRadius"));Steer=FindFProperty<FDoubleProperty>(C,TEXT("SteerAngle"));Step=FindFProperty<FDoubleProperty>(C,TEXT("SimulationStepDistance"));Lane=FindFProperty<FObjectPropertyBase>(C,TEXT("Lane"));}
 bool Valid()const{return Distance&&PreviousDistance&&Cruise&&Left&&Right&&Wheel&&PreviousWheel&&Radius&&Steer&&Step&&Lane;}};
 static TMap<UClass*,TUniquePtr<FStepFields>> Cache;auto& Slot=Cache.FindOrAdd(Visitor->GetClass());if(!Slot)Slot=MakeUnique<FStepFields>(Visitor->GetClass());auto& S=*Slot;if(!S.Valid())return;
 UObject* Lane=S.Lane->GetObjectPropertyValue_InContainer(Visitor);if(!IsValid(Lane))return;auto* RouteProperty=FindFProperty<FObjectPropertyBase>(Lane->GetClass(),TEXT("Route"));USplineComponent* Route=RouteProperty?Cast<USplineComponent>(RouteProperty->GetObjectPropertyValue_InContainer(Lane)):nullptr;if(!Route||Route->GetSplineLength()<=0.)return;
 double Distance=D(S.Distance,Visitor),OldYaw=D(F.NextYaw,Visitor),Dt=FMath::Clamp(DeltaTime,0.,.25);S.PreviousDistance->SetPropertyValue_InContainer(Visitor,Distance);*F.Previous->ContainerPtrToValuePtr<FVector>(Visitor)=V(F.Next,Visitor);F.Yaw->SetPropertyValue_InContainer(Visitor,OldYaw);S.PreviousWheel->SetPropertyValue_InContainer(Visitor,D(S.Wheel,Visitor));
 double Room=FMath::Max(Clearance,0.),Desired=FMath::Min(FMath::Min(FMath::Max(DesiredSpeed,0.),D(S.Cruise,Visitor)),FMath::Sqrt(Room*1300.));if(D(S.Left,Visitor)>.001||D(S.Right,Visitor)>.001)Desired=0.;double Current=D(F.Speed,Visitor),Approach=FMath::FInterpConstantTo(Current,Desired,Dt,Desired>Current?240.:650.);double Move=ClampRouteStep(Visitor,FMath::Min(Approach*Dt,Room));S.Step->SetPropertyValue_InContainer(Visitor,Move);F.Speed->SetPropertyValue_InContainer(Visitor,Move/FMath::Max(Dt,.000001));
 double NewDistance=FMath::Fmod(Distance+Move,Route->GetSplineLength());S.Distance->SetPropertyValue_InContainer(Visitor,NewDistance);*F.Next->ContainerPtrToValuePtr<FVector>(Visitor)=Route->GetLocationAtDistanceAlongSpline(NewDistance,ESplineCoordinateSpace::World);double Yaw=Route->GetDirectionAtDistanceAlongSpline(NewDistance,ESplineCoordinateSpace::World).Rotation().Yaw;F.NextYaw->SetPropertyValue_InContainer(Visitor,Yaw);S.Wheel->SetPropertyValue_InContainer(Visitor,FMath::Fmod(D(S.Wheel,Visitor)+Move/FMath::Max(D(S.Radius,Visitor),1.)*57.2957795,360.));S.Steer->SetPropertyValue_InContainer(Visitor,FMath::Clamp(FMath::FindDeltaAngleDegrees(OldYaw,Yaw)/FMath::Max(Dt,.000001)*.25,-25.,25.));
}

FVector UBogotaLaneLibrary::AdvanceFarRoute(const TArray<FVector>& Route,int32& RouteIndex,FVector Position,double Speed,double Dt,double HalfHeight) {
 if(Route.Num()<2 || Position.ContainsNaN() || !FMath::IsFinite(Dt)) return Position;
 double Budget=FMath::Max(0.,Speed*Dt);
 RouteIndex=FMath::Clamp(RouteIndex,0,Route.Num()-1);
 for(int32 Step=0;Step<32 && Budget>.01;++Step) {
  const FVector Goal=Route[RouteIndex]+FVector(0,0,HalfHeight+2.);
  const FVector Delta=Goal-Position;
  const double Distance=Delta.Size(),Travel=FMath::Min(Budget,Distance);
  Position+=Delta.GetSafeNormal()*Travel;Budget-=Travel;
  if(Distance<=Travel) RouteIndex=(RouteIndex+1)%Route.Num();
 }
 return Position;
}

namespace {
struct FCrossFields {
 FArrayProperty* Route=nullptr;
 FIntProperty* Index=nullptr;FIntProperty* Completed=nullptr;
 FBoolProperty* Crossing=nullptr;FBoolProperty* Permission=nullptr;
 FObjectPropertyBase* Manager=nullptr;
};
TMap<TWeakObjectPtr<UClass>,FCrossFields> CrossFields;
}
void UBogotaLaneLibrary::SimulateCrosswalk(AActor* Citizen,double TimeSeconds) {
 CSV_SCOPED_TIMING_STAT_EXCLUSIVE(BogotaCrosswalkStep);
 auto* Character=Cast<ACharacter>(Citizen);if(!IsValid(Character))return;
 FCrossFields* F=CrossFields.Find(Character->GetClass());
 if(!F) {
  FCrossFields New;auto* Class=Character->GetClass();
  New.Route=FindFProperty<FArrayProperty>(Class,TEXT("Route"));
  New.Index=FindFProperty<FIntProperty>(Class,TEXT("RouteIndex"));
  New.Completed=FindFProperty<FIntProperty>(Class,TEXT("CrossingsCompleted"));
  New.Crossing=FindFProperty<FBoolProperty>(Class,TEXT("Crossing"));
  New.Permission=FindFProperty<FBoolProperty>(Class,TEXT("R5MayCross"));
  New.Manager=FindFProperty<FObjectPropertyBase>(Class,TEXT("R5TrafficManager"));
  F=&CrossFields.Add(Class,New);
 }
 if(!F->Route||!F->Index||!F->Completed||!F->Crossing)return;
 FScriptArrayHelper Route(F->Route,F->Route->ContainerPtrToValuePtr<void>(Character));
 if(Route.Num()<2)return;
 const int32 Index=FMath::Clamp(F->Index->GetPropertyValue_InContainer(Character),0,Route.Num()-1);
 const FVector Goal=*reinterpret_cast<FVector*>(Route.GetRawPtr(Index));
 const FVector Start=Character->GetActorLocation(),Delta=Goal-Start;
 const bool Crossing=F->Crossing->GetPropertyValue_InContainer(Character);
 if(Delta.SizeSquared2D()<45.*45.) {
  if(Crossing)F->Completed->SetPropertyValue_InContainer(Character,F->Completed->GetPropertyValue_InContainer(Character)+1);
  F->Crossing->SetPropertyValue_InContainer(Character,false);
  F->Index->SetPropertyValue_InContainer(Character,(Index+1)%Route.Num());return;
 }
 const bool CrossingLeg=Index==1||Index==5;
 const double Phase=FMath::Fmod(TimeSeconds,264.);
 const bool Window=Phase>=224. && Phase<244.;bool Clear=true;
 if(CrossingLeg&&!Crossing&&Window&&F->Manager) {
  auto* Manager=Cast<AActor>(F->Manager->GetObjectPropertyValue_InContainer(Character));
  if(IsValid(Manager)) {
   if(auto* VehiclesProperty=FindFProperty<FArrayProperty>(Manager->GetClass(),TEXT("Vehicles"))) {
    static TWeakObjectPtr<AActor> CachedManager;static uint64 CachedFrame=MAX_uint64;static TArray<AActor*> Vehicles;
    if(CachedFrame!=GFrameCounter || CachedManager.Get()!=Manager) {
     CachedFrame=GFrameCounter;CachedManager=Manager;Vehicles.Reset();
     FScriptArrayHelper Array(VehiclesProperty,VehiclesProperty->ContainerPtrToValuePtr<void>(Manager));
     auto* Inner=CastField<FObjectPropertyBase>(VehiclesProperty->Inner);
     if(Inner)for(int32 I=0;I<Array.Num();++I)if(auto* Vehicle=Cast<AActor>(Inner->GetObjectPropertyValue(Array.GetRawPtr(I)))){if(IsValid(Vehicle))Vehicles.Add(Vehicle);}
    }
    Clear=PedestrianCorridorClear(Vehicles,Start,Goal);
   }
  }
 }
 if(F->Permission)F->Permission->SetPropertyValue_InContainer(Character,Clear);
 if(!CrossingLeg||Crossing||(Window&&Clear)) {
  F->Crossing->SetPropertyValue_InContainer(Character,Crossing||CrossingLeg);
  Character->AddMovementInput(Delta.GetSafeNormal2D(),1.,true);
 }
}
