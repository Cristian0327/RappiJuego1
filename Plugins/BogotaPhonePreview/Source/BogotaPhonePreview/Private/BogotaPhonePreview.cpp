#include "SonyGamepad.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Animation/SkeletalMeshActor.h"
#include "Engine/SkeletalMesh.h"
#include "Components/SpotLightComponent.h"
#include "Kismet/KismetSystemLibrary.h"
#include "AudioDevice.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundClass.h"
#include "Sound/SoundMix.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/ConfigCacheIni.h"
#include "FMODStudioModule.h"
#include "fmod_studio.hpp"
#include "GameFramework/GameUserSettings.h"
#include "Components/StaticMeshComponent.h"
#include "Components/WidgetComponent.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/UObjectIterator.h"
#include "Modules/ModuleManager.h"
#include "Interfaces/IPluginManager.h"
#include "Engine/Engine.h"
#include "Engine/Console.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/HUD.h"
#include "GameFramework/InputDeviceSubsystem.h"
#include "Components/TextBlock.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Widgets/Colors/SColorWheel.h"
#include "Widgets/Input/SSlider.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Texture2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SLeafWidget.h"
#include "Rendering/DrawElements.h"
#include "Widgets/Notifications/SProgressBar.h"
#include "EngineUtils.h"
#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetLayoutLibrary.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/Border.h"
#include "GameFramework/Pawn.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/SBoxPanel.h"
#include "Brushes/SlateColorBrush.h"
#include "GameFramework/PlayerController.h"
#include "Containers/Ticker.h"
#include "Framework/Application/SlateApplication.h"
#include "Framework/Application/IInputProcessor.h"
#include "Widgets/Layout/SConstraintCanvas.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SSpacer.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "ImageUtils.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include "UObject/Package.h"
#include "UObject/StructOnScope.h"

namespace
{
class SStreetMinimap final : public SLeafWidget
{
public:
    using FPaintMap = TFunction<int32(const FGeometry&, FSlateWindowElementList&, int32)>;

    SLATE_BEGIN_ARGS(SStreetMinimap) {}
        SLATE_ARGUMENT(FPaintMap, PaintMap)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs) { PaintMap = InArgs._PaintMap; }
    FVector2D ComputeDesiredSize(float) const override { return FVector2D::ZeroVector; }
    int32 OnPaint(const FPaintArgs&, const FGeometry& Geometry, const FSlateRect&, FSlateWindowElementList& Out,
        int32 Layer, const FWidgetStyle&, bool) const override
    {
        return PaintMap(Geometry, Out, Layer);
    }

private:
    FPaintMap PaintMap;
};

