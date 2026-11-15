from pathlib import Path
p=Path('work/build_complete_sky.py');s=p.read_text();a=s.index('float2 cloudUV=');z=s.index('float2 starCell=',a)
s=s[:a]+'''float2 cloudUV=floor((d.xy/max(.18,d.z+.16)*3+float2(CloudTime*.004,CloudTime*.0015))*12)/12;
float2 cell=floor(cloudUV),f=frac(cloudUV);f=f*f*(3-2*f);
float n00=frac(sin(dot(cell,float2(127.1,311.7)))*43758.5453);
float n10=frac(sin(dot(cell+float2(1,0),float2(127.1,311.7)))*43758.5453);
float n01=frac(sin(dot(cell+float2(0,1),float2(127.1,311.7)))*43758.5453);
float n11=frac(sin(dot(cell+float2(1,1),float2(127.1,311.7)))*43758.5453);
float noise=lerp(lerp(n00,n10,f.x),lerp(n01,n11,f.x),f.y);
float cloud=step(.63,noise)*smoothstep(.03,.16,d.z);
float shade=saturate((noise-.63)*3.5);
float3 cloudDay=lerp(float3(.56,.67,.8),float3(.95,.97,1),shade);
color=lerp(color,lerp(float3(.025,.035,.075),cloudDay,Daylight),cloud*.92);
'''+s[z:];p.write_text(s)
