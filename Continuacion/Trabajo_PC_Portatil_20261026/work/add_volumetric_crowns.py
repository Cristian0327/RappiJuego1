from pathlib import Path
p=Path('work/build_street_crowd.py');s=p.read_text();needle=" if hair=='beard' or s['age']>65:";assert needle in s
insert=""" # A stepped crown replaces the flat cylindrical hair silhouette.
 if hair not in ['cap','flatcap','beanie','hood','helmet','bald']:
  crown=74+(i%3) if hair!='curls' else 77+(i%2)
  for z in range(69,crown):
   t=(z-69)/max(1,crown-69)
   rx=9*math.sqrt(max(.05,1-t*t));ry=8*math.sqrt(max(.05,1-t*t))
   oval('Volumetric crown','hair_light' if z>=crown-2 else 'hair',z,z+1,rx,ry,cx=(i%3-1)*.6,cy=1)
  # A small offset lock gives each silhouette a visible part and asymmetry.
  oval('Crown lock','hair_light',crown-2,crown+1,2.5,3,cx=2 if i%2 else -2,cy=0)
 elif hair=='bald':
  for z,rx,ry in [(69,7,6),(70,5,4),(71,3,2)]:oval('Rounded scalp','skin',z,z+1,rx,ry,cy=1)
 if hair in ['cap','flatcap','beanie','hood','helmet']:
  hatpart=parts['Hat']
  for q in list(hatpart):
   x,y,z=q
   if z>=top-4:
    t=(z-(top-4))/4;rx=10*math.sqrt(max(.10,1-t*t));ry=9*math.sqrt(max(.10,1-t*t))
    if ((x+.5)/rx)**2+((y+.5-1)/ry)**2>1:del hatpart[q]
"""
s=s.replace(needle,insert+needle);p.write_text(s)