class FPhonePreview final : public IInputProcessor
{
public:
    void Tick(float DeltaTime, FSlateApplication& Slate, TSharedRef<ICursor>) override
    {
        UGameViewportClient* View = GEngine ? GEngine->GameViewport.Get() : nullptr;
        auto* World = View ? View->GetWorld() : nullptr;
        if (!World || !World->IsGameWorld()) { if (PauseMenu) ClosePause(); if (Overlay) Close(); RemoveRouteHUD(); return; }
#if PLATFORM_WINDOWS
        if (const auto Plugin = IPluginManager::Get().FindPlugin(TEXT("BogotaPhonePreview")))
            SonyGamepad.Tick(Slate, Plugin->GetBaseDir() / TEXT("Resources"));
#endif
        auto* PC = World->GetFirstPlayerController();
        UObject* Core = DeliveryFor(PC);
        const auto* Open = Core ? FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("PhoneOpen")) : nullptr;
        RefreshVehiclePaint(PC, Core);
        ApplyWorkshopDriveMultiplier(PC, Core);
        RefreshCargoModels(PC, Core);
        RefreshMotorcycleLamp(PC, Core);
        TrackParkedMapVehicle(PC);
        BlockMountedStoreEntry(PC);
        UpdateRecipientCollision(Core);
        const bool bPhoneOpen = Open && Open->GetPropertyValue_InContainer(Core);
        if (VolumeWorld.Get() != World && World->AllowAudioPlayback())
        {
            VolumeWorld = World;
            for (int32 Index = 0; Index < UE_ARRAY_COUNT(AudioKeys); ++Index)
                GConfig->GetFloat(TEXT("BogotaAudio"), AudioKeys[Index], AudioLevels[Index], GGameUserSettingsIni);
            ApplyAudioLevels(World);
        }
        if (World->AllowAudioPlayback() && FPlatformTime::Seconds() >= NextAudioScan)
        {
            NextAudioScan = FPlatformTime::Seconds() + .5;
            AssignAudioCategories();
        }
        if (!bStartupShown && Core && PC && PC->GetPawn())
        {
            bStartupShown = true;
            bAtStartup = true;
            OpenPause(View, PC);
            if (!PauseMenu) bStartupShown = bAtStartup = false;
            else UE_LOG(LogTemp, Display, TEXT("Bogota UI: menu principal listo"));
        }
        if (bStartupShown) FindStartupPreparation(World, View);
        if (bAtStartup && bStartupVideo && (!VideoMenu.IsValid() || !VideoMenu->IsInViewport()))
        {
            bStartupVideo = false;
            OpenPause(View, PC);
            if (PauseMenu) ShowPausePage(EPausePage::Settings);
        }
        if (bStartupShown && !bAtStartup && PC && !StartupPreparationFinished(PC, View)) return;
        UpdateTutorial(PC, Core, bPhoneOpen);
        UpdateValeriaPortrait();
        TrackSession(PC, Core);
        TrackSpecialTimers(Core, World);
        ApplySpecialOfferPremium(Core);
        TrackDeliveries(Core);
        StyleVideoMenu(World);
        UpdatePickupMarker(Core);
        RemoveLegacyPickupGuides(World);
        if (auto* Pickup = Cast<AActor>(ReadObject(Core, TEXT("PickupMarker")))) Pickup->SetActorHiddenInGame(true);
        if (auto* Recipient = ReadObject(Core, TEXT("Recipient")))
            if (auto* Marker = Cast<UStaticMeshComponent>(ReadObject(Recipient, TEXT("Marker")))) Marker->SetVisibility(false);
        UpdateRouteHUD(View, PC, Core, bPhoneOpen);
        if (!Open || !Open->GetPropertyValue_InContainer(Core))
        {
            if (Overlay) Close();
            UpdateMinimap(PhoneFor(Core));
            return;
        }
        MinimapPanel.Reset();
        if (!Overlay)
        {
            Viewport = View;
            Controller = PC;
            WorldState.Reset();
            Show(TEXT("Inicio"));
        }
        if (UUserWidget* Widget = PhoneFor(Core))
        {
            LegacyPhone = Widget;
            if (auto* Frame = Widget->GetWidgetFromName(TEXT("Frame")))
                Frame->SetRenderTransformPivot(FVector2D::ZeroVector);
            if (auto* ArtWidget = Widget->GetWidgetFromName(TEXT("PhoneArt")))
                ArtWidget->SetRenderScale(FVector2D(1,1));
            Widget->SetRenderOpacity(0.f);
            for (const TCHAR* Name : {TEXT("PhoneArt"), TEXT("PhoneShade"), TEXT("PhoneHints")})
                if (auto* Part = Widget->GetWidgetFromName(Name)) Part->SetRenderOpacity(0.f);
            Widget->SetVisibility(ESlateVisibility::HitTestInvisible);
        }
        RefreshElapsed += DeltaTime;
        if (Overlay && RefreshElapsed >= 0.5f)
        {
            RefreshElapsed = 0.f;
            RefreshWorld();
            RefreshOrders();
            RefreshGarage();
        }
    }

    bool HandleMouseWheelOrGestureEvent(FSlateApplication&, const FPointerEvent& Event, const FPointerEvent*) override
    {
        if (!bMapPage || !MapOpening || !MapOpening->GetCachedGeometry().IsUnderLocation(Event.GetScreenSpacePosition()))
            return false;
        ChangeMapZoom(Event.GetWheelDelta());
        return true;
    }

    void ChangeMapZoom(float Steps)
    {
        MapZoom = FMath::Clamp(MapZoom * FMath::Pow(1.25f, Steps), 1.f, 3.f);
        SetMapPan(MapPan);
    }

    void SetMapPan(const FVector2D& Pan)
    {
        const double Limit = (MapZoom - 1.) * .5;
        MapPan = FVector2D(FMath::Clamp(Pan.X, -Limit, Limit), FMath::Clamp(Pan.Y, -Limit, Limit));
    }

    // T_Mapa covers a 1280 m square. The minimap samples 16% of that texture.
    static constexpr double CityMapSpan = 128000.;
    static constexpr double MinimapSpan = CityMapSpan * .16;

    static FVector2D MapDelta(const FVector& WorldDelta, bool bMinimap)
    {
        return FVector2D(WorldDelta.Y, -WorldDelta.X) / (bMinimap ? MinimapSpan : CityMapSpan);
    }

    FVector2D MapPoint(const FVector& Position) const
    {
        return FVector2D(.5,.5) + MapDelta(Position, false) * MapZoom + MapPan;
    }

    static bool IsMapPointVisible(FVector2D Point)
    {
        return Point.X > .04 && Point.X < .96 && Point.Y > .04 && Point.Y < .96;
    }

    static AActor* ParkedVehicleFor(APlayerController* PC)
    {
        auto* Pawn = PC ? PC->GetPawn().Get() : nullptr;
        const auto* Riding = Pawn ? FindFProperty<FBoolProperty>(Pawn->GetClass(), TEXT("Riding")) : nullptr;
        if ((Riding && Riding->GetPropertyValue_InContainer(Pawn))
            || ReadNumber(Pawn, TEXT("TransitionState"), 0) != 0) return nullptr;
        auto* Vehicle = Cast<AActor>(ReadObject(Pawn, TEXT("ParkedVehicle")));
        return IsValid(Vehicle) && !Vehicle->IsHidden() ? Vehicle : nullptr;
    }

    void TrackParkedMapVehicle(APlayerController* PC)
    {
        auto* Vehicle = ParkedVehicleFor(PC);
        if (ParkedMapVehicle.Get() == Vehicle) return;
        ParkedMapVehicle = Vehicle;
        // Sample the final parked transform once, after the dismount has finished.
        if (Vehicle) ParkedMapLocation = Vehicle->GetActorLocation();
    }

    bool HasMinimap() const
    {
        return MinimapPanel.IsValid() && RouteCanvas && RouteController.IsValid() && RouteController->GetPawn()
            && !PauseMenu && !MinimapPanel->GetCachedGeometry().GetLocalSize().IsNearlyZero();
    }

    FMargin MinimapBounds() const
    {
        if (!HasMinimap()) return FMargin(0);
        const FGeometry& Panel = MinimapPanel->GetCachedGeometry();
        const FGeometry& Canvas = RouteCanvas->GetTickSpaceGeometry();
        const FVector2D TopLeft = Canvas.AbsoluteToLocal(Panel.LocalToAbsolute(FVector2D::ZeroVector));
        const FVector2D Size = Canvas.AbsoluteToLocal(Panel.LocalToAbsolute(Panel.GetLocalSize())) - TopLeft;
        return FMargin(TopLeft.X, TopLeft.Y, Size.X, Size.Y);
    }

    const FSlateBrush* VehicleMapArt(APlayerController* PC)
    {
        auto* Core = DeliveryFor(PC);
        const FName Model = ReadName(ParkedVehicleFor(PC), TEXT("ModelID"));
        const bool bMoto = !Model.IsNone() ? Model == ReadName(Core, TEXT("MotoModel"))
            : ReadNumber(Core, TEXT("Vehicle"), 0) == 1;
        return Art(bMoto ? TEXT("MotoIconoSolo") : TEXT("CiclaMapa"));
    }

    int32 PaintMinimap(const FGeometry& Geometry, FSlateWindowElementList& Out, int32 Layer)
    {
        auto* PC = RouteController.Get();
        const auto* Pawn = PC ? PC->GetPawn().Get() : nullptr;
        const auto* CityArt = FullMapArt();
        const FVector2D Size = Geometry.GetLocalSize();
        if (!Pawn || !CityArt->GetResourceObject() || Size.X < 1. || Size.Y < 1.) return Layer;

        const FVector2D Center = Size * .5;
        const FVector Origin = Pawn->GetActorLocation();
        const FVector ViewForward = FRotator(0., PC->GetControlRotation().Yaw, 0.).Vector();
        const FVector2D ViewHeading = MapDelta(ViewForward, true);
        const FQuat2D NorthToView(-FMath::Atan2(ViewHeading.X, -ViewHeading.Y));
        const double Scale = Size.X;
        // Expand the texture past the visible rectangle so its corners stay covered at every heading.
        const double Side = Size.Size() + 2.;
        const double HalfUV = Side * .5 / Scale * (MinimapSpan / CityMapSpan);
        const FVector2D OriginUV = FVector2D(.5,.5) + MapDelta(Origin, false);
        MinimapBrush = *CityArt;
        MinimapBrush.SetUVRegion(FBox2f(FVector2f(OriginUV - FVector2D(HalfUV)),
                                       FVector2f(OriginUV + FVector2D(HalfUV))));
        FSlateDrawElement::MakeBox(Out, Layer, Geometry.ToPaintGeometry(FVector2D(Side),
            FSlateLayoutTransform(Center - FVector2D(Side * .5)), FSlateRenderTransform(NorthToView)),
            &MinimapBrush);

        auto Project = [&](const FVector& Position)
        {
            return Center + NorthToView.TransformPoint(MapDelta(Position - Origin, true) * Scale);
        };
        auto DrawIcon = [&](const FSlateBrush* Brush, FVector2D Point, FVector2D IconSize, int32 IconLayer, double Angle = 0.)
        {
            if (Brush)
                FSlateDrawElement::MakeBox(Out, IconLayer,
                    Geometry.ToPaintGeometry(IconSize, FSlateLayoutTransform(Point - IconSize * .5),
                        FSlateRenderTransform(FQuat2D(Angle))), Brush);
        };
        auto* Core = DeliveryFor(PC);
        auto* Phone = PhoneFor(Core);
        const auto* Route = Phone ? FindFProperty<FArrayProperty>(Phone->GetClass(), TEXT("NavigationPoints")) : nullptr;
        const auto* RoutePoint = Route ? CastField<FStructProperty>(Route->Inner) : nullptr;
        if (RoutePoint && RoutePoint->Struct == TBaseStructure<FVector>::Get())
        {
            FScriptArrayHelper Points(Route, Route->ContainerPtrToValuePtr<void>(Phone));
            TArray<FVector2D> Line;
            Line.Reserve(Points.Num());
            for (int32 Index = 0; Index < Points.Num(); ++Index)
                Line.Add(Project(*reinterpret_cast<const FVector*>(Points.GetRawPtr(Index))));
            if (Line.Num() > 1)
                FSlateDrawElement::MakeLines(Out, Layer + 1, Geometry.ToPaintGeometry(), Line,
                    ESlateDrawEffect::None, FLinearColor(1.f,.57f,.12f), true, 2.f);
        }

        const auto* WaypointOn = Core ? FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("HasWaypoint")) : nullptr;
        const auto* Waypoint = Core ? FindFProperty<FStructProperty>(Core->GetClass(), TEXT("Waypoint")) : nullptr;
        const auto State = ReadNumber(Core, TEXT("State"), 0);
        TOptional<FVector> Target;
        if (State == 2 || State == 3) Target = OrderTarget(Core);
        else if (WaypointOn && WaypointOn->GetPropertyValue_InContainer(Core)
                 && Waypoint && Waypoint->Struct == TBaseStructure<FVector>::Get())
            Target = *Waypoint->ContainerPtrToValuePtr<FVector>(Core);
        if (Target) DrawIcon(Art(TEXT("Destino")), Project(*Target), FVector2D(18), Layer + 2);

        if (ParkedMapVehicle.IsValid())
            DrawIcon(VehicleMapArt(PC), Project(ParkedMapLocation), FVector2D(38,29), Layer + 3);
        const FVector2D RiderHeading = NorthToView.TransformPoint(MapDelta(Pawn->GetActorForwardVector(), true));
        DrawIcon(Art(TEXT("JugadorMapa")), Center, FVector2D(36), Layer + 4,
            FMath::Atan2(RiderHeading.X, -RiderHeading.Y));
        return Layer + 4;
    }

    TSharedRef<SWidget> MapMarker(bool bVehicle)
    {
        if (bVehicle)
            return SNew(SImage).Image_Lambda([this] { return VehicleMapArt(Controller.Get()); });

        return SNew(SImage).Image(Art(TEXT("JugadorMapa")))
            .RenderTransformPivot(FVector2D(.5,.5))
            .RenderTransform_Lambda([this] {
                const auto* PC = Controller.Get();
                const APawn* Pawn = PC ? PC->GetPawn() : nullptr;
                if (!Pawn) return TOptional<FSlateRenderTransform>();
                const FVector2D Heading = MapDelta(Pawn->GetActorForwardVector(), false) * FVector2D(292,354);
                return TOptional<FSlateRenderTransform>(
                    FSlateRenderTransform(FQuat2D(FMath::Atan2(Heading.X, -Heading.Y))));
            });
    }

    bool HandleKeyDownEvent(FSlateApplication&, const FKeyEvent& Event) override
    {
        if (Event.IsRepeat()) return false;
        const bool bBack = Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::Gamepad_FaceButton_Right;
        const bool bPauseButton = Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::Gamepad_Special_Right;
        auto* View = GEngine ? GEngine->GameViewport.Get() : nullptr;
        auto* World = View ? View->GetWorld() : nullptr;
        auto* PC = World && World->IsGameWorld() ? World->GetFirstPlayerController() : nullptr;
        auto* Core = DeliveryFor(PC);
        if (Core && !World->IsPaused() && !Overlay &&
            (Event.GetKey() == EKeys::LeftShift || Event.GetKey() == EKeys::RightShift ||
             Event.GetKey() == EKeys::Gamepad_RightShoulder || Event.GetKey() == EKeys::Gamepad_RightTrigger))
        {
            const APawn* Pawn = PC->GetPawn();
            const auto* Riding = Pawn ? FindFProperty<FBoolProperty>(Pawn->GetClass(), TEXT("Riding")) : nullptr;
            if (Riding && Riding->GetPropertyValue_InContainer(Pawn)) return true;
        }
        if (Core && Event.GetKey() == EKeys::L && !Overlay && !World->IsPaused() &&
            IsOnMotorcycle(PC, Core) && !(View->ViewportConsole && View->ViewportConsole->ConsoleActive()))
        {
            bMotorcycleLamp = !bMotorcycleLamp;
            RefreshMotorcycleLamp(PC, Core);
            return true;
        }
        if (bAtStartup && PauseMenu)
        {
            if (bBack && PausePage != EPausePage::Main)
            {
                if (PausePage == EPausePage::Sound) SaveAudioSettings();
                ShowPausePage(PausePage == EPausePage::Sound ? EPausePage::Settings : EPausePage::Main);
                return true;
            }
            if (PausePage == EPausePage::Main)
            {
                const FString Key = Event.GetKey().GetFName().ToString();
                if (Key.Len() == 1 && FChar::IsAlpha(Key[0]))
                {
                    StartupCode = (StartupCode + Key.ToUpper()).Right(6);
                    if (StartupCode == TEXT("ESOYAM")) EnterDeveloperGame(World);
                    return true;
                }
            }
            return false;
        }
        if (PauseMenu && (bBack || bPauseButton))
        {
            if (PausePage != EPausePage::Main) { if (PausePage == EPausePage::Sound) SaveAudioSettings(); ShowPausePage(PausePage == EPausePage::Sound ? EPausePage::Settings : EPausePage::Main); }
            else ClosePause();
            return true;
        }
        if (Core && (bPauseButton || (Overlay && bBack)) && !bPaintPickerOpen && !World->IsPaused() &&
            !(View->ViewportConsole && View->ViewportConsole->ConsoleActive()))
        {
            if (Overlay)
            {
                if (CurrentPhonePage != TEXT("Inicio"))
                    Navigate(CurrentPhonePage == TEXT("Cicla") || CurrentPhonePage == TEXT("Moto") || CurrentPhonePage == TEXT("Carga")
                        ? TEXT("Taller") : TEXT("Inicio"));
                else { Invoke(Core, TEXT("TogglePhone")); Close(); }
                return true;
            }
            OpenPause(View, PC);
            return true;
        }
        if (Event.GetKey() == EKeys::M && Core && !World->IsPaused() &&
            !(View->ViewportConsole && View->ViewportConsole->ConsoleActive()) &&
            !Event.IsControlDown() && !Event.IsAltDown() && !Event.IsCommandDown())
        {
            if (CompletesDeveloperCode(World)) return false;
            Viewport = View;
            Controller = PC;
            if (Overlay && bMapPage)
            {
                Invoke(Core, TEXT("TogglePhone"));
                Close();
                return true;
            }
            const auto* Open = FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("PhoneOpen"));
            if (!Open || !Open->GetPropertyValue_InContainer(Core))
                Invoke(PC->GetPawn(), TEXT("PhonePressed"));
            if (Open && Open->GetPropertyValue_InContainer(Core))
                Navigate(TEXT("Mapa"));
            return true;
        }
        if (!Overlay) return false;
        if (Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::Tab)
        {
            if (bPaintPickerOpen) { PaintHSV = PickerInitialHSV; bPaintPickerOpen = false; RefreshGarage(); return true; }
            Invoke(DeliveryFor(Controller.Get()), TEXT("TogglePhone"));
            Close();
            return true;
        }
        return false;
    }

    void ClosePause()
    {
        auto* PC = PauseController.Get();
        if (PauseViewport.IsValid() && PauseMenu) PauseViewport->RemoveViewportWidgetContent(PauseMenu.ToSharedRef());
        PauseMenu.Reset();
        if (PC)
        {
            PC->SetPause(false);
            PC->bShowMouseCursor = false;
            PC->SetInputMode(FInputModeGameOnly());
        }
        RestoreLegacyHUD();
        PauseController.Reset();
        PauseViewport.Reset();
    }

    enum class EPausePage { Main, Save, Load, Settings, Sound, Exit, MainMenu };

    static constexpr const TCHAR* AudioKeys[] = {
        TEXT("MasterVolume"), TEXT("AmbienceVolume"), TEXT("EffectsVolume"), TEXT("MusicVolume"), TEXT("DialogueVolume")
    };
    static constexpr const TCHAR* AudioLabels[] = {
        TEXT("General"), TEXT("Ambiente"), TEXT("Efectos"), TEXT("Música"), TEXT("Diálogos de NPC")
    };

    void AssignAudioCategories()
    {
        if (!AudioMix.IsValid()) return;
        for (TObjectIterator<USoundBase> It; It; ++It)
        {
            auto* Sound = *It;
            if (!IsValid(Sound) || Sound->IsTemplate() || !AudioClass[0].IsValid()) continue;
            bool bAssigned = false;
            for (const auto& Category : AudioClass) bAssigned |= Sound->SoundClassObject == Category.Get();
            if (bAssigned) continue;
            const FString Path = Sound->GetPathName();
            const FString Name = Sound->GetName();
            if (!Path.StartsWith(TEXT("/Game/"))) continue;
            const int32 Category = Path.Contains(TEXT("/NPC/")) || Name.Contains(TEXT("Voice")) || Name.Contains(TEXT("Announcement"))
                ? 3 : Name.Contains(TEXT("Music")) || Path.Contains(TEXT("/Music/")) ? 2
                : Path.Contains(TEXT("/Ambience/")) || Name.Contains(TEXT("Rain")) || Name.Contains(TEXT("Ambience"))
                    || Name.Contains(TEXT("Thunder")) ? 0 : 1;
            Sound->SoundClassObject = AudioClass[Category].Get();
        }
    }

    void ApplyAudioLevels(UWorld* World)
    {
        if (!World) return;
        for (float& Value : AudioLevels) Value = FMath::Clamp(Value, 0.f, 1.f);
        if (auto Device = World->GetAudioDevice())
        {
            if (!AudioMix.IsValid())
            {
                AudioMix.Reset(NewObject<USoundMix>(GetTransientPackage()));
                for (auto& Category : AudioClass) Category.Reset(NewObject<USoundClass>(GetTransientPackage()));
            }
            if (MixWorld.Get() != World)
            {
                MixWorld = World;
                for (auto& Category : AudioClass) Device->RegisterSoundClass(Category.Get());
                UGameplayStatics::PushSoundMixModifier(World, AudioMix.Get());
            }
            Device->SetTransientPrimaryVolume(AudioLevels[0]);
            for (int32 Index = 0; Index < UE_ARRAY_COUNT(AudioClass); ++Index)
                UGameplayStatics::SetSoundMixClassOverride(World, AudioMix.Get(), AudioClass[Index].Get(),
                    AudioLevels[Index + 1], 1.f, .04f, false);
            AssignAudioCategories();
        }
        if (IFMODStudioModule::IsAvailable())
            if (auto* Studio = IFMODStudioModule::Get().GetStudioSystem(EFMODSystemContext::Runtime))
            {
                FMOD::Studio::Bus* Master = nullptr;
                if (Studio->getBus("bus:/", &Master) == FMOD_OK && Master)
                    Master->setVolume(AudioLevels[0] * AudioLevels[2]);
            }
    }

    static FString ProfileSlot(UObject* Core)
    {
        auto* Get = Core ? Core->FindFunction(TEXT("ProfileSlot")) : nullptr;
        const auto* Result = Get ? CastField<FStrProperty>(Get->GetReturnProperty()) : nullptr;
        if (!Result || Get->NumParms != 1) return {};
        FStructOnScope Args(Get);
        Core->ProcessEvent(Get, Args.GetStructMemory());
        return Result->GetPropertyValue_InContainer(Args.GetStructMemory());
    }

    void UseSaveSlot(int32 Slot)
    {
        auto* PC = PauseController.Get();
        auto* Core = DeliveryFor(PC);
        const FString Profile = ProfileSlot(Core);
        const FString Name = Slot == 0 ? TEXT("Bogota_Partida_Anterior") : FString::Printf(TEXT("Bogota_Partida_%d"), Slot);
        if (!PC || Profile.IsEmpty()) return;
        const bool bLoading = PausePage == EPausePage::Load;
        const auto* Dev = FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("DeveloperMode"));
        if (Dev && Dev->GetPropertyValue_InContainer(Core))
        {
            PauseStatus = FText::FromString(TEXT("Sal del modo desarrollador primero"));
            return;
        }
        if (bLoading && !UGameplayStatics::DoesSaveGameExist(Name, 0)) return;
        if ((bLoading || UGameplayStatics::DoesSaveGameExist(Name, 0)) && PendingSlot != Slot)
        {
            PendingSlot = Slot;
            PauseStatus = FText::FromString(bLoading ? TEXT("Pulsa otra vez para cargar y reiniciar") : TEXT("Pulsa otra vez para sobrescribir"));
            return;
        }
        if (!bLoading && !SaveCurrentSession(PC, Core))
        {
            PauseStatus = FText::FromString(TEXT("El juego no pudo guardar"));
            return;
        }
        TArray<uint8> Data;
        if (!UGameplayStatics::LoadDataFromSlot(Data, bLoading ? Name : Profile, 0) ||
            !UGameplayStatics::SaveDataToSlot(Data, bLoading ? Profile : Name, 0))
        {
            PauseStatus = FText::FromString(TEXT("No se pudo escribir la partida"));
            return;
        }
        PendingSlot = INDEX_NONE;
        PauseStatus = FText::FromString(TEXT("Partida guardada"));
        if (bLoading)
        {
            UWorld* World = PC->GetWorld();
            bAtStartup = false;
            TutorialStep = INDEX_NONE;
            ClosePause();
            ReloadCity(World);
        }
    }

    static void ReloadCity(UWorld* World)
    {
        // Slate callbacks must finish before destroying the current world.
        FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Level = TWeakObjectPtr<UWorld>(World)](float)
        {
            if (Level.IsValid())
                UGameplayStatics::OpenLevel(Level.Get(), FName(TEXT("/Game/Maps/Bogota_Juego_Final")));
            return false;
        }));
    }

    void EnterDeveloperGame(UWorld* World)
    {
        if (!World) return;
        static const TWeakObjectPtr<UClass> CodeClass(FindObject<UClass>(nullptr,
            TEXT("/Game/Delivery/BlueprintGameplay/Developer/BP_DeveloperCodes.BP_DeveloperCodes_C")));
        if (!CodeClass.IsValid()) return;
        for (TActorIterator<AActor> It(World, CodeClass.Get()); It; ++It)
        {
            auto* Feed = It->FindFunction(TEXT("FeedLetter"));
            const auto* Letter = Feed ? FindFProperty<FStrProperty>(Feed, TEXT("Letter")) : nullptr;
            if (!Letter) continue;
            bAtStartup = false;
            ClosePause();
            for (TCHAR Key : FString(TEXT("ESOYAM")))
            {
                FStructOnScope Args(Feed);
                Letter->SetPropertyValue_InContainer(Args.GetStructMemory(), FString::Chr(Key));
                It->ProcessEvent(Feed, Args.GetStructMemory());
            }
            return;
        }
        PauseStatus = FText::FromString(TEXT("No se pudo activar el modo desarrollador"));
    }

    void StartNewGame()
    {
        auto* PC = PauseController.Get();
        auto* Core = DeliveryFor(PC);
        if (!PC || !Core) return;
        const FString Profile = ProfileSlot(Core);
        if (Profile.IsEmpty()) return;
        const bool bHasProfile = UGameplayStatics::DoesSaveGameExist(Profile, 0);
        if (bHasProfile)
        {
            if (!bConfirmNew)
            {
                bConfirmNew = true;
                PauseStatus = FText::FromString(TEXT("Pulsa Nueva partida otra vez. Tu partida actual quedará en la ranura Anterior."));
                return;
            }
            TArray<uint8> Data;
            if (!UGameplayStatics::LoadDataFromSlot(Data, Profile, 0) ||
                !UGameplayStatics::SaveDataToSlot(Data, TEXT("Bogota_Partida_Anterior"), 0) ||
                !UGameplayStatics::DeleteGameInSlot(Profile, 0))
            {
                PauseStatus = FText::FromString(TEXT("No se pudo respaldar o reiniciar la partida"));
                return;
            }
        }
        const FString Totals = FPaths::ProjectSavedDir() / TEXT("SaveGames/PhoneDeliveryTotals.txt");
        if (IFileManager::Get().FileExists(*Totals))
            IFileManager::Get().Move(*(Totals + TEXT(".anterior")), *Totals, true);
        TutorialStep = 0;
        TutorialDeliveries = 0;
        bTutorialDrifted = false;
        bConfirmNew = bAtStartup = false;
        TWeakObjectPtr<UWorld> World(PC->GetWorld());
        ClosePause();
        if (bHasProfile)
        {
            ReloadCity(World.Get());
        }
        UE_LOG(LogTemp, Display, TEXT("Bogota UI: tutorial de nueva partida iniciado"));
    }

    bool NearTutorialStore() const
    {
        auto* PC = RouteController.Get();
        auto* Pawn = PC ? PC->GetPawn().Get() : nullptr;
        const auto Target = OrderTarget(PC ? DeliveryFor(PC) : nullptr);
        return Pawn && Target && FVector::DistSquared2D(Pawn->GetActorLocation(), *Target) <= FMath::Square(450.);
    }

    void UpdateTutorial(APlayerController* PC, UObject* Core, bool bPhoneOpen)
    {
        if (TutorialStep == INDEX_NONE || !PC || !Core || bAtStartup || PC->GetWorld()->IsPaused()) return;
        if (TutorialStep == 7 && !bPhoneOpen)
        {
            const double Now = FPlatformTime::Seconds();
            if (TutorialFinishedUntil == 0.) TutorialFinishedUntil = Now + 12.;
            if (Now >= TutorialFinishedUntil) TutorialStep = INDEX_NONE;
        }
        auto* Pawn = PC->GetPawn().Get();
        const auto* Riding = Pawn ? FindFProperty<FBoolProperty>(Pawn->GetClass(), TEXT("Riding")) : nullptr;
        const bool Mounted = Riding && Riding->GetPropertyValue_InContainer(Pawn);
        const double State = ReadNumber(Core, TEXT("State"), 0);
        auto* HandlingClass = FindObject<UClass>(nullptr, TEXT("/Script/BogotaRuntime.BogotaTwoWheelHandling"));
        auto* Handling = HandlingClass ? PC->GetWorld()->GetSubsystemBase(HandlingClass) : nullptr;
        const int32 Previous = TutorialStep;
        switch (TutorialStep)
        {
        case 0: if (Mounted) TutorialStep = 1; break;
        case 1: if (State == 2) TutorialStep = TutorialDeliveries == 0 && !bTutorialDrifted ? 9 : 2; break;
        case 9:
            bTutorialDrifted = QueryBool(Handling, TEXT("IsDrifting"));
            if (bTutorialDrifted) TutorialStep = 2;
            [[fallthrough]];
        case 2:
            if (State == 3) TutorialStep = 5;
            else if (!Mounted && ReadObject(Core, TEXT("InsideStore"))) TutorialStep = 3;
            break;
        case 3:
            if (State == 3) TutorialStep = 5;
            else if (QueryBool(Core, TEXT("ShopReady"))) TutorialStep = 4;
            break;
        case 4: if (State == 3) TutorialStep = 5; break;
        case 5:
            if (State != 3)
            {
                const auto* Status = FindFProperty<FTextProperty>(Core->GetClass(), TEXT("StatusMessage"));
                if (Status && Status->GetPropertyValue_InContainer(Core).ToString().StartsWith(TEXT("Entrega completada")))
                    ++TutorialDeliveries;
                TutorialStep = TutorialDeliveries >= 2 && TutorialBill(Core) != INDEX_NONE ? 6 : 1;
            }
            break;
        }
        if (Previous != TutorialStep && Previous != 5) PlayTutorialSuccess(PC->GetWorld());
    }

    static void PlayTutorialSuccess(UWorld* World)
    {
        if (auto* Cue = LoadObject<USoundBase>(nullptr,
            TEXT("/Game/Audio/SharedSounds/Delivery/Accomplish_mission.Accomplish_mission")))
            UGameplayStatics::PlaySound2D(World, Cue, .65f);
    }

    FText TutorialText() const
    {
        if (TutorialStep == 1 && TutorialDeliveries == 1)
            return FText::FromString(TEXT("¡Bien hecho! Abre Pedidos con Tab y haz una segunda entrega."));
        if (TutorialStep == 1 && TutorialDeliveries >= 2)
            return FText::FromString(TEXT("Todavía no alcanza para Servicios. Acepta otro pedido para completar el saldo."));
        if (TutorialStep == 6)
        {
            auto* Core = DeliveryFor(RouteController.Get());
            const int32 Index = TutorialBill(Core);
            if (Index != INDEX_NONE)
                return FText::FromString(FString::Printf(TEXT("Abre el celular con Tab. En Servicios, paga %s por %s."),
                    Bills[Index].Name, *Pesos(ServicePayment(Core, Index))));
        }
        if (TutorialStep == 2 || TutorialStep == 9)
        {
            if (NearTutorialStore())
            {
                auto* Pawn = RouteController.IsValid() ? RouteController->GetPawn().Get() : nullptr;
                const auto* Riding = Pawn ? FindFProperty<FBoolProperty>(Pawn->GetClass(), TEXT("Riding")) : nullptr;
                return FText::FromString(Riding && Riding->GetPropertyValue_InContainer(Pawn)
                    ? TEXT("Baja de la cicla con F y entra a pie.") : TEXT("Entra al local a pie."));
            }
            if (TutorialStep == 2) return FText::FromString(TEXT("Sigue la ruta al local."));
        }
        if (TutorialStep == 5)
            return FText::FromString(CanDeliver(DeliveryFor(RouteController.Get()))
                ? TEXT("Cuando estés cerca, mantén E para entregar.") : TEXT("Sigue la ruta al cliente."));
        static const TCHAR* Tips[] = {
            TEXT("Soy Valeria. Busca la cicla en el minimapa y pulsa F para montar."),
            TEXT("Abre el celular con Tab. En Pedidos, mantén pulsada la oferta más cercana."),
            TEXT("Sigue la ruta al local. Baja de la cicla con F y entra a pie."),
            TEXT("Acércate al producto señalado y mantén E para recogerlo."),
            TEXT("Ve a la caja señalada y mantén E para pagar."),
            TEXT(""),
            TEXT("Abre Servicios en el celular para pagar tu primera factura."),
            TEXT("Terminaste el tutorial. Sigue jugando para mejorar el vehículo y tu bolsa."), TEXT(""),
            TEXT("En una curva, mantén Espacio mientras giras con A o D. Suéltalo para ganar impulso si cargaste el derrape.")
        };
        return TutorialStep >= 0 && TutorialStep < UE_ARRAY_COUNT(Tips)
            ? FText::FromString(Tips[TutorialStep]) : FText::GetEmpty();
    }

    void FindStartupPreparation(UWorld* World, UGameViewportClient* View)
    {
        if (StartupWorld.Get() != World)
        {
            if (LoadingCover) View->RemoveViewportWidgetContent(LoadingCover.ToSharedRef());
            LoadingCover.Reset();
            StartupWorld = World;
            StartupPreparation.Reset();
            StartupWaitStarted = 0.;
            auto* PrepClass = FindObject<UClass>(nullptr,
                TEXT("/Game/Reconstruction/Optimization/BP_StartupPreparation.BP_StartupPreparation_C"));
            if (PrepClass)
                for (TActorIterator<AActor> It(World, PrepClass); It; ++It)
                {
                    StartupPreparation = *It;
                    break;
                }
        }

        // The Blueprint creates its own cover at a higher Z-order than the graphics menu.
        if (auto* Loading = Cast<UUserWidget>(ReadObject(StartupPreparation.Get(), TEXT("LoadingScreen"))))
            Loading->SetVisibility(ESlateVisibility::Collapsed);
    }

    bool StartupPreparationFinished(APlayerController* PC, UGameViewportClient* View)
    {
        auto* Preparation = StartupPreparation.Get();
        if (!Preparation || !Preparation->IsActorTickEnabled())
        {
            if (LoadingCover) View->RemoveViewportWidgetContent(LoadingCover.ToSharedRef());
            LoadingCover.Reset();
            return true;
        }
        if (!LoadingCover)
        {
            static const FSlateColorBrush Shade(FLinearColor(.012f,.027f,.046f,.57f));
            LoadingCover = SNew(SOverlay).Visibility(EVisibility::HitTestInvisible).Clipping(EWidgetClipping::ClipToBoundsAlways)
                + SOverlay::Slot()[SNew(SScaleBox).Stretch(EStretch::ScaleToFill)
                    [SNew(SImage).Image(Art(TEXT("PreparacionCiudad")))]]
                + SOverlay::Slot()[SNew(SImage).Image(&Shade)]
                + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
                    [SNew(STextBlock).Font(SecondaryFont(24)).ColorAndOpacity(FLinearColor::White)
                     .Text(FText::FromString(TEXT("Preparando sombreadores y ciudad…")))];
            View->AddViewportWidgetContent(LoadingCover.ToSharedRef(), 10050);
        }
        if (StartupWaitStarted == 0.) StartupWaitStarted = FPlatformTime::Seconds();
        const auto Elapsed = FPlatformTime::Seconds() - StartupWaitStarted;
        if (Elapsed < 30.) return false;

        // A missing readiness signal must not leave its widget and input locks active forever.
        if (auto* Loading = Cast<UUserWidget>(ReadObject(Preparation, TEXT("LoadingScreen"))))
        {
            if (Loading->IsInViewport())
            {
                Loading->RemoveFromParent();
                PC->SetIgnoreMoveInput(false);
                PC->SetIgnoreLookInput(false);
            }
        }
        Preparation->SetActorTickEnabled(false);
        if (LoadingCover) View->RemoveViewportWidgetContent(LoadingCover.ToSharedRef());
        LoadingCover.Reset();
        UE_LOG(LogTemp, Warning, TEXT("Bogota UI: preparacion agotada; se entrega el control al menu inicial"));
        return true;
    }

    void OpenPause(UGameViewportClient* View, APlayerController* PC)
    {
        if (!View || !PC || !PC->SetPause(true)) return;
        PauseController = PC;
        PauseViewport = View;
        ShowPausePage(EPausePage::Main);
    }

    static TSharedPtr<SWidget> FirstFocusableControl(const TSharedRef<SWidget>& Root)
    {
        if (!Root->IsEnabled() || !Root->GetVisibility().IsVisible()) return nullptr;
        if (Root->SupportsKeyboardFocus()) return Root;
        auto* Children = Root->GetChildren();
        for (int32 Index = 0; Children && Index < Children->Num(); ++Index)
            if (auto Child = FirstFocusableControl(Children->GetChildAt(Index))) return Child;
        return nullptr;
    }

    void ShowPausePage(EPausePage Page)
    {
        auto* View = PauseViewport.Get();
        auto* PC = PauseController.Get();
        if (!View || !PC) return;
        if (PauseMenu) View->RemoveViewportWidgetContent(PauseMenu.ToSharedRef());
        PausePage = Page;
        PendingSlot = INDEX_NONE;
        PauseStatus = FText::GetEmpty();
        static const FSlateColorBrush Shade(FLinearColor(0, 0, 0, .55f));
        static const FSlateColorBrush Edge(FLinearColor(.025f,.095f,.14f));
        static const FSlateColorBrush Panel(FLinearColor(.011f,.027f,.041f));
        const bool bTitle = bAtStartup && Page == EPausePage::Main;
        auto Actions = SNew(SVerticalBox);
        const TCHAR* Title = bAtStartup && Page == EPausePage::Main ? TEXT("DELIVERAZY") : Page == EPausePage::Settings ? TEXT("AJUSTES") : Page == EPausePage::MainMenu ? TEXT("¿VOLVER AL MENÚ PRINCIPAL?") : Page == EPausePage::Exit ? TEXT("¿SALIR DEL JUEGO?") : Page == EPausePage::Sound ? TEXT("SONIDO") : Page == EPausePage::Save ? TEXT("GUARDAR PARTIDA")
            : Page == EPausePage::Load ? TEXT("CARGAR PARTIDA") : TEXT("PAUSA");
        const FSlateBrush* Logo = bAtStartup && Page == EPausePage::Main ? Art(TEXT("DELIVERAZY")) : nullptr;
        if (Logo)
            Actions->AddSlot().AutoHeight().Padding(0,0,0,22)
                [SNew(SBox).HeightOverride(46)
                 [SNew(SScaleBox).Stretch(EStretch::ScaleToFit)
                  [SNew(SImage).Image(Logo)]]];
        else if (bTitle)
            Actions->AddSlot().AutoHeight().Padding(0,0,0,22)
                [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                 .HAlign(HAlign_Left)
                 [SNew(STextBlock).Font(SecondaryFont(32)).ColorAndOpacity(FLinearColor::White)
                  .ShadowOffset(FVector2D(2,2)).ShadowColorAndOpacity(FLinearColor(.02f,.03f,.04f))
                  .Text(FText::FromString(Title))]];
        else
            Actions->AddSlot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,14)
                [SNew(STextBlock).Font(SecondaryFont(20)).Text(FText::FromString(Title))];
        auto Button = [&](TFunction<FText()> Label, FOnClicked Execute, bool bEnabled = true)
        {
            if (bAtStartup)
            {
                Actions->AddSlot().AutoHeight().Padding(0,5)
                    [SNew(SBox).HeightOverride(52)
                     [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").IsEnabled(bEnabled).OnClicked(Execute)
                      .HAlign(HAlign_Center).VAlign(VAlign_Center)
                      [SNew(STextBlock).Font(SecondaryFont(21)).ColorAndOpacity(FLinearColor::White)
                       .ShadowOffset(FVector2D(2,2)).ShadowColorAndOpacity(FLinearColor(.01f,.03f,.04f))
                       .Text_Lambda(MoveTemp(Label))]]];
                return;
            }
            Actions->AddSlot().AutoHeight().Padding(0,4)
                [SNew(SBox).HeightOverride(42)
                 [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").ContentPadding(0).IsEnabled(bEnabled).OnClicked(Execute)
                  [SNew(SOverlay)
                   + SOverlay::Slot()[SNew(SImage).Image(Art(TEXT("BotonReposo"))).DesiredSizeOverride(FVector2D(1,1))]
                   + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
                   [SNew(STextBlock).Font(SecondaryFont(14)).Text_Lambda(MoveTemp(Label))]]]];
        };
        auto Fixed = [&](const TCHAR* Label, FOnClicked Execute, bool bEnabled = true)
        {
            Button([Label] { return FText::FromString(Label); }, MoveTemp(Execute), bEnabled);
        };
        if (Page == EPausePage::Main && bAtStartup)
        {
            Fixed(TEXT("NUEVA PARTIDA"), FOnClicked::CreateLambda([this] { StartNewGame(); return FReply::Handled(); }));
            Fixed(TEXT("CARGAR PARTIDA"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Load); return FReply::Handled(); }));
            Fixed(TEXT("AJUSTES"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Settings); return FReply::Handled(); }));
            Fixed(TEXT("SALIR DEL JUEGO"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Exit); return FReply::Handled(); }));
            Actions->AddSlot().AutoHeight().HAlign(HAlign_Center).Padding(0,8)
                [SNew(STextBlock).Font(SecondaryFont(11)).WrapTextAt(310).Text_Lambda([this] { return PauseStatus; })];
        }
        else if (Page == EPausePage::Main)
        {
            Fixed(TEXT("CONTINUAR"), FOnClicked::CreateLambda([this] { ClosePause(); return FReply::Handled(); }));
            Fixed(TEXT("GUARDAR PARTIDA"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Save); return FReply::Handled(); }));
            Fixed(TEXT("CARGAR"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Load); return FReply::Handled(); }));
            Fixed(TEXT("AJUSTES"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Settings); return FReply::Handled(); }));
            Fixed(TEXT("VOLVER AL MENÚ PRINCIPAL"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::MainMenu); return FReply::Handled(); }));
            Fixed(TEXT("SALIR DEL JUEGO"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Exit); return FReply::Handled(); }));
        }
        else if (Page == EPausePage::Settings)
        {
            Fixed(TEXT("SONIDO"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Sound); return FReply::Handled(); }));
            Fixed(TEXT("VIDEO"), FOnClicked::CreateLambda([this]
            {
                bStartupVideo = bAtStartup;
                auto* Controller = PauseController.Get();
                ClosePause();
                if (Controller) OpenVideo(Controller->GetWorld());
                return FReply::Handled();
            }));
            Fixed(TEXT("VOLVER"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Main); return FReply::Handled(); }));
        }
        else if (Page == EPausePage::MainMenu)
        {
            Fixed(TEXT("GUARDAR Y VOLVER"), FOnClicked::CreateLambda([this] {
                if (!SaveCurrentSession(PauseController.Get(), DeliveryFor(PauseController.Get())))
                {
                    PauseStatus = FText::FromString(TEXT("No se pudo guardar la partida."));
                    return FReply::Handled();
                }
                bAtStartup = true;
                bConfirmNew = false;
                StartupCode.Reset();
                ShowPausePage(EPausePage::Main);
                return FReply::Handled();
            }));
            Fixed(TEXT("CANCELAR"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Main); return FReply::Handled(); }));
            Actions->AddSlot().AutoHeight().Padding(0,8)
                [SNew(STextBlock).Font(SecondaryFont(12)).Text_Lambda([this] { return PauseStatus; })];
        }
        else if (Page == EPausePage::Exit)
        {
            Fixed(TEXT("CONFIRMAR"), FOnClicked::CreateLambda([this]
            {
                if (auto* Controller = PauseController.Get())
                {
                    auto* Core = DeliveryFor(Controller);
                    const auto* Dev = Core ? FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("DeveloperMode")) : nullptr;
                    if (!bAtStartup && Core && !(Dev && Dev->GetPropertyValue_InContainer(Core)) &&
                        !SaveCurrentSession(Controller, Core))
                    {
                        PauseStatus = FText::FromString(TEXT("No se pudo guardar la partida."));
                        return FReply::Handled();
                    }
                    UKismetSystemLibrary::QuitGame(Controller->GetWorld(), Controller, EQuitPreference::Quit, false);
                }
                return FReply::Handled();
            }));
            Fixed(TEXT("VOLVER"), FOnClicked::CreateLambda([this] { ShowPausePage(EPausePage::Main); return FReply::Handled(); }));
            Actions->AddSlot().AutoHeight().Padding(0,8)
                [SNew(STextBlock).Font(SecondaryFont(12)).Text_Lambda([this] { return PauseStatus; })];
        }
        else
        {
            if (Page == EPausePage::Sound)
            {
                for (int32 Index = 0; Index < UE_ARRAY_COUNT(AudioLabels); ++Index)
                {
                    Actions->AddSlot().AutoHeight().Padding(0,4)
                        [SNew(STextBlock).Font(SecondaryFont(14)).Text_Lambda([this, Index] {
                            return FText::FromString(FString::Printf(TEXT("%s  %d %%"), AudioLabels[Index],
                                FMath::RoundToInt(AudioLevels[Index] * 100)));
                        })];
                    Actions->AddSlot().AutoHeight().Padding(0,3,0,8)
                        [SNew(SSlider).Value_Lambda([this, Index] { return AudioLevels[Index]; })
                         .OnValueChanged_Lambda([this, Index](float Value) {
                             AudioLevels[Index] = Value;
                             if (auto* Controller = PauseController.Get()) ApplyAudioLevels(Controller->GetWorld());
                         })
                         .OnMouseCaptureEnd_Lambda([this] { SaveAudioSettings(); })
                         .OnControllerCaptureEnd_Lambda([this] { SaveAudioSettings(); })];
                }
            }
            else
            {
                if (bAtStartup && Page == EPausePage::Load)
                    Fixed(TEXT("PARTIDA ACTUAL"), FOnClicked::CreateLambda([this] {
                        bConfirmNew = bAtStartup = false;
                        TutorialStep = INDEX_NONE;
                        ClosePause();
                        return FReply::Handled();
                    }), UGameplayStatics::DoesSaveGameExist(ProfileSlot(DeliveryFor(PC)), 0));
                for (int32 Slot = 1; Slot <= 3; ++Slot)
                    Button([Slot] {
                        const bool Exists = UGameplayStatics::DoesSaveGameExist(FString::Printf(TEXT("Bogota_Partida_%d"), Slot), 0);
                        return FText::FromString(FString::Printf(TEXT("PARTIDA %d  ·  %s"), Slot, Exists ? TEXT("Guardada") : TEXT("Vacía")));
                    }, FOnClicked::CreateLambda([this, Slot] { UseSaveSlot(Slot); return FReply::Handled(); }));
                if (Page == EPausePage::Load && UGameplayStatics::DoesSaveGameExist(TEXT("Bogota_Partida_Anterior"), 0))
                    Fixed(TEXT("PARTIDA ANTERIOR"), FOnClicked::CreateLambda([this] { UseSaveSlot(0); return FReply::Handled(); }));
            }
            Fixed(TEXT("VOLVER"), FOnClicked::CreateLambda([this] { if (PausePage == EPausePage::Sound) { SaveAudioSettings(); ShowPausePage(EPausePage::Settings); } else ShowPausePage(EPausePage::Main); return FReply::Handled(); }));
            Actions->AddSlot().AutoHeight().HAlign(HAlign_Center).Padding(0,8)
                [SNew(STextBlock).Font(SecondaryFont(11)).WrapTextAt(310).Text_Lambda([this] { return PauseStatus; })];
        }
        if (bAtStartup)
        {
            PauseMenu = SNew(SOverlay).Clipping(EWidgetClipping::ClipToBoundsAlways)
                + SOverlay::Slot()
                [SNew(SScaleBox).Stretch(EStretch::ScaleToFill)
                 [SNew(SImage).Image(Art(TEXT("PortadaCiudad")))]]
                + SOverlay::Slot().HAlign(HAlign_Right).VAlign(VAlign_Fill).Padding(48,24)
                [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                 [SNew(SBox).WidthOverride(400)[Actions]]];
        }
        else
        {
            PauseMenu = SNew(SOverlay)
                + SOverlay::Slot()[SNew(SImage).Image(&Shade)]
                + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
                [SNew(SBox).WidthOverride(360)
                 [SNew(SBorder).BorderImage(&Edge).Padding(2)
                  [SNew(SBorder).BorderImage(&Panel).Padding(22)[Actions]]]];
        }
        View->AddViewportWidgetContent(PauseMenu.ToSharedRef(), bAtStartup ? 10100 : 1300);
        PC->bShowMouseCursor = true;
        const auto Focus = FirstFocusableControl(Actions);
        PC->SetInputMode(FInputModeUIOnly().SetWidgetToFocus(Focus));
        if (Focus) FSlateApplication::Get().SetAllUserFocus(Focus, EFocusCause::Navigation);
    }

    void SaveAudioSettings()
    {
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(AudioKeys); ++Index)
            GConfig->SetFloat(TEXT("BogotaAudio"), AudioKeys[Index], AudioLevels[Index], GGameUserSettingsIni);
        GConfig->Flush(false, GGameUserSettingsIni);
    }

    void OpenVideo(UWorld* World)
    {
        for (TActorIterator<AActor> It(World); It; ++It)
            if (It->GetClass()->GetName().StartsWith(TEXT("BP_GraphicsSettings")))
            {
                Invoke(*It, TEXT("ToggleGraphics"));
                VideoMenu = Cast<UUserWidget>(ReadObject(*It, TEXT("Menu")));
                return;
            }
    }

    void RemoveRouteHUD()
    {
        if (RouteViewport.IsValid() && RouteHUD)
            RouteViewport->RemoveViewportWidgetContent(RouteHUD.ToSharedRef());
        RouteHUD.Reset();
        RouteCanvas.Reset();
        MinimapPanel.Reset();
        RouteViewport.Reset();
        RouteController.Reset();
        RestoreLegacyHUD();
    }

    void Close()
    {
        if (Viewport.IsValid() && Overlay) Viewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
        if (LegacyPhone.IsValid())
        {
            LegacyPhone->SetRenderOpacity(1.f);
            for (const TCHAR* Name : {TEXT("PhoneArt"), TEXT("PhoneShade"), TEXT("PhoneHints")})
                if (auto* Part = LegacyPhone->GetWidgetFromName(Name)) Part->SetRenderOpacity(1.f);
        }
        LegacyPhone.Reset();
        if (FSlateApplication::IsInitialized()) FSlateApplication::Get().SetAllUserFocusToGameViewport();
        Overlay.Reset();
        bGarageTutorialVisible = false;
        bPaintPickerOpen = false;
        PaintSelection = INDEX_NONE;
        bGarageMoto = false;
        Orders.Reset();
        OrderSnapshot.Reset();
        ActiveOrderSnapshot.Reset();
        OrderCapacitySnapshot = 0;
        HoldingOrder = INDEX_NONE;
        GarageImage.Reset();
        GarageBrush.SetResourceObject(nullptr);
        Clock.Reset();
        Weather.Reset();
        Viewport.Reset();
        Controller.Reset();

    }

