from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUsability.cpp');s=p.read_text().replace('#include "Misc/CoreDelegates.h"','#include "Framework/Application/SlateApplication.h"');s=s.replace('FCoreDelegates::ApplicationWillDeactivateDelegate.Broadcast();','FSlateApplication::Get().OnApplicationActivationStateChanged().Broadcast(false);');p.write_text(s)
