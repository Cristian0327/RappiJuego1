"""Test a smaller plugin set in the disposable runtime project, using real dependencies."""
from pathlib import Path
import json,shutil,os,re
R=Path(__file__).resolve().parent;engine=Path(r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins');project=R.parent/'BogotaVoxel';required=json.loads((R/'AdversarialQA_20261026/required_packages.json').read_text());plugins={};modules={}
for root in [engine,project/'Plugins']:
 if not root.exists():continue
 files=[]
 for directory,folders,names in os.walk(root):
  folders[:]=[n for n in folders if n not in {'Content','Source','Binaries','Intermediate','Resources','Build','Config','Documentation','Extras'}]
  files.extend(Path(directory)/n for n in names if n.endswith('.uplugin'))
 for file in files:
  try:
   raw=file.read_text(encoding='utf-8-sig');raw='\n'.join(line for line in raw.splitlines() if not line.lstrip().startswith('//'));data=json.loads(re.sub(r',\s*([}\]])',r'\1',raw))
  except (ValueError,UnicodeDecodeError):continue
  name=file.stem;plugins[name]=(file,data)
  for module in data.get('Modules',[]):modules.setdefault(module['Name'],set()).add(name)
original=json.loads((project/'BogotaVoxel.uproject').read_text(encoding='utf-8-sig'));selected={p['Name'] for p in original.get('Plugins',[]) if p.get('Enabled')}
for module in required['script_modules']:selected.update(modules.get(module,set()))
selected.update(n for n in required['external_roots'] if n in plugins)
# Preserve already-enabled shader providers. Removing vertex factories changes
# default material shader-map keys and causes a prohibitively costly cold rebuild.
baseline=(R/'AdversarialQA_20261026/runtime.log').read_text(encoding='utf-8',errors='replace')
mounted=set(re.findall(r'Mounting Engine plugin (\w+)',baseline))
shader_plugins={n for n in mounted if n in plugins and (plugins[n][0].parent/'Shaders').is_dir()}
selected.update(shader_plugins)
if 'ContentBrowserAssetDataSource' in plugins:selected.add('ContentBrowserAssetDataSource')
# Build/cooking backends are selected dynamically by module name, not serialized
# as UObject package dependencies. Preserve the baseline providers and codecs.
backend_modules={'SkeletalMeshReduction','QuadricMeshReduction','ProxyLODMeshReduction','TextureFormatOodle','TextureFormatDXT','TextureFormatASTC','TextureFormatETC2','TextureFormatUncompressed'}
backend_plugins=set()
for module in backend_modules:backend_plugins.update(modules.get(module,set()))
backend_plugins.update(n for n in mounted if n in plugins and re.search(r'Reduction|TextureFormat|Compression|Oodle|Audio|Codec',n,re.I))
selected.update(backend_plugins)
pending=list(selected)
while pending:
 name=pending.pop();assert name in plugins,name
 for dependency in plugins[name][1].get('Plugins',[]):
  if dependency.get('Enabled',False) and dependency['Name'] not in selected:
   selected.add(dependency['Name']);pending.append(dependency['Name'])
config=dict(original);config['DisableEnginePluginsByDefault']=True;old={p['Name']:p for p in original.get('Plugins',[])};config['Plugins']=[dict(old.get(n,{'Name':n}),Enabled=True) for n in sorted(selected)]+[p for p in original.get('Plugins',[]) if not p.get('Enabled')]
target=R/'ModulelessRuntime/BogotaVoxel.uproject';backup=R/'AdversarialQA_20261026/runtime_descriptor_before.json'
if not backup.exists():shutil.copy2(target,backup)
target.write_text(json.dumps(config,indent=2),encoding='utf-8')
assert 'SkeletalMeshReduction' in modules and modules['SkeletalMeshReduction']<=selected,'Skeletal reduction provider must be retained'
report=dict(status='prepared_for_runtime_test',enabled_plugins=sorted(selected),preserved_shader_plugins=sorted(shader_plugins),preserved_backend_plugins=sorted(backend_plugins),script_modules=required['script_modules'],external_roots=required['external_roots'],original_project_descriptor_modified=False,descriptor=str(target));(R/'AdversarialQA_20261026/lightweight_plugins.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
