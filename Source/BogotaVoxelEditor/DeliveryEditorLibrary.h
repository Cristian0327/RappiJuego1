#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "DeliveryEditorLibrary.generated.h"
class USkeleton;
class UAnimSequence;
UCLASS() class UDeliveryEditorLibrary:public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
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

