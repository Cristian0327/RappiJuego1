"""Prepare authoring from the current canonical project and write scalable settings."""
from pathlib import Path
import shutil,hashlib,json,datetime
R=Path(__file__).resolve().parent; P=R.parent/'BogotaVoxel'; A=R/'BlueprintAuthoring'
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S'); backup=R/('optimization_backup_'+stamp)
backup.mkdir(); manifest=[]
for f in (P/'Content').rglob('*'):
 if not f.is_file():continue
 target=A/'Content'/f.relative_to(P/'Content')
 if not target.exists() or hashlib.sha256(f.read_bytes()).digest()!=hashlib.sha256(target.read_bytes()).digest():
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
for name in ['DefaultEngine.ini','DefaultScalability.ini','DefaultGameUserSettings.ini','DefaultEditorPerProjectUserSettings.ini']:
 f=P/'Config'/name
 if f.exists():shutil.copy2(f,backup/name)
 manifest.append(dict(path=str(f),existed=f.exists()))
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
(R/'optimization_backup_path.txt').write_text(str(backup))
# Remove console priority overrides of user-adjustable scalability values.
f=P/'Config/DefaultEngine.ini';s=f.read_text(encoding='utf-8-sig')
drop={'r.ScreenPercentage','r.Streaming.PoolSize','r.Shadow.DistanceScale','r.Shadow.MaxResolution','r.Shadow.CSM.MaxCascades','r.ViewDistanceScale','r.BloomQuality','r.SSR.Quality','r.AmbientOcclusionLevels','r.SkeletalMeshLODBias','r.VSync','t.MaxFPS','r.DynamicRes.OperationMode'}
s='\n'.join(line for line in s.splitlines() if line.split('=',1)[0] not in drop)+'\n'
s=s.replace('DefaultGraphicsRHI=DefaultGraphicsRHI_DX12','DefaultGraphicsRHI=DefaultGraphicsRHI_DX11')
s=s.replace('bForceRebuildOnLoad=True','bForceRebuildOnLoad=False')
# Keep dynamic navigation for real changes; don't force a full rebuild on every load.
s+='''
[ConsoleVariables]
r.Streaming.LimitPoolSizeToVRAM=1
r.Streaming.UsePerTextureBias=1
r.Streaming.FramesForFullUpdate=10
r.Streaming.MaxTempMemoryAllowed=32
r.AllowOcclusionQueries=1
r.HZBOcclusion=0
r.PSOPrecache.GlobalShaders=1
r.PSOPrecache.ProxyCreationDelayStrategy=0
r.pso.PrecompileThreadPoolSize=1
s.AsyncLoadingThreadEnabled=1

[/Script/UnrealEd.EditorPerformanceSettings]
bThrottleCPUWhenNotForeground=True
'''
f.write_text(s,encoding='utf-8')
# Each quality is a complete tier. LOD0 remains untouched. Cine is a playable maximum.
profiles=[(.30,2.2,256,2,0,512,1,0,0,0,55),(.5,1.65,384,1,1,1024,1,1,0,0,70),(.75,1.25,768,0,2,1024,2,2,1,1,85),(1.,1.,1536,0,3,2048,3,3,2,2,100),(1.25,.8,0,0,4,2048,4,3,3,3,100)]
lines=['; BogotaVoxel: 0 minima, 1 baja, 2 media, 3 alta, Cine maxima.']
for i,(distance,lod,pool,bias,shadow,res,casc,aa,ao,ssr,screen) in enumerate(profiles):
 tier='Cine' if i==4 else str(i)
 groups={
 'ViewDistanceQuality':{'r.ViewDistanceScale':distance,'r.StaticMeshLODDistanceScale':lod,'r.SkeletalMeshLODBias':1 if i==0 else 0},
 'TextureQuality':{'r.Streaming.PoolSize':pool,'r.Streaming.MipBias':bias,'r.MaxAnisotropy':[2,4,8,16,16][i]},
 'ShadowQuality':{'r.ShadowQuality':shadow,'r.Shadow.MaxResolution':res,'r.Shadow.CSM.MaxCascades':casc,'r.Shadow.DistanceScale':[.25,.4,.65,1,1.2][i]},
 'AntiAliasingQuality':{'r.PostProcessAAQuality':aa},
 'PostProcessQuality':{'r.BloomQuality':[0,1,3,4,5][i],'r.AmbientOcclusionLevels':ao,'r.MotionBlurQuality':0,'r.DepthOfFieldQuality':[0,0,1,2,2][i]},
 'ReflectionQuality':{'r.SSR.Quality':ssr},
 'FoliageQuality':{'foliage.DensityScale':1,'grass.DensityScale':[.3,.5,.7,1,1][i]},
 }
 for group,values in groups.items():
  lines+=['',f'[{group}@{tier}]']+[f'{k}={v}' for k,v in values.items()]
(P/'Config/DefaultScalability.ini').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(P/'Config/DefaultGameUserSettings.ini').write_text('''; Safe first-run preset. Existing player choices take precedence.
[/Script/Engine.GameUserSettings]
Version=5
bUseVSync=False
bUseDynamicResolution=False
ResolutionSizeX=1280
ResolutionSizeY=720
LastUserConfirmedResolutionSizeX=1280
LastUserConfirmedResolutionSizeY=720
FullscreenMode=2
LastConfirmedFullscreenMode=2
FrameRateLimit=30.000000
AudioQualityLevel=0

[ScalabilityGroups]
sg.ResolutionQuality=55.000000
sg.ViewDistanceQuality=0
sg.AntiAliasingQuality=0
sg.ShadowQuality=0
sg.GlobalIlluminationQuality=0
sg.ReflectionQuality=0
sg.PostProcessQuality=0
sg.TextureQuality=0
sg.EffectsQuality=0
sg.FoliageQuality=0
sg.ShadingQuality=0
''',encoding='utf-8')
for name in ['DefaultEngine.ini','DefaultScalability.ini','DefaultGameUserSettings.ini']:
 shutil.copy2(P/'Config'/name,A/'Config'/name)
print(json.dumps(dict(backup=str(backup),status='prepared'),indent=2))
