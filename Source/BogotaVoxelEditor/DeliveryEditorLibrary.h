#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "DeliveryEditorLibrary.generated.h"
class USkeleton;
class UAnimSequence;
UCLASS() class UDeliveryEditorLibrary:public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static int32 CleanCityDuplicateBikes();
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static int32 CleanBlueprint(UBlueprint* Blueprint);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static FString AuditBlueprint(UBlueprint* Blueprint);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static FString ValidateTrafficPaint(UClass* CityClass);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static FString ValidateMapRoutes(float Seconds);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static bool RemoveDeliveriesApp(UBlueprint* Blueprint);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static bool StylePhoneTypography(UBlueprint* Blueprint,class UFont* Font);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static bool BuildPhoneDesigner(UBlueprint* Blueprint);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static bool BuildPhoneAppLayouts(UBlueprint* Blueprint);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static UBlueprint* BuildCharacterAnimationBlueprint(FName AssetName,USkeleton* Skeleton,UAnimSequence* Idle,UAnimSequence* Walk,UAnimSequence* Bike,UAnimSequence* Moto,UAnimSequence* Jump);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static UBlueprint* BuildLocomotionBlueprint(USkeleton* Skeleton,UAnimSequence* Idle,UAnimSequence* Walk,UAnimSequence* Bike,UAnimSequence* Moto,UAnimSequence* Jump);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static bool BuildLogicGraph(UBlueprint* Blueprint,FName FunctionName,const FString& Specification);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static bool BuildRewardGraph(UBlueprint* Blueprint);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static bool AddActionGraph(UBlueprint* Blueprint,FName GraphName,FName NativeFunction);
 UFUNCTION(BlueprintCallable,Category="Delivery|Editor") static bool SetGameplayComponent(UBlueprint* Blueprint,UClass* GameplayClass);
};