private:
    static bool CompletesDeveloperCode(UWorld* World)
    {
        static TWeakObjectPtr<UClass> CodeClass;
        if (!CodeClass.IsValid())
            CodeClass = FindObject<UClass>(nullptr, TEXT("/Game/Delivery/BlueprintGameplay/Developer/BP_DeveloperCodes.BP_DeveloperCodes_C"));
        if (!CodeClass.IsValid()) return false;
        for (TActorIterator<AActor> It(World, CodeClass.Get()); It; ++It)
        {
            const auto* Buffer = FindFProperty<FStrProperty>(It->GetClass(), TEXT("CodeBuffer"));
            if (Buffer && World->GetTimeSeconds() - ReadNumber(*It, TEXT("LastKeyTime"), -10.) <= 3.
                && Buffer->GetPropertyValue_InContainer(*It).EndsWith(TEXT("ESOYA")))
                return true;
        }
        return false;
    }

    static bool IsOnMotorcycle(APlayerController* PC, UObject* Core)
    {
        const auto* Pawn = PC ? PC->GetPawn().Get() : nullptr;
        const auto* Riding = Pawn ? FindFProperty<FBoolProperty>(Pawn->GetClass(), TEXT("Riding")) : nullptr;
        return Riding && Riding->GetPropertyValue_InContainer(Pawn) && ReadNumber(Core, TEXT("Vehicle"), 0) == 1;
    }

    void RefreshMotorcycleLamp(APlayerController* PC, UObject* Core)
    {
        auto* Pawn = PC ? PC->GetPawn().Get() : nullptr;
        const bool bOn = bMotorcycleLamp && IsOnMotorcycle(PC, Core);
        if (MotorcycleLamp.IsValid() && MotorcycleLamp->GetOwner() != Pawn)
        {
            MotorcycleLamp->DestroyComponent();
            MotorcycleLamp.Reset();
        }
        if (bOn && !MotorcycleLamp.IsValid())
        {
            auto* Lamp = NewObject<USpotLightComponent>(Pawn);
            Pawn->AddInstanceComponent(Lamp);
            Lamp->SetupAttachment(Pawn->GetRootComponent());
            Lamp->SetRelativeLocation(FVector(76,0,36));
            Lamp->SetRelativeRotation(FRotator(-10,0,0));
            Lamp->SetIntensity(3800.f);
            Lamp->SetAttenuationRadius(2000.f);
            Lamp->SetInnerConeAngle(15.f);
            Lamp->SetOuterConeAngle(27.f);
            Lamp->SetLightColor(FLinearColor(1.f,.86f,.65f));
            Lamp->RegisterComponent();
            MotorcycleLamp = Lamp;
        }
        if (MotorcycleLamp.IsValid()) MotorcycleLamp->SetVisibility(bOn);
    }

    void BlockMountedStoreEntry(APlayerController* PC)
    {
        auto* Rider = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
        if (!Rider) { StoreRider.Reset(); LastOutsideStore.Reset(); return; }
        UWorld* World = Rider->GetWorld();
        if (!World || World->IsPaused()) return;
        if (StoreWorld.Get() != World)
        {
            StoreWorld = World;
            DeliveryStores.Reset();
            static const TStrongObjectPtr<UClass> StoreClass(LoadClass<AActor>(nullptr,
                TEXT("/Game/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore.BP_DeliveryStore_C")));
            if (StoreClass.IsValid())
                for (TActorIterator<AActor> It(World, StoreClass.Get()); It; ++It) DeliveryStores.Add(*It);
        }
        if (StoreRider.Get() != Rider)
        {
            StoreRider = Rider;
            LastOutsideStore.Reset();
        }

        const FVector Location = Rider->GetActorLocation();
        bool bInside = false;
        for (const auto& Entry : DeliveryStores)
        {
            auto* Store = Entry.Get();
            if (!Store || FVector::DistSquared2D(Store->GetActorLocation(), Location) > FMath::Square(3000.)) continue;
            auto* Query = Store->FindFunction(TEXT("ContainsVisitor"));
            const auto* Position = Query ? FindFProperty<FStructProperty>(Query, TEXT("Position")) : nullptr;
            const auto* Result = Query ? CastField<FBoolProperty>(Query->GetReturnProperty()) : nullptr;
            if (!Position || Position->Struct != TBaseStructure<FVector>::Get() || !Result) continue;
            FStructOnScope Args(Query);
            *Position->ContainerPtrToValuePtr<FVector>(Args.GetStructMemory()) = Location;
            Store->ProcessEvent(Query, Args.GetStructMemory());
            if (Result->GetPropertyValue_InContainer(Args.GetStructMemory()))
            {
                bInside = true;
                break;
            }
        }
        if (!bInside) { LastOutsideStore = Location; return; }

        const auto* Riding = FindFProperty<FBoolProperty>(Rider->GetClass(), TEXT("Riding"));
        if (LastOutsideStore && Riding && Riding->GetPropertyValue_InContainer(Rider))
        {
            if (FVector::DistSquared(LastOutsideStore.GetValue(), Location) <= FMath::Square(250.))
            {
                Rider->SetActorLocation(LastOutsideStore.GetValue(), false, nullptr, ETeleportType::TeleportPhysics);
                Rider->GetCharacterMovement()->StopMovementImmediately();
            }
        }
    }

    void UpdateRecipientCollision(UObject* Core)
    {
        auto* Recipient = Cast<AActor>(ReadObject(Core, TEXT("Recipient")));
        if (RecipientCollision.IsValid() && RecipientCollision.Get() == Recipient) return;
        RecipientCollision = Recipient;
        if (!IsValid(Recipient) || !Recipient->GetRootComponent()) return;
        auto* Capsule = NewObject<UCapsuleComponent>(Recipient);
        Recipient->AddInstanceComponent(Capsule);
        Capsule->SetupAttachment(Recipient->GetRootComponent());
        Capsule->SetCapsuleSize(24, 67);
        Capsule->SetRelativeLocation(FVector(0,0,65));
        Capsule->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        Capsule->SetCollisionObjectType(ECC_WorldDynamic);
        Capsule->SetCollisionResponseToAllChannels(ECR_Ignore);
        Capsule->SetCollisionResponseToChannel(ECC_Pawn, ECR_Block);
        Capsule->RegisterComponent();
        Recipient->SetActorEnableCollision(true);
    }

    void UpdateMinimap(UUserWidget* Phone)
    {
        if (Phone) Phone->SetRenderOpacity(bAtStartup ? 0.f : 1.f);
        auto* ArtWidget = Phone ? Cast<UImage>(Phone->GetWidgetFromName(TEXT("PhoneArt"))) : nullptr;
        auto* Frame = Phone ? Cast<UBorder>(Phone->GetWidgetFromName(TEXT("Frame"))) : nullptr;
        auto* ArtSlot = ArtWidget ? Cast<UCanvasPanelSlot>(ArtWidget->Slot) : nullptr;
        const auto* Bezel = Art(TEXT("Minimapa"));
        if (!ArtSlot || !Frame || !Bezel) return;
        if (ArtWidget->GetBrush().GetResourceObject() != Bezel->GetResourceObject()) ArtWidget->SetBrush(*Bezel);
        const FVector2D Base = ArtSlot->GetSize() / FVector2D(300, 180);
        ArtWidget->SetRenderTransformPivot(FVector2D(0,1));
        constexpr double MinimapScale = 1.48;
        ArtWidget->SetRenderScale(FVector2D(MinimapScale,MinimapScale));
        Frame->SetRenderTransformPivot(FVector2D(0,1));
        Frame->SetRenderScale(Base * MinimapScale);
        for (const TCHAR* Name : {TEXT("Notice"), TEXT("EnergyBar"), TEXT("HoldBar")})
            if (auto* Widget = Phone->GetWidgetFromName(Name)) Widget->SetRenderOpacity(0.f);

        MinimapPanel = Phone->GetWidgetFromName(TEXT("MiniMap"));
    }

    static bool QueryBool(UObject* Object, FName Name)
    {
        auto* Function = Object ? Object->FindFunction(Name) : nullptr;
        const auto* Result = Function ? CastField<FBoolProperty>(Function->GetReturnProperty()) : nullptr;
        if (!Result || Function->NumParms != 1) return false;
        FStructOnScope Args(Function);
        Object->ProcessEvent(Function, Args.GetStructMemory());
        return Result->GetPropertyValue_InContainer(Args.GetStructMemory());
    }

    struct FDeliveryRecord
    {
        FDateTime Date;
        int64 Payment = 0;
        double Meters = 0;
        int32 Kind = INDEX_NONE;
        FIntPoint Zone = FIntPoint::ZeroValue;
        bool bHasZone = false;
    };

    static FDeliveryRecord ReadDeliveryRecord(UObject* Core)
    {
        FDeliveryRecord Record;
        const auto* Order = FindFProperty<FStructProperty>(Core->GetClass(), TEXT("Order"));
        if (!Order) return Record;
        const void* Data = Order->ContainerPtrToValuePtr<void>(Core);
        for (TFieldIterator<FProperty> It(Order->Struct); It; ++It)
        {
            const FString Name = It->GetName();
            if (Name.StartsWith(TEXT("DistanceMeters")))
            {
                if (const auto* Field = CastField<FNumericProperty>(*It); Field && Field->IsFloatingPoint())
                    Record.Meters = FMath::Max(0., Field->GetFloatingPointPropertyValue(Field->ContainerPtrToValuePtr<void>(Data)));
            }
            else if (Name.StartsWith(TEXT("StoreKind")))
            {
                if (const auto* Field = CastField<FNumericProperty>(*It); Field && Field->IsInteger())
                    Record.Kind = static_cast<int32>(Field->GetSignedIntPropertyValue(Field->ContainerPtrToValuePtr<void>(Data)));
            }
            else if (Name.StartsWith(TEXT("Dropoff_")) || Name == TEXT("Dropoff"))
            {
                const auto* Field = CastField<FStructProperty>(*It);
                if (Field && Field->Struct == TBaseStructure<FVector>::Get())
                {
                    const FVector Position = *Field->ContainerPtrToValuePtr<FVector>(Data);
                    Record.Zone = FIntPoint(FMath::FloorToInt(Position.X / 10000.), FMath::FloorToInt(Position.Y / 10000.));
                    Record.bHasZone = true;
                }
            }
        }
        return Record;
    }

    struct FStatsSummary
    {
        int32 Count = 0;
        int64 Money = 0;
        double Meters = 0;
        TMap<int32, int32> Kinds;
        TMap<FIntPoint, int32> Zones;
        double MoneyByDay[7]{};
        double MetersByDay[7]{};
    };

    void RefreshDeliverySummary()
    {
        Summary = {};
        const FDateTime Today = FDateTime::Today();
        const int32 DaysSinceMonday = static_cast<int32>(Today.GetDayOfWeek());
        if (StatsPeriod == 2)
        {
            Summary.Count = Deliveries - DeliveryHistory.Num();
            Summary.Money = Earnings;
            for (const auto& Row : DeliveryHistory) Summary.Money -= Row.Payment;
        }
        for (const auto& Row : DeliveryHistory)
        {
            const int32 Age = (Today - Row.Date.GetDate()).GetDays();
            if ((StatsPeriod == 0 && Age != 0) || (StatsPeriod == 1 && (Age < 0 || Age > DaysSinceMonday))) continue;
            ++Summary.Count;
            Summary.Money += Row.Payment;
            Summary.Meters += Row.Meters;
            if (Row.Kind >= 0) ++Summary.Kinds.FindOrAdd(Row.Kind);
            if (Row.bHasZone) ++Summary.Zones.FindOrAdd(Row.Zone);
            if (Age >= 0 && Age < 7)
            {
                Summary.MoneyByDay[6 - Age] += Row.Payment;
                Summary.MetersByDay[6 - Age] += Row.Meters;
            }
        }
        SummaryDate = Today;
    }

    void TrackDeliveries(UObject* Core)
    {
        if (!Core) { StatsCore.Reset(); return; }
        const auto* Developer = FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("DeveloperMode"));
        const bool bDeveloper = Developer && Developer->GetPropertyValue_InContainer(Core);
        const int32 Active = CountItems(Core, TEXT("ActiveOrders"));
        const int32 Balance = static_cast<int32>(ReadNumber(Core, TEXT("Balance"), 0));
        const auto* Status = FindFProperty<FTextProperty>(Core->GetClass(), TEXT("StatusMessage"));
        const FString Message = Status ? Status->GetPropertyValue_InContainer(Core).ToString() : FString();
        const FString File = FPaths::ProjectSavedDir() / TEXT("SaveGames/PhoneDeliveryTotals.txt");
        if (StatsCore.Get() != Core)
        {
            StatsCore = Core;
            FString Stored;
            FFileHelper::LoadFileToString(Stored, *File);
            TArray<FString> Values;
            Stored.ParseIntoArrayLines(Values);
            Deliveries = Values.IsValidIndex(0) ? FMath::Max(0, FCString::Atoi(*Values[0])) : 0;
            Earnings = Values.IsValidIndex(1) ? FMath::Max<int64>(0, FCString::Atoi64(*Values[1])) : 0;
            DeliveryHistory.Reset();
            for (int32 Index = 2; Index < Values.Num(); ++Index)
            {
                TArray<FString> Fields;
                Values[Index].ParseIntoArray(Fields, TEXT("|"), false);
                FDeliveryRecord Row;
                if (Fields.Num() != 7 || !FDateTime::ParseIso8601(*Fields[0], Row.Date)) continue;
                Row.Payment = FCString::Atoi64(*Fields[1]);
                Row.Meters = FCString::Atod(*Fields[2]);
                Row.Kind = FCString::Atoi(*Fields[3]);
                Row.Zone = FIntPoint(FCString::Atoi(*Fields[4]), FCString::Atoi(*Fields[5]));
                Row.bHasZone = Fields[6] == TEXT("1");
                if (Row.Payment > 0 && FMath::IsFinite(Row.Meters) && Row.Meters >= 0) DeliveryHistory.Add(Row);
            }
            RefreshDeliverySummary();
            PreviousActive = Active;
            PreviousBalance = Balance;
            bPreviousDeveloper = bDeveloper;
        }
        const int64 Payment = static_cast<int64>(Balance) - PreviousBalance;
        const bool bCompleted = PreviousActive > Active && Message.StartsWith(TEXT("Entrega completada"));
        if (!bDeveloper && !bPreviousDeveloper && bCompleted && Payment > 0)
        {
            Deliveries += PreviousActive - Active;
            Earnings += Payment;
            PreviousOrder.Date = FDateTime::Now();
            PreviousOrder.Payment = Payment;
            DeliveryHistory.Add(PreviousOrder);
            RefreshDeliverySummary();
            FString Data = FString::Printf(TEXT("%d\n%lld"), Deliveries, Earnings);
            for (const auto& Row : DeliveryHistory)
                Data += FString::Printf(TEXT("\n%s|%lld|%.3f|%d|%d|%d|%d"), *Row.Date.ToString(TEXT("%Y-%m-%dT%H:%M:%S")),
                    Row.Payment, Row.Meters, Row.Kind, Row.Zone.X, Row.Zone.Y, int32(Row.bHasZone));
            IFileManager::Get().MakeDirectory(*FPaths::GetPath(File), true);
            const FString Temp = File + TEXT(".tmp");
            if (!FFileHelper::SaveStringToFile(Data, *Temp)
                || !IFileManager::Get().Move(*File, *Temp, true))
                UE_LOG(LogTemp, Warning, TEXT("Could not save phone delivery totals"));
        }
        if (SummaryDate != FDateTime::Today()) RefreshDeliverySummary();
        if (ReadNumber(Core, TEXT("State"), 0) == 3) PreviousOrder = ReadDeliveryRecord(Core);
        else PreviousOrder = {};
        PreviousActive = Active;
        PreviousBalance = Balance;
        bPreviousDeveloper = bDeveloper;
    }

    static bool CanDeliver(UObject* Core)
    {
        return ReadNumber(Core, TEXT("State"), 0) == 3 && QueryBool(Core, TEXT("IsAtTarget"));
    }

    static TOptional<FVector> QueryPosition(UObject* Object, FName Function)
    {
        auto* Query = Object ? Object->FindFunction(Function) : nullptr;
        const auto* Result = Query ? CastField<FStructProperty>(Query->GetReturnProperty()) : nullptr;
        if (!Result || Query->NumParms != 1 || Result->Struct != TBaseStructure<FVector>::Get()) return {};
        FStructOnScope Args(Query);
        Object->ProcessEvent(Query, Args.GetStructMemory());
        return *Result->ContainerPtrToValuePtr<FVector>(Args.GetStructMemory());
    }

    static TOptional<FVector> OrderTarget(UObject* Core)
    {
        return QueryPosition(Core, TEXT("GetOrderTarget"));
    }

    static void UpdatePickupMarker(UObject* Core)
    {
        if (ReadNumber(Core, TEXT("State"), 0) != 2) return;
        auto* Marker = Cast<AActor>(ReadObject(Core, TEXT("PickupMarker")));
        if (!IsValid(Marker)) return;
        if (const auto Target = OrderTarget(Core))
        {
            const FVector Position = *Target + FVector(0, 0, 130);
            if (!Marker->GetActorLocation().Equals(Position, 1.0))
                Marker->SetActorLocation(Position);
        }
    }

    void StyleVideoMenu(UWorld* World)
    {
        if (!World->IsPaused()) { StyledVideo.Reset(); return; }
        const auto* Settings = GEngine ? GEngine->GetGameUserSettings() : nullptr;
        const int32 Preset = Settings ? Settings->GetOverallScalabilityLevel() : INDEX_NONE;
        if (StyledVideo.IsValid() && StyledVideo->IsInViewport() && StyledPreset == Preset) return;
        const auto* Panel = Art(TEXT("VideoPanel"));
        const auto* Button = Art(TEXT("VideoBoton"));
        const auto* Active = Art(TEXT("VideoActivo"));
        if (!Panel || !Button || !Active) return;
        for (TObjectIterator<UUserWidget> It; It; ++It)
        {
            auto* Menu = *It;
            if (Menu->GetWorld() != World || !Menu->IsInViewport() ||
                Menu->GetClass()->GetFName() != TEXT("WBP_GraphicsSettings_C")) continue;
            if (auto* Backdrop = Cast<UBorder>(Menu->GetWidgetFromName(TEXT("GraphicsBackdrop"))))
            {
                Backdrop->SetBrush(*Panel);
                Backdrop->SetBrushColor(FLinearColor::White);
            }
            const TCHAR* Names[] = {TEXT("Preset0"), TEXT("Preset1"), TEXT("Preset2"), TEXT("Preset3"), TEXT("Preset4"),
                TEXT("View"), TEXT("Shadow"), TEXT("Texture"), TEXT("AA"), TEXT("Effects"), TEXT("Post"), TEXT("Foliage"),
                TEXT("Shading"), TEXT("Reflection"), TEXT("Resolution"), TEXT("FPS"), TEXT("VSync"), TEXT("Dynamic"),
                TEXT("Output"), TEXT("Window"), TEXT("Detect"), TEXT("Apply"), TEXT("Close")};
            for (const TCHAR* Name : Names)
            {
                auto* Control = Cast<UButton>(Menu->GetWidgetFromName(Name));
                if (!Control) continue;
                FButtonStyle Style = Control->GetStyle();
                const FString ControlName(Name);
                const bool Selected = ControlName.StartsWith(TEXT("Preset")) && FCString::Atoi(Name + 6) == Preset;
                Style.SetNormal(Selected || ControlName == TEXT("Apply") ? *Active : *Button);
                Style.SetHovered(*Active).SetPressed(*Active);
                Control->SetStyle(Style);
                Control->SetBackgroundColor(FLinearColor::White);
                if (auto* Label = Cast<UTextBlock>(Control->GetChildAt(0))) Label->SetFont(SecondaryFont(16));
            }
            if (auto* Title = Cast<UTextBlock>(Menu->GetWidgetFromName(TEXT("GraphicsTitle"))))
            {
                Title->SetText(FText::FromString(TEXT("CONFIGURACIÓN DE VIDEO")));
                Title->SetFont(SecondaryFont(25));
            }
            if (auto* Help = Cast<UTextBlock>(Menu->GetWidgetFromName(TEXT("GraphicsHelp"))))
                Help->SetText(FText::FromString(TEXT("F10 o 8 para abrir y cerrar. Aplica para guardar los cambios.")));
            for (const TCHAR* Name : {TEXT("GraphicsHelp"), TEXT("GraphicsCustom"), TEXT("GraphicsStatus")})
                if (auto* Label = Cast<UTextBlock>(Menu->GetWidgetFromName(Name))) Label->SetFont(SecondaryFont(15));
            StyledVideo = Menu;
            StyledPreset = Preset;
            return;
        }
    }

    void RemoveLegacyPickupGuides(UWorld* World)
    {
        const double Now = FPlatformTime::Seconds();
        if (GuideWorld.Get() == World && Now < NextGuideScan) return;
        GuideWorld = World;
        NextGuideScan = Now + 1.0;
        for (TActorIterator<AActor> It(World); It; ++It)
        {
            AActor* Actor = *It;
            if (!Actor->GetClass()->GetPathName().Contains(TEXT("/Restore20261102/BP_PickupGuide."))) continue;
            Actor->SetActorHiddenInGame(true);
            for (UActorComponent* Component : Actor->GetComponents())
                if (auto* Mesh = Cast<UStaticMeshComponent>(Component)) Mesh->SetVisibility(false, true);
        }
    }

    void PositionAction(APlayerController* PC, UObject* Core)
    {
        ActionPosition.Reset();
        BikePosition.Reset();
        if (!bRouteVisible || QueryBool(RescueSubsystem(), TEXT("IsRobberyPromptActive"))) return;
        const FVector2D Size = UWidgetLayoutLibrary::GetViewportWidgetGeometry(PC).GetLocalSize();
        auto Project = [PC, Size](const FVector& Anchor) -> TOptional<FVector2D>
        {
            FVector2D Point;
            if (!UWidgetLayoutLibrary::ProjectWorldLocationToWidgetPosition(PC, Anchor, Point, false)
                || Point.X < 0 || Point.X > Size.X || Point.Y < 0 || Point.Y > Size.Y) return {};
            return FVector2D(FMath::Clamp(Point.X, 55., FMath::Max(55., Size.X - 55.)),
                FMath::Clamp(Point.Y, 105., FMath::Max(105., Size.Y - 10.)));
        };

        auto* Rider = PC->GetPawn().Get();
        auto* Parked = Cast<AActor>(ReadObject(Rider, TEXT("ParkedVehicle")));
        const auto* Riding = Rider ? FindFProperty<FBoolProperty>(Rider->GetClass(), TEXT("Riding")) : nullptr;
        auto* CurrentStore = ReadObject(Core, TEXT("InsideStore"));
        if (IsValid(Parked) && !Parked->IsHidden() && !CurrentStore &&
            (!Riding || !Riding->GetPropertyValue_InContainer(Rider)))
            BikePosition = Project(Parked->GetActorLocation() + FVector(0,0,105));

        RouteAction = static_cast<int32>(ReadNumber(Core, TEXT("State"), 0));
        if (RouteAction == 2 && CurrentStore)
        {
            auto* Query = Core->FindFunction(TEXT("OrderStore"));
            const auto* Result = Query ? CastField<FObjectPropertyBase>(Query->GetReturnProperty()) : nullptr;
            if (Result && Query->NumParms == 1)
            {
                FStructOnScope Args(Query);
                Core->ProcessEvent(Query, Args.GetStructMemory());
                if (Result->GetObjectPropertyValue_InContainer(Args.GetStructMemory()) != CurrentStore) return;
            }
            if (QueryBool(Core, TEXT("ShopReady")))
            {
                if (const auto* Counter = Cast<UPrimitiveComponent>(ReadObject(CurrentStore, TEXT("Counter"))))
                    ActionPosition = Project(Counter->Bounds.Origin + FVector(0,0,Counter->Bounds.BoxExtent.Z + 60.));
                else if (const auto Checkout = QueryPosition(CurrentStore, TEXT("CheckoutPosition")))
                    ActionPosition = Project(*Checkout + FVector(0,0,170));
            }
            else if (const auto Target = OrderTarget(Core))
                ActionPosition = Project(*Target + FVector(0,0,100));
        }
        else if (CanDeliver(Core))
        {
            auto* Recipient = Cast<AActor>(ReadObject(Core, TEXT("Recipient")));
            if (IsValid(Recipient))
            {
                const auto* Body = Recipient->FindComponentByClass<USkeletalMeshComponent>();
                const double Head = Body ? Body->Bounds.Origin.Z + Body->Bounds.BoxExtent.Z
                    : Recipient->GetActorLocation().Z + 150.;
                const FVector Center = Body ? Body->Bounds.Origin : Recipient->GetActorLocation();
                ActionPosition = Project(FVector(Center.X, Center.Y, Head + 10.));
            }
        }
    }

    int32 PendingProducts(UObject* Core) const
    {
        auto* Store = ReadObject(Core, TEXT("InsideStore"));
        auto* Count = Store ? Store->FindFunction(TEXT("ItemCount")) : nullptr;
        const auto* Result = Count ? CastField<FIntProperty>(Count->GetReturnProperty()) : nullptr;
        if (!Result || Count->NumParms != 1) return INDEX_NONE;
        FStructOnScope Args(Count);
        Store->ProcessEvent(Count, Args.GetStructMemory());
        return FMath::Max(0, Result->GetPropertyValue_InContainer(Args.GetStructMemory()) -
            static_cast<int32>(ReadNumber(Core, TEXT("BasketCount"), 0)));
    }

    bool ChecklistComplete(int32 Step) const
    {
        if (Step == 0) return ChecklistState == 3 || ChecklistPending == 0 || bChecklistDelivered;
        if (Step == 1) return ChecklistState == 3 || bChecklistDelivered;
        return bChecklistDelivered;
    }

    TSharedRef<SWidget> DeliveryChecklist()
    {
        auto List = SNew(SVerticalBox);
        List->AddSlot().AutoHeight().Padding(0,0,0,4)
            [SNew(STextBlock).Font(SecondaryFont(12)).Text(FText::FromString(TEXT("PEDIDO EN CURSO")))];
        List->AddSlot().AutoHeight().Padding(0,4)
            [SNew(STextBlock).Font(SecondaryFont(12)).ColorAndOpacity(FLinearColor(1,.70f,.22f))
             .Visibility_Lambda([this] { return FocusedSpecialSeconds >= 0 ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
             .Text_Lambda([this] {
                 if (FocusedSpecialSeconds == 0) return FText::FromString(TEXT("Bonificación vencida"));
                 return FText::FromString(FString::Printf(TEXT("Especial  %d:%02d"),
                     FocusedSpecialSeconds / 60, FocusedSpecialSeconds % 60));
             })];
        for (int32 Step = 0; Step < 3; ++Step)
            List->AddSlot().AutoHeight().Padding(0,3)
                [SNew(SHorizontalBox)
                 + SHorizontalBox::Slot().AutoWidth().Padding(0,0,8,0)
                 [SNew(SBox).WidthOverride(26)
                  [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular", 16))
                   .ColorAndOpacity_Lambda([this, Step] {
                       const float Alpha = FMath::Clamp(float((FPlatformTime::Seconds() - ChecklistCheckTime[Step]) * 4), .12f, 1.f);
                       return FSlateColor(ChecklistComplete(Step) ? FLinearColor(.35f,1.f,.76f,Alpha) : FLinearColor::White);
                   })
                   .Text_Lambda([this, Step] { return FText::FromString(ChecklistComplete(Step) ? TEXT("✓") : TEXT("□")); })]]
                 + SHorizontalBox::Slot().FillWidth(1)
                 [SNew(STextBlock).Font(SecondaryFont(12)).Text_Lambda([this, Step] {
                     if (Step == 0 && ChecklistPending > 0)
                         return FText::FromString(FString::Printf(TEXT("Recoger productos (%d)"), ChecklistPending));
                     return FText::FromString(Step == 0 ? TEXT("Recoger productos") :
                         Step == 1 ? TEXT("Pagar en caja") : TEXT("Entregar al cliente"));
                 })]];
        static const FSlateColorBrush Panel(FLinearColor(.012f,.035f,.052f,.90f));
        return SNew(SBorder).BorderImage(&Panel).Padding(12)
            .Visibility_Lambda([this] {
                return ChecklistState == 2 || ChecklistState == 3 || bChecklistDelivered ?
                    EVisibility::HitTestInvisible : EVisibility::Collapsed;
            })[List];
    }

    const FSlateBrush* ActionGlyph(int32 Action)
    {
        const auto* Local = RouteController.IsValid() ? RouteController->GetLocalPlayer() : nullptr;
        const auto* Devices = UInputDeviceSubsystem::Get();
        if (Local && Devices)
        {
            const auto Device = Devices->GetMostRecentlyUsedHardwareDevice(Local->GetPlatformUserId());
            if (Device.PrimaryDeviceType == EHardwareDevicePrimaryType::Gamepad)
            {
                const FString Id = Device.HardwareDeviceIdentifier.ToString();
                const bool Sony = Id.Contains(TEXT("DualSense")) || Id.Contains(TEXT("DualShock")) ||
                    Id.Contains(TEXT("PlayStation")) || Id.Contains(TEXT("Sony"));
                if (Action == 4) return Art(Sony ? TEXT("Robo22") : TEXT("Robo12"));
                const bool Pickup = Action == 2;
                return Art(Sony ? (Pickup ? TEXT("Accion21") : TEXT("Accion20")) : (Pickup ? TEXT("Accion11") : TEXT("Accion10")));
            }
        }
        return Art(Action == 4 ? TEXT("Robo03") : TEXT("Accion01"));
    }

    void RestoreLegacyHUD()
    {
        if (OldHUD.IsValid()) OldHUD->bShowHUD = bOldHUDVisible;
        OldHUD.Reset();
    }

    void UpdateRouteHUD(UGameViewportClient* View, APlayerController* PC, UObject* Core, bool bPhoneOpen)
    {
        auto* HUD = PC ? PC->GetHUD() : nullptr;
        if (PauseMenu && HUD && HUD->GetClass()->GetFName() == FName(TEXT("BP_BlueprintHUD_C")))
        {
            if (OldHUD.Get() != HUD)
            {
                RestoreLegacyHUD();
                OldHUD = HUD;
                bOldHUDVisible = HUD->bShowHUD;
            }
            HUD->bShowHUD = false;
            bRouteVisible = false;
            ActionPosition.Reset();
            BikePosition.Reset();
            return;
        }
        if (!Core || !HUD || HUD->GetClass()->GetFName() != FName(TEXT("BP_BlueprintHUD_C")) ||
            PC->GetWorld()->IsPaused() || !Art(TEXT("RutaIndicadores")) || !Art(TEXT("RutaAccion")) || !Art(TEXT("RutaAviso")))
        {
            RemoveRouteHUD();
            return;
        }
        if (OldHUD.Get() != HUD)
        {
            RestoreLegacyHUD();
            OldHUD = HUD;
            bOldHUDVisible = HUD->bShowHUD;
        }
        HUD->bShowHUD = false;
        RouteController = PC;
        bRouteVisible = !bPhoneOpen && bOldHUDVisible;
        if (auto* Recipient = Cast<AActor>(ReadObject(Core, TEXT("Recipient"))))
        {
            TInlineComponentArray<UTextRenderComponent*> Labels(Recipient);
            for (auto* Label : Labels) Label->SetVisibility(false);
        }
        const bool PreviousChecks[] = {ChecklistComplete(0), ChecklistComplete(1), ChecklistComplete(2)};
        const int32 NewState = static_cast<int32>(ReadNumber(Core, TEXT("State"), 0));
        const double Now = FPlatformTime::Seconds();
        if (ChecklistState == 3 && NewState < 2)
        {
            const auto* Status = FindFProperty<FTextProperty>(Core->GetClass(), TEXT("StatusMessage"));
            if (Status && Status->GetPropertyValue_InContainer(Core).ToString().StartsWith(TEXT("Entrega completada")))
                ChecklistDeliveryUntil = Now + 2.0;
        }
        ChecklistState = NewState;
        ChecklistPending = NewState == 2 ? PendingProducts(Core) : INDEX_NONE;
        bChecklistDelivered = NewState < 2 && Now < ChecklistDeliveryUntil;
        for (int32 Step = 0; Step < 3; ++Step)
            if (!PreviousChecks[Step] && ChecklistComplete(Step)) ChecklistCheckTime[Step] = Now;
        PositionAction(PC, Core);
        if (RouteHUD) return;
        RouteViewport = View;
        static const FSlateColorBrush ActionCaption(FLinearColor(.012f,.035f,.052f,.82f));
        static const FSlateColorBrush ActionFill(FLinearColor(.10f,.58f,.53f,.96f));
        RouteHUD = SNew(SOverlay).Visibility(EVisibility::HitTestInvisible)
          + SOverlay::Slot().HAlign(HAlign_Fill).VAlign(VAlign_Bottom).Padding(24,0,24,22)
          [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
           .Visibility_Lambda([this] { return TutorialStep != INDEX_NONE && !PauseMenu && !Overlay
               ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
           [SNew(SBox).WidthOverride(880).MinDesiredHeight(160)
            [SNew(SOverlay)
             + SOverlay::Slot()[SNew(SImage).Image(Art(TEXT("PanelTutorial")))]
             + SOverlay::Slot().Padding(28,15,25,16)
             [SNew(SHorizontalBox)
              + SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(0,0,12,0)
              [SNew(SVerticalBox)
               + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,8)
               [SNew(STextBlock).Font(SecondaryFont(17)).ColorAndOpacity(FLinearColor(.35f,.86f,.83f))
                .Text_Lambda([this] { return FText::FromString(TutorialStep == 0 ? TEXT("VALERIA · CICLA")
                    : TutorialStep == 7 ? TEXT("VALERIA · TUTORIAL COMPLETO")
                    : TutorialStep == 6 ? TEXT("VALERIA · SERVICIOS") : TutorialStep == 9 ? TEXT("VALERIA · DERRAPE") : TEXT("VALERIA · PEDIDO")); })]
               + SVerticalBox::Slot().AutoHeight()
               [SNew(STextBlock).Font(SecondaryFont(17)).AutoWrapText(true)
                .Text_Lambda([this] { return TutorialText(); })]]
              + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,14,0)
              [SNew(SBox).WidthOverride(98).HeightOverride(43)
               .Visibility_Lambda([this] { return ((TutorialStep >= 0 && TutorialStep <= 6 && (TutorialStep != 2 || NearTutorialStore())) || TutorialStep == 9)
                   && (TutorialStep != 5 || CanDeliver(DeliveryFor(RouteController.Get())))
                   ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
               [SNew(SOverlay)
                + SOverlay::Slot()[SNew(SImage).Image(Art(TEXT("TeclaTutorial")))]
                + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
                [SNew(STextBlock).Font(SecondaryFont(18)).Text_Lambda([this] {
                    if (TutorialStep == 9 && NearTutorialStore()) return FText::FromString(TEXT("F"));
                    static const TCHAR* Keys[] = {TEXT("F"), TEXT("TAB"), TEXT("F"), TEXT("E"),
                        TEXT("E"), TEXT("E"), TEXT("TAB"), TEXT(""), TEXT(""), TEXT("ESPACIO")};
                    return TutorialStep >= 0 && TutorialStep < UE_ARRAY_COUNT(Keys)
                        ? FText::FromString(Keys[TutorialStep]) : FText::GetEmpty();
                })]]]
              + SHorizontalBox::Slot().AutoWidth()
              [ValeriaPortrait(155)]]]]]
          + SOverlay::Slot().HAlign(HAlign_Right).VAlign(VAlign_Top).Padding(0,14,16,0)
          [SNew(SVerticalBox).Visibility_Lambda([this] { return bRouteVisible ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
           + SVerticalBox::Slot().AutoHeight()
           [SNew(SBox).WidthOverride(326).HeightOverride(138)
            [SNew(SOverlay)
             + SOverlay::Slot()[SNew(SImage).Image(Art(TEXT("RutaIndicadores")))]
             + SOverlay::Slot().Padding(16,11,16,9)
             [SNew(SVerticalBox)
              + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,8)
              [SNew(STextBlock).Font(SecondaryFont(15)).Text(FText::FromString(TEXT("RUTA / BOGOTÁ")))]
              + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,5)
              [SNew(STextBlock).Font(SecondaryFont(16)).Text_Lambda([this]
               {
                   auto* Data = DeliveryFor(RouteController.Get());
                   return FText::FromString(Pesos(static_cast<int64>(ReadNumber(Data, TEXT("Balance"), 0))));
               })]
              + SVerticalBox::Slot().FillHeight(1).HAlign(HAlign_Left).VAlign(VAlign_Center).Padding(0,6,0,0)
              [SNew(STextBlock).Font(SecondaryFont(13)).Text_Lambda([this]
               {
                   const APawn* Rider = RouteController.IsValid() ? RouteController->GetPawn().Get() : nullptr;
                   return FText::FromString(FString::Printf(TEXT("%d km/h"), Rider ? FMath::RoundToInt(Rider->GetVelocity().Size2D() * .036) : 0));
               })]]]]
           + SVerticalBox::Slot().AutoHeight().Padding(0,6,0,0)[DeliveryChecklist()]]
          + SOverlay::Slot()
          [SAssignNew(RouteCanvas, SConstraintCanvas)
           + SConstraintCanvas::Slot().Alignment(FVector2D::ZeroVector).ZOrder(1)
           .Offset_Lambda([this] { return MinimapBounds(); })
           [SNew(SStreetMinimap).Clipping(EWidgetClipping::ClipToBoundsAlways)
            .ForceVolatile(true)
            .Visibility_Lambda([this] { return HasMinimap() ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
            .PaintMap([this](const FGeometry& Geometry, FSlateWindowElementList& Out, int32 Layer) {
                return PaintMinimap(Geometry, Out, Layer);
            })]
           + SConstraintCanvas::Slot().AutoSize(true).Alignment(FVector2D(.5,1))
           .Offset_Lambda([this] {
               const auto Point = BikePosition.Get(FVector2D::ZeroVector);
               return FMargin(Point.X, Point.Y, 0, 0);
           })
           [SNew(SBox).WidthOverride(39).HeightOverride(33)
            .Visibility_Lambda([this] { return BikePosition && !Overlay ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
            [SNew(SImage).Image_Lambda([this] { return ActionGlyph(4); })]]
           + SConstraintCanvas::Slot().AutoSize(true).Alignment(FVector2D(.5,1))
           .Offset_Lambda([this] {
               const auto Point = ActionPosition.Get(FVector2D::ZeroVector);
               return FMargin(Point.X, Point.Y, 0, 0);
           })
           [SNew(SVerticalBox)
            .Visibility_Lambda([this] { return ActionPosition && !Overlay ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })
            + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,3)
            [SNew(SOverlay)
             + SOverlay::Slot()[SNew(SImage).Image(&ActionCaption)]
             + SOverlay::Slot()
             [SNew(SProgressBar).BackgroundImage(FCoreStyle::Get().GetBrush("NoBrush"))
              .FillImage(&ActionFill).FillColorAndOpacity(FLinearColor::White)
              .BorderPadding(FVector2D::ZeroVector)
              .Percent_Lambda([this]() -> TOptional<float> {
                  return FMath::Clamp(ReadNumber(DeliveryFor(RouteController.Get()), TEXT("HoldProgress"), 0.), 0., 1.);
              })]
             + SOverlay::Slot().Padding(7,3)
             [SNew(STextBlock).Font(SecondaryFont(15)).ColorAndOpacity(FLinearColor::White)
              .Text_Lambda([this] {
                  if (RouteAction == 3) return FText::FromString(TEXT("Mantén para entregar"));
                  return FText::FromString(QueryBool(DeliveryFor(RouteController.Get()), TEXT("ShopReady"))
                      ? TEXT("Mantén para pagar") : TEXT("Mantén para recoger"));
              })]]
            + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,2)
            [SNew(SBox).WidthOverride(39).HeightOverride(33)
             [SNew(SImage).Image_Lambda([this] { return ActionGlyph(RouteAction); })]]
            + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
            [SNew(SBox).WidthOverride(22).HeightOverride(22)
             [SNew(SImage).Image(Art(TEXT("JugadorMapa"))).ColorAndOpacity(FLinearColor(.35f,.87f,1.f))
              .RenderTransformPivot(FVector2D(.5,.5)).RenderTransform(FSlateRenderTransform(FQuat2D(PI)))]]]];
        View->AddViewportWidgetContent(RouteHUD.ToSharedRef(), 1100);
    }

    TSharedRef<SWidget> ValeriaPortrait(float Width)
    {
        const auto* Portrait = Art(TEXT("RetratoValeria"));
        const float Height = Portrait ? Width * Portrait->ImageSize.Y / Portrait->ImageSize.X : Width;
        static const FSlateColorBrush Mouth(FLinearColor(.21f,.076f,.049f));
        return SNew(SBox).WidthOverride(Width).HeightOverride(Height)
            [SNew(SOverlay).RenderTransformPivot(FVector2D(.5, .85))
             .RenderTransform_Lambda([this]() -> TOptional<FSlateRenderTransform> {
                 const double Age = FPlatformTime::Seconds() - ValeriaLineStarted;
                 const float Nod = Age < 6. ? .016f * FMath::Sin(Age * 7.) : 0.f;
                 return FSlateRenderTransform(FQuat2D(Nod));
             })
             + SOverlay::Slot()[SNew(SImage).Image(Portrait)]
             + SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top).Padding(Width*.402f, Height*.585f, 0, 0)
             [SNew(SBox).WidthOverride(Width*.075f).HeightOverride_Lambda([this, Height]() -> FOptionalSize {
                 const double Age = FPlatformTime::Seconds() - ValeriaLineStarted;
                 return Age < 6. ? Height * .019f * FMath::Square(FMath::Sin(Age * 12.)) : 0.f;
             })[SNew(SImage).Image(&Mouth)]]];
    }

    void UpdateValeriaPortrait()
    {
        const FText Line = Overlay && bGarageTutorialVisible
            ? FText::FromString(TEXT("Taller")) : TutorialText();
        const FString Text = Line.ToString();
        if (LastValeriaLine != Text)
        {
            LastValeriaLine = Text;
            ValeriaLineStarted = FPlatformTime::Seconds();
        }
    }

    struct FArt
    {
        TStrongObjectPtr<UTexture2D> Texture;
        FSlateBrush Brush;
    };

    const FSlateBrush* Art(const FString& Name)
    {
        if (const TUniquePtr<FArt>* Existing = Images.Find(Name)) return &(*Existing)->Brush;
        const auto Plugin = IPluginManager::Get().FindPlugin(TEXT("BogotaPhonePreview"));
        if (!Plugin) return nullptr;
        const FString File = FPaths::Combine(Plugin->GetBaseDir(), TEXT("Resources"), Name + TEXT(".png"));
        UTexture2D* Texture = FImageUtils::ImportFileAsTexture2D(File);
        if (!Texture) return nullptr;
        Texture->Filter = TF_Bilinear;
        Texture->NeverStream = true;
        Texture->UpdateResource();
        auto Entry = MakeUnique<FArt>();
        Entry->Texture.Reset(Texture);
        Entry->Brush.SetResourceObject(Texture);
        Entry->Brush.ImageSize = FVector2D(Texture->GetSizeX(), Texture->GetSizeY());
        const FSlateBrush* Result = &Entry->Brush;
        Images.Add(Name, MoveTemp(Entry));
        return Result;
    }

    static FString Pesos(int64 Amount)
    {
        FString Number = LexToString(Amount);
        const int32 FirstDigit = Amount < 0 ? 1 : 0;
        for (int32 Index = Number.Len() - 3; Index > FirstDigit; Index -= 3)
            Number.InsertAt(Index, TEXT('.'));
        return TEXT("$") + Number;
    }

    static double ReadNumber(UObject* Object, FName Name, double Fallback)
    {
        if (!Object) return Fallback;
        const FNumericProperty* P = FindFProperty<FNumericProperty>(Object->GetClass(), Name);
        if (!P) return Fallback;
        const void* Value = P->ContainerPtrToValuePtr<void>(Object);
        if (P->IsFloatingPoint()) return P->GetFloatingPointPropertyValue(Value);
        if (CastField<FByteProperty>(P)) return P->GetUnsignedIntPropertyValue(Value);
        return P->GetSignedIntPropertyValue(Value);
    }

    int32 CountItems(UObject* Core, FName Name) const
    {
        const auto* Field = Core ? FindFProperty<FArrayProperty>(Core->GetClass(), Name) : nullptr;
        return Field ? FScriptArrayHelper(Field, Field->ContainerPtrToValuePtr<void>(Core)).Num() : 0;
    }

    FText LiveBalance() const
    {
        auto* Core = DeliveryFor(Controller.Get());
        return Core ? FText::FromString(Pesos(static_cast<int64>(ReadNumber(Core, TEXT("Balance"), 0.)))) : FText::GetEmpty();
    }

    FText LiveOrders() const
    {
        auto* Core = DeliveryFor(Controller.Get());
        return Core ? (CountItems(Core, TEXT("ActiveOrders")) > 0 ? FText::AsNumber(CountItems(Core, TEXT("ActiveOrders"))) : FText::GetEmpty()) : FText::GetEmpty();
    }

    bool OwnsUpgrade(FName Name) const
    {
        return OwnsUpgrade(DeliveryFor(Controller.Get()), Name);
    }

    static bool OwnsUpgrade(UObject* Core, FName Name)
    {
        const auto* Array = Core ? FindFProperty<FArrayProperty>(Core->GetClass(), TEXT("Purchased")) : nullptr;
        const auto* Field = Array ? CastField<FNameProperty>(Array->Inner) : nullptr;
        if (!Field) return false;
        FScriptArrayHelper Items(Array, Array->ContainerPtrToValuePtr<void>(Core));
        for (int32 Index = 0; Index < Items.Num(); ++Index)
            if (Field->GetPropertyValue(Items.GetRawPtr(Index)) == Name) return true;
        return false;
    }

    static int32 CountVehicleUpgrades(UObject* Core, bool bBike)
    {
        static const FName BikeParts[] = {TEXT("BikePedals"), TEXT("BikeFrame"), TEXT("BikeGears"), TEXT("BikeMotor")};
        static const FName MotoParts[] = {TEXT("MotoTurbo"), TEXT("MotoAero"), TEXT("MotoDisplacement"), TEXT("MotoInjection")};
        int32 Count = 0;
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(BikeParts); ++Index)
            Count += OwnsUpgrade(Core, bBike ? BikeParts[Index] : MotoParts[Index]);
        return Count;
    }

    static void ApplyWorkshopDriveMultiplier(APlayerController* PC, UObject* Core)
    {
        auto* Pawn = PC ? PC->GetPawn().Get() : nullptr;
        auto* Field = Pawn ? FindFProperty<FNumericProperty>(Pawn->GetClass(), TEXT("WorkshopDriveMultiplier")) : nullptr;
        if (Core && Field && Field->IsFloatingPoint())
        {
            const int32 Count = CountVehicleUpgrades(Core, ReadNumber(Core, TEXT("Vehicle"), 0) == 0);
            Field->SetFloatingPointPropertyValue(Field->ContainerPtrToValuePtr<void>(Pawn), 1. + .1 * Count);
        }
    }

    template <typename TComponent>
    static TComponent* AttachCargo(AActor& Owner, USceneComponent* Parent, FName Name)
    {
        auto* Component = NewObject<TComponent>(&Owner, Name);
        Owner.AddInstanceComponent(Component);
        Component->SetupAttachment(Parent);
        Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Component->RegisterComponent();
        return Component;
    }

    static void ShowWearableCargo(UObject* Core, ACharacter& Rider, FName Upgrade,
        const TCHAR* AssetPath, TWeakObjectPtr<USkeletalMeshComponent>& Cargo)
    {
        const bool bOwned = OwnsUpgrade(Core, Upgrade);
        if (bOwned && !Cargo.IsValid())
        {
            auto* Mesh = LoadObject<USkeletalMesh>(nullptr, AssetPath);
            if (!Mesh) return;
            Cargo = AttachCargo<USkeletalMeshComponent>(Rider, Rider.GetMesh(), Upgrade);
            Cargo->SetSkeletalMeshAsset(Mesh);
            Cargo->SetLeaderPoseComponent(Rider.GetMesh());
        }
        if (auto* Component = Cargo.Get()) Component->SetHiddenInGame(!bOwned);
    }

    void RefreshCargoModels(APlayerController* PC, UObject* Core)
    {
        auto* Rider = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
        if (!Rider || !Core) return;
        if (CargoRider.Get() != Rider)
        {
            CargoRider = Rider;
            Backpack.Reset();
            WaistPack.Reset();
            RiderPanniers.Reset();
        }
        ShowWearableCargo(Core, *Rider, TEXT("CargoBackpack"),
            TEXT("/Game/Delivery/Art/SK_CargoBackpack.SK_CargoBackpack"), Backpack);
        ShowWearableCargo(Core, *Rider, TEXT("CargoWaist"),
            TEXT("/Game/Delivery/Art/SK_CargoWaist.SK_CargoWaist"), WaistPack);

        const bool bOwned = OwnsUpgrade(Core, TEXT("CargoPanniers"));
        const bool bMoto = ReadNumber(Core, TEXT("Vehicle"), 0) == 1;
        const auto* Riding = FindFProperty<FBoolProperty>(Rider->GetClass(), TEXT("Riding"));
        const bool bRiding = Riding && Riding->GetPropertyValue_InContainer(Rider);
        auto* Parked = Cast<AActor>(ReadObject(Rider, TEXT("ParkedVehicle")));
        if (PannierVehicle.Get() != Parked)
        {
            if (auto* Component = ParkedPanniers.Get()) Component->DestroyComponent();
            ParkedPanniers.Reset();
            PannierVehicle = Parked;
        }
        if (bOwned && bMoto && !RiderPanniers.IsValid())
        {
            auto* Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Delivery/Art/SM_CargoPanniers.SM_CargoPanniers"));
            if (!Mesh) return;
            RiderPanniers = AttachCargo<UStaticMeshComponent>(*Rider, Rider->GetRootComponent(), TEXT("CargoPanniers"));
            RiderPanniers->SetStaticMesh(Mesh);
            RiderPanniers->SetRelativeLocation(FVector(0, 0, -90));
        }
        if (bOwned && bMoto && Parked && !ParkedPanniers.IsValid() && RiderPanniers.IsValid())
        {
            ParkedPanniers = AttachCargo<UStaticMeshComponent>(*Parked, Parked->GetRootComponent(), TEXT("CargoPanniers"));
            ParkedPanniers->SetStaticMesh(RiderPanniers->GetStaticMesh());
        }
        if (RiderPanniers.IsValid()) RiderPanniers->SetHiddenInGame(!bOwned || !bMoto || !bRiding);
        if (ParkedPanniers.IsValid()) ParkedPanniers->SetHiddenInGame(!bOwned || !bMoto || bRiding);
    }

    static UObject* ReadObject(UObject* Object, FName Name)
    {
        const auto* Field = Object ? FindFProperty<FObjectPropertyBase>(Object->GetClass(), Name) : nullptr;
        return Field ? Field->GetObjectPropertyValue_InContainer(Object) : nullptr;
    }

    static FName ReadName(UObject* Object, FName Name)
    {
        const auto* Field = Object ? FindFProperty<FNameProperty>(Object->GetClass(), Name) : nullptr;
        return Field ? Field->GetPropertyValue_InContainer(Object) : NAME_None;
    }

    static FName PaintKey(FName Model)
    {
        return FName(*(TEXT("PhonePaint_") + Model.ToString()));
    }

    static TOptional<FScriptMapHelper> PaintMap(UObject* Core)
    {
        const auto* Field = Core ? FindFProperty<FMapProperty>(Core->GetClass(), TEXT("ModelColors")) : nullptr;
        if (!Field || !CastField<FNameProperty>(Field->KeyProp) || !CastField<FIntProperty>(Field->ValueProp))
            return {};
        return FScriptMapHelper(Field, Field->ContainerPtrToValuePtr<void>(Core));
    }

    struct FServiceBill
    {
        const TCHAR* Name;
        const TCHAR* Key;
        int32 PeriodDays;
        int32 Price;
    };

    static constexpr FServiceBill Bills[] = {
        {TEXT("Luz"), TEXT("ServicePower"), 5, 6000},
        {TEXT("Agua"), TEXT("ServiceWater"), 7, 5000},
        {TEXT("Internet"), TEXT("ServiceInternet"), 9, 7000},
        {TEXT("Nefliz"), TEXT("ServiceStreaming"), 12, 7000},
        {TEXT("Gas"), TEXT("ServiceGas"), 8, 4500},
        {TEXT("Arriendo"), TEXT("ServiceRent"), 30, 42500}
    };

    static int32 ServiceValue(FScriptMapHelper& Map, FName Key)
    {
        const auto* Value = reinterpret_cast<const int32*>(Map.FindValueFromHash(&Key));
        return Value ? *Value : 0;
    }

    static AActor* FindCityClock(UWorld* World)
    {
        for (TActorIterator<AActor> It(World); It; ++It)
            if (It->GetClass()->GetFName() == TEXT("BP_WorldState_C")) return *It;
        return nullptr;
    }

    static void WriteClockNumber(UObject* Clock, FName Name, double Value)
    {
        if (const auto* Field = Clock ? FindFProperty<FNumericProperty>(Clock->GetClass(), Name) : nullptr)
        {
            void* Address = Field->ContainerPtrToValuePtr<void>(Clock);
            if (Field->IsFloatingPoint()) Field->SetFloatingPointPropertyValue(Address, Value);
            else Field->SetIntPropertyValue(Address, static_cast<int64>(Value));
        }
    }

    // Session fields live in the profile's existing persisted map so backups and manual slots
    // copy a complete snapshot together. Older profiles have no SessionVersion key.
    static void StoreSession(FScriptMapHelper& Map, APlayerController* PC, AActor* Clock)
    {
        auto* Pawn = PC->GetPawn().Get();
        const FVector Point = Pawn->GetActorLocation();
        const FRotator View = PC->GetControlRotation();
        const int32 Day = static_cast<int32>(ReadNumber(Clock, TEXT("GameDay"), 1));
        const double Phase = ReadNumber(Clock, TEXT("CycleSeconds"), 0.);
        const TPair<FName, int32> Snapshot[] = {
            {TEXT("SessionVersion"), 1}, {TEXT("SessionDay"), Day},
            {TEXT("SessionPhase"), FMath::RoundToInt(Phase * 100000.)},
            {TEXT("SessionHour"), FMath::RoundToInt(ReadNumber(Clock, TEXT("Hour"), 9.) * 1000000.)},
            {TEXT("SessionX"), FMath::RoundToInt(Point.X * 100.)},
            {TEXT("SessionY"), FMath::RoundToInt(Point.Y * 100.)},
            {TEXT("SessionZ"), FMath::RoundToInt(Point.Z * 100.)},
            {TEXT("SessionYaw"), FMath::RoundToInt(View.Yaw * 1000.)},
            {TEXT("SessionPitch"), FMath::RoundToInt(View.Pitch * 1000.)},
        };
        for (const auto& Field : Snapshot) Map.AddPair(&Field.Key, &Field.Value);

        const auto* Parked = Cast<AActor>(ReadObject(Pawn, TEXT("ParkedVehicle")));
        const auto* Riding = FindFProperty<FBoolProperty>(Pawn->GetClass(), TEXT("Riding"));
        const bool bMounted = Riding && Riding->GetPropertyValue_InContainer(Pawn);
        FVector ParkedPoint = Parked ? Parked->GetActorLocation() : FVector::ZeroVector;
        double ParkedYaw = Parked ? Parked->GetActorRotation().Yaw : 0.;
        bool bHasParked = IsValid(Parked) && !Parked->IsHidden();
        if (bMounted)
        {
            FCollisionQueryParams Query(SCENE_QUERY_STAT(SaveParkedVehicle), false, Pawn);
            if (Parked) Query.AddIgnoredActor(Parked);
            const FVector Side = Pawn->GetActorRightVector();
            for (const double Offset : {130., -130.})
            {
                FHitResult Wall, Ground;
                const FVector Candidate = Point + Side * Offset;
                if (!Pawn->GetWorld()->LineTraceSingleByChannel(Wall, Point, Candidate, ECC_Visibility, Query) &&
                    Pawn->GetWorld()->LineTraceSingleByChannel(Ground, Candidate, Candidate - FVector(0, 0, 350),
                        ECC_Visibility, Query))
                {
                    ParkedPoint = Ground.ImpactPoint;
                    ParkedYaw = Pawn->GetActorRotation().Yaw;
                    bHasParked = true;
                    break;
                }
            }
        }
        const TPair<FName, int32> Vehicle[] = {
            {TEXT("SessionHasParked"), bHasParked ? 1 : 0},
            {TEXT("SessionParkedX"), FMath::RoundToInt(ParkedPoint.X * 100.)},
            {TEXT("SessionParkedY"), FMath::RoundToInt(ParkedPoint.Y * 100.)},
            {TEXT("SessionParkedZ"), FMath::RoundToInt(ParkedPoint.Z * 100.)},
            {TEXT("SessionParkedYaw"), FMath::RoundToInt(ParkedYaw * 1000.)},
        };
        for (const auto& Field : Vehicle) Map.AddPair(&Field.Key, &Field.Value);
    }

    void RestoreSession(FScriptMapHelper& Map, APlayerController* PC, AActor* ClockActor)
    {
        if (ServiceValue(Map, TEXT("SessionVersion")) != 1) return;
        const FVector Point(ServiceValue(Map, TEXT("SessionX")) / 100.,
            ServiceValue(Map, TEXT("SessionY")) / 100., ServiceValue(Map, TEXT("SessionZ")) / 100.);
        const FRotator View(ServiceValue(Map, TEXT("SessionPitch")) / 1000.,
            ServiceValue(Map, TEXT("SessionYaw")) / 1000., 0.);
        auto* Pawn = PC->GetPawn().Get();
        Pawn->SetActorLocationAndRotation(Point, FRotator(0., View.Yaw, 0.), false, nullptr, ETeleportType::ResetPhysics);
        if (auto* Character = Cast<ACharacter>(Pawn)) Character->GetCharacterMovement()->StopMovementImmediately();
        PC->SetControlRotation(View);
        if (ServiceValue(Map, TEXT("SessionHasParked")) == 1)
            if (auto* Parked = Cast<AActor>(ReadObject(Pawn, TEXT("ParkedVehicle"))))
            {
                const FVector ParkedPoint(ServiceValue(Map, TEXT("SessionParkedX")) / 100.,
                    ServiceValue(Map, TEXT("SessionParkedY")) / 100., ServiceValue(Map, TEXT("SessionParkedZ")) / 100.);
                Parked->SetActorLocationAndRotation(ParkedPoint,
                    FRotator(0., ServiceValue(Map, TEXT("SessionParkedYaw")) / 1000., 0.), false, nullptr, ETeleportType::ResetPhysics);
                ParkedMapVehicle.Reset();
            }
        WriteClockNumber(ClockActor, TEXT("GameDay"), FMath::Max(1, ServiceValue(Map, TEXT("SessionDay"))));
        const double Phase = FMath::Clamp(ServiceValue(Map, TEXT("SessionPhase")) / 100000., 0., 1439.99999);
        WriteClockNumber(ClockActor, TEXT("CycleSeconds"), Phase);
        const double Hour = ServiceValue(Map, TEXT("SessionHour")) / 1000000.;
        WriteClockNumber(ClockActor, TEXT("Hour"), Hour);
        UE_LOG(LogTemp, Display, TEXT("Bogota save: restored %s, day %d at %.4f"), *Point.ToString(),
            ServiceValue(Map, TEXT("SessionDay")), Hour);
    }

    bool SaveCurrentSession(APlayerController* PC, UObject* Core)
    {
        const auto* Dev = Core ? FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("DeveloperMode")) : nullptr;
        if (Dev && Dev->GetPropertyValue_InContainer(Core)) return false;
        if (PC && PC->GetPawn() && SessionCore.Get() == Core && CityClock.IsValid())
            if (auto Map = PaintMap(Core)) StoreSession(*Map, PC, CityClock.Get());
        return QueryBool(Core, TEXT("SaveProfile"));
    }

    void TrackSession(APlayerController* PC, UObject* Core)
    {
        UWorld* World = PC ? PC->GetWorld() : nullptr;
        if (!World || !PC->GetPawn() || !Core || bAtStartup || World->IsPaused()) return;
        if (SessionCore.Get() != Core)
        {
            SessionCore = Core;
            CityClock = FindCityClock(World);
            LastServiceDay = INDEX_NONE;
            NextSessionSnapshot = 0.;
        }
        if (!CityClock.IsValid()) return;
        const auto* Dev = FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("DeveloperMode"));
        if (Dev && Dev->GetPropertyValue_InContainer(Core)) return;
        auto Map = PaintMap(Core);
        if (!Map) return;
        if (LastServiceDay == INDEX_NONE) RestoreSession(*Map, PC, CityClock.Get());
        const int32 Day = static_cast<int32>(ReadNumber(CityClock.Get(), TEXT("GameDay"), 1));
        const int32 ElapsedDays = LastServiceDay == INDEX_NONE ? 0 : FMath::Max(0, Day - LastServiceDay);
        LastServiceDay = Day;
        if (ElapsedDays > 0)
        {
            const FName Key(TEXT("ServiceClockMinutes"));
            const int32 Updated = static_cast<int32>(FMath::Min<int64>(MAX_int32,
                ServiceValue(*Map, Key) + int64(ElapsedDays) * 1440));
            Map->AddPair(&Key, &Updated);
            SaveCurrentSession(PC, Core);
        }
        if (World->GetTimeSeconds() >= NextSessionSnapshot)
        {
            NextSessionSnapshot = World->GetTimeSeconds() + 1.;
            StoreSession(*Map, PC, CityClock.Get());
        }
    }

    static int32 BillDue(UObject* Core, int32 Index)
    {
        auto Map = PaintMap(Core);
        if (!Map) return 0;
        const auto& Bill = Bills[Index];
        const int32 Cycles = ServiceValue(*Map, TEXT("ServiceClockMinutes")) / 1440 / Bill.PeriodDays;
        const int64 Due = int64(FMath::Max(0, Cycles - ServiceValue(*Map, Bill.Key))) * Bill.Price;
        return static_cast<int32>(FMath::Min<int64>(MAX_int32, Due));
    }

    static int64 TotalBillsDue(UObject* Core)
    {
        int64 Total = 0;
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(Bills); ++Index)
            Total += BillDue(Core, Index);
        return Total;
    }

    UObject* RescueSubsystem() const
    {
        auto* World = Viewport.IsValid() ? Viewport->GetWorld() : nullptr;
        auto* Type = FindObject<UClass>(nullptr, TEXT("/Script/BogotaRuntime.BogotaRobbery"));
        return World && Type ? World->GetSubsystemBase(Type) : nullptr;
    }

    int32 RescueQuote() const
    {
        auto* Rescue = RescueSubsystem();
        auto* Query = Rescue ? Rescue->FindFunction(TEXT("ServiceRescueQuote")) : nullptr;
        const auto* Result = Query ? CastField<FIntProperty>(Query->GetReturnProperty()) : nullptr;
        if (!Result || Query->NumParms != 1) return INDEX_NONE;
        FStructOnScope Args(Query);
        Rescue->ProcessEvent(Query, Args.GetStructMemory());
        return Result->GetPropertyValue_InContainer(Args.GetStructMemory());
    }

    int32 TutorialBill(UObject* Core) const
    {
        auto Map = PaintMap(Core);
        if (!Map) return INDEX_NONE;
        const int32 Cash = ReadNumber(Core, TEXT("Balance"), 0);
        int32 Best = INDEX_NONE;
        int32 Cheapest = MAX_int32;
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(Bills); ++Index)
        {
            const int32 Due = BillDue(Core, Index);
            if (Due == 0 && ServiceValue(*Map, Bills[Index].Key) >
                ServiceValue(*Map, TEXT("ServiceClockMinutes")) / 1440 / Bills[Index].PeriodDays) continue;
            const int32 Price = Due > 0 ? Due : Bills[Index].Price;
            if (Price <= Cash && Price < Cheapest)
            {
                Best = Index;
                Cheapest = Price;
            }
        }
        return Best;
    }

    int32 ServicePayment(UObject* Core, int32 Index) const
    {
        const int32 Due = BillDue(Core, Index);
        return Due == 0 && TutorialStep == 6 && TutorialBill(Core) == Index ? Bills[Index].Price : Due;
    }

    void PayService(int32 Index)
    {
        auto* Core = DeliveryFor(Controller.Get());
        const auto* Balance = Core ? FindFProperty<FIntProperty>(Core->GetClass(), TEXT("Balance")) : nullptr;
        if (!Balance) return;
        const auto* Dev = FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("DeveloperMode"));
        if (Dev && Dev->GetPropertyValue_InContainer(Core))
        {
            ServiceStatus = FText::FromString(TEXT("Sal del modo desarrollador para pagar"));
            return;
        }
        const bool bRescue = Index == UE_ARRAY_COUNT(Bills);
        const int32 Due = bRescue ? RescueQuote() : ServicePayment(Core, Index);
        const int32 Cash = Balance->GetPropertyValue_InContainer(Core);
        if (Due <= 0) return;
        if (Cash < Due)
        {
            ServiceStatus = FText::FromString(TEXT("Saldo insuficiente"));
            return;
        }
        if (bRescue)
        {
            Invoke(RescueSubsystem(), TEXT("PayServiceRescue"));
            ServiceStatus = FText::FromString(RescueQuote() == 0 ? TEXT("Vehículo marcado en el mapa") : TEXT("No se pudo pagar el rescate"));
            return;
        }
        auto Map = PaintMap(Core);
        if (!Map) return;
        const FName Key(Bills[Index].Key);
        const bool HadValue = Map->FindValueFromHash(&Key) != nullptr;
        const int32 Before = ServiceValue(*Map, Key);
        const bool bTutorialPayment = TutorialStep == 6 && TutorialBill(Core) == Index;
        const int32 PaidThrough = ServiceValue(*Map, TEXT("ServiceClockMinutes")) / 1440 / Bills[Index].PeriodDays
            + (BillDue(Core, Index) == 0 ? 1 : 0);
        Balance->SetPropertyValue_InContainer(Core, Cash - Due);
        Map->AddPair(&Key, &PaidThrough);
        if (!QueryBool(Core, TEXT("SaveProfile")))
        {
            if (HadValue) Map->AddPair(&Key, &Before);
            else Map->RemovePair(&Key);
            Balance->SetPropertyValue_InContainer(Core, Cash);
            ServiceStatus = FText::FromString(TEXT("No se pudo guardar el pago"));
            return;
        }
        if (bTutorialPayment)
        {
            TutorialStep = 7;
            TutorialFinishedUntil = 0.;
            PlayTutorialSuccess(Core->GetWorld());
        }
        ServiceStatus = FText::FromString(TEXT("Pago guardado"));
        Invoke(Core, TEXT("Changed"));
    }

    void PaySpecialService()
    {
        auto* Core = DeliveryFor(Controller.Get());
        if (HasSpecialAccess(Core)) return;
        if (ReadNumber(Core, TEXT("Balance"), 0) < SpecialAccessPrice)
        {
            ServiceStatus = FText::FromString(TEXT("Saldo insuficiente"));
            return;
        }
        BuySpecialAccess();
        ServiceStatus = FText::FromString(HasSpecialAccess(Core)
            ? TEXT("Especiales desbloqueados") : TEXT("No se pudo desbloquear"));
    }

    TSharedRef<SWidget> ServicesList()
    {
        static const FSlateColorBrush TutorialPaymentBackground(FLinearColor(.16f,.55f,.48f));
        static const FSlateColorBrush ListBackground(FLinearColor(.012f,.035f,.052f));
        auto Content = SNew(SScrollBox).ScrollBarVisibility(EVisibility::Collapsed);
        static const FSlateColorBrush RowBackground(FLinearColor(.025f,.11f,.16f));
        static const FSlateColorBrush ButtonBackground(FLinearColor(.035f,.34f,.31f));
        const auto* Atlas = Art(TEXT("ServiciosLista"));
        if (Atlas)
        {
            ServiceCalendarArt = *Atlas;
            ServiceCalendarArt.SetUVRegion(FBox2f(FVector2f(137.f / 528.f, 73.f / 861.f),
                                                  FVector2f(161.f / 528.f, 98.f / 861.f)));
        }
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(Bills) + 2; ++Index)
        {
            const bool bRescue = Index == UE_ARRAY_COUNT(Bills);
            const bool bSpecial = Index == UE_ARRAY_COUNT(Bills) + 1;
            auto Due = [this, Index, bRescue, bSpecial] {
                auto* Core = DeliveryFor(Controller.Get());
                if (bSpecial) return HasSpecialAccess(Core) ? 0 : SpecialAccessPrice;
                return bRescue ? RescueQuote() : ServicePayment(Core, Index);
            };
            auto& RowArt = ServiceRowArt[Index];
            if (Atlas)
            {
                RowArt = *Atlas;
                const float Y = 30.f + 117.f * FMath::Min(Index, int32(UE_ARRAY_COUNT(Bills)));
                RowArt.SetUVRegion(FBox2f(FVector2f(46.f / 528.f, (Y + 10.f) / 861.f),
                                          FVector2f(127.f / 528.f, (Y + 80.f) / 861.f)));
            }
            Content->AddSlot().Padding(3,2,5,5)
            [SNew(SBox).HeightOverride(66)
             [SNew(SBorder).BorderImage(&RowBackground).Padding(8,6)
              [SNew(SHorizontalBox)
               + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,9,0)
               [SNew(SBox).WidthOverride(46).HeightOverride(40)
                [SNew(SImage).Image(bSpecial ? Art(TEXT("EspecialServicio")) : Atlas ? &RowArt : &RowBackground)]]
               + SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)
               [SNew(SVerticalBox)
                + SVerticalBox::Slot().AutoHeight()
                [SNew(STextBlock).Font(SecondaryFont(13))
                 .Text(FText::FromString(bSpecial ? TEXT("Especiales") : bRescue ? TEXT("Rescate") : Bills[Index].Name))]
                + SVerticalBox::Slot().AutoHeight().Padding(0,3,0,0)
                [SNew(SHorizontalBox)
                 + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,4,0)
                 [SNew(SBox).WidthOverride(14).HeightOverride(14)
                  .Visibility_Lambda([Atlas, bRescue, bSpecial, Due] {
                      return Atlas && !bRescue && !bSpecial && Due() <= 0
                          ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
                  })
                  [SNew(SImage).Image(&ServiceCalendarArt)]]
                 + SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)
                 [SNew(STextBlock).Font(SecondaryFont(10)).Text_Lambda([this, Index, bRescue, bSpecial, Due] {
                     const int32 Amount = Due();
                     if (Amount > 0) return FText::FromString(Pesos(Amount));
                     if (bSpecial) return FText::FromString(TEXT("Desbloqueados"));
                     if (bRescue) return FText::FromString(Amount == 0 ? TEXT("Ubicaci\u00f3n marcada") : TEXT("Sin robo"));
                     auto Map = PaintMap(DeliveryFor(Controller.Get()));
                     if (!Map) return FText::GetEmpty();
                     const int32 Day = ServiceValue(*Map, TEXT("ServiceClockMinutes")) / 1440;
                     const int32 Period = Bills[Index].PeriodDays;
                     const int32 Remaining = FMath::Max(Day / Period, ServiceValue(*Map, Bills[Index].Key)) * Period + Period - Day;
                     return FText::FromString(FString::Printf(TEXT("%d %s"), Remaining,
                         Remaining == 1 ? TEXT("d\u00eda restante") : TEXT("d\u00edas restantes")));
                 })]]]
               + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(4,0,0,0)
               [SNew(SBox).WidthOverride(80).HeightOverride(30)
                [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").ContentPadding(0)
                 .HAlign(HAlign_Fill).VAlign(VAlign_Fill)
                 .IsEnabled_Lambda([Due] { return Due() > 0; })
                 .OnClicked_Lambda([this, Index, bSpecial] {
                     if (bSpecial) PaySpecialService();
                     else PayService(Index);
                     return FReply::Handled();
                 })
                 [SNew(SBorder).BorderImage_Lambda([this, Index]() -> const FSlateBrush* {
                     return TutorialStep == 6 && TutorialBill(DeliveryFor(Controller.Get())) == Index
                         ? &TutorialPaymentBackground : &ButtonBackground;
                  }).HAlign(HAlign_Center).VAlign(VAlign_Center)
                  [SNew(STextBlock).Font(SecondaryFont(11)).ColorAndOpacity(FLinearColor::White)
                   .Text(FText::FromString(TEXT("PAGAR")))]]]]]]];
        }
        return SNew(SBorder).BorderImage(&ListBackground).Padding(0)
            .Clipping(EWidgetClipping::ClipToBoundsAlways)
            [Content];
    }

    static TOptional<FLinearColor> ReadPaint(UObject* Core, FName Model)
    {
        auto Map = PaintMap(Core);
        if (!Map || Model.IsNone()) return {};
        const FName Key = PaintKey(Model);
        const auto* Value = reinterpret_cast<const int32*>(Map->FindValueFromHash(&Key));
        return Value ? TOptional<FLinearColor>(FLinearColor::FromSRGBColor(FColor((*Value >> 16) & 255, (*Value >> 8) & 255, *Value & 255))) : TOptional<FLinearColor>();
    }

    static FLinearColor PresetPaint(int32 Index)
    {
        static const FLinearColor Colors[] = {
            {.025f,.65f,.86f}, {1.f,.22f,.025f}, {.94f,.72f,.025f},
            {.72f,.025f,.055f}, {.79f,.76f,.64f}, {.035f,.045f,.06f}
        };
        return Colors[FMath::Clamp(Index, 0, 5)];
    }

    static bool ApplyPaint(UStaticMeshComponent* Mesh, const FLinearColor& Color)
    {
        if (!IsValid(Mesh)) return false;
        static const FName Parameter(TEXT("PaintColor"));
        bool bChanged = false;
        for (int32 Index = 0; Index < Mesh->GetNumMaterials(); ++Index)
        {
            auto* Material = Cast<UMaterialInstanceDynamic>(Mesh->GetMaterial(Index));
            FLinearColor Existing;
            if (Material && Material->GetVectorParameterValue(FHashedMaterialParameterInfo(Parameter), Existing)
                && !Existing.Equals(Color, .0001f))
            {
                Material->SetVectorParameterValue(Parameter, Color);
                bChanged = true;
            }
        }
        return bChanged;
    }

    static void RefreshVehiclePaint(APlayerController* PC, UObject* Core)
    {
        if (!Core) return;
        APawn* Rider = PC->GetPawn();
        for (bool bMoto : {false, true})
        {
            const auto Color = ReadPaint(Core, ReadName(Core, bMoto ? TEXT("MotoModel") : TEXT("BikeModel")));
            if (Color)
                ApplyPaint(Cast<UStaticMeshComponent>(ReadObject(Rider, bMoto ? TEXT("MotoFrame") : TEXT("Bicycle"))), *Color);
        }
        auto* Parked = ReadObject(Rider, TEXT("ParkedVehicle"));
        if (const auto Color = ReadPaint(Core, ReadName(Parked, TEXT("ModelID"))))
            ApplyPaint(Cast<UStaticMeshComponent>(ReadObject(Parked, TEXT("Body"))), *Color);
    }

    void RefreshGarage()
    {
        if (!GarageImage) return;
        auto* Core = DeliveryFor(Controller.Get());
        auto* Phone = PhoneFor(Core);
        auto* Preview = ReadObject(Phone, TEXT("GaragePreview"));
        auto* Texture = Cast<UTextureRenderTarget2D>(ReadObject(Preview, TEXT("PreviewTexture")));
        if (GarageBrush.GetResourceObject() != Texture)
        {
            GarageBrush.SetResourceObject(Texture);
            GarageImage->Invalidate(EInvalidateWidgetReason::Paint);
        }
        const FName Model = ReadName(Core, bGarageMoto ? TEXT("MotoModel") : TEXT("BikeModel"));
        const int32 Index = static_cast<int32>(ReadNumber(Core, bGarageMoto ? TEXT("MotoColor") : TEXT("BikeColor"), 0));
        const auto Saved = ReadPaint(Core, Model);
        const FLinearColor Color = bPaintPickerOpen || bCustomPaintSelected ? PaintHSV.HSVToLinearRGB()
            : PaintSelection != INDEX_NONE ? PresetPaint(PaintSelection) : Saved.Get(PresetPaint(Index));
        if (ApplyPaint(Cast<UStaticMeshComponent>(ReadObject(Preview, TEXT("Body"))), Color))
            if (auto* Capture = Cast<USceneCaptureComponent2D>(ReadObject(Preview, TEXT("WorkshopCamera"))))
                Capture->CaptureScene();
    }

    void BuyPaint()
    {
        auto* Core = DeliveryFor(Controller.Get());
        const FName IndexName = bGarageMoto ? TEXT("MotoColor") : TEXT("BikeColor");
        const auto* Index = Core ? FindFProperty<FIntProperty>(Core->GetClass(), IndexName) : nullptr;
        const auto* Balance = Core ? FindFProperty<FIntProperty>(Core->GetClass(), TEXT("Balance")) : nullptr;
        const auto* Developer = Core ? FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("DeveloperMode")) : nullptr;
        auto* Save = Core ? Core->FindFunction(TEXT("SaveProfile")) : nullptr;
        const auto* Result = Save ? CastField<FBoolProperty>(Save->GetReturnProperty()) : nullptr;
        auto Map = PaintMap(Core);
        const FName Model = ReadName(Core, bGarageMoto ? TEXT("MotoModel") : TEXT("BikeModel"));
        if (!Map || Model.IsNone() || !Index || !Balance || !Result || Save->NumParms != 1) return;
        if (bGarageMoto && !OwnsUpgrade(TEXT("Motorcycle")))
        {
            PaintMessage = FText::FromString(TEXT("Primero compra la moto"));
            return;
        }

        const FName Key = PaintKey(Model);
        const auto* Prior = reinterpret_cast<const int32*>(Map->FindValueFromHash(&Key));
        const TOptional<int32> OldCustom = Prior ? TOptional<int32>(*Prior) : TOptional<int32>();
        const auto* PriorPreset = reinterpret_cast<const int32*>(Map->FindValueFromHash(&Model));
        const TOptional<int32> OldPreset = PriorPreset ? TOptional<int32>(*PriorPreset) : TOptional<int32>();
        const int32 OldIndex = Index->GetPropertyValue_InContainer(Core);
        const int32 NewIndex = PaintSelection == INDEX_NONE ? OldIndex : PaintSelection;
        const int32 Custom = static_cast<int32>(PaintHSV.HSVToLinearRGB().ToFColorSRGB().ToPackedARGB());
        if (bCustomPaintSelected ? (OldCustom && *OldCustom == Custom) : (!OldCustom && NewIndex == OldIndex))
        {
            PaintMessage = FText::FromString(TEXT("Ya tiene ese color"));
            return;
        }
        const int32 Funds = Balance->GetPropertyValue_InContainer(Core);
        if (Funds < 2000)
        {
            PaintMessage = FText::FromString(TEXT("Necesitas $2.000"));
            return;
        }

        if (bCustomPaintSelected) Map->AddPair(&Key, &Custom);
        else
        {
            Map->RemovePair(&Key);
            Map->AddPair(&Model, &NewIndex);
            Index->SetPropertyValue_InContainer(Core, NewIndex);
        }
        Balance->SetPropertyValue_InContainer(Core, Funds - 2000);
        FStructOnScope Args(Save);
        Core->ProcessEvent(Save, Args.GetStructMemory());
        if (!Result->GetPropertyValue_InContainer(Args.GetStructMemory()))
        {
            if (OldCustom) Map->AddPair(&Key, &*OldCustom);
            else Map->RemovePair(&Key);
            if (OldPreset) Map->AddPair(&Model, &*OldPreset);
            else Map->RemovePair(&Model);
            Index->SetPropertyValue_InContainer(Core, OldIndex);
            Balance->SetPropertyValue_InContainer(Core, Funds);
            PaintMessage = FText::FromString(TEXT("No se pudo guardar"));
            return;
        }

        if (!bCustomPaintSelected)
        {
            APawn* Rider = Controller.IsValid() ? Controller->GetPawn().Get() : nullptr;
            ApplyPaint(Cast<UStaticMeshComponent>(ReadObject(Rider, bGarageMoto ? TEXT("MotoFrame") : TEXT("Bicycle"))), PresetPaint(NewIndex));
            auto* Parked = ReadObject(Rider, TEXT("ParkedVehicle"));
            if (ReadName(Parked, TEXT("ModelID")) == Model)
                ApplyPaint(Cast<UStaticMeshComponent>(ReadObject(Parked, TEXT("Body"))), PresetPaint(NewIndex));
        }
        PaintMessage = FText::FromString(Developer && Developer->GetPropertyValue_InContainer(Core)
            ? TEXT("Pintado en modo desarrollador") : TEXT("Color aplicado"));
        Invoke(Core, TEXT("Changed"));
        RefreshGarage();
    }

    void RefreshWorld()
    {
        UWorld* World = Viewport.IsValid() ? Viewport->GetWorld() : nullptr;
        if (!World) return;
        if (!WorldState.IsValid())
        {
            for (TActorIterator<AActor> It(World); It; ++It)
            {
                if (It->GetClass()->GetFName() == FName(TEXT("BP_WorldState_C")))
                {
                    WorldState = *It;
                    break;
                }
            }
        }
        if (!WorldState.IsValid()) return;
        const double Hour = ReadNumber(WorldState.Get(), TEXT("Hour"), -1.);
        if (Clock && Hour >= 0.)
        {
            const int32 Minutes = FMath::FloorToInt(Hour * 60.) % 1440;
            Clock->SetText(FText::FromString(FString::Printf(TEXT("%02d:%02d"), Minutes / 60, Minutes % 60)));
        }
        if (Weather)
        {
            const double Rain = ReadNumber(WorldState.Get(), TEXT("RainIntensity"), 0.);
            Weather->SetImage(Art(Rain > .32 ? TEXT("Lluvia") : Rain > .05 ? TEXT("Nublado") : TEXT("Soleado")));
        }
    }

    FSlateFontInfo SecondaryFont(int32 Size) const
    {
        Size = FMath::Max(14, FMath::RoundToInt(Size * 1.40f));
        const auto Plugin = IPluginManager::Get().FindPlugin(TEXT("BogotaPhonePreview"));
        const FString File = Plugin ? FPaths::Combine(Plugin->GetBaseDir(), TEXT("Resources/f1-secuencia-quad-ffp.ttf")) : FString();
        return FPaths::FileExists(File) ? FSlateFontInfo(File, Size) : FCoreStyle::GetDefaultFontStyle("Regular", Size);
    }

    static FGuid OrderID(const UStruct* Type, const void* Entry)
    {
        for (TFieldIterator<FStructProperty> It(Type); It; ++It)
            if (It->Struct == TBaseStructure<FGuid>::Get() && It->GetName().StartsWith(TEXT("ID")))
                return *It->ContainerPtrToValuePtr<FGuid>(Entry);
        return {};
    }

    static bool IsSpecialOffer(const UStruct* Type, const void* Entry, FGuid& ID)
    {
        ID = OrderID(Type, Entry);
        return ID.IsValid() && GetTypeHash(ID) % 8 == 0;
    }

    static bool HasSpecialAccess(UObject* Core)
    {
        auto Map = PaintMap(Core);
        const FName Key(TEXT("SpecialDeliveryLicense"));
        return Map && Map->FindValueFromHash(&Key);
    }

    static constexpr int32 SpecialAccessPrice = 180000;

    void BuySpecialAccess()
    {
        auto* Core = DeliveryFor(Controller.Get());
        if (!Core || HasSpecialAccess(Core)) return;
        const auto* Dev = FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("DeveloperMode"));
        const auto* Balance = FindFProperty<FIntProperty>(Core->GetClass(), TEXT("Balance"));
        auto Map = PaintMap(Core);
        if (!Balance || !Map || (Dev && Dev->GetPropertyValue_InContainer(Core))) return;
        const int32 Cash = Balance->GetPropertyValue_InContainer(Core);
        if (Cash < SpecialAccessPrice) return;
        const FName Key(TEXT("SpecialDeliveryLicense"));
        const int32 Enabled = 1;
        Balance->SetPropertyValue_InContainer(Core, Cash - SpecialAccessPrice);
        Map->AddPair(&Key, &Enabled);
        if (!QueryBool(Core, TEXT("SaveProfile")))
        {
            Map->RemovePair(&Key);
            Balance->SetPropertyValue_InContainer(Core, Cash);
        }
        ApplySpecialOfferPremium(Core);
        RefreshOrders();
    }

    void TrackSpecialTimers(UObject* Core, UWorld* World)
    {
        FocusedSpecialSeconds = INDEX_NONE;
        if (!Core || (PremiumOffers.IsEmpty() && SpecialDeadlines.IsEmpty())) return;
        const auto* Active = FindFProperty<FArrayProperty>(Core->GetClass(), TEXT("ActiveOrders"));
        const auto* ActiveType = Active ? CastField<FStructProperty>(Active->Inner) : nullptr;
        const auto* Focus = FindFProperty<FStructProperty>(Core->GetClass(), TEXT("Order"));
        if (!ActiveType || !Focus) return;
        const FStructProperty* Nested = nullptr;
        for (TFieldIterator<FStructProperty> It(ActiveType->Struct); It; ++It)
            if (It->Struct == Focus->Struct) { Nested = *It; break; }
        if (!Nested) return;
        auto* FocusData = Focus->ContainerPtrToValuePtr<void>(Core);
        const FGuid FocusID = OrderID(Focus->Struct, FocusData);
        const double Now = World->GetTimeSeconds();
        FScriptArrayHelper Entries(Active, Active->ContainerPtrToValuePtr<void>(Core));
        TSet<FGuid> Current;
        for (int32 Index = 0; Index < Entries.Num(); ++Index)
        {
            void* Data = Nested->ContainerPtrToValuePtr<void>(Entries.GetRawPtr(Index));
            const FGuid ID = OrderID(Nested->Struct, Data);
            if (!PremiumOffers.Contains(ID) && !SpecialDeadlines.Contains(ID)) continue;
            Current.Add(ID);
            const double Deadline = SpecialDeadlines.FindOrAdd(ID, Now + 300.0);
            if (ID == FocusID) FocusedSpecialSeconds = FMath::Max(0, FMath::CeilToInt(Deadline - Now));
            if (Deadline <= Now)
                if (const auto* Base = SpecialBaseRewards.Find(ID))
                    for (TFieldIterator<FIntProperty> It(Nested->Struct); It; ++It)
                        if (It->GetName().StartsWith(TEXT("Reward")))
                        {
                            It->SetPropertyValue_InContainer(Data, *Base);
                            if (ID == FocusID) It->SetPropertyValue_InContainer(FocusData, *Base);
                            break;
                        }
        }
        for (auto It = SpecialDeadlines.CreateIterator(); It; ++It)
            if (!Current.Contains(It.Key())) It.RemoveCurrent();
    }

    void ApplySpecialOfferPremium(UObject* Core)
    {
        if (PremiumCore.Get() != Core)
        {
            PremiumCore = Core;
            PremiumOffers.Reset();
            SpecialBaseRewards.Reset();
            SpecialDeadlines.Reset();
        }
        if (!HasSpecialAccess(Core)) return;
        const auto* Offers = Core ? FindFProperty<FArrayProperty>(Core->GetClass(), TEXT("Offers")) : nullptr;
        const auto* OrderType = Offers ? CastField<FStructProperty>(Offers->Inner) : nullptr;
        if (!OrderType) return;
        FScriptArrayHelper Entries(Offers, Offers->ContainerPtrToValuePtr<void>(Core));
        TSet<FGuid> Current;
        for (int32 Index = 0; Index < Entries.Num(); ++Index)
        {
            void* Entry = Entries.GetRawPtr(Index);
            FGuid ID;
            if (!IsSpecialOffer(OrderType->Struct, Entry, ID)) continue;
            for (TFieldIterator<FIntProperty> It(OrderType->Struct); It; ++It)
            {
                if (!It->GetName().StartsWith(TEXT("Reward"))) continue;
                const int32 Base = It->GetPropertyValue_InContainer(Entry);
                if (Base <= 0) break;
                Current.Add(ID);
                if (!PremiumOffers.Contains(ID))
                {
                    SpecialBaseRewards.Add(ID, Base);
                    It->SetPropertyValue_InContainer(Entry, static_cast<int32>(FMath::Min<int64>(MAX_int32, Base + (static_cast<int64>(Base) + 2) / 4)));
                }
                break;
            }
        }
        PremiumOffers = MoveTemp(Current);
        for (auto It = SpecialBaseRewards.CreateIterator(); It; ++It)
            if (!PremiumOffers.Contains(It.Key()) && !SpecialDeadlines.Contains(It.Key())) It.RemoveCurrent();
    }

    TSharedRef<SWidget> OrderDetails(const FString& Entry)
    {
        TArray<FString> Lines;
        Entry.ParseIntoArrayLines(Lines, false);
        if (Lines.Num() < 3)
            return SNew(STextBlock).Font(SecondaryFont(12)).Text(FText::FromString(Entry));
        const FString Name = Lines[0];
        const FString Lower = Name.ToLower();
        const TCHAR* Store = TEXT("Mercado");
        if (Lower.Contains(TEXT("caf"))) Store = TEXT("Cafe");
        else if (Lower.Contains(TEXT("drog")) || Lower.Contains(TEXT("farmacia"))) Store = TEXT("Farmacia");
        else if (Lower.Contains(TEXT("circuito")) || Lower.Contains(TEXT("laboratorio"))) Store = TEXT("Electronica");
        else if (Lower.Contains(TEXT("flor"))) Store = TEXT("Flores");
        else if (Lower.Contains(TEXT("ferreter"))) Store = TEXT("Ferreteria");
        else if (Lower.Contains(TEXT("huellas"))) Store = TEXT("Mascotas");
        else if (Lower.Contains(TEXT("esquina"))) Store = TEXT("Panaderia");
        else if (Lower.Contains(TEXT("cuadra"))) Store = TEXT("Pizza");
        else if (Lower.Contains(TEXT("plancha")) || Lower.Contains(TEXT("parada"))) Store = TEXT("Comida");
        const bool bSpecial = Lines.Num() > 3;
        static const FSlateColorBrush GoldTrim(FLinearColor(.91f,.53f,.09f));
        auto Details = SNew(SVerticalBox);
        if (bSpecial)
            Details->AddSlot().AutoHeight().Padding(0,0,0,3)
                [SNew(STextBlock).Font(SecondaryFont(11)).ColorAndOpacity(FLinearColor(1,.74f,.27f))
                 .Text(FText::FromString(TEXT("ESPECIAL · +25 % EN 5 MIN")))];
        Details->AddSlot().AutoHeight()[SNew(STextBlock).Font(SecondaryFont(13)).AutoWrapText(true).Text(FText::FromString(Name))];
        for (int32 I=1; I<3; ++I)
        {
            Details->AddSlot().AutoHeight().Padding(0,3)
            [
                SNew(SHorizontalBox)
                + SHorizontalBox::Slot().AutoWidth().Padding(0,0,7,0)
                [SNew(SBox).WidthOverride(16).HeightOverride(16)
                 [SNew(SScaleBox).Stretch(EStretch::ScaleToFit)
                  [SNew(SImage).Image(Art(I==1 ? TEXT("DineroPedido") : TEXT("Destino")))]]]
                + SHorizontalBox::Slot().FillWidth(1)
                [SNew(STextBlock).Font(SecondaryFont(12)).Text(FText::FromString(Lines[I]))]
            ];
        }
        return SNew(SHorizontalBox)
            + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,10,0)
            [SNew(SBox).WidthOverride(49).HeightOverride(49)
             [SNew(SOverlay)
              + SOverlay::Slot()[SNew(SImage).Image(bSpecial ? &GoldTrim : FCoreStyle::Get().GetBrush("NoBrush"))]
              + SOverlay::Slot().Padding(bSpecial ? 2 : 0)[SNew(SImage).Image(Art(Store))]] ]
            + SHorizontalBox::Slot().FillWidth(1)[Details];
    }

    static int32 OrderCapacity(UObject* Core)
    {
        auto* Capacity = Core ? Core->FindFunction(TEXT("CargoCapacity")) : nullptr;
        const auto* Moto = Capacity ? FindFProperty<FBoolProperty>(Capacity, TEXT("Motorcycle")) : nullptr;
        const auto* Result = Capacity ? CastField<FIntProperty>(Capacity->GetReturnProperty()) : nullptr;
        if (!Moto || !Result || Capacity->NumParms != 2) return 1;
        FStructOnScope Args(Capacity);
        Moto->SetPropertyValue_InContainer(Args.GetStructMemory(), ReadNumber(Core, TEXT("Vehicle"), 0) == 1);
        Core->ProcessEvent(Capacity, Args.GetStructMemory());
        return Result->GetPropertyValue_InContainer(Args.GetStructMemory());
    }

    static bool SelectOrder(UObject* Core, FName Method, int32 Index)
    {
        auto* Function = Core ? Core->FindFunction(Method) : nullptr;
        const auto* Entry = Function ? FindFProperty<FIntProperty>(Function, TEXT("Index")) : nullptr;
        const auto* Result = Function ? CastField<FBoolProperty>(Function->GetReturnProperty()) : nullptr;
        if (!Entry || !Result || Function->NumParms != 2) return false;
        FStructOnScope Args(Function);
        Entry->SetPropertyValue_InContainer(Args.GetStructMemory(), Index);
        Core->ProcessEvent(Function, Args.GetStructMemory());
        return Result->GetPropertyValue_InContainer(Args.GetStructMemory());
    }

    static constexpr const TCHAR* CargoUpgrades[] = {TEXT("CargoBackpack"), TEXT("CargoWaist"), TEXT("CargoPanniers")};

    void PurchaseCargo(int32 Index)
    {
        if (Index < 0 || Index >= UE_ARRAY_COUNT(CargoUpgrades)) return;
        auto* Core = DeliveryFor(Controller.Get());
        auto* Purchase = Core ? Core->FindFunction(TEXT("PurchaseUpgrade")) : nullptr;
        const auto* ID = Purchase ? FindFProperty<FNameProperty>(Purchase, TEXT("ID")) : nullptr;
        if (!ID || Purchase->NumParms != 2) return;
        FStructOnScope Args(Purchase);
        ID->SetPropertyValue_InContainer(Args.GetStructMemory(), FName(CargoUpgrades[Index]));
        Core->ProcessEvent(Purchase, Args.GetStructMemory());
    }

    TArray<FString> ActiveOrderLabels(UObject* Core) const
    {
        TArray<FString> Labels;
        const auto* Active = Core ? FindFProperty<FArrayProperty>(Core->GetClass(), TEXT("ActiveOrders")) : nullptr;
        const auto* Type = Active ? CastField<FStructProperty>(Active->Inner) : nullptr;
        const auto* Focus = Core ? FindFProperty<FStructProperty>(Core->GetClass(), TEXT("Order")) : nullptr;
        if (!Type || !Focus) return Labels;
        const FGuid Selected = OrderID(Focus->Struct, Focus->ContainerPtrToValuePtr<void>(Core));
        const FStructProperty* Nested = nullptr;
        for (TFieldIterator<FStructProperty> It(Type->Struct); It; ++It)
            if (It->Struct == Focus->Struct) { Nested = *It; break; }
        if (!Nested) return Labels;

        const FTextProperty* Pickup = nullptr;
        const FTextProperty* Destination = nullptr;
        for (TFieldIterator<FTextProperty> It(Nested->Struct); It; ++It)
        {
            if (It->GetName().StartsWith(TEXT("PickupName"))) Pickup = *It;
            if (It->GetName().StartsWith(TEXT("DropoffName"))) Destination = *It;
        }
        FScriptArrayHelper Entries(Active, Active->ContainerPtrToValuePtr<void>(Core));
        for (int32 Index = 0; Index < Entries.Num(); ++Index)
        {
            const void* Data = Nested->ContainerPtrToValuePtr<void>(Entries.GetRawPtr(Index));
            const bool bSelected = OrderID(Nested->Struct, Data) == Selected;
            Labels.Add(FString::Printf(TEXT("%d. %s%s\n%s"), Index + 1,
                Pickup ? *Pickup->GetPropertyValue_InContainer(Data).ToString() : TEXT("Pedido"),
                bSelected ? TEXT(" · EN RUTA") : TEXT(""),
                Destination ? *Destination->GetPropertyValue_InContainer(Data).ToString() : TEXT("")));
        }
        return Labels;
    }

    void RefreshOrders()
    {
        if (!Orders) return;
        APawn* Pawn = Controller.IsValid() ? Controller->GetPawn() : nullptr;
        const auto* DeliveryField = Pawn ? FindFProperty<FObjectPropertyBase>(Pawn->GetClass(), TEXT("Delivery")) : nullptr;
        UObject* Delivery = DeliveryField ? DeliveryField->GetObjectPropertyValue_InContainer(Pawn) : nullptr;
        const auto* Offers = Delivery ? FindFProperty<FArrayProperty>(Delivery->GetClass(), TEXT("Offers")) : nullptr;
        const auto* OrderType = Offers ? CastField<FStructProperty>(Offers->Inner) : nullptr;
        TArray<FString> Rows;
        if (OrderType)
        {
            const void* Array = Offers->ContainerPtrToValuePtr<void>(Delivery);
            FScriptArrayHelper Entries(Offers, Array);
            for (int32 Index = 0; Index < Entries.Num(); ++Index)
            {
                const void* Entry = Entries.GetRawPtr(Index);
                FString Pickup, Dropoff;
                double Meters = 0;
                int32 Reward = 0;
                for (TFieldIterator<FProperty> It(OrderType->Struct); It; ++It)
                {
                    const FString Name = It->GetName();
                    if (const auto* Field = CastField<FTextProperty>(*It))
                    {
                        if (Name.StartsWith(TEXT("PickupName"))) Pickup = Field->GetPropertyValue_InContainer(Entry).ToString();
                        if (Name.StartsWith(TEXT("DropoffName"))) Dropoff = Field->GetPropertyValue_InContainer(Entry).ToString();
                    }
                    if (Name.StartsWith(TEXT("DistanceMeters")))
                        if (const auto* Field = CastField<FNumericProperty>(*It); Field && Field->IsFloatingPoint())
                            Meters = Field->GetFloatingPointPropertyValue(Field->ContainerPtrToValuePtr<void>(Entry));
                    if (Name.StartsWith(TEXT("Reward")))
                    {
                        if (const auto* Field = CastField<FNumericProperty>(*It))
                        {
                            const void* Value = Field->ContainerPtrToValuePtr<void>(Entry);
                            Reward = Field->IsFloatingPoint() ? FMath::RoundToInt(Field->GetFloatingPointPropertyValue(Value)) : static_cast<int32>(Field->GetSignedIntPropertyValue(Value));
                        }
                    }
                }
                FGuid ID;
                const bool bSpecial = IsSpecialOffer(OrderType->Struct, Entry, ID) && PremiumOffers.Contains(ID);
                Rows.Add(FString::Printf(TEXT("%s\n%s\n%.1f km%s"), *Pickup, *Pesos(Reward), Meters / 1000.,
                    bSpecial ? TEXT("\nEspecial") : TEXT("")));
            }
        }
        if (Rows.IsEmpty()) Rows.Add(Delivery ? TEXT("No hay pedidos disponibles") : TEXT("Esperando datos de pedidos"));
        auto ActiveRows = ActiveOrderLabels(Delivery);
        const int32 Capacity = OrderCapacity(Delivery);
        if (Rows == OrderSnapshot && ActiveRows == ActiveOrderSnapshot && Capacity == OrderCapacitySnapshot) return;
        if (HoldingOrder != INDEX_NONE) return;
        OrderSnapshot = MoveTemp(Rows);
        ActiveOrderSnapshot = MoveTemp(ActiveRows);
        OrderCapacitySnapshot = Capacity;
        Orders->ClearChildren();
        const bool bHasSpace = ActiveOrderSnapshot.Num() < Capacity;
        Orders->AddSlot().Padding(5,3,5,7)
            [SNew(STextBlock).Font(SecondaryFont(12)).Text(FText::FromString(FString::Printf(
                TEXT("ENTREGAS ACTIVAS   %d / %d"), ActiveOrderSnapshot.Num(), Capacity)))];
        for (int32 Index = 0; Index < ActiveOrderSnapshot.Num(); ++Index)
            Orders->AddSlot().Padding(0,0,0,5)
            [SNew(SButton).HAlign(HAlign_Fill).ContentPadding(FMargin(8,4))
             .OnClicked_Lambda([this, Index] {
                 if (SelectOrder(DeliveryFor(Controller.Get()), TEXT("SelectActiveOrder"), Index)) RefreshOrders();
                 return FReply::Handled();
             })
             [SNew(STextBlock).Font(SecondaryFont(11)).AutoWrapText(true)
              .Text(FText::FromString(ActiveOrderSnapshot[Index]))]];
        if (!bHasSpace)
        {
            Orders->AddSlot().Padding(5,8)
                [SNew(STextBlock).Font(SecondaryFont(11)).AutoWrapText(true)
                 .Text(FText::FromString(TEXT("Completa una entrega para aceptar otro pedido.")))];
            return;
        }
        for (int32 Index = 0; Index < OrderSnapshot.Num(); ++Index)
        {
            static const FSlateColorBrush Tile(FLinearColor(.015f, .065f, .095f));
            Orders->AddSlot().Padding(0, 0, 0, 7)
            [
                SNew(SBorder).BorderImage(&Tile).Padding(10.f)
                [
                    SNew(SVerticalBox)
                    + SVerticalBox::Slot().AutoHeight()
                    [OrderDetails(OrderSnapshot[Index])]
                    + SVerticalBox::Slot().AutoHeight().Padding(0, 5, 0, 0)
                    [
                        SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").ContentPadding(0).Visibility(OrderType && FScriptArrayHelper(Offers, Offers->ContainerPtrToValuePtr<void>(Delivery)).IsValidIndex(Index)
                            ? EVisibility::Visible : EVisibility::Collapsed)
                        .OnPressed_Lambda([this, Index]() {
                            if (SelectOrder(DeliveryFor(Controller.Get()), TEXT("SelectOffer"), Index))
                            {
                                HoldingOrder = Index;
                                PhoneAction(TEXT("AcceptPressed"));
                            }
                        })
                        .OnReleased_Lambda([this]() { HoldingOrder = INDEX_NONE; PhoneAction(TEXT("AcceptReleased")); })
                        [
                         SNew(SBox).HeightOverride(25)
                         [SNew(SOverlay)
                         + SOverlay::Slot()
                         [SNew(SImage).Image(Art(TEXT("AceptarPedido"))).ColorAndOpacity(FLinearColor(.65f,.77f,.80f))]
                         + SOverlay::Slot()
                         [SNew(SProgressBar).Visibility(EVisibility::HitTestInvisible)
                          .BackgroundImage(FCoreStyle::Get().GetBrush("NoBrush"))
                          .FillImage(Art(TEXT("AceptarPedido")))
                          .BorderPadding(FVector2D::ZeroVector)
                          .FillColorAndOpacity(FLinearColor::White)
                          .Percent_Lambda([this,Index]() -> TOptional<float>
                          {
                              return HoldingOrder == Index ? static_cast<float>(FMath::Clamp(ReadNumber(DeliveryFor(Controller.Get()), TEXT("HoldProgress"),0.),0.,1.)) : 0.f;
                          })]
                         + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
                         [SNew(STextBlock).Font(SecondaryFont(10)).Text(FText::FromString(TEXT("Mantén para aceptar")))]]
                        ]
                    ]
                ]
            ];
        }
    }

    static UObject* DeliveryFor(APlayerController* Controller)
    {
        APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
        const auto* Field = Pawn ? FindFProperty<FObjectPropertyBase>(Pawn->GetClass(), TEXT("Delivery")) : nullptr;
        return Field ? Field->GetObjectPropertyValue_InContainer(Pawn) : nullptr;
    }

    static UUserWidget* PhoneFor(UObject* Core)
    {
        const auto* Field = Core ? FindFProperty<FObjectPropertyBase>(Core->GetClass(), TEXT("PhoneWidget")) : nullptr;
        return Field ? Cast<UUserWidget>(Field->GetObjectPropertyValue_InContainer(Core)) : nullptr;
    }

    static void Invoke(UObject* Object, FName Name)
    {
        UFunction* Function = Object ? Object->FindFunction(Name) : nullptr;
        if (Function && Function->ParmsSize == 0) Object->ProcessEvent(Function, nullptr);
    }

    void SelectEntry(int32 Index)
    {
        UUserWidget* Phone = PhoneFor(DeliveryFor(Controller.Get()));
        UFunction* Function = Phone ? Phone->FindFunction(TEXT("SelectEntry")) : nullptr;
        if (!Function || Function->ParmsSize != sizeof(int32)) return;
        Phone->ProcessEvent(Function, &Index);
    }

    void PhoneAction(FName Name) { Invoke(PhoneFor(DeliveryFor(Controller.Get())), Name); }

    const FSlateBrush* FullMapArt()
    {
        if (!FullMapBrush.GetResourceObject())
        {
            auto* Texture = LoadObject<UTexture2D>(nullptr, TEXT("/Game/Polish20261102/T_Mapa.T_Mapa"));
            FullMapBrush.SetResourceObject(Texture);
            FullMapBrush.DrawAs = ESlateBrushDrawType::Image;
        }
        return &FullMapBrush;
    }

    void Navigate(const FString& Page)
    {
        if (Page == TEXT("Configuracion"))
        {
            auto* PC = Controller.Get();
            auto* World = PC ? PC->GetWorld() : nullptr;
            if (!World) return;
            auto* View = Viewport.Get();
            Invoke(DeliveryFor(PC), TEXT("TogglePhone"));
            Close();
            OpenPause(View, PC);
            return;
        }
        if (Page == TEXT("Pedidos")) PhoneAction(TEXT("OpenOrders"));
        else if (Page == TEXT("Inicio")) PhoneAction(TEXT("OpenHome"));
        else if (Page == TEXT("Mapa")) PhoneAction(TEXT("OpenMap"));
        else if (Page == TEXT("Taller")) PhoneAction(TEXT("OpenShop"));
        else if (Page == TEXT("Cicla")) { PhoneAction(TEXT("OpenShop")); PhoneAction(TEXT("GarageBike")); }
        else if (Page == TEXT("Moto")) { PhoneAction(TEXT("OpenShop")); PhoneAction(TEXT("GarageMoto")); }
        else if (Page == TEXT("Carga")) PhoneAction(TEXT("OpenCargo"));
        Show(Page);
    }

    int32 PhoneTutorialTarget(const FString& Page) const
    {
        if (Page == TEXT("Inicio") && TutorialStep == 1) return 75;
        if (Page == TEXT("Inicio") && TutorialStep == 6) return 260;
        return INDEX_NONE;
    }

    void Show(const FString& Page)
    {
        CurrentPhonePage = Page;
        if (!Viewport.IsValid()) return;
        if (Overlay) Viewport->RemoveViewportWidgetContent(Overlay.ToSharedRef());
        Orders.Reset();
        OrderSnapshot.Reset();
        ActiveOrderSnapshot.Reset();
        OrderCapacitySnapshot = 0;
        HoldingOrder = INDEX_NONE;
        GarageImage.Reset();
        GarageBrush.SetResourceObject(nullptr);
        Clock.Reset();
        Weather.Reset();
        const bool Map = Page == TEXT("Mapa");
        bMapPage = Map;
        MapOpening.Reset();
        MapInput.Reset();
        MapZoom = 1.f;
        MapPan = FVector2D::ZeroVector;
        const bool LayeredGarage = Page == TEXT("Cicla") || Page == TEXT("Moto");
        bGarageMoto = Page == TEXT("Moto");
        CargoSelection = 0;
        bPaintPickerOpen = false;
        bCustomPaintSelected = false;
        PaintSelection = INDEX_NONE;
        PaintMessage = FText::GetEmpty();
        const float Width = 352.f;
        const float Height = 644.f;
        auto Canvas = SNew(SConstraintCanvas);
        Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(0, 0, Width, Height))[SNew(SImage).Image(Art(Map ? FString(TEXT("MapaVertical")) : LayeredGarage ? Page + TEXT("Fondo") : Page)).Visibility(EVisibility::HitTestInvisible)];

        const FString List = Page + TEXT("Lista");
        if (Page == TEXT("Servicios"))
        {
            ServiceStatus = FText::GetEmpty();
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(24, 164, 304, 371)).ZOrder(4)[ServicesList()];
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(94, 132, 65, 16)).ZOrder(4)
                [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                 [SNew(STextBlock).Font(SecondaryFont(10)).Text_Lambda([this] {
                     auto* Core = DeliveryFor(Controller.Get());
                     return FText::FromString(Pesos(TotalBillsDue(Core) + FMath::Max(0, RescueQuote())));
                 })]];
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(217, 132, 86, 16)).ZOrder(4)
                [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                 [SNew(STextBlock).Font(SecondaryFont(10)).Text_Lambda([this] { return LiveBalance(); })]];
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(31, 146, 286, 24)).ZOrder(4)
                [SNew(SBox).HAlign(HAlign_Center).VAlign(VAlign_Center)
                 [SNew(STextBlock).Font(SecondaryFont(10)).Text_Lambda([this] {
                     auto* Core = DeliveryFor(Controller.Get());
                     const int32 Index = TutorialStep == 6 ? TutorialBill(Core) : INDEX_NONE;
                     return ServiceStatus.IsEmpty() && Index != INDEX_NONE
                         ? FText::FromString(FString::Printf(TEXT("Primer pago  ·  %s"), Bills[Index].Name))
                         : ServiceStatus;
                 })]];
        }

        if (Page == TEXT("Cicla") || Page == TEXT("Moto") || Page == TEXT("Carga"))
        {
            const FSlateBrush* Brush = Art(List);
            const float Top = 304.f;
            if (Brush)
            {
                const float Scale = 304.f / Brush->ImageSize.X;
                const float Cell = Scale * 3.f;
                // The row starts with the number at pixel 3 and ends at pixel 488.
                constexpr float RowCenter = (3.f + 488.f) * .5f;
                const float RowOffset = (Brush->ImageSize.X * .5f - RowCenter) * Scale;
                const float ArtWidth = Brush->ImageSize.X - RowOffset / Scale;
                const bool bMotoList = Page == TEXT("Moto");
                constexpr float RetiredRowTop = 537.f;
                constexpr float RetiredRowHeight = 102.f;
                const float ArtHeight = Brush->ImageSize.Y - (bMotoList ? RetiredRowHeight : 0.f);
                const float UpperHeight = bMotoList ? RetiredRowTop : ArtHeight;
                auto CropList = [&](FSlateBrush& Out, float TopPixel, float BottomPixel)
                {
                    Out = *Brush;
                    Out.SetUVRegion(FBox2f(FVector2f(0, TopPixel / Brush->ImageSize.Y),
                        FVector2f(ArtWidth / Brush->ImageSize.X, BottomPixel / Brush->ImageSize.Y)));
                };
                CropList(WorkshopListBrush, 0.f, UpperHeight);
                auto Content = SNew(SConstraintCanvas)
                    .RenderTransform(FSlateRenderTransform(FVector2D(RowOffset,0)));
                Content->AddSlot().Alignment(FVector2D::ZeroVector)
                    .Offset(FMargin(0, 0, ArtWidth * Scale, UpperHeight * Scale))
                    [SNew(SImage).Image(&WorkshopListBrush)];
                if (bMotoList)
                {
                    CropList(WorkshopListBottomBrush, RetiredRowTop + RetiredRowHeight, Brush->ImageSize.Y);
                    Content->AddSlot().Alignment(FVector2D::ZeroVector)
                        .Offset(FMargin(0, UpperHeight * Scale, ArtWidth * Scale, (ArtHeight - UpperHeight) * Scale))
                        [SNew(SImage).Image(&WorkshopListBottomBrush)];
                }
                auto Action = [&](int32 X, int32 Y, int32 W, int32 H, int32 Entry, FName Method)
                {
                    Content->AddSlot().Alignment(FVector2D::ZeroVector)
                        .Offset(FMargin(X * Cell, Y * Cell, W * Cell, H * Cell)).ZOrder(2)
                    [
                        SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder")
                        .OnClicked_Lambda([this, Entry, Method]()
                        {
                            if (Entry >= 10 && Entry <= 12) CargoSelection = Entry - 10;
                            if (Entry >= 0) SelectEntry(Entry);
                            if (Method == TEXT("BuySelected") && Entry >= 10 && Entry <= 12)
                                PurchaseCargo(Entry - 10);
                            else if (!Method.IsNone()) PhoneAction(Method);
                            return FReply::Handled();
                        })
                    ];
                };
                const bool Bike = Page == TEXT("Cicla"), Moto = Page == TEXT("Moto"), Cargo = Page == TEXT("Carga");
                if (Bike || Moto || Cargo)
                {
                    const int32 Count = Bike ? 4 : Moto ? 5 : 3;
                    const int32 First = Bike ? 0 : Moto ? 4 : 10;
                    for (int32 Index = 0; Index < Count; ++Index)
                    {
                        const int32 Y = 9 + 34 * Index;
                        static const FSlateColorBrush NumberTile(FLinearColor(.06f,.40f,.40f));
                        Content->AddSlot().Alignment(FVector2D::ZeroVector)
                            .Offset(FMargin(1*Cell,(Y+6)*Cell,10*Cell,15*Cell)).ZOrder(3)
                            [SNew(SBorder).BorderImage(&NumberTile).Padding(0).HAlign(HAlign_Center).VAlign(VAlign_Center)
                             [SNew(STextBlock).Font(SecondaryFont(13)).Text(FText::AsNumber(Index+1))]];

                        Action(13, Y, 100, 27, First + Index, NAME_None);
                        Action(106, Y + 11, 53, 15, First + Index, TEXT("BuySelected"));
                        static const TCHAR* Ids[] = {TEXT("BikePedals"), TEXT("BikeFrame"), TEXT("BikeGears"), TEXT("BikeMotor"),
                            TEXT("Motorcycle"), TEXT("MotoTurbo"), TEXT("MotoAero"), TEXT("MotoDisplacement"), TEXT("MotoInjection"), TEXT("MotoSportEngine"),
                            TEXT("CargoBackpack"), TEXT("CargoWaist"), TEXT("CargoPanniers")};
                        static const int32 Prices[] = {15000, 40000, 85000, 180000, 350000, 150000, 240000, 400000, 650000, 1200000, 80000, 160000, 450000};
                        const int32 Entry = First + Index;
                        Content->AddSlot().Alignment(FVector2D::ZeroVector)
                            .Offset(FMargin(106 * Cell, (Y + 11) * Cell, 53 * Cell, 15 * Cell)).ZOrder(3)
                            [SNew(SImage).Image(Art(TEXT("BotonActivo"))).Visibility(EVisibility::HitTestInvisible)];
                        Content->AddSlot().Alignment(FVector2D::ZeroVector)
                            .Offset(FMargin(109 * Cell, (Y + 12) * Cell, 47 * Cell, 13 * Cell)).ZOrder(4)
                        [
                            SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                            .HAlign(HAlign_Center).VAlign(VAlign_Center).Visibility(EVisibility::HitTestInvisible)
                            [SNew(STextBlock).Font(SecondaryFont(10)).ColorAndOpacity(FLinearColor(.015f,.04f,.06f))
                                .Text_Lambda([this, Entry]()
                                {
                                    if (OwnsUpgrade(Ids[Entry])) return FText::FromString(TEXT("INSTALADO"));
                                    if (Entry != 0 && Entry != 10 && !OwnsUpgrade(Ids[Entry - 1]))
                                        return FText::FromString(TEXT("BLOQUEADO"));
                                    return FText::FromString(Pesos(Prices[Entry]));
                                })]
                        ];
                    }
                    if (!Cargo)
                    {
                        const int32 Y = 12 + 34 * Count;
                        for (int32 Index = 0; Index < 6; ++Index)
                        {
                            Content->AddSlot().Alignment(FVector2D::ZeroVector)
                                .Offset(FMargin((36 + 11 * Index)*Cell,(Y+9)*Cell,11*Cell,14*Cell)).ZOrder(2)
                                [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder")
                                 .OnClicked_Lambda([this, Index]
                                 {
                                     bCustomPaintSelected = false;
                                     PaintSelection = Index;
                                     PaintMessage = FText::GetEmpty();
                                     RefreshGarage();
                                     return FReply::Handled();
                                 })];
                        }
                        Content->AddSlot().Alignment(FVector2D::ZeroVector)
                            .Offset(FMargin(106*Cell,(Y+9)*Cell,9*Cell,14*Cell)).ZOrder(2)
                            [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").ContentPadding(0)
                             .HAlign(HAlign_Center).VAlign(VAlign_Center).ToolTipText(FText::FromString(TEXT("Color personalizado")))
                             .OnClicked_Lambda([this]
                             {
                                 auto* Core = DeliveryFor(Controller.Get());
                                 const FName Model = ReadName(Core, bGarageMoto ? TEXT("MotoModel") : TEXT("BikeModel"));
                                 const int32 Index = static_cast<int32>(ReadNumber(Core, bGarageMoto ? TEXT("MotoColor") : TEXT("BikeColor"), 0));
                                 if (!bCustomPaintSelected)
                                     PaintHSV = (PaintSelection == INDEX_NONE ? ReadPaint(Core, Model).Get(PresetPaint(Index)) : PresetPaint(PaintSelection)).LinearRGBToHSV();
                                 PickerInitialHSV = PaintHSV;
                                 bPaintPickerOpen = true;
                                 PaintMessage = FText::GetEmpty();
                                 return FReply::Handled();
                             })
                             [SNew(SSpacer).Size(FVector2D(10,10))]];
                        Content->AddSlot().Alignment(FVector2D::ZeroVector)
                            .Offset(FMargin(117*Cell,(Y+8)*Cell,42*Cell,16*Cell)).ZOrder(2)
                            [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").ToolTipText(FText::FromString(TEXT("Pintar por $2.000")))
                             .OnClicked_Lambda([this] { BuyPaint(); return FReply::Handled(); })];
                        Content->AddSlot().Alignment(FVector2D::ZeroVector)
                            .Offset(FMargin(17*Cell,(Y+26)*Cell,144*Cell,13*Cell)).ZOrder(2)
                            [SNew(STextBlock).Font(SecondaryFont(10)).Text_Lambda([this] { return PaintMessage; })];
                    }
                }
                static const FSlateColorBrush ScrollBackground(FLinearColor::FromSRGBColor(FColor(16,38,53)));
                Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(24, Top-6, 304, 540-Top+6)).ZOrder(4)
                    [SNew(SImage).Image(&ScrollBackground)];
                Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(24, Top, 304, 540 - Top)).ZOrder(5)
                [
                    SNew(SScrollBox).ScrollBarVisibility(EVisibility::Collapsed).Clipping(EWidgetClipping::ClipToBounds)
                    + SScrollBox::Slot()
                    [
                        SNew(SBox).HeightOverride(ArtHeight * Scale)
                        [Content]
                    ]
                ];
            }
        }

        if (Page == TEXT("Carga"))
        {
            static const FSlateColorBrush CargoBackground(FLinearColor(.012f,.035f,.052f));
            static const FSlateColorBrush CargoPlatform(FLinearColor(.029f,.080f,.106f));
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(24, 162, 304, 378)).ZOrder(1)
                [SNew(SImage).Image(&CargoBackground).Visibility(EVisibility::HitTestInvisible)];
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(88, 178, 176, 108)).ZOrder(2)
                [SNew(SImage).Image(&CargoPlatform).Visibility(EVisibility::HitTestInvisible)];
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(120, 184, 111, 87)).ZOrder(3)
                [SNew(SScaleBox).Stretch(EStretch::ScaleToFit)
                 [SNew(SImage).Image_Lambda([this]
                  {
                      static const TCHAR* Names[] = {TEXT("CargoBackpack"), TEXT("CargoWaist"), TEXT("CargoPanniers")};
                      return Art(Names[CargoSelection]);
                  })]];
        }

        if (Page == TEXT("Estadisticas"))
        {
            const auto* Sheet = Art(TEXT("EstadisticasPanel"));
            auto Stats = SNew(SConstraintCanvas);
            constexpr float Scale = 304.f / 528.f;
            Stats->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(0, 0, 304, 932 * Scale))
                [SNew(SImage).Image(Sheet).Visibility(EVisibility::HitTestInvisible)];
            auto Value = [&](float X, float Y, float W, float H, TFunction<FText()> GetText)
            {
                Stats->AddSlot().Alignment(FVector2D::ZeroVector)
                    .Offset(FMargin(X * Scale, (Y - 76) * Scale, W * Scale, H * Scale)).ZOrder(1)
                    [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                     .HAlign(HAlign_Center).VAlign(VAlign_Center)
                     [SNew(STextBlock).Font(SecondaryFont(14)).Text_Lambda(MoveTemp(GetText))]];
            };
            const TCHAR* Periods[] = {TEXT("HOY"), TEXT("SEMANA"), TEXT("TOTAL")};
            for (int32 Period = 0; Period < 3; ++Period)
            {
                Stats->AddSlot().Alignment(FVector2D::ZeroVector)
                    .Offset(FMargin((42 + 148 * Period) * Scale, 0, 140 * Scale, 16)).ZOrder(2)
                    [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").ContentPadding(0)
                     .OnClicked_Lambda([this, Period] { StatsPeriod = Period; RefreshDeliverySummary(); return FReply::Handled(); })
                     [SNew(SOverlay)
                      + SOverlay::Slot()[SNew(SImage).Image_Lambda([this, Period] {
                          return Art(StatsPeriod == Period ? TEXT("BotonActivo") : TEXT("BotonReposo"));
                      })]
                      + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
                      [SNew(STextBlock).Font(SecondaryFont(10)).Text(FText::FromString(Periods[Period]))]]];
            }
            Value(49, 174, 122, 42, [this] { return FText::AsNumber(Summary.Count); });
            Value(197, 174, 120, 42, [this] {
                return FText::FromString(Pesos(Summary.Money));
            });
            Value(344, 174, 120, 42, [this] {
                return FText::FromString(FString::Printf(TEXT("%.1f km"), Summary.Meters / 1000.));
            });
            auto Rows = [&](float Y, bool bZones)
            {
                for (int32 Rank = 0; Rank < 5; ++Rank)
                    Value(58, Y + Rank * 25, 400, 25, [this, bZones, Rank]
                    {
                        TArray<TPair<int32, FString>> Lines;
                        if (bZones)
                        {
                            for (const auto& Pair : Summary.Zones)
                                Lines.Emplace(Pair.Value, FString::Printf(TEXT("Sector %d, %d"), Pair.Key.X, Pair.Key.Y));
                        }
                        else
                        {
                            const TCHAR* Names[] = {TEXT("Mercado"), TEXT("Comida"), TEXT("Tecnología"), TEXT("Droguería"), TEXT("Flores")};
                            for (const auto& Pair : Summary.Kinds)
                                Lines.Emplace(Pair.Value, Pair.Key < UE_ARRAY_COUNT(Names) ? FString(Names[Pair.Key]) : TEXT("Otros"));
                        }
                        Lines.Sort([](const auto& A, const auto& B) { return A.Key != B.Key ? A.Key > B.Key : A.Value < B.Value; });
                        if (!Lines.IsValidIndex(Rank))
                            return Rank == 0 ? FText::FromString(TEXT("Sin entregas registradas")) : FText::GetEmpty();
                        return FText::FromString(FString::Printf(TEXT("%s  ·  %d"), *Lines[Rank].Value, Lines[Rank].Key));
                    });
            };
            Rows(316, false);
            Rows(748, true);
            for (int32 Chart = 0; Chart < 2; ++Chart)
            {
                static const FSlateColorBrush Gold(FLinearColor(.93f,.53f,.09f));
                static const FSlateColorBrush Teal(FLinearColor(.18f,.67f,.57f));
                const float X = Chart == 0 ? 60.f : 285.f;
                for (int32 Day = 0; Day < 7; ++Day)
                    Stats->AddSlot().Alignment(FVector2D::ZeroVector)
                        .Offset_Lambda([this, Chart, Day, X]
                        {
                            const double* Series = Chart == 0 ? Summary.MoneyByDay : Summary.MetersByDay;
                            double Peak = 0;
                            for (int32 Index = 0; Index < 7; ++Index) Peak = FMath::Max(Peak, Series[Index]);
                            const float Height = Peak > 0 ? 100 * Series[Day] / Peak : 0;
                            return FMargin((X + Day * 27) * Scale, (648 - Height - 76) * Scale, 18 * Scale, Height * Scale);
                        }).ZOrder(2)[SNew(SImage).Image(Chart == 0 ? &Gold : &Teal)];
                Value(X, 653, 175, 18, [this] { return FText::FromString(StatsPeriod == 0 ? TEXT("Hoy") : TEXT("Últimos 7 días")); });
            }
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(24, 101, 304, 434)).ZOrder(3)
                [SNew(SScrollBox).ScrollBarVisibility(EVisibility::Collapsed).Clipping(EWidgetClipping::ClipToBounds)
                 + SScrollBox::Slot()[SNew(SBox).HeightOverride(932 * Scale)[Stats]]];
        }

        if (Page == TEXT("Cicla") || Page == TEXT("Moto"))
        {
            GarageBrush.DrawAs = ESlateBrushDrawType::Image;
            GarageBrush.ImageSize = FVector2D(180, 89);
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector)
                .Offset(FMargin(24.7f, 162.7f, 302.f, 135.3f)).ZOrder(2)
                [SAssignNew(GarageImage, SImage).Image(&GarageBrush).Visibility(EVisibility::HitTestInvisible)];
            PhoneAction(TEXT("RefreshGaragePreview"));
            RefreshGarage();
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector)
                .Offset(FMargin(0, 0, Width, Height)).ZOrder(3)
                [SNew(SImage).Image(Art(Page + TEXT("Frente"))).Visibility(EVisibility::HitTestInvisible)];
        }

        if (Page == TEXT("Cicla") || Page == TEXT("Moto"))
        {
            const bool Bike = Page == TEXT("Cicla");
            static const FSlateColorBrush StatsShade(FLinearColor(.015f,.042f,.065f,.85f));
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(38, 170, 43, 26)).ZOrder(5)
                [SNew(SImage).Image(Art(Page + TEXT("IconoSolo"))).Visibility(EVisibility::HitTestInvisible)];
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(198,168,126,94)).ZOrder(5)
                [SNew(SBorder).BorderImage(&StatsShade).Padding(7,6)
                 [SNew(STextBlock).Font(SecondaryFont(9)).Text_Lambda([this, Bike] {
                     const int32 Count = CountVehicleUpgrades(DeliveryFor(Controller.Get()), Bike);
                     const double Gain = 1. + .1 * Count;
                     return FText::FromString(FString::Printf(
                         TEXT("Velocidad %.1f km/h\nAceleración %.1f m/s²\nFrenado %.1f m/s²\nMejoras +%d %%"),
                         (Bike ? 36. : 45.) * Gain, (Bike ? 2.65 : 3.3125) * Gain, 6.5 * Gain, Count * 10));
                 })]];
        }

        if (Page == TEXT("Pedidos"))
        {
            static const FSlateColorBrush Background(FLinearColor(.012f, .035f, .052f));
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(25, 164, 302, 373)).ZOrder(2)
            [
                SNew(SBorder).BorderImage(&Background).Padding(6.f)
                [SAssignNew(Orders, SScrollBox).ScrollBarVisibility(EVisibility::Collapsed)]
            ];
        }

        if (!Map && Page != TEXT("Estadisticas") && Page != TEXT("Musica") && Page != TEXT("Servicios"))
        {
            const float HeaderY = Page == TEXT("Inicio") ? 75.f : 123.f;
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(75, HeaderY, 94, 22)).ZOrder(2)
                [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                 .HAlign(HAlign_Left).VAlign(VAlign_Center)
                 [SNew(STextBlock).Font(SecondaryFont(18)).Text_Lambda([this]() { return LiveBalance(); })]];
            static const FSlateColorBrush Occupied(FLinearColor(.95f,.52f,.08f));
            for (int32 I=0; I<7; ++I)
                Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(231+12*I, HeaderY+4, 10, 10)).ZOrder(2)
                [SNew(SImage).Image(&Occupied).Visibility_Lambda([this,I]() {
                    return I < CountItems(DeliveryFor(Controller.Get()),TEXT("ActiveOrders"))
                        ? EVisibility::HitTestInvisible : EVisibility::Hidden;
                })];
        }

        auto Hit = [&](float X, float Y, float W, float H, const TCHAR* Destination)
        {
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(X,Y,W,H)).ZOrder(3)
            [
                SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder")
                .OnClicked_Lambda([this, Target = FString(Destination)]()
                {
                    Navigate(Target);
                    return FReply::Handled();
                })
            ];
        };

        if (Page == TEXT("Cicla") || Page == TEXT("Moto"))
        {
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(246, 264, 75, 24)).ZOrder(4)
            [
                SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder")
                .ContentPadding(0)
                .OnClicked_Lambda([this]() { PhoneAction(TEXT("SwitchPressed")); return FReply::Handled(); })
                [SNew(SOverlay)
                 + SOverlay::Slot()[SNew(SImage).Image(Art(TEXT("BotonActivo")))]
                 + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
                 [SNew(STextBlock).Font(SecondaryFont(12)).Text(FText::FromString(TEXT("USAR")))]] 
            ];
        }
        if (Map)
        {
            static const FSlateColorBrush MapBackground(FLinearColor(.12f,.16f,.13f));
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(30,124,292,354)).ZOrder(1)
                [SAssignNew(MapOpening,SBox).Clipping(EWidgetClipping::ClipToBoundsAlways)
                 [SAssignNew(MapInput,SBorder).BorderImage(&MapBackground).Padding(0)
                   .OnMouseButtonDown_Lambda([this](const FGeometry& Geometry, const FPointerEvent& Event)
                   {
                       if (Event.GetEffectingButton() != EKeys::LeftMouseButton) return FReply::Unhandled();
                       MapDragStart = Geometry.AbsoluteToLocal(Event.GetScreenSpacePosition());
                       MapPanStart = MapPan;
                       bMapDragged = false;
                       return FReply::Handled().CaptureMouse(MapInput.ToSharedRef());
                   })
                   .OnMouseMove_Lambda([this](const FGeometry& Geometry, const FPointerEvent& Event)
                   {
                       if (!MapInput->HasMouseCapture()) return FReply::Unhandled();
                       const FVector2D Delta = Geometry.AbsoluteToLocal(Event.GetScreenSpacePosition()) - MapDragStart;
                       const FVector2D Size = Geometry.GetLocalSize();
                       bMapDragged |= Delta.SizeSquared() >= 16.;
                       if (bMapDragged && !Size.IsNearlyZero()) SetMapPan(MapPanStart + Delta / Size);
                       return FReply::Handled();
                   })
                   .OnMouseButtonUp_Lambda([this](const FGeometry& Geometry, const FPointerEvent& Event)
                   {
                       if (Event.GetEffectingButton() != EKeys::LeftMouseButton || !MapInput->HasMouseCapture())
                           return FReply::Unhandled();
                       if (bMapDragged) return FReply::Handled().ReleaseMouseCapture();
                       auto* Core = DeliveryFor(Controller.Get());
                       auto* Function = Core ? Core->FindFunction(TEXT("SetWaypoint")) : nullptr;
                       auto* Location = Function ? FindFProperty<FStructProperty>(Function, TEXT("Location")) : nullptr;
                       const auto Size = Geometry.GetLocalSize();
                       if (!Location || Location->Struct != TBaseStructure<FVector>::Get() || Size.IsNearlyZero())
                           return FReply::Handled().ReleaseMouseCapture();
                       const FVector2D Center(.5,.5);
                       const FVector2D Point = Center + (Geometry.AbsoluteToLocal(Event.GetScreenSpacePosition()) / Size - Center - MapPan) / MapZoom;
                       FStructOnScope Args(Function);
                       *Location->ContainerPtrToValuePtr<FVector>(Args.GetStructMemory()) =
                           FVector((.5 - Point.Y) * CityMapSpan, (Point.X - .5) * CityMapSpan, 0.);
                       Core->ProcessEvent(Function, Args.GetStructMemory());
                       return FReply::Handled().ReleaseMouseCapture();
                   })
                   [SNew(SImage).Image(FullMapArt())
                    .RenderTransformPivot(FVector2D(.5,.5))
                    .RenderTransform_Lambda([this] {
                        return TOptional<FSlateRenderTransform>(FSlateRenderTransform(MapZoom, MapPan * FVector2D(292,354)));
                    })]]];
            static const FSlateColorBrush WaypointInk(FLinearColor(.04f,.09f,.11f));
            static const FSlateColorBrush WaypointFill(FLinearColor(1.f,.45f,.06f));
            Canvas->AddSlot().Alignment(FVector2D(.5,.5)).AutoSize(true).ZOrder(5)
                .Offset_Lambda([this]
                {
                    const APawn* Pawn = Controller.IsValid() ? Controller->GetPawn().Get() : nullptr;
                    const FVector Position = Pawn ? Pawn->GetActorLocation() : FVector::ZeroVector;
                    const FVector2D Point = MapPoint(Position);
                    return FMargin(30 + 292 * Point.X, 124 + 354 * Point.Y, 0, 0);
                })
                [SNew(SBox).WidthOverride(36).HeightOverride(36)
                 .Visibility_Lambda([this]
                 {
                     const APawn* Pawn = Controller.IsValid() ? Controller->GetPawn().Get() : nullptr;
                     if (!Pawn) return EVisibility::Collapsed;
                     return IsMapPointVisible(MapPoint(Pawn->GetActorLocation()))
                         ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
                 })
                 [MapMarker(false)]];
            Canvas->AddSlot().Alignment(FVector2D(.5,.5)).AutoSize(true).ZOrder(4)
                .Offset_Lambda([this] {
                    if (!ParkedMapVehicle.IsValid()) return FMargin(0);
                    const FVector2D Point = MapPoint(ParkedMapLocation) * FVector2D(292,354);
                    return FMargin(30 + Point.X, 124 + Point.Y, 0, 0);
                })
                [SNew(SBox).WidthOverride(38).HeightOverride(29)
                 .Visibility_Lambda([this] {
                     return ParkedMapVehicle.IsValid() && IsMapPointVisible(MapPoint(ParkedMapLocation))
                         ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
                 })
                 [MapMarker(true)]];
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).AutoSize(true).ZOrder(4)
                .Offset_Lambda([this]
                {
                    auto* Core = DeliveryFor(Controller.Get());
                    const auto* Field = Core ? FindFProperty<FStructProperty>(Core->GetClass(), TEXT("Waypoint")) : nullptr;
                    const FVector Position = Field && Field->Struct == TBaseStructure<FVector>::Get()
                        ? *Field->ContainerPtrToValuePtr<FVector>(Core) : FVector::ZeroVector;
                    const FVector2D Point = MapPoint(Position);
                    return FMargin(30 + 292 * Point.X - 5, 124 + 354 * Point.Y - 5, 0, 0);
                })
                [SNew(SBox).WidthOverride(10).HeightOverride(10)
                 .Visibility_Lambda([this]
                 {
                     auto* Core = DeliveryFor(Controller.Get());
                     const auto* Field = Core ? FindFProperty<FBoolProperty>(Core->GetClass(), TEXT("HasWaypoint")) : nullptr;
                     const auto* Location = Core ? FindFProperty<FStructProperty>(Core->GetClass(), TEXT("Waypoint")) : nullptr;
                     if (!Field || !Field->GetPropertyValue_InContainer(Core) || !Location ||
                         Location->Struct != TBaseStructure<FVector>::Get()) return EVisibility::Collapsed;
                     const FVector Position = *Location->ContainerPtrToValuePtr<FVector>(Core);
                     return IsMapPointVisible(MapPoint(Position))
                        ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
                 })
                 [SNew(SBorder).BorderImage(&WaypointInk).Padding(2)
                  [SNew(SImage).Image(&WaypointFill)]]];
            Hit(35, 552, 90, 66, TEXT("Inicio"));
            Hit(225, 552, 92, 66, TEXT("Configuracion"));
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(30,488,292,36)).ZOrder(3)
                [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder")
                 .OnClicked_Lambda([this]() { PhoneAction(TEXT("ClearPoint")); return FReply::Handled(); })];
        }
        else
        {
            Hit(35, 552, 90, 66, TEXT("Inicio"));
            Hit(128, 552, 95, 66, TEXT("Mapa"));
            Hit(226, 552, 95, 66, TEXT("Configuracion"));
            if (Page != TEXT("Inicio")) Hit(32, 50, 47, 43, LayeredGarage || Page == TEXT("Carga") ? TEXT("Taller") : TEXT("Inicio"));
            if (Page == TEXT("Inicio"))
            {
                Hit(33, 345, 85, 79, TEXT("Pedidos"));
                Hit(125, 345, 85, 79, TEXT("Taller"));
                Hit(218, 345, 85, 79, TEXT("Servicios"));
                Hit(33, 435, 85, 79, TEXT("Estadisticas"));
                Hit(125, 435, 85, 79, TEXT("Musica"));
                Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(37, 31, 70, 24)).ZOrder(2)
                    [SAssignNew(Clock, STextBlock).Font(SecondaryFont(12))];
                Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(220, 213, 102, 44)).ZOrder(2)
                    [SAssignNew(Weather, SImage)];
                Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(259, 219, 59, 33)).ZOrder(3)
                    [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                     .HAlign(HAlign_Center).VAlign(VAlign_Center)
                     [SNew(STextBlock).Font(SecondaryFont(18)).Text_Lambda([this]()
                    {
                        if (!WorldState.IsValid()) return FText::GetEmpty();
                        const double Temp = ReadNumber(WorldState.Get(), TEXT("Temperature"), -999.);
                        if (Temp > -100.) return FText::FromString(FString::Printf(TEXT("%.0f °C"), Temp));
                        const double Hour = ReadNumber(WorldState.Get(), TEXT("Hour"), 12.);
                        const double Rain = ReadNumber(WorldState.Get(), TEXT("RainIntensity"), 0.);
                        const double Estimate = 14. + 5. * FMath::Cos((Hour - 14.) * UE_DOUBLE_PI / 12.) - 2. * Rain;
                        return FText::FromString(FString::Printf(TEXT("~%.0f °C"), Estimate));
                    })]];
            }
            if (Page == TEXT("Taller"))
            {
                Hit(31, 177, 287, 59, TEXT("Cicla"));
                Hit(31, 247, 287, 59, TEXT("Moto"));
                Hit(31, 317, 287, 59, TEXT("Carga"));
                Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(31, 386, 287, 26)).ZOrder(4)
                    [SNew(SBox).HAlign(HAlign_Center).VAlign(VAlign_Center)
                     .Visibility_Lambda([this] {
                         return TotalBillsDue(DeliveryFor(Controller.Get())) > 0
                             ? EVisibility::HitTestInvisible : EVisibility::Collapsed;
                     })
                     [SNew(STextBlock).Font(SecondaryFont(12)).Text_Lambda([this] {
                         return FText::FromString(TEXT("Servicios por pagar  ")
                             + Pesos(TotalBillsDue(DeliveryFor(Controller.Get()))));
                     })]];
                const TCHAR* Names[] = {TEXT("Cicla"), TEXT("Moto"), TEXT("Almacenamiento")};
                const float RowY[] = {177, 247, 317};
                for (int32 I = 0; I < 3; ++I)
                    Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(115,RowY[I],173,59)).ZOrder(4)
                        [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::DownOnly)
                         .HAlign(HAlign_Left).VAlign(VAlign_Center).Visibility(EVisibility::HitTestInvisible)
                         [SNew(STextBlock).Font(SecondaryFont(17)).Justification(ETextJustify::Left).Text(FText::FromString(Names[I]))]];
            }
        }

        if (LayeredGarage)
        {
            static const FSlateColorBrush PickerPanel(FLinearColor(.018f,.064f,.086f));
            Canvas->AddSlot().Alignment(FVector2D::ZeroVector).Offset(FMargin(33, 326, 286, 210)).ZOrder(50)
            [
                SNew(SBorder).BorderImage(&PickerPanel).Padding(8)
                .Visibility_Lambda([this] { return bPaintPickerOpen ? EVisibility::Visible : EVisibility::Collapsed; })
                [SNew(SVerticalBox)
                 + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
                 [SNew(STextBlock).Font(SecondaryFont(12)).Text(FText::FromString(TEXT("COLOR PERSONALIZADO")))]
                 + SVerticalBox::Slot().FillHeight(1).HAlign(HAlign_Center).Padding(4)
                 [SNew(SBox).WidthOverride(112).HeightOverride(112)
                  [SNew(SColorWheel).SelectedColor_Lambda([this] { return PaintHSV; })
                   .OnValueChanged_Lambda([this](FLinearColor Color) { PaintHSV = Color; RefreshGarage(); })]]
                 + SVerticalBox::Slot().AutoHeight().Padding(16, 0)
                 [SNew(SSlider).Value_Lambda([this] { return PaintHSV.B; })
                  .OnValueChanged_Lambda([this](float Value) { PaintHSV.B = Value; RefreshGarage(); })]
                 + SVerticalBox::Slot().AutoHeight().Padding(2)
                 [SNew(SHorizontalBox)
                  + SHorizontalBox::Slot().FillWidth(1).Padding(2)
                  [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").ContentPadding(0).OnClicked_Lambda([this]
                   { PaintHSV = PickerInitialHSV; bPaintPickerOpen = false; RefreshGarage(); return FReply::Handled(); })
                   [SNew(SBox).HeightOverride(26)[SNew(SOverlay)
                    + SOverlay::Slot()[SNew(SImage).Image(Art(TEXT("BotonReposo")))]
                    + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)[SNew(STextBlock).Font(SecondaryFont(10)).Text(FText::FromString(TEXT("CANCELAR")))]]]]
                  + SHorizontalBox::Slot().FillWidth(1).Padding(2)
                  [SNew(SButton).ButtonStyle(FCoreStyle::Get(), "NoBorder").ContentPadding(0).OnClicked_Lambda([this]
                   { bCustomPaintSelected = true; bPaintPickerOpen = false; RefreshGarage(); return FReply::Handled(); })
                   [SNew(SBox).HeightOverride(26)[SNew(SOverlay)
                    + SOverlay::Slot()[SNew(SImage).Image(Art(TEXT("BotonActivo")))]
                    + SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)[SNew(STextBlock).Font(SecondaryFont(10)).Text(FText::FromString(TEXT("ELEGIR")))]]]]]]
            ];
        }
        const bool bGaragePage = Page == TEXT("Taller") || Page == TEXT("Cicla") || Page == TEXT("Moto") || Page == TEXT("Carga");
        auto* Core = DeliveryFor(Controller.Get());
        if (!bGaragePage) bGarageTutorialVisible = false;
        else if (!bGarageTutorialVisible)
        {
            if (auto Progress = PaintMap(Core); Progress && !ServiceValue(*Progress, TEXT("GarageLessonSeen")))
            {
                const FName Key(TEXT("GarageLessonSeen"));
                const int32 Seen = 1;
                Progress->AddPair(&Key, &Seen);
                QueryBool(Core, TEXT("SaveProfile"));
                bGarageTutorialVisible = true;
            }
        }
        Canvas->AddSlot().Alignment(FVector2D(.5,1)).Offset_Lambda([this, Page] {
            return FMargin(PhoneTutorialTarget(Page), 345, 27, 27);
        }).ZOrder(12)
        [SNew(SImage).Image(Art(TEXT("FlechaTutorial")))
         .Visibility_Lambda([this, Page] { return PhoneTutorialTarget(Page) != INDEX_NONE
             ? EVisibility::HitTestInvisible : EVisibility::Collapsed; })];

        const bool bServicePage = Page == TEXT("Servicios");
        Overlay = SNew(SOverlay)
        + SOverlay::Slot().Padding(18.f)
        [SNew(SScaleBox).Stretch(EStretch::ScaleToFit).StretchDirection(EStretchDirection::Both)
         [SNew(SHorizontalBox)
          + SHorizontalBox::Slot().AutoWidth()
          [SNew(SBox).WidthOverride(Width).HeightOverride(Height)[Canvas]]
          + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(18,0,0,0)
          [SNew(SBox).WidthOverride(386)
           .Visibility_Lambda([this] {
               return bGarageTutorialVisible || TutorialStep == 1 || TutorialStep == 6
                   ? EVisibility::Visible : EVisibility::Collapsed;
           })
           [SNew(SOverlay)
            + SOverlay::Slot()[SNew(SImage).Image(Art(TEXT("PanelTutorial")))]
            + SOverlay::Slot().Padding(18,16)
            [SNew(SHorizontalBox)
             + SHorizontalBox::Slot().FillWidth(1).Padding(0,0,6,0)
             [SNew(SVerticalBox)
             + SVerticalBox::Slot().AutoHeight().Padding(0,0,0,8)
             [SNew(STextBlock).Font(SecondaryFont(16)).ColorAndOpacity(FLinearColor(.35f,.86f,.83f))
              .Text_Lambda([this] { return FText::FromString(bGarageTutorialVisible ? TEXT("VALERIA · TALLER") : TEXT("VALERIA")); })]
             + SVerticalBox::Slot().AutoHeight()
             [SNew(STextBlock).Font(SecondaryFont(15)).AutoWrapText(true)
              .Text_Lambda([this, bServicePage] {
                  if (bGarageTutorialVisible)
                      return FText::FromString(TEXT("En Cicla o Moto compra mejoras en orden. Cada una suma 10 % a la velocidad, aceleración y frenado. En Carga amplías lo que puedes llevar."));
                  if (bServicePage && TutorialStep == 6)
                  {
                      auto* Data = DeliveryFor(Controller.Get());
                      const int32 Index = TutorialBill(Data);
                      if (Index != INDEX_NONE)
                          return FText::FromString(FString::Printf(TEXT("Pulsa PAGAR en %s para pagar %s."),
                              Bills[Index].Name, *Pesos(ServicePayment(Data, Index))));
                  }
                  return TutorialText();
              })]
             + SVerticalBox::Slot().AutoHeight().Padding(0,8,0,0)
             [SNew(SButton).HAlign(HAlign_Center).Text(FText::FromString(TEXT("ENTENDIDO")))
              .Visibility_Lambda([this] { return bGarageTutorialVisible ? EVisibility::Visible : EVisibility::Collapsed; })
              .OnClicked_Lambda([this] { bGarageTutorialVisible = false; return FReply::Handled(); })]]
             + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
             [ValeriaPortrait(112)]]]]]];
        Viewport->AddViewportWidgetContent(Overlay.ToSharedRef(), 1200);
        if (const auto Focus = FirstFocusableControl(Canvas))
            FSlateApplication::Get().SetAllUserFocus(Focus, EFocusCause::Navigation);
        RefreshWorld();
        RefreshOrders();
        UE_LOG(LogTemp, Display, TEXT("Phone UI preview: %s"), *Page);
    }

    TWeakObjectPtr<UGameViewportClient> RouteViewport;
    TWeakObjectPtr<APlayerController> RouteController;
    TWeakObjectPtr<AHUD> OldHUD;
    TSharedPtr<SWidget> RouteHUD;
    bool bOldHUDVisible = false;
    bool bRouteVisible = false;
    TWeakObjectPtr<UUserWidget> StyledVideo;
    int32 StyledPreset = INDEX_NONE;
    TWeakObjectPtr<UWorld> GuideWorld;
    double NextGuideScan = 0;
    TOptional<FVector2D> BikePosition;
    int32 ChecklistState = 0;
    int32 ChecklistPending = INDEX_NONE;
    double ChecklistCheckTime[3]{};
    double ChecklistDeliveryUntil = 0;
    bool bChecklistDelivered = false;
    int32 RouteAction = 0;
    TOptional<FVector2D> ActionPosition;
    TWeakObjectPtr<UObject> StatsCore;
    TWeakObjectPtr<UObject> PremiumCore;
    TSet<FGuid> PremiumOffers;
    TMap<FGuid, double> SpecialDeadlines;
    TMap<FGuid, int32> SpecialBaseRewards;
    int32 FocusedSpecialSeconds = INDEX_NONE;
    int32 PreviousActive = 0;
    int32 PreviousBalance = 0;
    bool bPreviousDeveloper = false;
    FDeliveryRecord PreviousOrder;
    TArray<FDeliveryRecord> DeliveryHistory;
    FStatsSummary Summary;
    FDateTime SummaryDate;
    int32 StatsPeriod = 2;
    int32 Deliveries = 0;
    int64 Earnings = 0;
    int32 CargoSelection = 0;
    TWeakObjectPtr<UGameViewportClient> Viewport;
    TWeakObjectPtr<APlayerController> Controller;
    TWeakObjectPtr<AActor> WorldState;
    TWeakObjectPtr<UObject> SessionCore;
    TWeakObjectPtr<AActor> CityClock;
    int32 LastServiceDay = INDEX_NONE;
    double NextSessionSnapshot = 0.;
    TWeakObjectPtr<ACharacter> CargoRider;
    TWeakObjectPtr<USkeletalMeshComponent> Backpack;
    TWeakObjectPtr<USkeletalMeshComponent> WaistPack;
    TWeakObjectPtr<UStaticMeshComponent> RiderPanniers;
    TWeakObjectPtr<AActor> PannierVehicle;
    TWeakObjectPtr<UStaticMeshComponent> ParkedPanniers;
    FText ServiceStatus;
    TMap<FString, TUniquePtr<FArt>> Images;
    TSharedPtr<SWidget> Overlay;
    TSharedPtr<SWidget> PauseMenu;
    TWeakObjectPtr<UGameViewportClient> PauseViewport;
    TWeakObjectPtr<APlayerController> PauseController;
    FText PauseStatus;
    FString CurrentPhonePage;
    bool bMotorcycleLamp = false;
    TWeakObjectPtr<USpotLightComponent> MotorcycleLamp;
    TWeakObjectPtr<AActor> ParkedMapVehicle;
    FVector ParkedMapLocation = FVector::ZeroVector;
    TWeakObjectPtr<UWorld> StoreWorld;
    TWeakObjectPtr<ACharacter> StoreRider;
    TArray<TWeakObjectPtr<AActor>> DeliveryStores;
    TOptional<FVector> LastOutsideStore;
    TWeakObjectPtr<AActor> RecipientCollision;
    EPausePage PausePage = EPausePage::Main;
    int32 PendingSlot = INDEX_NONE;
