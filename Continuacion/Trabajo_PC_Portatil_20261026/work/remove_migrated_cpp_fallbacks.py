from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[1]
src=root/'RappiJuego1/Source/BogotaVoxel'
audit=json.loads((root/'work/blueprint_audit.json').read_text())
coverage={a['parent'].split('.')[-1]:{g['name'] for g in a['graphs']} for a in audit}
pattern=re.compile(r'(?:^|(?<=\}))\s*(?:[\w:<>,*&]+\s+)+(\w+)::(\w+)_Implementation\s*\([^)]*\)\s*(?:const\s*)?\{',re.M)
removed=[];total=0
for p in src.glob('*.cpp'):
 text=p.read_text(encoding='utf-8-sig');ranges=[]
 for m in pattern.finditer(text):
  cls,name=m.group(1,2);assert name in coverage.get(cls[1:],set()),(cls,name)
  i=m.end();depth=1;state='code'
  while depth:
   c=text[i];n=text[i:i+2]
   if state=='code':
    if n=='//':state='line';i+=2;continue
    if n=='/*':state='comment';i+=2;continue
    if c=='"':state='string'
    elif c=="'":state='char'
    elif c=='{':depth+=1
    elif c=='}':depth-=1
   elif state=='line':
    if c=='\n':state='code'
   elif state=='comment':
    if n=='*/':state='code';i+=2;continue
   else:
    if c=='\\':i+=2;continue
    if (state=='string' and c=='"') or (state=='char' and c=="'"):state='code'
   i+=1
  ranges.append((m.start(),i));removed.append({'class':cls,'function':name,'bytes':i-m.start()})
 for start,end in reversed(ranges):text=text[:start]+'\n'+text[end:]
 if ranges:p.write_text(text,encoding='utf-8');total+=len(ranges)
assert total==93,total
for p in src.glob('*.h'):
 text=p.read_text(encoding='utf-8-sig').replace('BlueprintNativeEvent','BlueprintImplementableEvent')
 text=re.sub(r'^\s*virtual (?:bool|void) (?:CanDeliver|ReceiveDelivery)_Implementation\([^;]+;\n','\n',text,flags=re.M)
 p.write_text(text,encoding='utf-8')
(root/'work/cpp_fallbacks_removed.json').write_text(json.dumps({'functions':total,'bytes':sum(x['bytes'] for x in removed),'removed':removed},indent=2))
print(total,'duplicate C++ implementations removed,',sum(x['bytes'] for x in removed),'bytes')
