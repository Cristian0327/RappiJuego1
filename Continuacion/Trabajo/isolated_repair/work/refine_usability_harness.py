from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUsability.cpp');s=p.read_text();s=s.replace('static float WalletBefore=0;','')
s=s.replace(' if(ValidationStage==0&&ValidationTime>3){',''' static int32 ShotStage=-1;
 if(ValidationTime>.5f&&ShotStage!=ValidationStage){if(ValidationStage==1)Capture(TEXT("QA_Home.png"));if(ValidationStage==2)Capture(TEXT("QA_Map.png"));if(ValidationStage==8)Capture(TEXT("QA_Garage_Locked.png"));ShotStage=ValidationStage;}
 if(ValidationStage==0&&ValidationTime>3){''')
s=s.replace('  Capture(TEXT("QA_Home.png"));Key(EKeys::One);','  Key(EKeys::One);').replace('  Capture(TEXT("QA_Map.png"));Key(EKeys::Two);','  Key(EKeys::Two);').replace('Capture(TEXT("QA_Garage_Locked.png"));\n  UI->OpenHome();','\n  UI->OpenHome();')
s=s.replace('  for(auto* W:UI->AppControls)if(W)Check(W->GetVisibility()==ESlateVisibility::Collapsed,','  Next();\n }else if(ValidationStage==13&&ValidationTime>.4f){\n  for(auto* W:UI->AppControls)if(W)Check(W->GetVisibility()==ESlateVisibility::Collapsed,')
p.write_text(s)
