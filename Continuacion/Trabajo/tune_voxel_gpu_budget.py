from pathlib import Path
p=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1/Config/DefaultEngine.ini');s=p.read_text();s=s.replace('r.DynamicRes.MinScreenPercentage=60','r.DynamicRes.MinScreenPercentage=40');keys={'r.SeparateTranslucencyScreenPercentage':'50','r.TranslucencyLightingVolume':'0','r.Tonemapper.Quality':'0','r.Upscale.Quality':'0'}
for k,v in keys.items():
 if any(line.startswith(k+'=') for line in s.splitlines()):s='\n'.join(k+'='+v if line.startswith(k+'=') else line for line in s.splitlines())+'\n'
 else:
  at=s.index('[ConsoleVariables]')+len('[ConsoleVariables]');s=s[:at]+'\n'+k+'='+v+s[at:]
p.write_text(s,encoding='utf-8')
