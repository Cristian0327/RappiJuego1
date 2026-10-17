#include "DeliverySystem.h"
#include "BogotaGame.h"
#include "Blueprint/WidgetTree.h"
#include "Blueprint/WidgetLayoutLibrary.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Border.h"
#include "Components/TextBlock.h"
#include "Components/Button.h"
#include "Components/ButtonSlot.h"
#include "Components/Image.h"
#include "Engine/Texture2D.h"
#include "Engine/Font.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Components/ProgressBar.h"
#include "GameFramework/PlayerController.h"
#include "Rendering/DrawElements.h"
#include "InputCoreTypes.h"
#include "EngineUtils.h"

namespace {
const FLinearColor Ink(.009,.019,.026,1),Panel(.035,.085,.105,1),Mint(.06,.85,.74,1),Gold(1,.36,.065,1),Paper(.94,.96,.87,1);
// A tiny, point-sampled relief tile. Nine-slice preserves its square steps at every size.
UTexture2D* VoxelTile(bool Pressed=false){
 static UTexture2D* Tiles[2]={};auto*& T=Tiles[Pressed?1:0];if(T)return T;
 T=UTexture2D::CreateTransient(16,16,PF_B8G8R8A8);T->AddToRoot();T->Filter=TF_Nearest;T->SRGB=true;T->NeverStream=true;
 auto& M=T->GetPlatformData()->Mips[0];auto* Pixels=static_cast<FColor*>(M.BulkData.Lock(LOCK_READ_WRITE));
 for(int Y=0;Y<16;Y++)for(int X=0;X<16;X++){
  const bool Cut=(X<2||X>=14)&&(Y<2||Y>=14);
  int V=230;if(X<2||Y<2)V=Pressed?75:255;else if(X>=14||Y>=14)V=Pressed?255:70;else if(X<4||Y<4)V=Pressed?130:245;else if(X>=12||Y>=12)V=Pressed?245:135;
  Pixels[Y*16+X]=FColor(V,V,V,Cut?0:255);
 }M.BulkData.Unlock();T->UpdateResource();return T;
}
FSlateBrush VoxelBrush(FLinearColor Color,bool Pressed=false){FSlateBrush B;B.SetResourceObject(VoxelTile(Pressed));B.DrawAs=ESlateBrushDrawType::Box;B.ImageSize=FVector2D(16,16);B.Margin=FMargin(.25f);B.TintColor=Color;return B;}
UTexture2D* VoxelCategory(int32 Kind){
 static UTexture2D* Tiles[5]={};Kind=FMath::Clamp(Kind,0,4);if(Tiles[Kind])return Tiles[Kind];
 const char* Icons[]={"0100010" "0010100" "1111111" "1000001" "1010101" "1000001" "1111111", "0011100" "0111110" "1111111" "0000000" "1111111" "0000000" "0111110", "0101010" "0111110" "1100011" "0101010" "1100011" "0111110" "0101010", "0011100" "0011100" "1111111" "1111111" "1111111" "0011100" "0011100", "0011100" "0100010" "1001001" "0100010" "0011100" "0001000" "0111000"};
 const FColor Colors[]={FColor(92,235,142),FColor(255,178,80),FColor(72,210,255),FColor(232,255,241),FColor(255,124,192)};
 auto* T=UTexture2D::CreateTransient(16,16,PF_B8G8R8A8);T->AddToRoot();T->Filter=TF_Nearest;T->SRGB=true;T->NeverStream=true;
 auto& M=T->GetPlatformData()->Mips[0];auto* P=static_cast<FColor*>(M.BulkData.Lock(LOCK_READ_WRITE));
 for(int32 Y=0;Y<16;Y++)for(int32 X=0;X<16;X++){const int32 C=(X-1)/2,R=(Y-1)/2;P[Y*16+X]=X>=1&&X<15&&Y>=1&&Y<15&&Icons[Kind][R*7+C]=='1'?Colors[Kind]:FColor(0,0,0,0);}
 M.BulkData.Unlock();T->UpdateResource();Tiles[Kind]=T;return T;
}
void VoxelButton(UButton* B,FLinearColor Color=Panel){auto S=B->GetStyle();S.Normal=VoxelBrush(Color);S.Hovered=VoxelBrush(FLinearColor(.055,.15,.17));S.Pressed=VoxelBrush(FLinearColor(.055,.15,.17),true);S.Disabled=VoxelBrush(FLinearColor(.045,.065,.075));S.NormalPadding=FMargin(6,3,6,5);S.PressedPadding=FMargin(6,5,6,3);B->SetStyle(S);}
}
int32 UDeliveryMapWidget::NativePaint(const FPaintArgs& Args,const FGeometry& G,const FSlateRect& Cull,FSlateWindowElementList& E,int32 L,const FWidgetStyle& Style,bool Enabled)const{
 L=Super::NativePaint(Args,G,Cull,E,L,Style,Enabled);if(!Delivery)return L;auto* P=Cast<ABogotaPlayer>(Delivery->GetOwner());if(!P||!P->City)return L;
 auto Size=G.GetLocalSize();FVector Center=FullMap?FVector::ZeroVector:P->GetActorLocation();float NX=FullMap?45000:8500,EY=FullMap?30000:8500;
 auto Point=[&](FVector V){return FVector2D(Size.X*.5+(V.Y-Center.Y)/EY*Size.X*.46,Size.Y*.5-(V.X-Center.X)/NX*Size.Y*.46);};
 auto Line=[&](FVector A,FVector B,FLinearColor C,float Thick){
  FVector2D From=Point(A),To=Point(B),Delta=To-From;double Lo=0,Hi=1;
  auto Clip=[&](double P,double Q){if(FMath::Abs(P)<.0001)return Q>=0;double R=Q/P;if(P<0){if(R>Hi)return false;Lo=FMath::Max(Lo,R);}else{if(R<Lo)return false;Hi=FMath::Min(Hi,R);}return true;};
  if(!Clip(-Delta.X,From.X-5)||!Clip(Delta.X,Size.X-5-From.X)||!Clip(-Delta.Y,From.Y-5)||!Clip(Delta.Y,Size.Y-5-From.Y))return;
  TArray<FVector2D> Points={From+Delta*Lo,From+Delta*Hi};FSlateDrawElement::MakeLines(E,L+1,G.ToPaintGeometry(),Points,ESlateDrawEffect::None,C,false,Thick);
 };
 FSlateBrush Brush;Brush.DrawAs=ESlateBrushDrawType::Box;Brush.TintColor=FLinearColor::White;FSlateDrawElement::MakeBox(E,L,G.ToPaintGeometry(),&Brush,ESlateDrawEffect::None,FLinearColor(.045,.065,.09));
 auto Block=[&](FVector2D Pos,FVector2D Extent,FLinearColor Color){if(Pos.X<1||Pos.Y<1||Pos.X+Extent.X>Size.X-1||Pos.Y+Extent.Y>Size.Y-1)return;FSlateDrawElement::MakeBox(E,L+1,G.ToPaintGeometry(Extent,FSlateLayoutTransform(Pos)),&Brush,ESlateDrawEffect::None,Color);};
 // Real building footprints and reserved parks, mapped from the world rather than invented blocks.
 for(const auto& Foot:P->City->MapFootprints){auto A=Point(Foot.Center-FVector(Foot.Extent.X,Foot.Extent.Y,0)),B=Point(Foot.Center+FVector(Foot.Extent.X,Foot.Extent.Y,0));FVector2D TL(FMath::Min(A.X,B.X),FMath::Min(A.Y,B.Y)),SZ(FMath::Abs(A.X-B.X),FMath::Abs(A.Y-B.Y));Block(TL,SZ,FLinearColor(.16,.21,.26));}
 for(FVector Park:{FVector(-6000,16500,0),FVector(18000,16500,0),FVector(30000,16500,0),FVector(6000,-5500,0)}){auto A=Point(Park-FVector(3000,2500,0)),B=Point(Park+FVector(3000,2500,0));Block(FVector2D(FMath::Min(A.X,B.X),FMath::Min(A.Y,B.Y)),FVector2D(FMath::Abs(A.X-B.X),FMath::Abs(A.Y-B.Y)),FLinearColor(.075,.25,.20));}
 for(float X:P->City->NorthRoads)if(FullMap||FMath::Abs(X-Center.X)<NX){Line(FVector(X,-26500,0),FVector(X,26500,0),FLinearColor(.21,.29,.36),8);Line(FVector(X,-26500,0),FVector(X,26500,0),FLinearColor(.46,.56,.61),3);}
 for(float Y:P->City->EastRoads)if(FullMap||FMath::Abs(Y-Center.Y)<EY){Line(FVector(-42000,Y,0),FVector(42000,Y,0),FLinearColor(.21,.29,.36),8);Line(FVector(-42000,Y,0),FVector(42000,Y,0),Y==0?FLinearColor(.83,.59,.25):FLinearColor(.46,.56,.61),3);}
 if(FullMap){for(int32 I=0;I<P->City->NorthRoads.Num();I++){auto At=Point(FVector(P->City->NorthRoads[I],-25000,0));FSlateDrawElement::MakeText(E,L+3,G.ToPaintGeometry(FVector2D(65,14),FSlateLayoutTransform(At+FVector2D(0,-12))),FString::Printf(TEXT("CALLE %d"),10+I*12),FSlateFontInfo(LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font")),8),ESlateDrawEffect::None,FLinearColor(.75,.83,.87));}for(int32 I=0;I<P->City->EastRoads.Num();I++){auto At=Point(FVector(41000,P->City->EastRoads[I],0));FSlateDrawElement::MakeText(E,L+3,G.ToPaintGeometry(FVector2D(55,14),FSlateLayoutTransform(At+FVector2D(-12,3))),FString::Printf(TEXT("CRA %d"),7+I*5),FSlateFontInfo(LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font")),8),ESlateDrawEffect::None,FLinearColor(.75,.83,.87));}}
 auto Dot=[&](FVector V,FLinearColor C,float S){auto Pos=Point(V);Pos.X=FMath::Clamp(Pos.X,8.,double(Size.X-8));Pos.Y=FMath::Clamp(Pos.Y,8.,double(Size.Y-8));FSlateDrawElement::MakeBox(E,L+2,G.ToPaintGeometry(FVector2D(S,S),FSlateLayoutTransform(Pos-FVector2D(S/2,S/2))),&Brush,ESlateDrawEffect::None,C);};
 if(Delivery->State==EDeliveryState::Pickup||Delivery->State==EDeliveryState::Dropoff||Delivery->HasWaypoint){FVector End=Delivery->HasWaypoint&&Delivery->State!=EDeliveryState::Pickup&&Delivery->State!=EDeliveryState::Dropoff?Delivery->Waypoint:Delivery->GetOrderTarget();auto Route=Delivery->NavigationRoute();for(int32 I=1;I<Route.Num();I++){Line(Route[I-1],Route[I],FLinearColor(.012,.025,.035),8);Line(Route[I-1],Route[I],FLinearColor(.03,.88,.83),4);}Dot(End,Delivery->State==EDeliveryState::Pickup?Gold:FLinearColor(1,.8,.05),12);}
 const FLinearColor ShopColors[]={FLinearColor(.24,.80,.40),FLinearColor(1,.58,.19),FLinearColor(.20,.72,.98),FLinearColor(.84,.92,.94),FLinearColor(.95,.36,.62)};
 // Five hand-drawn pixel symbols: basket, burger, chip, pharmacy cross and flower.
 const char* Symbols[]={"0100010" "0010100" "1111111" "1000001" "1010101" "1000001" "1111111", "0011100" "0111110" "1111111" "0000000" "1111111" "0000000" "0111110", "0101010" "0111110" "1100011" "0101010" "1100011" "0111110" "0101010", "0011100" "0011100" "1111111" "1111111" "1111111" "0011100" "0011100", "0011100" "0100010" "1001001" "0100010" "0011100" "0001000" "0111000"};
 for(TActorIterator<ADeliveryPoint> It(GetWorld());It;++It){FVector V=It->GetActorLocation();auto Pos=Point(V);if(Pos.X<12||Pos.X>Size.X-12||Pos.Y<12||Pos.Y>Size.Y-12)continue;int32 Kind=FMath::Clamp(It->StoreKind,0,4);if(!FullMap){Dot(V,ShopColors[Kind],5);continue;}Block(Pos-FVector2D(10,10),FVector2D(20,20),FLinearColor(.035,.05,.075));for(int32 Row=0;Row<7;Row++)for(int32 Col=0;Col<7;Col++)if(Symbols[Kind][Row*7+Col]=='1')Block(Pos+FVector2D(Col*2-7,Row*2-7),FVector2D(2,2),ShopColors[Kind]);}
 if(Delivery->HasWaypoint)Dot(Delivery->Waypoint,FLinearColor(.70,.4,1),10);
 for(const FVector& POI:{FVector(-6000,16500,0),FVector(3700,7000,0),FVector(18000,16500,0),FVector(30000,16500,0)})if(FullMap)Dot(POI,FLinearColor(.48,.55,.49),5);
 Dot(P->GetActorLocation(),Mint,9);FVector Facing=P->GetActorForwardVector()*NX*.12f;Line(P->GetActorLocation(),P->GetActorLocation()+Facing,Mint,3);FSlateDrawElement::MakeText(E,L+3,G.ToPaintGeometry(FVector2D(20,16),FSlateLayoutTransform(FVector2D(Size.X*.5-5,4))),TEXT("N"),FCoreStyle::GetDefaultFontStyle(TEXT("Bold"),10),ESlateDrawEffect::None,Paper);if(FullMap){auto Pos=MapCursor*Size;TArray<FVector2D> H={Pos-FVector2D(9,0),Pos+FVector2D(9,0)},V={Pos-FVector2D(0,9),Pos+FVector2D(0,9)};FSlateDrawElement::MakeLines(E,L+3,G.ToPaintGeometry(),H,ESlateDrawEffect::None,Paper,false,1);FSlateDrawElement::MakeLines(E,L+3,G.ToPaintGeometry(),V,ESlateDrawEffect::None,Paper,false,1);
  auto Font=FSlateFontInfo(LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font")),9);for(const auto& Place:TArray<TPair<FVector,FString>>{{FVector(30000,11000,0),TEXT("USAQUÉN")},{FVector(12000,-7000,0),TEXT("CHAPINERO")},{FVector(-6000,16000,0),TEXT("CENTRO")},{FVector(-28000,-12000,0),TEXT("RESTREPO")}}){auto LabelPos=Point(Place.Key);FSlateDrawElement::MakeText(E,L+3,G.ToPaintGeometry(FVector2D(90,18),FSlateLayoutTransform(LabelPos)),Place.Value,Font,ESlateDrawEffect::None,Paper);}
 }return L+3;
}
FReply UDeliveryMapWidget::NativeOnMouseButtonDown(const FGeometry& G,const FPointerEvent& E){if(FullMap&&Delivery&&E.GetEffectingButton()==EKeys::LeftMouseButton){auto P=G.AbsoluteToLocal(E.GetScreenSpacePosition());auto S=G.GetLocalSize();Delivery->SetWaypoint(FVector(-(P.Y-S.Y*.5)/(S.Y*.46)*45000,(P.X-S.X*.5)/(S.X*.46)*30000,0));return FReply::Handled();}return Super::NativeOnMouseButtonDown(G,E);}
void UDeliveryChoiceButton::Choose(){if(Phone)Phone->SelectEntry(Choice);}
FName UDeliveryPhoneWidget::NextLayoutName(){return BuildingLayout?FName(*FString::Printf(TEXT("Voxel2_App%d_%s_%02d"),Page,PreviewMoto?TEXT("Moto"):TEXT("Bike"),LayoutIndex++)):NAME_None;}
void UDeliveryPhoneWidget::AuthorAppLayouts(){
 for(int32 Mode=0;Mode<2;Mode++){PreviewMoto=Mode==1;for(int32 App=1;App<=6;App++)BuildPage(App);}
 for(auto* W:AppControls)if(W)W->SetVisibility(ESlateVisibility::Collapsed);
 if(MainMap)MainMap->SetVisibility(ESlateVisibility::Collapsed);
}
UTextBlock* UDeliveryPhoneWidget::AddText(const FString& T,FVector2D P,FVector2D S,int32 Size){
 const FName LayoutName=NextLayoutName();if(auto* Existing=Cast<UTextBlock>(WidgetTree->FindWidget(LayoutName)))return Existing;
 auto* W=WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(),LayoutName);W->SetText(FText::FromString(T));W->SetColorAndOpacity(Paper);auto Font=W->GetFont();Font.Size=Size;Font.TypefaceFontName=TEXT("Bold");if(auto* PixelFont=LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font")))Font.FontObject=PixelFont;W->SetFont(Font);W->SetAutoWrapText(true);auto* L=Screen->AddChildToCanvas(W);L->SetPosition(P);L->SetSize(S);return W;
}
UButton* UDeliveryPhoneWidget::AddButton(const FString& T,FVector2D P,FVector2D S){
 const FName LayoutName=NextLayoutName();if(auto* Existing=Cast<UButton>(WidgetTree->FindWidget(LayoutName))){if(auto* LayoutSlot=Cast<UCanvasPanelSlot>(Existing->Slot)){LayoutSlot->SetPosition(P);LayoutSlot->SetSize(S);}if(auto* Label=Cast<UTextBlock>(Existing->GetContent()))Label->SetText(FText::FromString(T));Existing->OnClicked.Clear();Existing->OnPressed.Clear();Existing->OnReleased.Clear();AppControls.Add(Existing);return Existing;}
 auto* B=WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(),LayoutName);auto Style=B->GetStyle();for(auto* Brush:{&Style.Normal,&Style.Hovered,&Style.Pressed,&Style.Disabled}){Brush->DrawAs=ESlateBrushDrawType::Box;Brush->Margin=FMargin(0);Brush->TintColor=Panel;}Style.Hovered.TintColor=FLinearColor(.15,.25,.32);Style.Pressed.TintColor=Gold;Style.Disabled.TintColor=FLinearColor(.045,.055,.07);B->SetStyle(Style);
 auto* Label=WidgetTree->ConstructWidget<UTextBlock>();Label->SetText(FText::FromString(T));Label->SetColorAndOpacity(Paper);auto Font=Label->GetFont();Font.Size=12;Font.TypefaceFontName=TEXT("Bold");if(auto* PixelFont=LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font")))Font.FontObject=PixelFont;Label->SetFont(Font);Label->SetJustification(ETextJustify::Center);B->AddChild(Label);auto* L=Screen->AddChildToCanvas(B);L->SetPosition(P);L->SetSize(S);AppControls.Add(B);return B;
}
UDeliveryChoiceButton* UDeliveryPhoneWidget::AddChoice(const FString& T,int32 Index,FVector2D P,FVector2D S){
 const FName LayoutName=NextLayoutName();if(auto* Existing=Cast<UDeliveryChoiceButton>(WidgetTree->FindWidget(LayoutName))){if(auto* LayoutSlot=Cast<UCanvasPanelSlot>(Existing->Slot)){LayoutSlot->SetPosition(P);LayoutSlot->SetSize(S);}Existing->Phone=this;Existing->Choice=Index;Existing->OnClicked.Clear();Existing->OnClicked.AddDynamic(Existing,&UDeliveryChoiceButton::Choose);AppControls.Add(Existing);Choices.Add(Existing);return Existing;}
 auto* B=WidgetTree->ConstructWidget<UDeliveryChoiceButton>(UDeliveryChoiceButton::StaticClass(),LayoutName);B->Phone=this;B->Choice=Index;B->OnClicked.AddDynamic(B,&UDeliveryChoiceButton::Choose);auto Style=B->GetStyle();for(auto* Brush:{&Style.Normal,&Style.Hovered,&Style.Pressed}){Brush->DrawAs=ESlateBrushDrawType::Box;Brush->Margin=FMargin(0);Brush->TintColor=Panel;}Style.Hovered.TintColor=FLinearColor(.18,.27,.33);Style.Pressed.TintColor=Gold;B->SetStyle(Style);
 auto* Label=WidgetTree->ConstructWidget<UTextBlock>();Label->SetText(FText::FromString(T));Label->SetColorAndOpacity(Paper);auto Font=Label->GetFont();Font.Size=11;Font.TypefaceFontName=TEXT("Bold");if(auto* PixelFont=LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font")))Font.FontObject=PixelFont;Label->SetFont(Font);Label->SetAutoWrapText(true);B->AddChild(Label);auto* L=Screen->AddChildToCanvas(B);L->SetPosition(P);L->SetSize(S);AppControls.Add(B);Choices.Add(B);return B;
}
UImage* UDeliveryPhoneWidget::AddArt(const FString& Name,FVector2D P,FVector2D S){
 const FName LayoutName=NextLayoutName();if(auto* Existing=Cast<UImage>(WidgetTree->FindWidget(LayoutName))){if(auto* LayoutSlot=Cast<UCanvasPanelSlot>(Existing->Slot)){LayoutSlot->SetPosition(P);LayoutSlot->SetSize(S);}AppControls.Add(Existing);return Existing;}
 auto* W=WidgetTree->ConstructWidget<UImage>(UImage::StaticClass(),LayoutName);if(auto* Texture=LoadObject<UTexture2D>(nullptr,*(TEXT("/Game/Delivery/Art/")+Name+TEXT(".")+Name))){Texture->SetForceMipLevelsToBeResident(30.f);W->SetBrushFromTexture(Texture);}auto* L=Screen->AddChildToCanvas(W);L->SetPosition(P);L->SetSize(S);W->SetVisibility(ESlateVisibility::HitTestInvisible);AppControls.Add(W);return W;
}
void UDeliveryPhoneWidget::NativeConstruct(){Super::NativeConstruct();}
TSharedRef<SWidget> UDeliveryPhoneWidget::RebuildWidget(){
 PhoneTextures.Empty();for(const TCHAR* Name:{TEXT("T_AppMap"),TEXT("T_AppOrders"),TEXT("T_AppWorkshop"),TEXT("T_ParcelCoffee"),TEXT("T_ParcelFood"),TEXT("T_ParcelMarket"),TEXT("T_RutaBog"),TEXT("T_UrbanShell"),TEXT("T_BogotaWallpaper")})if(auto* T=LoadObject<UTexture2D>(nullptr,*(FString(TEXT("/Game/Delivery/Art/"))+Name+TEXT(".")+Name))){PhoneTextures.Add(T);T->SetForceMipLevelsToBeResident(60.f);}
 SetIsFocusable(true);if(!Delivery)if(auto* P=Cast<ABogotaPlayer>(GetOwningPlayerPawn()))Delivery=P->Delivery;
 Root=Cast<UCanvasPanel>(WidgetTree->FindWidget(TEXT("Root")));
 if(Root){
  PhoneShade=Cast<UBorder>(WidgetTree->FindWidget(TEXT("PhoneShade")));
  PhoneArt=Cast<UImage>(WidgetTree->FindWidget(TEXT("PhoneArt")));
  Frame=Cast<UBorder>(WidgetTree->FindWidget(TEXT("Frame")));
  Screen=Cast<UCanvasPanel>(WidgetTree->FindWidget(TEXT("Screen")));
  MiniMap=Cast<UDeliveryMapWidget>(WidgetTree->FindWidget(TEXT("MiniMap")));
  Notice=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("Notice")));
  PhoneHints=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("PhoneHints")));
  EnergyText=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("EnergyText")));
  EnergyBar=Cast<UProgressBar>(WidgetTree->FindWidget(TEXT("EnergyBar")));
  HoldBar=Cast<UProgressBar>(WidgetTree->FindWidget(TEXT("HoldBar")));
  Header=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("Header")));
  Details=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("Details")));
  PageTitle=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("PageTitle")));
  if(MiniMap)MiniMap->Delivery=Delivery;
 }
 if(!Root||!Frame||!Screen||!MiniMap||!Header||!Details||!PageTitle||!PhoneArt||!PhoneShade||!Notice||!PhoneHints||!EnergyText||!EnergyBar||!HoldBar){
 Root=WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(),TEXT("Root"));WidgetTree->RootWidget=Root;
 PhoneShade=WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(),TEXT("PhoneShade"));PhoneShade->SetBrushColor(FLinearColor(0,0,0,.5));auto* ShadeSlot=Root->AddChildToCanvas(PhoneShade);ShadeSlot->SetAnchors(FAnchors(0,0,1,1));ShadeSlot->SetOffsets(FMargin(0));PhoneShade->SetVisibility(ESlateVisibility::Collapsed);
 PhoneArt=WidgetTree->ConstructWidget<UImage>(UImage::StaticClass(),TEXT("PhoneArt"));PhoneArt->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr,TEXT("/Game/Delivery/Art/T_UrbanShell.T_UrbanShell")));Root->AddChildToCanvas(PhoneArt);PhoneArt->SetVisibility(ESlateVisibility::HitTestInvisible);
 Frame=WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(),TEXT("Frame"));Frame->SetBrushColor(FLinearColor::Transparent);Frame->SetPadding(FMargin(24,48,24,36));Root->AddChildToCanvas(Frame);
 Screen=WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(),TEXT("Screen"));Screen->SetClipping(EWidgetClipping::ClipToBounds);Frame->AddChild(Screen);
 auto* Background=WidgetTree->ConstructWidget<UBorder>();Background->SetBrushColor(Ink);auto* BS=Screen->AddChildToCanvas(Background);BS->SetAnchors(FAnchors(0,0,1,1));BS->SetOffsets(FMargin(0));Background->SetVisibility(ESlateVisibility::HitTestInvisible);
 MiniMap=WidgetTree->ConstructWidget<UDeliveryMapWidget>(UDeliveryMapWidget::StaticClass(),TEXT("MiniMap"));MiniMap->Delivery=Delivery;auto* MS=Screen->AddChildToCanvas(MiniMap);MS->SetAnchors(FAnchors(0,0,1,1));MS->SetOffsets(FMargin(0));
 Header=AddText(TEXT("RUTA BOG"),FVector2D(8,6),FVector2D(322,24),12);Header->SetColorAndOpacity(Paper);
 Header->Rename(TEXT("Header"),WidgetTree);
 Details=AddText(TEXT(""),FVector2D(8,84),FVector2D(356,58),12);
 Details->Rename(TEXT("Details"),WidgetTree);
 PageTitle=AddText(TEXT(""),FVector2D(8,36),FVector2D(350,42),26);
 PageTitle->Rename(TEXT("PageTitle"),WidgetTree);
 Notice=WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(),TEXT("Notice"));Notice->SetColorAndOpacity(Paper);Notice->SetAutoWrapText(true);auto Font=Notice->GetFont();Font.Size=14;Notice->SetFont(Font);auto* NS=Root->AddChildToCanvas(Notice);NS->SetPosition(FVector2D(28,28));NS->SetSize(FVector2D(620,90));
 PhoneHints=WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(),TEXT("PhoneHints"));PhoneHints->SetColorAndOpacity(Paper);PhoneHints->SetAutoWrapText(true);auto HintFont=PhoneHints->GetFont();HintFont.Size=11;PhoneHints->SetFont(HintFont);PhoneHints->SetJustification(ETextJustify::Center);PhoneHints->SetText(FText::FromString(TEXT("E / A / X: aceptar · Cruceta: elegir · TAB / Select: cerrar\n1 Mapa · 2 Pedidos · 3 Taller · 4 Maletas · 5 Garaje")));auto* HintSlot=Root->AddChildToCanvas(PhoneHints);HintSlot->SetAnchors(FAnchors(0,1,1,1));HintSlot->SetOffsets(FMargin(12,-62,12,58));HintSlot->SetZOrder(99);
 EnergyText=WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(),TEXT("EnergyText"));EnergyText->SetColorAndOpacity(Mint);auto* ES=Root->AddChildToCanvas(EnergyText);ES->SetPosition(FVector2D(28,135));ES->SetSize(FVector2D(350,26));
 EnergyBar=WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(),TEXT("EnergyBar"));EnergyBar->SetFillColorAndOpacity(Mint);auto* EB=Root->AddChildToCanvas(EnergyBar);EB->SetPosition(FVector2D(28,165));EB->SetSize(FVector2D(220,8));
 HoldBar=WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(),TEXT("HoldBar"));HoldBar->SetFillColorAndOpacity(Gold);auto* HB=Root->AddChildToCanvas(HoldBar);HB->SetPosition(FVector2D(28,187));HB->SetSize(FVector2D(220,8));
 auto* InitialFrame=Cast<UCanvasPanelSlot>(Frame->Slot);InitialFrame->SetPosition(FVector2D(20,20));InitialFrame->SetSize(FVector2D(420,680));
 auto* InitialArt=Cast<UCanvasPanelSlot>(PhoneArt->Slot);InitialArt->SetPosition(FVector2D(20,20));InitialArt->SetSize(FVector2D(420,680));
 }
 PhoneHints->SetText(FText::FromString(TEXT("Flechas/Cruceta: elegir · E/Enter/A-X: mantener · TAB/ESC/Select: cerrar\n1 Mapa · 2 Pedidos · 3 Taller · 4 Maletas · 5 Garaje")));
 if(Delivery&&Delivery->Upgrades){UpgradeIDs=Delivery->Upgrades->GetRowNames();UpgradeIDs.Sort([&](FName A,FName B){return Delivery->Upgrades->FindRow<FDeliveryUpgrade>(A,TEXT("UI"))->SortIndex<Delivery->Upgrades->FindRow<FDeliveryUpgrade>(B,TEXT("UI"))->SortIndex;});}
 ModelIDs={TEXT("BikeCity"),TEXT("BikeCargo"),TEXT("BikeBMX"),TEXT("MotoStreet"),TEXT("MotoCargo"),TEXT("MotoSport")};
 ApplyVoxelTheme();if(!AuthoringPhoneTemplate)BuildPage(0);return Super::RebuildWidget();
}
void UDeliveryPhoneWidget::ApplyVoxelTheme(){
 auto* Pixel=LoadObject<UFont>(nullptr,TEXT("/Game/Delivery/UI/Fonts/RutaPixel_Bold_Font.RutaPixel_Bold_Font"));
 TArray<UWidget*> All;WidgetTree->GetAllWidgets(All);
 for(auto* W:All){
  if(W->GetName().StartsWith(TEXT("App")))W->SetVisibility(ESlateVisibility::Collapsed);
  if(auto* B=Cast<UButton>(W))VoxelButton(B);
  if(auto* T=Cast<UTextBlock>(W)){auto F=T->GetFont();if(Pixel)F.FontObject=Pixel;T->SetFont(F);T->SetColorAndOpacity(Paper);T->SetShadowOffset(FVector2D(0,2));T->SetShadowColorAndOpacity(FLinearColor(0,0,0,.65));}
  if(auto* I=Cast<UImage>(W))if(auto* Texture=Cast<UTexture2D>(I->GetBrush().GetResourceObject()))Texture->Filter=TF_Nearest;
 }
 Header->SetColorAndOpacity(Mint);PageTitle->SetColorAndOpacity(Paper);
 for(const TCHAR* Name:{TEXT("HomeMap"),TEXT("HomeOrders"),TEXT("HomeWorkshop"),TEXT("HomeCargo"),TEXT("HomeVehicles")})if(auto* B=Cast<UButton>(WidgetTree->FindWidget(Name)))if(auto* HomeSlot=Cast<UCanvasPanelSlot>(B->Slot))HomeSlot->SetSize(FVector2D(104,116));
 PhoneShade->SetBrushColor(FLinearColor(.003,.01,.016,.8));
 if(auto* B=Cast<UBorder>(WidgetTree->FindWidget(TEXT("HomeStatusPanel")))){B->SetBrush(VoxelBrush(Panel));B->SetBrushColor(FLinearColor::White);}
 if(auto* T=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("HomeTagline"))))T->SetText(FText::FromString(TEXT("BOGOTÁ SE MUEVE CONTIGO")));
 for(auto* Bar:{EnergyBar,HoldBar}){FProgressBarStyle Style;Style.BackgroundImage=VoxelBrush(Ink);Style.FillImage=VoxelBrush(FLinearColor::White);Style.MarqueeImage=Style.FillImage;Bar->SetWidgetStyle(Style);}
 EnergyBar->SetFillColorAndOpacity(Mint);HoldBar->SetFillColorAndOpacity(Gold);
}
void UDeliveryPhoneWidget::BuildPage(int32 NewPage){
 if(Delivery)Delivery->EndAction();Page=FMath::Clamp(NewPage,0,6);
 if(Page==6)Selection=FMath::Clamp(Selection,10,12);
 if(Page==3)Selection=FMath::Clamp(Selection,PreviewMoto?4:0,PreviewMoto?9:3);
 if(Page==4)CatalogSelection=FMath::Clamp(CatalogSelection,PreviewMoto?3:0,PreviewMoto?5:2);
 for(auto* W:AppControls)if(W)W->SetVisibility(ESlateVisibility::Collapsed);AppControls.Empty();Choices.Empty();AcceptButton=nullptr;ModelBuyButton=nullptr;ModelEquipButton=nullptr;PreviewArt=nullptr;SelectionTitle=nullptr;if(MainMap){MainMap->SetVisibility(ESlateVisibility::Collapsed);MainMap=nullptr;}
 LayoutIndex=0;BuildingLayout=true;
 auto Caption=[&](const FString& T,FVector2D P,FVector2D S,int32 Font){auto* W=AddText(T,P,S,Font);AppControls.Add(W);return W;};
 auto DetailFont=Details->GetFont();DetailFont.Size=(Page==3||Page==4)?10:12;Details->SetFont(DetailFont);Details->SetWrapTextAt(356);
 const bool GaragePage=Page==3||Page==4;const float ContentWidth=372.f;
 auto TitleFont=PageTitle->GetFont();TitleFont.Size=GaragePage?17:26;PageTitle->SetFont(TitleFont);
 PageTitle->SetAutoWrapText(false);PageTitle->SetClipping(EWidgetClipping::ClipToBounds);
 Cast<UCanvasPanelSlot>(PageTitle->Slot)->SetSize(FVector2D(GaragePage?164:350,42));
 auto* DSlot=Cast<UCanvasPanelSlot>(Details->Slot);DSlot->SetPosition(FVector2D(8,84));DSlot->SetSize(FVector2D(356,56));
 auto* Close=AddButton(TEXT("X"),FVector2D(ContentWidth-34,0),FVector2D(32,28));Close->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::ClosePressed);
 if(Page==0&&!WidgetTree->FindWidget(TEXT("DesignerHome"))){
  AddArt(TEXT("T_BogotaWallpaper"),FVector2D(0,35),FVector2D(372,506));AddArt(TEXT("T_RutaBog"),FVector2D(14,56),FVector2D(196,98));
  Caption(TEXT("MIS CALLES. MIS RUTAS."),FVector2D(15,166),FVector2D(330,24),12);
  const FString Icons[]={TEXT("T_AppMap"),TEXT("T_AppOrders"),TEXT("T_AppWorkshop")};const TCHAR* Labels[]={TEXT("MAPA"),TEXT("PEDIDOS"),TEXT("TALLER")};
  for(int32 I=0;I<3;I++){auto* B=AddButton(Labels[I],FVector2D(8+I*122,411),FVector2D(112,116));if(I==0)B->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenMap);if(I==1)B->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenOrders);if(I==2)B->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenShop);if(auto* T=Cast<UTextBlock>(B->GetContent())){T->SetText(FText::FromString(FString(TEXT("\n\n\n\n"))+Labels[I]));}AddArt(Icons[I],FVector2D(30+I*122,417),FVector2D(70,77));}
 }
 if(Page==1){

  const FName MapName=NextLayoutName();MainMap=Cast<UDeliveryMapWidget>(WidgetTree->FindWidget(MapName));const bool NewMap=!MainMap;if(NewMap)MainMap=WidgetTree->ConstructWidget<UDeliveryMapWidget>(UDeliveryMapWidget::StaticClass(),MapName);MainMap->Delivery=Delivery;MainMap->FullMap=true;MainMap->SetClipping(EWidgetClipping::ClipToBounds);if(NewMap){auto* L=Screen->AddChildToCanvas(MainMap);L->SetPosition(FVector2D(8,152));L->SetSize(FVector2D(356,334));}auto* MapSlot=Cast<UCanvasPanelSlot>(MainMap->Slot);MapSlot->SetPosition(FVector2D(8,152));MapSlot->SetSize(FVector2D(356,334));auto* Clear=AddButton(TEXT("QUITAR MI MARCA"),FVector2D(8,500),FVector2D(356,34));Clear->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::ClearPoint);
 }
 if(Page==2){
  DSlot->SetPosition(FVector2D(8,382));DSlot->SetSize(FVector2D(356,96));
  auto* Routes=AddButton(TEXT("VER PEDIDOS ACEPTADOS"),FVector2D(8,75),FVector2D(356,23));Routes->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenActiveOrders);
  for(int32 I=0;I<6;I++){auto* Card=AddChoice(TEXT(""),I,FVector2D(8,102+I*46),FVector2D(356,42));if(auto* CardSlot=Cast<UButtonSlot>(Card->GetContent()->Slot)){CardSlot->SetPadding(FMargin(40,2,4,2));CardSlot->SetHorizontalAlignment(HAlign_Fill);}if(auto* CardText=Cast<UTextBlock>(Card->GetContent())){CardText->SetClipping(EWidgetClipping::ClipToBounds);CardText->SetAutoWrapText(false);CardText->SetJustification(ETextJustify::Left);auto CardFont=CardText->GetFont();CardFont.Size=10;CardText->SetFont(CardFont);}const TCHAR* Icons[]={TEXT("T_ParcelCoffee"),TEXT("T_ParcelFood"),TEXT("T_ParcelMarket")};AddArt(Icons[I%3],FVector2D(12,106+I*46),FVector2D(32,32));}
  AcceptButton=AddButton(TEXT("MANTÉN PARA TOMAR LA RUTA"),FVector2D(8,483),FVector2D(356,37));AcceptButton->OnPressed.AddDynamic(this,&UDeliveryPhoneWidget::AcceptPressed);AcceptButton->OnReleased.AddDynamic(this,&UDeliveryPhoneWidget::AcceptReleased);
  auto* Ignore=AddButton(TEXT("PASAR ESTA OFERTA"),FVector2D(8,523),FVector2D(356,22));Ignore->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::IgnorePressed);
 }
 if(Page==3||Page==4){
  auto* Cargo=AddButton(TEXT("MALETAS"),FVector2D(178,40),FVector2D(80,29));Cargo->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenCargo);
  auto* Catalog=AddButton(Page==3?TEXT("VEHÍCULOS"):TEXT("MEJORAS"),FVector2D(264,40),FVector2D(100,29));if(Page==3)Catalog->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenCatalog);else Catalog->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenShop);
  auto* B=AddButton(TEXT("CICLAS"),FVector2D(8,80),FVector2D(174,29));B->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::GarageBike);auto* M=AddButton(TEXT("MOTOS"),FVector2D(190,80),FVector2D(174,29));M->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::GarageMoto);
  PreviewArt=AddArt(TEXT("T_SM_BikeStage0"),FVector2D(8,112),FVector2D(356,176));
  SelectionTitle=Caption(TEXT(""),FVector2D(8,292),FVector2D(356,22),13);SelectionTitle->SetColorAndOpacity(Mint);
  if(Page==3){
   const int32 Start=PreviewMoto?4:0,End=PreviewMoto?10:4;const TCHAR* Names[]={TEXT("01 PEDALES"),TEXT("02 MARCO"),TEXT("03 DISCOS"),TEXT("04 MOTOR"),TEXT("01 VEHÍCULO"),TEXT("02 TURBO"),TEXT("03 AERO"),TEXT("04 CILINDRAJE"),TEXT("05 INYECCIÓN"),TEXT("06 MOTOR")};
   SelectionTitle->SetVisibility(ESlateVisibility::Collapsed);AppControls.Remove(SelectionTitle);
   const FVector2D NodePos[]={FVector2D(8,360),FVector2D(200,360),FVector2D(200,410),FVector2D(8,410),FVector2D(8,460),FVector2D(200,460)};
   auto Wire=[&](FVector2D Pos,FVector2D Size){const FName N=NextLayoutName();auto* W=Cast<UBorder>(WidgetTree->FindWidget(N));if(!W){W=WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(),N);Screen->AddChildToCanvas(W);}W->SetBrushColor(FLinearColor(.12,.30,.32));auto* WS=Cast<UCanvasPanelSlot>(W->Slot);WS->SetPosition(Pos);WS->SetSize(Size);AppControls.Add(W);};
   for(int32 J=0;J<End-Start-1;J++){const auto A=NodePos[J],NextNode=NodePos[J+1];if(A.Y==NextNode.Y){Wire(FVector2D(172,A.Y+20),FVector2D(28,4));Caption(J==2?TEXT("<"):TEXT(">"),FVector2D(180,A.Y+6),FVector2D(12,12),8);}else{Wire(FVector2D(A.X+80,A.Y+44),FVector2D(4,6));}}
   for(int32 I=Start;I<End;I++)AddChoice(Names[I],I,NodePos[I-Start],FVector2D(164,44));
   if(!PreviewMoto){auto* Next=AddButton(TEXT("SIGUIENTE RAMA: MOTOS >"),FVector2D(8,460),FVector2D(356,44));Next->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::GarageMoto);Next->SetToolTipText(FText::FromString(TEXT("Instala el motor de cicla para desbloquear la rama de motos.")));}
   DSlot->SetPosition(FVector2D(8,300));DSlot->SetSize(FVector2D(356,54));
   AcceptButton=AddButton(TEXT("INSTALAR PIEZA"),FVector2D(8,512),FVector2D(222,32));AcceptButton->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::BuySelected);
   auto* Equip=AddButton(TEXT("USAR"),FVector2D(238,512),FVector2D(126,32));Equip->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::SwitchPressed);
   for(int32 I=0;I<6;I++)AddChoice(TEXT(""),100+I,FVector2D(8+I*35,264),FVector2D(29,22));
   auto* Paint=AddButton(TEXT("PINTAR $2.000"),FVector2D(224,264),FVector2D(140,22));Paint->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::PaintSelected);
  }else{
   DSlot->SetPosition(FVector2D(8,468));DSlot->SetSize(FVector2D(356,42));
   for(int32 J=0;J<3;J++)AddChoice(TEXT(""),(PreviewMoto?3:0)+J,FVector2D(8,320+J*50),FVector2D(356,44));
   ModelBuyButton=AddButton(TEXT("COMPRAR VEHÍCULO"),FVector2D(8,515),FVector2D(224,30));ModelBuyButton->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::BuyModel);ModelEquipButton=AddButton(TEXT("EQUIPAR"),FVector2D(240,515),FVector2D(124,30));ModelEquipButton->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::EquipModel);
  }
 }
 if(Page==5){
  DSlot->SetPosition(FVector2D(8,80));DSlot->SetSize(FVector2D(356,70));
  for(int32 I=0;I<5;I++)AddChoice(TEXT(""),I,FVector2D(8,160+I*64),FVector2D(356,56));
  auto* More=AddButton(TEXT("BUSCAR OTRO PEDIDO"),FVector2D(8,495),FVector2D(356,40));More->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenOrders);
 }
 if(Page==6){
  DSlot->SetPosition(FVector2D(8,370));DSlot->SetSize(FVector2D(356,96));
  PreviewArt=AddArt(TEXT("T_CargoBackpack"),FVector2D(8,80),FVector2D(356,176));
  AddChoice(TEXT("MOCHILA +1"),10,FVector2D(8,266),FVector2D(172,42));
  AddChoice(TEXT("CANGURERA +1"),11,FVector2D(192,266),FVector2D(172,42));
  AddChoice(TEXT("MALETAS MOTO +2"),12,FVector2D(8,317),FVector2D(356,42));
  AcceptButton=AddButton(TEXT("COMPRAR Y EQUIPAR"),FVector2D(8,480),FVector2D(356,45));AcceptButton->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::BuySelected);
 }
 auto* H=AddButton(TEXT("CASA"),FVector2D(8,552),FVector2D(82,33));H->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenHome);
 auto* M=AddButton(TEXT("MAPA"),FVector2D(99,552),FVector2D(82,33));M->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenMap);
 auto* O=AddButton(TEXT("PEDIDOS"),FVector2D(190,552),FVector2D(82,33));O->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenOrders);
 auto* S=AddButton(TEXT("TALLER"),FVector2D(281,552),FVector2D(83,33));S->OnClicked.AddDynamic(this,&UDeliveryPhoneWidget::OpenShop);
 BuildingLayout=false;
 for(auto* W:AppControls)if(auto* B=Cast<UButton>(W))VoxelButton(B);
 for(auto* B:{H,M,O,S}){const bool Current=(B==H&&Page==0)||(B==M&&Page==1)||(B==O&&(Page==2||Page==5))||(B==S&&(Page==3||Page==4||Page==6));if(Current){auto Style=B->GetStyle();Style.Normal.TintColor=Mint;Style.Hovered.TintColor=Mint;Style.Pressed.TintColor=Mint;B->SetStyle(Style);if(auto* T=Cast<UTextBlock>(B->GetContent())){T->SetColorAndOpacity(Ink);T->SetShadowOffset(FVector2D::ZeroVector);}}}
 RefreshText();
}























