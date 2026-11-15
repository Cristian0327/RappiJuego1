from pathlib import Path
s=(Path(__file__).parent/'build_cohesive_shops.py').read_text(encoding='utf-8');s=s.replace("for kind,label in enumerate(['Market','Restaurant','Tech','Pharmacy','Florist']):","for kind,label in enumerate(['Market','Restaurant','Tech','Pharmacy','Florist']):\n if kind!=1:continue");exec(compile(s,str(Path(__file__).parent/'build_cohesive_shops.py'),'exec'))
