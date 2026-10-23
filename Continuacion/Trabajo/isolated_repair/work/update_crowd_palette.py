from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'work/build_street_crowd.py';s=p.read_text();exec(compile(s[:s.index('weightcode=')],str(p),'exec'),{'__file__':str(p)})
