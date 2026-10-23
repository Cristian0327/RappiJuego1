import csv,collections,json
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/work');p=r/'PureBlueprintCPU.csv'
with p.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.DictReader(f);print('HEADERS',rd.fieldnames)
 rows=0;end=0
 for row in rd:
  rows+=1;end=max(end,float(row['EndTime']))
window=(max(0,end-18),end-4);totals=collections.defaultdict(lambda:[0.,0.,0]);stack=[]
def flush():
 n,d,ch=stack.pop();totals[n][0]+=d;totals[n][1]+=max(0,d-ch);totals[n][2]+=1
with p.open(encoding='utf-8-sig',newline='') as f:
 for row in csv.DictReader(f):
  s=float(row['StartTime']);e=float(row['EndTime']);duration=max(0,min(e,window[1])-max(s,window[0]));depth=int(row['Depth'])
  if duration<=0:continue
  while len(stack)>depth:flush()
  if stack:stack[-1][2]+=duration
  stack.append([row['TimerName'],duration,0.])
while stack:flush()
out={'rows':rows,'window':window,'exclusive':sorted(([n,*v] for n,v in totals.items()),key=lambda x:x[2],reverse=True)[:55],'inclusive_blueprint':sorted(([n,*v] for n,v in totals.items() if 'BP_' in n or 'Blueprint' in n or 'EventGraph' in n),key=lambda x:x[1],reverse=True)[:55]};(r/'pure_blueprint_cpu_analysis.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
