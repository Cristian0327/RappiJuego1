from pathlib import Path
import shutil,re
R=Path(__file__).resolve().parent;P=R.parent/'BogotaVoxel';A=R/'BlueprintAuthoring';backup=Path((R/'optimization_backup_path.txt').read_text())
for project in [P,A]:
 f=project/'Config/DefaultEngine.ini';s=f.read_text();s=s.replace('r.DynamicRes.MinScreenPercentage=70','r.DynamicRes.MinScreenPercentage=55');s=s.replace('r.DynamicRes.FrameTimeBudget=16.666667','r.DynamicRes.FrameTimeBudget=16.000000')
 if 'r.DynamicRes.OperationMode=1' not in s:s+='\n[ConsoleVariables]\nr.DynamicRes.OperationMode=1\nr.MeshStreaming=1\nr.SkeletalMesh.StreamLODs=1\n'
 # Dynamic modifiers update doors/obstacles without recooking all city triangles.
 s=s.replace('RuntimeGeneration=Dynamic\n','RuntimeGeneration=DynamicModifiersOnly\n');f.write_text(s,encoding='utf-8')
 f=project/'Config/DefaultGameUserSettings.ini';s=f.read_text().replace('FrameRateLimit=30.000000','FrameRateLimit=60.000000').replace('bUseDynamicResolution=False','bUseDynamicResolution=True');f.write_text(s,encoding='utf-8')
 f=project/'Config/DefaultInput.ini';s=f.read_text(encoding='utf-8-sig')
 if 'ActionName="GraphicsMenu"' not in s:s+='\n[/Script/Engine.InputSettings]\n+ActionMappings=(ActionName="GraphicsMenu",bShift=False,bCtrl=False,bAlt=False,bCmd=False,Key=F10)\n'
 if project==P and not (backup/'DefaultInput.ini').exists():shutil.copy2(f,backup/'DefaultInput.ini')
 f.write_text(s,encoding='utf-8')
# Seed only this workstation's existing legacy settings; subsequent menu changes persist.
for f in (P/'Saved/Config').glob('Windows*/GameUserSettings.ini'):
 target=backup/('Saved_'+f.parent.name+'_GameUserSettings.ini')
 if target.exists():continue
 shutil.copy2(f,target)
 s=f.read_text(encoding='utf-8-sig')
 s=re.sub(r'(?m)^sg\.(ViewDistance|AntiAliasing|Shadow|GlobalIllumination|Reflection|PostProcess|Texture|Effects|Foliage|Shading)Quality=.*$',lambda m:'sg.'+m.group(1)+'Quality=0',s)
 s=re.sub(r'(?m)^sg.ResolutionQuality=.*$','sg.ResolutionQuality=55.000000',s)
 s=re.sub(r'(?m)^FrameRateLimit=.*$','FrameRateLimit=60.000000',s)
 s=s.replace('bUseDynamicResolution=False','bUseDynamicResolution=True')
 f.write_text(s,encoding='utf-8')
print('OPTIMIZATION_CONFIG_READY')
