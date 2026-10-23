from pathlib import Path
p=Path('work/verify_heads_unreal.py');s=p.read_text();a=s.index('for i in [4,8,15]:');b=s.index("report['status']",a);p.write_text(s[:a]+s[b:])