#if PLATFORM_WINDOWS
    FSonyGamepad SonyGamepad;
#endif
    TSharedPtr<SWidget> LoadingCover;
    TWeakObjectPtr<UWorld> StartupWorld;
    TWeakObjectPtr<AActor> StartupPreparation;
    double StartupWaitStarted = 0.;
    bool bStartupShown = false;
    bool bAtStartup = false;
    bool bStartupVideo = false;
    TWeakObjectPtr<UUserWidget> VideoMenu;
    bool bConfirmNew = false;
    FString StartupCode;
    bool bGarageTutorialVisible = false;
    FString LastValeriaLine;
    double ValeriaLineStarted = -10.;
    double TutorialFinishedUntil = 0.;
    int32 TutorialDeliveries = 0;
    bool bTutorialDrifted = false;
    int32 TutorialStep = INDEX_NONE;
    float AudioLevels[5] = {1.f, 1.f, 1.f, 1.f, 1.f};
    double NextAudioScan = 0.;
    TWeakObjectPtr<UWorld> MixWorld;
    TStrongObjectPtr<USoundMix> AudioMix;
    TStrongObjectPtr<USoundClass> AudioClass[4];
    TWeakObjectPtr<UWorld> VolumeWorld;
    TSharedPtr<STextBlock> Clock;
    TSharedPtr<SImage> Weather;
    TSharedPtr<SImage> GarageImage;
    FSlateBrush GarageBrush;
    TSharedPtr<SScrollBox> Orders;
    TArray<FString> OrderSnapshot;
    TArray<FString> ActiveOrderSnapshot;
    int32 OrderCapacitySnapshot = 0;
    float RefreshElapsed = 0.f;
    TWeakObjectPtr<UUserWidget> LegacyPhone;
    bool bMapPage = false;
    bool bGarageMoto = false;
    bool bPaintPickerOpen = false;
    bool bCustomPaintSelected = false;
    int32 PaintSelection = INDEX_NONE;
    FLinearColor PaintHSV = FLinearColor(0, 0, 1);
    FLinearColor PickerInitialHSV = PaintHSV;
    FText PaintMessage;
    int32 HoldingOrder = INDEX_NONE;
    TSharedPtr<SBox> MapOpening;
    TSharedPtr<SBorder> MapInput;
    FVector2D MapPan = FVector2D::ZeroVector;
    FVector2D MapDragStart = FVector2D::ZeroVector;
    FVector2D MapPanStart = FVector2D::ZeroVector;
    bool bMapDragged = false;
    FSlateBrush FullMapBrush;
    FSlateBrush MinimapBrush;
    TWeakObjectPtr<UWidget> MinimapPanel;
    TSharedPtr<SConstraintCanvas> RouteCanvas;
    FSlateBrush ServiceRowArt[UE_ARRAY_COUNT(Bills) + 2];
    FSlateBrush ServiceCalendarArt;
    FSlateBrush WorkshopListBrush;
    FSlateBrush WorkshopListBottomBrush;
    float MapZoom = 1.f;
};
}

class FBogotaPhonePreviewModule final : public IModuleInterface
{
    TSharedPtr<FPhonePreview> Preview;
    virtual void StartupModule() override
    {
        if (!FSlateApplication::IsInitialized() || IsRunningCommandlet()) return;
        Preview = MakeShared<FPhonePreview>();
        FSlateApplication::Get().RegisterInputPreProcessor(Preview);
    }
    virtual void ShutdownModule() override
    {
        if (Preview && FSlateApplication::IsInitialized())
        {
            Preview->Close();
            Preview->RemoveRouteHUD();
            FSlateApplication::Get().UnregisterInputPreProcessor(Preview);
        }
        Preview.Reset();
    }
};
IMPLEMENT_MODULE(FBogotaPhonePreviewModule, BogotaPhonePreview)





