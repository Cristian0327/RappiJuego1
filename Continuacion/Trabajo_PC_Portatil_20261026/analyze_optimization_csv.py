from pathlib import Path
import csv,json,statistics,sys,math
p=Path(sys.argv[1]);rows=list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
# UE appends a repeated header and metadata. Only real frame rows contribute.
def is_frame(row):
 try:return math.isfinite(float(row.get('FrameTime',''))) and float(row['FrameTime'])>0 and not str(next(iter(row.values()),'')).startswith('[')
 except (ValueError,TypeError):return False
rows=[row for row in rows if is_frame(row)]
def values(name):
 out=[]
 for row in rows:
  try:
   value=float(row.get(name,''))
   if math.isfinite(value) and value>0:out.append(value)
  except (ValueError,TypeError):pass
 return out
times=values('FrameTime');assert times,'No FrameTime samples in '+str(p)
ordered=sorted(times)
def percentile(q):return ordered[min(len(ordered)-1,int((len(ordered)-1)*q))]
report=dict(csv=str(p.resolve()),frames=len(times),mean_ms=statistics.mean(times),mean_fps=1000/statistics.mean(times),p50_ms=percentile(.5),p95_ms=percentile(.95),p99_ms=percentile(.99),one_percent_low_fps=1000/percentile(.99),worst_ms=max(times),frames_over_16_667ms=sum(t>1000/60 for t in times),frames_over_33_333ms=sum(t>1000/30 for t in times),one_percent_low_at_least_60=percentile(.99)<=1000/60,all_sampled_frames_at_least_60=max(times)<=1000/60,stats={})
for name in ['GameThreadTime','RenderThreadTime','RHIThreadTime','Exclusive/GameThread/TickActors','Exclusive/GameThread/CharacterMovement','Exclusive/GameThread/UI']:
 data=values(name)
 if data:report['stats'][name]=statistics.mean(data)
report['stats_unit']='milliseconds'
report['gpu_timing_note']='GPUTime excluded: DX11 driver timestamps in this capture exceed wall frame time and are not reliable for bottleneck attribution.'
out=p.with_name(p.stem+'_analysis.json');out.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