void UDeliveryPhoneWidget::RefreshText(){
 if(!Delivery||!Details)return;FString T;const TCHAR* Titles[]={TEXT(""),TEXT("MIS CALLES"),TEXT("PEDIDOS"),TEXT("MIS MEJORAS"),TEXT("MI GARAJE"),TEXT("PEDIDOS"),TEXT("EQUIPO DE CARGA")};PageTitle->SetText(FText::FromString(Titles[FMath::Clamp(Page,0,6)]));
 Header->SetText(FText::FromString(FString::Printf(TEXT("BOG   /   BOLSILLO  $%s"),*FText::AsNumber(Delivery->Balance).ToString())));
 if(auto* HomeStatus=Cast<UTextBlock>(WidgetTree->FindWidget(TEXT("HomeStatus"))))HomeStatus->SetText(FText::FromString(FString::Printf(TEXT("%d rutas disponibles\n%d / %d espacios ocupados"),Delivery->Offers.Num(),Delivery->ActiveOrders.Num(),Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle))));
 if(Page==1)T=TEXT("Mercado · Comida · Tecnología\nDroguería · Flores\nClic: marcar destino · Turquesa: tu ruta");
 if(Page==2){
  auto ShortName=[](FString Name){return Name.Len()>14?Name.Left(13)+TEXT("…"):Name;};
  const bool Active=Delivery->State==EDeliveryState::Pickup||Delivery->State==EDeliveryState::Dropoff;
  for(auto* B:Choices){const int32 I=B->Choice;bool Valid=Delivery->Offers.IsValidIndex(I);B->SetVisibility(Delivery->PhoneOpen&&Valid?ESlateVisibility::Visible:ESlateVisibility::Collapsed);B->SetIsEnabled(Delivery->ActiveOrders.Num()<Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));if(!Valid)continue;const auto& O=Delivery->Offers[I];const int32 IconIndex=AppControls.IndexOfByKey(B)+1;if(AppControls.IsValidIndex(IconIndex))if(auto* Icon=Cast<UImage>(AppControls[IconIndex]))Icon->SetBrushFromTexture(VoxelCategory(O.StoreKind));B->SetToolTipText(FText::FromString(O.PickupName.ToString()+TEXT(" > ")+O.DropoffName.ToString()));const bool Selected=Delivery->SelectedIncoming()&&O.ID==Delivery->SelectedIncoming()->ID;auto Style=B->GetStyle();Style.Normal.TintColor=Selected?Gold:Panel;Style.Hovered.TintColor=Selected?FLinearColor(1,.54,.13):FLinearColor(.055,.15,.17);B->SetStyle(Style);if(auto* L=Cast<UTextBlock>(B->GetContent())){L->SetColorAndOpacity(Selected?Ink:Paper);L->SetShadowOffset(Selected?FVector2D::ZeroVector:FVector2D(0,1));L->SetText(FText::FromString(FString::Printf(TEXT("  $%s    %.0f m    /    %.0f s\n  %s  >  %s"),*FText::AsNumber(O.Reward).ToString(),O.DistanceMeters,FMath::Max(0.f,O.ExpiresAt-GetWorld()->GetTimeSeconds()),*ShortName(O.PickupName.ToString()),*ShortName(O.DropoffName.ToString().Replace(TEXT("Casa de "),TEXT(""))))));}}
  if(Active)T=FString::Printf(TEXT("GANANCIA $%s · Dinero para ti\n%s\n%s"),*FText::AsNumber(Delivery->Order.Reward).ToString(),Delivery->State==EDeliveryState::Pickup?*FString::Printf(TEXT("Cliente paga $%d · Bolsa %d/%d"),Delivery->Order.GoodsCost,Delivery->BasketCount,Delivery->Order.StoreKind==1?1:3):TEXT("Entrega al cliente amarillo."),Delivery->State==EDeliveryState::Pickup?TEXT("Entra al local, recoge y paga en caja."):TEXT("Detente y pulsa E / A / X."));
  else if(Delivery->State==EDeliveryState::Offered)T=FString::Printf(TEXT("Tu ruta: $%s\nMantén E / A / X durante 2 segundos."),*FText::AsNumber(Delivery->Order.Reward).ToString());else T=Delivery->Offers.IsEmpty()?TEXT("Buscando nuevas rutas por el barrio…"):TEXT("Selecciona una ruta antes de aceptar el pedido.");
  if(const auto* Incoming=Delivery->SelectedIncoming())T=FString::Printf(TEXT("Recoge: %s\nEntrega: %s\n$%s · Cupo %d/%d · Mantén E/Enter 2 s"),*Incoming->PickupName.ToString(),*Incoming->DropoffName.ToString().Replace(TEXT("Casa de "),TEXT("")),*FText::AsNumber(Incoming->Reward).ToString(),Delivery->ActiveOrders.Num(),Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));
  const bool Full=Delivery->ActiveOrders.Num()>=Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle);
  AcceptButton->SetIsEnabled(Delivery->SelectedIncoming()&&!Full);
  if(Full)T=TEXT("Carga completa. Entrega un pedido para liberar espacio.\nTus pedidos están en VER PEDIDOS ACEPTADOS.");
  if(auto* L=Cast<UTextBlock>(AcceptButton->GetContent()))L->SetText(FText::FromString(Full?TEXT("SIN ESPACIO DE CARGA"):Delivery->HoldProgress>0?TEXT("ACEPTANDO... SUELTA PARA CANCELAR"):TEXT("MANTÉN E / ENTER  2 s PARA ACEPTAR")));
 }
 if(Page==5){
  Delivery->StoreFocusedOrder();T=FString::Printf(TEXT("%d / %d espacios · Elige un pedido para guiarte.\nCada pedido conserva sus artículos y su pago."),Delivery->ActiveOrders.Num(),Delivery->CargoCapacity(Delivery->Vehicle==EDeliveryVehicle::Motorcycle));
  if(Delivery->ActiveOrders.IsEmpty())T=TEXT("Todavía no tienes pedidos.\nPulsa BUSCAR OTRO PEDIDO y elige tu primera ruta.");
  for(auto* B:Choices){const int32 I=B->Choice;bool Valid=Delivery->ActiveOrders.IsValidIndex(I);B->SetVisibility(Delivery->PhoneOpen&&Valid?ESlateVisibility::Visible:ESlateVisibility::Collapsed);if(!Valid)continue;const auto& A=Delivery->ActiveOrders[I];auto Style=B->GetStyle();Style.Normal.TintColor=A.Order.ID==Delivery->Order.ID?Gold:Panel;B->SetStyle(Style);if(auto* L=Cast<UTextBlock>(B->GetContent())){auto F=L->GetFont();F.Size=10;L->SetFont(F);L->SetText(FText::FromString(FString::Printf(TEXT("%d · %s · $%s\n%s"),I+1,A.State==EDeliveryState::Pickup?TEXT("RECOGER"):TEXT("ENTREGAR"),*FText::AsNumber(A.Order.Reward).ToString(),*(A.State==EDeliveryState::Pickup?A.Order.PickupName:A.Order.DropoffName).ToString())));}}
 }
 if(Page==6&&Selection>=10&&Selection<=12&&Delivery->Upgrades&&UpgradeIDs.IsValidIndex(Selection)){
  const FName ID=UpgradeIDs[Selection];const auto* R=Delivery->Upgrades->FindRow<FDeliveryUpgrade>(ID,TEXT("CargoUI"));if(R){bool Owned=Delivery->Owns(ID),Ready=(R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite))&&(ID!=TEXT("CargoPanniers")||Delivery->Owns(TEXT("Motorcycle")));
   const TCHAR* Desc=Selection==10?TEXT("Mochila expandible: 2 pedidos en total."):Selection==11?TEXT("Cangurera: 3 pedidos en total."):TEXT("Dos maletas laterales: 5 pedidos en moto.");
   T=FString::Printf(TEXT("%s · $%s\n%s\n%s\nLa cicla usa solo mochila y cangurera."),*R->Title.ToString(),*FText::AsNumber(R->Price).ToString(),Desc,Owned?TEXT("EQUIPADA"):Ready?TEXT("Disponible"):TEXT("Requiere la mejora anterior; las maletas requieren moto."));AcceptButton->SetIsEnabled(!Owned&&Ready&&Delivery->Balance>=R->Price);
   const TCHAR* Art[]={TEXT("T_CargoBackpack"),TEXT("T_CargoWaist"),TEXT("T_CargoPanniers")};if(PreviewArt)PreviewArt->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr,*FString::Printf(TEXT("/Game/Delivery/Art/%s.%s"),Art[Selection-10],Art[Selection-10])));
  }
 }
 if((Page==3||Page==4)&&Delivery->VehicleCatalog){
  FName Model=Page==4&&ModelIDs.IsValidIndex(CatalogSelection)?ModelIDs[CatalogSelection]:(PreviewMoto?Delivery->MotoModel:Delivery->BikeModel);
  const auto* Spec=Delivery->VehicleCatalog->FindRow<FDeliveryVehicleSpec>(Model,TEXT("Preview"));int32 Stage=Delivery->VisualStage(PreviewMoto);
  if(Page==3&&UpgradeIDs.IsValidIndex(Selection)){const FName ID=UpgradeIDs[Selection];const auto* R=Delivery->Upgrades->FindRow<FDeliveryUpgrade>(ID,TEXT("UI"));if(R){const bool Owned=Delivery->Owns(ID);const bool Ready=R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite);FString Req=TEXT("Lista para instalar");if(!Ready){const auto* Prev=Delivery->Upgrades->FindRow<FDeliveryUpgrade>(R->Prerequisite,TEXT("Title"));Req=TEXT("Primero: ")+(Prev?Prev->Title.ToString():R->Prerequisite.ToString());}FString Effect;switch(R->Effect){case EUpgradeEffect::BikeCapacity:case EUpgradeEffect::MotoCapacity:Effect=FString::Printf(TEXT("+%.0f%% capacidad"),R->Magnitude*100);break;case EUpgradeEffect::BikeDrain:case EUpgradeEffect::MotoDrain:Effect=FString::Printf(TEXT("-%.0f%% consumo"),R->Magnitude*100);break;case EUpgradeEffect::MotoRegen:Effect=FString::Printf(TEXT("+%.0f%% recarga"),R->Magnitude*100);break;case EUpgradeEffect::Motorcycle:Effect=TEXT("Desbloquea las motos");break;case EUpgradeEffect::Turbo:Effect=TEXT("Activa el turbo");break;default:Effect=TEXT("Impulso infinito");break;}T=FString::Printf(TEXT("%s · $%s\n%s · %s"),*R->Title.ToString(),*FText::AsNumber(R->Price).ToString(),*Effect,Owned?TEXT("INSTALADA"):*Req);AcceptButton->SetIsEnabled(!Owned&&Ready&&Delivery->Balance>=R->Price);Stage=FMath::Max(Stage,PreviewMoto?Selection-4:Selection+1);}}
  if(Page==4&&Spec){T=Spec->Description.ToString();const bool CanBuy=!Delivery->OwnsVehicle(Model)&&Delivery->Balance>=Spec->Price&&(Spec->Prerequisite.IsNone()||Delivery->Owns(Spec->Prerequisite));if(ModelBuyButton)ModelBuyButton->SetIsEnabled(CanBuy);if(ModelEquipButton)ModelEquipButton->SetIsEnabled(Delivery->OwnsVehicle(Model)&&Delivery->ActiveOrders.Num()<=Delivery->CargoCapacity(Spec->Motorcycle));}
  for(auto* B:Choices){auto Style=B->GetStyle();if(B->Choice>=100){const FLinearColor C[]={Mint,Gold,FLinearColor(.94,.72,.025),FLinearColor(.72,.025,.055),Paper,FLinearColor(.08,.10,.13)};Style.Normal.TintColor=C[B->Choice-100];if(auto* L=Cast<UTextBlock>(B->GetContent()))L->SetText(FText::FromString(PaintSelection==B->Choice-100?TEXT("+"):TEXT("")));}else if(Page==3){bool Selected=B->Choice==Selection;const auto* R=Delivery->Upgrades->FindRow<FDeliveryUpgrade>(UpgradeIDs[B->Choice],TEXT("ProgressNode"));const bool Owned=Delivery->Owns(UpgradeIDs[B->Choice]);const bool Ready=R&&(R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite));Style.Normal.TintColor=Selected?Gold:Owned?FLinearColor(.02,.13,.14):Panel;if(R)if(auto* L=Cast<UTextBlock>(B->GetContent())){const TCHAR* Short[]={TEXT("Pedales"),TEXT("Marco"),TEXT("Discos"),TEXT("Motor cicla"),TEXT("Moto"),TEXT("Turbo"),TEXT("Aerodinámica"),TEXT("Cilindraje"),TEXT("Inyección"),TEXT("Motor deportivo")};auto F=L->GetFont();F.Size=10;L->SetFont(F);L->SetWrapTextAt(0);L->SetAutoWrapText(false);if(auto* NodeSlot=Cast<UButtonSlot>(L->Slot)){NodeSlot->SetHorizontalAlignment(HAlign_Fill);NodeSlot->SetPadding(FMargin(6,0,6,0));}L->SetClipping(EWidgetClipping::ClipToBounds);L->SetJustification(ETextJustify::Center);L->SetText(FText::FromString(FString::Printf(TEXT("%02d %s\n%s"),B->Choice-(PreviewMoto?4:0)+1,Short[B->Choice],Owned?TEXT("[+] INSTALADA"):*(FString(Ready?TEXT(""):TEXT("[X] "))+TEXT("$")+FText::AsNumber(R->Price).ToString()))));}}else if(Page==4&&ModelIDs.IsValidIndex(B->Choice)){const auto ID=ModelIDs[B->Choice];const auto* R=Delivery->VehicleCatalog->FindRow<FDeliveryVehicleSpec>(ID,TEXT("Card"));Style.Normal.TintColor=B->Choice==CatalogSelection?Gold:Panel;if(R)if(auto* L=Cast<UTextBlock>(B->GetContent()))L->SetText(FText::FromString(FString::Printf(TEXT("%s  /  %s\n%s"),*R->Title.ToString(),Delivery->OwnsVehicle(ID)?TEXT("[+] EN TU GARAJE"):*FString::Printf(TEXT("$%s"),*FText::AsNumber(R->Price).ToString()),Delivery->OwnsVehicle(ID)?TEXT("SELECCIONA Y EQUIPA"):R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite)?TEXT("DISPONIBLE"):TEXT("[X] REQUIERE MEJORAS"))));}B->SetStyle(Style);}
  if(Spec&&SelectionTitle)SelectionTitle->SetText(FText::FromString(Spec->Title.ToString()+TEXT("  /  VISTA PREVIA")));
  FString Prefix=PreviewMoto?TEXT("SM_Moto"):TEXT("SM_Bike");if(Model==TEXT("BikeCargo")||Model==TEXT("MotoCargo"))Prefix+=TEXT("Cargo");if(Model==TEXT("BikeBMX"))Prefix+=TEXT("BMX");if(Model==TEXT("MotoSport"))Prefix+=TEXT("Sport");FString Mesh=Prefix+FString::Printf(TEXT("Stage%d"),FMath::Clamp(Stage,0,PreviewMoto?5:4));
  if(!VehiclePreview)VehiclePreview=GetWorld()->SpawnActor<ADeliveryVehiclePreview>(FVector(-90000,-90000,-10000),FRotator::ZeroRotator);
  if(VehiclePreview){VehiclePreview->ShowVehicle(Mesh,PaintSelection);if(PreviewArt&&VehiclePreview->Target){FSlateBrush Brush;Brush.SetResourceObject(VehiclePreview->Target);Brush.ImageSize=FVector2D(640,316);PreviewArt->SetBrush(Brush);}}
 }
 // Finish every selection with the same readable selected/owned/disabled vocabulary.
 for(auto* B:Choices){bool Selected=Page==2?(Delivery->SelectedIncoming()&&Delivery->Offers.IsValidIndex(B->Choice)&&Delivery->Offers[B->Choice].ID==Delivery->SelectedIncoming()->ID):Page==5?(Delivery->ActiveOrders.IsValidIndex(B->Choice)&&Delivery->ActiveOrders[B->Choice].Order.ID==Delivery->Order.ID):Page==4?B->Choice==CatalogSelection:B->Choice==Selection;
  if(Page==6){auto Style=B->GetStyle();Style.Normal.TintColor=Selected?Gold:Panel;B->SetStyle(Style);}
  auto Style=B->GetStyle();Style.Pressed.TintColor=B->Choice>=100?Style.Normal.TintColor:Selected?Gold:Panel;Style.Hovered.TintColor=B->Choice>=100?Style.Normal.TintColor:Selected?Gold:FLinearColor(.055,.15,.17);B->SetStyle(Style);
  if(auto* Label=Cast<UTextBlock>(B->GetContent())){const auto Face=Style.Normal.TintColor.GetSpecifiedColor();const bool DarkText=B->Choice>=100?(.2126*Face.R+.7152*Face.G+.0722*Face.B)>.25:Selected;Label->SetColorAndOpacity(DarkText?Ink:Paper);Label->SetShadowOffset(Selected?FVector2D::ZeroVector:FVector2D(0,1));}
 }
 if(Page==4&&ModelIDs.IsValidIndex(CatalogSelection)){
  const auto* Spec=Delivery->VehicleCatalog->FindRow<FDeliveryVehicleSpec>(ModelIDs[CatalogSelection],TEXT("Explain"));
  if(Spec){if(Delivery->OwnsVehicle(ModelIDs[CatalogSelection])){T=Delivery->ActiveOrders.Num()>Delivery->CargoCapacity(Spec->Motorcycle)?TEXT("No admite tu carga actual. Entrega pedidos antes de equiparlo."):TEXT("En tu garaje. Elige EQUIPAR para usarlo.");}else if(!Spec->Prerequisite.IsNone()&&!Delivery->Owns(Spec->Prerequisite)){const auto* Required=Delivery->Upgrades?Delivery->Upgrades->FindRow<FDeliveryUpgrade>(Spec->Prerequisite,TEXT("RequirementTitle")):nullptr;T=FString::Printf(TEXT("Requiere: %s.\nÁbrela en MIS MEJORAS para desbloquear este modelo."),Required?*Required->Title.ToString():*Spec->Prerequisite.ToString());}else if(Delivery->Balance<Spec->Price)T=FString::Printf(TEXT("Te faltan $%s para comprarlo."),*FText::AsNumber(Spec->Price-Delivery->Balance).ToString());}
 }
 if((Page==3||Page==6)&&AcceptButton&&!AcceptButton->GetIsEnabled()&&UpgradeIDs.IsValidIndex(Selection)){
  const auto* R=Delivery->Upgrades->FindRow<FDeliveryUpgrade>(UpgradeIDs[Selection],TEXT("Explain"));if(R&&!Delivery->Owns(UpgradeIDs[Selection])&&(R->Prerequisite.IsNone()||Delivery->Owns(R->Prerequisite))&&Delivery->Balance<R->Price)T+=FString::Printf(TEXT("\nTe faltan $%s."),*FText::AsNumber(R->Price-Delivery->Balance).ToString());
 }
 for(auto* B:{AcceptButton,ModelBuyButton,ModelEquipButton})if(B){auto Style=B->GetStyle();Style.Normal.TintColor=Mint;Style.Hovered.TintColor=FLinearColor(.25,1,.85);Style.Pressed.TintColor=Mint;B->SetStyle(Style);if(auto* L=Cast<UTextBlock>(B->GetContent())){L->SetColorAndOpacity(B->GetIsEnabled()?Ink:FLinearColor(.58,.67,.68));L->SetShadowOffset(FVector2D::ZeroVector);}}
 if(Page==3||Page==4)for(auto* W:AppControls)if(auto* B=Cast<UButton>(W))if(auto* L=Cast<UTextBlock>(B->GetContent())){auto Label=L->GetText().ToString();if(Label==TEXT("CICLAS")||Label==TEXT("MOTOS")){const bool Current=PreviewMoto?Label==TEXT("MOTOS"):Label==TEXT("CICLAS");auto Style=B->GetStyle();Style.Normal.TintColor=Current?Mint:Panel;Style.Hovered.TintColor=Current?Mint:FLinearColor(.055,.15,.17);Style.Pressed.TintColor=Style.Normal.TintColor;B->SetStyle(Style);L->SetColorAndOpacity(Current?Ink:Paper);}}
 Details->SetText(FText::FromString(T));Details->SetVisibility(Delivery->PhoneOpen&&Page!=0?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);
}
void UDeliveryPhoneWidget::NativeTick(const FGeometry& G,float Dt){
 Super::NativeTick(G,Dt);if(!Delivery||!Frame)return;const bool Open=Delivery->PhoneOpen;
 if(auto* Home=WidgetTree->FindWidget(TEXT("DesignerHome")))Home->SetVisibility(Open&&Page==0?ESlateVisibility::SelfHitTestInvisible:ESlateVisibility::Collapsed);
 if(Open&&MainMap)if(auto* PC=GetOwningPlayer()){MainMap->MapCursor+=FVector2D(PC->GetInputAnalogKeyState(EKeys::Gamepad_LeftX),-PC->GetInputAnalogKeyState(EKeys::Gamepad_LeftY))*Dt*.35;MainMap->MapCursor.X=FMath::Clamp(MainMap->MapCursor.X,.02,.98);MainMap->MapCursor.Y=FMath::Clamp(MainMap->MapCursor.Y,.02,.98);}
 if(Open!=LastOpen){if(Open){BuildPage(Page);SetKeyboardFocus();}LastOpen=Open;}
 OpenAlpha=FMath::FInterpConstantTo(OpenAlpha,Open?1.f:0.f,Dt,4.f);const float A=FMath::SmoothStep(0.f,1.f,OpenAlpha);const float ViewportScale=FMath::Max(.1f,UWidgetLayoutLibrary::GetViewportScale(this));const FVector2D View=UWidgetLayoutLibrary::GetViewportSize(this)/ViewportScale;
 auto HintFont=PhoneHints->GetFont();const int32 HintSize=FMath::CeilToInt(12.f/ViewportScale);if(HintFont.Size!=HintSize){HintFont.Size=HintSize;PhoneHints->SetFont(HintFont);}
 auto NoticeFont=Notice->GetFont();const int32 NoticeSize=FMath::CeilToInt(14.f/ViewportScale);if(NoticeFont.Size!=NoticeSize){NoticeFont.Size=NoticeSize;Notice->SetFont(NoticeFont);}

 auto* HintsSlot=Cast<UCanvasPanelSlot>(PhoneHints->Slot);HintsSlot->SetOffsets(FMargin(12.f/ViewportScale,-54.f/ViewportScale,12.f/ViewportScale,50.f/ViewportScale));
 auto* ProgressSlot=Cast<UCanvasPanelSlot>(HoldBar->Slot);ProgressSlot->SetZOrder(100);
 if(Open&&Page==2&&AcceptButton){const auto& ButtonGeometry=AcceptButton->GetCachedGeometry();const FVector2D ButtonSize=ButtonGeometry.GetLocalSize();
  if(ButtonSize.X>0){FVector2D Start=G.AbsoluteToLocal(ButtonGeometry.LocalToAbsolute(FVector2D(0,ButtonSize.Y-5))),End=G.AbsoluteToLocal(ButtonGeometry.LocalToAbsolute(ButtonSize));ProgressSlot->SetPosition(Start);ProgressSlot->SetSize(FVector2D(End.X-Start.X,FMath::Max(3.f/ViewportScale,End.Y-Start.Y)));}
 }else {ProgressSlot->SetPosition(FVector2D(28,187));ProgressSlot->SetSize(FVector2D(220,8));}const float OpenWidth=420.f;const float Scale=FMath::Min((View.Y-114)/680.f,(View.X-48)/OpenWidth);
 const float ClosedScale=FMath::Max(.1f,FMath::Min(1.f,FMath::Min((View.X-32)/300.f,(View.Y-32)/180.f)));const FVector2D ClosedSize=FVector2D(300,180)*ClosedScale;const FVector2D ClosedPos(16,FMath::Max(16.,View.Y-ClosedSize.Y-16));
 const FVector2D Size=FMath::Lerp(ClosedSize,FVector2D(OpenWidth*Scale,680*Scale),A),Pos=FMath::Lerp(ClosedPos,(View-FVector2D(OpenWidth*Scale,680*Scale+64))*.5,A);
 auto* Shell=LoadObject<UTexture2D>(nullptr,TEXT("/Game/Delivery/Art/T_UrbanShell.T_UrbanShell"));if(PhoneArt->GetBrush().GetResourceObject()!=Shell)PhoneArt->SetBrushFromTexture(Shell);
 // Keep a fixed logical screen size and scale the whole phone once, avoiding double DPI scaling.
 auto* FS=Cast<UCanvasPanelSlot>(Frame->Slot);FS->SetPosition(Pos);FS->SetSize(Open?FVector2D(OpenWidth,680):FVector2D(300,180));Frame->SetPadding(Open?FMargin(24,48,24,36):FMargin(22,18,22,18));Frame->SetRenderTransformPivot(FVector2D::ZeroVector);Frame->SetRenderScale(Open?FVector2D(Scale,Scale):FVector2D(ClosedScale,ClosedScale));Frame->SetRenderTransformAngle(0);
 auto* PS=Cast<UCanvasPanelSlot>(PhoneArt->Slot);PS->SetPosition(Pos);PS->SetSize(Size);PhoneArt->SetRenderTransformAngle(0);
 PhoneHints->SetVisibility(Open?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);PhoneShade->SetVisibility(Open?ESlateVisibility::Visible:ESlateVisibility::Collapsed);MiniMap->SetVisibility(Open?ESlateVisibility::Collapsed:ESlateVisibility::HitTestInvisible);Header->SetVisibility(Open?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);PageTitle->SetVisibility(Open?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);for(auto* W:AppControls)W->SetVisibility(Open?(Cast<UImage>(W)?ESlateVisibility::HitTestInvisible:ESlateVisibility::Visible):ESlateVisibility::Collapsed);if(MainMap)MainMap->SetVisibility(Open?ESlateVisibility::Visible:ESlateVisibility::Collapsed);const bool Transition=OpenAlpha>0&&OpenAlpha<1;Frame->SetVisibility(Transition?ESlateVisibility::Hidden:Open?ESlateVisibility::Visible:ESlateVisibility::HitTestInvisible);
 FString S=Delivery->State==EDeliveryState::Pickup?Delivery->ShoppingInstruction():Delivery->StatusMessage.ToString();if(Delivery->InsideStore&&Delivery->State!=EDeliveryState::Pickup)S=TEXT("Sal caminando por la puerta.");if(Delivery->State==EDeliveryState::Offered&&!Delivery->InsideStore)S=FString::Printf(TEXT("%d RUTAS CERCA  ·  TAB para elegir en Pedidos"),Delivery->Offers.Num());else if(Delivery->State==EDeliveryState::Pickup||Delivery->State==EDeliveryState::Dropoff)S+=FString::Printf(TEXT("\nDestino a %.0f m"),FVector::Dist2D(Delivery->GetOwner()->GetActorLocation(),Delivery->GetOrderTarget())/100);
 const bool Active=Delivery->State==EDeliveryState::Pickup||Delivery->State==EDeliveryState::Dropoff;Notice->SetVisibility(Open?ESlateVisibility::Collapsed:ESlateVisibility::HitTestInvisible);EnergyText->SetVisibility(Active&&!Open?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);EnergyBar->SetVisibility(Active&&!Open?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);Notice->SetText(FText::FromString(S));EnergyText->SetText(FText::FromString(FString::Printf(TEXT("%s  /  IMPULSO %s"),Delivery->Vehicle==EDeliveryVehicle::Bicycle?TEXT("CICLA"):TEXT("MOTO"),Delivery->InfiniteBoost?TEXT("∞"):*FString::Printf(TEXT("%.0f%%"),100*Delivery->Energy/FMath::Max(1.f,Delivery->Capacity)))));EnergyBar->SetPercent(Delivery->InfiniteBoost?1:Delivery->Energy/FMath::Max(1.f,Delivery->Capacity));HoldBar->SetPercent(Delivery->HoldProgress);HoldBar->SetVisibility(Delivery->HoldProgress>0?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);RefreshText();
}
FReply UDeliveryPhoneWidget::NativeOnPreviewKeyDown(const FGeometry& G,const FKeyEvent& E){
 if(!Delivery||!Delivery->PhoneOpen)return Super::NativeOnPreviewKeyDown(G,E);auto K=E.GetKey();
 const bool Confirm=K==EKeys::E||K==EKeys::Enter||K==EKeys::Gamepad_FaceButton_Bottom;
 if(E.IsRepeat()&&Confirm)return FReply::Handled();
 if(K==EKeys::Tab||K==EKeys::Gamepad_Special_Left||K==EKeys::Escape){ClosePressed();return FReply::Handled();}
 if(K==EKeys::Four){OpenCargo();return FReply::Handled();}if(K==EKeys::Five){OpenCatalog();return FReply::Handled();}
 if(K==EKeys::One){OpenMap();return FReply::Handled();}if(K==EKeys::Two){OpenOrders();return FReply::Handled();}if(K==EKeys::Three){OpenShop();return FReply::Handled();}
 if(Page==3){FVector2D Direction=FVector2D::ZeroVector;if(K==EKeys::Left||K==EKeys::Gamepad_DPad_Left)Direction.X=-1;if(K==EKeys::Right||K==EKeys::Gamepad_DPad_Right)Direction.X=1;if(K==EKeys::Up||K==EKeys::Gamepad_DPad_Up)Direction.Y=-1;if(K==EKeys::Down||K==EKeys::Gamepad_DPad_Down)Direction.Y=1;
  if(!Direction.IsNearlyZero()){FVector2D Origin=FVector2D::ZeroVector;for(auto* B:Choices)if(B->Choice==Selection)if(auto* L=Cast<UCanvasPanelSlot>(B->Slot))Origin=L->GetPosition();float Best=MAX_flt;int32 Target=Selection;for(auto* B:Choices)if(B->Choice<100)if(auto* L=Cast<UCanvasPanelSlot>(B->Slot)){const auto Delta=L->GetPosition()-Origin;const float Forward=FVector2D::DotProduct(Delta,Direction);if(Forward<=0)continue;const float Side=FMath::Abs(Delta.X*Direction.Y-Delta.Y*Direction.X);const float Score=Forward+Side*4;if(Score<Best){Best=Score;Target=B->Choice;}}SelectEntry(Target);return FReply::Handled();}
 }
 if((Page==2||Page==3||Page==4||Page==5||Page==6)&&(K==EKeys::Down||K==EKeys::Right||K==EKeys::Gamepad_DPad_Down||K==EKeys::Gamepad_DPad_Right)){if(Page==2&&!Delivery->SelectedIncoming())SelectEntry(0);else SelectNext();return FReply::Handled();}if((Page==2||Page==3||Page==4||Page==5||Page==6)&&(K==EKeys::Up||K==EKeys::Left||K==EKeys::Gamepad_DPad_Up||K==EKeys::Gamepad_DPad_Left)){if(Page==2&&!Delivery->SelectedIncoming())SelectEntry(0);else SelectPrevious();return FReply::Handled();}
 if(Page==1&&MainMap&&K==EKeys::Gamepad_FaceButton_Bottom){auto C=MainMap->MapCursor;Delivery->SetWaypoint(FVector(-(C.Y-.5)/.46*45000,(C.X-.5)/.46*30000,0));return FReply::Handled();}
 if(Confirm){if(Page==2)AcceptPressed();else if(Page==3||Page==6)BuySelected();else if(Page==4)BuyModel();return FReply::Handled();}
 return Super::NativeOnPreviewKeyDown(G,E);
}
FReply UDeliveryPhoneWidget::NativeOnKeyUp(const FGeometry& G,const FKeyEvent& E){if(Delivery&&(E.GetKey()==EKeys::E||E.GetKey()==EKeys::Enter||E.GetKey()==EKeys::Gamepad_FaceButton_Bottom)){AcceptReleased();return FReply::Handled();}return Super::NativeOnKeyUp(G,E);}
void UDeliveryPhoneWidget::NativeDestruct(){if(Delivery)Delivery->EndAction();if(VehiclePreview)VehiclePreview->Destroy();Super::NativeDestruct();}

