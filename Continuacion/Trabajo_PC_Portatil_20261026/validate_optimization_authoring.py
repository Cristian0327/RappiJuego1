"""Validate generated authoring code without modifying Unreal assets."""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent;real_exec=exec;compiled=[]
class UnrealStub:
 def log(self,*args):pass
def capture(code,scope):
 if code.co_filename=='QualityStoreBudget':real_exec(code,dict(scope,exec=capture))
 else:compiled.append(code.co_filename)
for name in ['scale_service_significance.py','scale_store_significance.py','scale_crowd_significance.py']:
 text=(R/'scripts'/name).read_text(encoding='utf-8-sig');body=text[text.index('source=(R/'):]
 real_exec(compile(body,name,'exec'),dict(R=R,unreal=UnrealStub(),__file__=str(R/'scripts'/name),exec=capture))
assert len(compiled)==3,compiled
for p in (R/'scripts').glob('*.py'):
 if any(key in p.name for key in ['optimization','significance','graphics','shader_warmup','static_lods','lod_scales','skeletal_lod_streaming']):ast.parse(p.read_text(encoding='utf-8-sig'),str(p))
print(json.dumps(dict(status='valid',generated_scripts=compiled),indent=2))
