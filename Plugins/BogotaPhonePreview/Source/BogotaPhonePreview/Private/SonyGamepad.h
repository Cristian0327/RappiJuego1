#pragma once

#if PLATFORM_WINDOWS
#include "Framework/Application/SlateApplication.h"
#include "GenericPlatform/GenericPlatformInputDeviceMapper.h"
#include "HAL/PlatformProcess.h"

struct SDL_Gamepad;

// SDL 3 gamepad bridge for Sony HID devices. Xbox and other XInput pads use Unreal's input.
class FSonyGamepad
{
public:
    ~FSonyGamepad()
    {
        if (Pad) Close(Pad);
        if (bReady) Quit(InitGamepad);
        if (Library) FPlatformProcess::FreeDllHandle(Library);
    }

    void Tick(FSlateApplication& Slate, const FString& Resources)
    {
        if (!bTried)
        {
            bTried = true;
            Initialize(Resources);
        }
        if (!bReady) return;
        Update();
        if (Pad && !Connected(Pad))
        {
            Dispatch(Slate, false);
            Close(Pad);
            Pad = nullptr;
        }
        if (!Pad && FPlatformTime::Seconds() >= NextScan)
        {
            NextScan = FPlatformTime::Seconds() + .5;
            int Count = 0;
            auto* Ids = GetPads(&Count);
            for (int Index = 0; Ids && Index < Count && !Pad; ++Index)
                if (GetVendor(Ids[Index]) == 0x054C) Pad = Open(Ids[Index]);
            Free(Ids);
            if (Pad) UE_LOG(LogTemp, Display, TEXT("Bogota input: mando PlayStation detectado"));
        }

        // Avoid doubling input when Steam Input or another mapper presents an XInput pad.
        Dispatch(Slate, Pad && Slate.IsActive() && !Slate.IsGamepadAttached());
    }

private:
    static constexpr uint32 InitGamepad = 0x00002000;
    void* Library = nullptr;
    SDL_Gamepad* Pad = nullptr;
    bool bTried = false;
    bool bReady = false;
    double NextScan = 0.;
    float Axes[6] = {};
    bool Buttons[17] = {};

    bool (*Init)(uint32) = nullptr;
    void (*Quit)(uint32) = nullptr;
    void (*Update)() = nullptr;
    uint32* (*GetPads)(int*) = nullptr;
    uint16 (*GetVendor)(uint32) = nullptr;
    SDL_Gamepad* (*Open)(uint32) = nullptr;
    void (*Close)(SDL_Gamepad*) = nullptr;
    bool (*Connected)(SDL_Gamepad*) = nullptr;
    int16 (*Axis)(SDL_Gamepad*, int) = nullptr;
    bool (*Button)(SDL_Gamepad*, int) = nullptr;
    void (*Free)(void*) = nullptr;
    bool (*SetHint)(const char*, const char*) = nullptr;

    void Initialize(const FString& Resources)
    {
        Library = FPlatformProcess::GetDllHandle(*(Resources / TEXT("SDL3.dll")));
        if (!Library) return;
        auto Load = [this](auto& Function, const TCHAR* Name)
        {
            Function = reinterpret_cast<std::remove_reference_t<decltype(Function)>>(
                FPlatformProcess::GetDllExport(Library, Name));
            return Function != nullptr;
        };
        if (!Load(Init, TEXT("SDL_InitSubSystem")) || !Load(Quit, TEXT("SDL_QuitSubSystem"))
            || !Load(Update, TEXT("SDL_UpdateGamepads")) || !Load(GetPads, TEXT("SDL_GetGamepads"))
            || !Load(GetVendor, TEXT("SDL_GetGamepadVendorForID")) || !Load(Open, TEXT("SDL_OpenGamepad"))
            || !Load(Close, TEXT("SDL_CloseGamepad")) || !Load(Connected, TEXT("SDL_GamepadConnected"))
            || !Load(Axis, TEXT("SDL_GetGamepadAxis")) || !Load(Button, TEXT("SDL_GetGamepadButton"))
            || !Load(Free, TEXT("SDL_free")) || !Load(SetHint, TEXT("SDL_SetHint"))) return;
        SetHint("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1");
        bReady = Init(InitGamepad);
        if (bReady) UE_LOG(LogTemp, Display, TEXT("Bogota input: lector PlayStation listo"));
    }

    void Dispatch(FSlateApplication& Slate, bool bRead)
    {
        auto& Mapper = IPlatformInputDeviceMapper::Get();
        const auto User = Mapper.GetPrimaryPlatformUser();
        const auto Device = Mapper.GetDefaultInputDevice();

        // SDL orders the axes left stick, right stick, then triggers. Y increases downwards.
        const FName AxisKeys[] = {FGamepadKeyNames::LeftAnalogX, FGamepadKeyNames::LeftAnalogY,
            FGamepadKeyNames::RightAnalogX, FGamepadKeyNames::RightAnalogY,
            FGamepadKeyNames::LeftTriggerAnalog, FGamepadKeyNames::RightTriggerAnalog};
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(Axes); ++Index)
        {
            const float Value = bRead ? FMath::Clamp(Axis(Pad, Index) / 32767.f, -1.f, 1.f)
                * ((Index == 1 || Index == 3) ? -1.f : 1.f) : 0.f;
            if (Value != 0.f || Axes[Index] != 0.f) Slate.OnControllerAnalog(AxisKeys[Index], User, Device, Value);
            Axes[Index] = Value;
        }

        const FName Keys[] = {FGamepadKeyNames::FaceButtonBottom, FGamepadKeyNames::FaceButtonRight,
            FGamepadKeyNames::FaceButtonLeft, FGamepadKeyNames::FaceButtonTop,
            FGamepadKeyNames::SpecialLeft, FGamepadKeyNames::SpecialRight,
            FGamepadKeyNames::LeftThumb, FGamepadKeyNames::RightThumb,
            FGamepadKeyNames::LeftShoulder, FGamepadKeyNames::RightShoulder,
            FGamepadKeyNames::DPadUp, FGamepadKeyNames::DPadDown, FGamepadKeyNames::DPadLeft, FGamepadKeyNames::DPadRight,
            FGamepadKeyNames::LeftTriggerThreshold, FGamepadKeyNames::RightTriggerThreshold};
        const int32 SDLButtons[] = {0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, -1, -1};
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(Keys); ++Index)
        {
            bool Pressed = bRead && (Index < 14 ? Button(Pad, SDLButtons[Index]) : Axes[Index - 10] > .15f);
            if (Index == 4 && bRead) Pressed |= Button(Pad, 20); // Touchpad click also opens the phone.
            if (Pressed == Buttons[Index]) continue;
            Buttons[Index] = Pressed;
            if (Pressed) Slate.OnControllerButtonPressed(Keys[Index], User, Device, false);
            else Slate.OnControllerButtonReleased(Keys[Index], User, Device, false);
        }
    }
};
#endif
