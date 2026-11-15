from pathlib import Path
p=Path('outputs/BogotaVoxel/Source/BogotaVoxel/DeliveryUI.cpp');s=p.read_text(encoding='utf-8-sig');needle=' PhoneHints->SetFont(HintFont);' # Font setter is guarded in the native tick.
anchor='auto* ProgressSlot=Cast<UCanvasPanelSlot>(HoldBar->Slot);ProgressSlot->SetZOrder(100);'
assert anchor in s
s=s.replace(anchor,'auto* HintsSlot=Cast<UCanvasPanelSlot>(PhoneHints->Slot);HintsSlot->SetOffsets(FMargin(12.f/ViewportScale,-54.f/ViewportScale,12.f/ViewportScale,50.f/ViewportScale));\n '+anchor)
p.write_text(s,encoding='utf-8')
p=Path('work/run_usability_review.ps1');s=p.read_text(encoding='utf-8-sig');s=s.replace("if($taskResult.status -ne 'PASS'){throw", "$taskEngineErrors=@(Select-String -LiteralPath $taskLog -Pattern ': Error:|Fatal error')\n$taskEngineErrors | ForEach-Object {$_.Line} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'errores_motor.json') -Encoding utf8\nif($taskEngineErrors.Count -gt 0){throw \"Engine errors in $taskLog\"}\nif($taskResult.status -ne 'PASS'){throw")
p.write_text(s,encoding='utf-8')
