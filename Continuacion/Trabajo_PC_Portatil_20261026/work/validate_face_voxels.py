import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'work/build_street_crowd.py').read_text()
source=source[:source.index(' V,F,M,tags=emit(vox,U)')]
source+='''
 visible=[]
 for x in [-6,-5,4,5]:
  for z in [61,62]:
   cells=[(q[1],v[0]) for q,v in vox.items() if q[0]==x and q[2]==z]
   visible.append(min(cells)[1] if cells else 'hole')
 ear_gaps=[q for x in [-8,8] for z in range(61,65) if (q:=(x,-2,z)) not in vox]
 eye_whites=[]
 for a,b in [(-7,-3),(3,7)]:
  eye_whites.append(sum(min((q[1],v[0]) for q,v in vox.items() if q[0]==x and q[2]==62)[1]=='white' for x in range(a,b)))
 report.append({'name':s['name'],'visible_eye_pixels':visible,'ear_gaps':ear_gaps,'white_pixels_per_eye':eye_whites,'pass':all(m in ['white','eye'] for m in visible) and not ear_gaps and min(eye_whites)>=2})
'''
ns={'__file__':str(root/'work/build_street_crowd.py'),'report':[]}
exec(compile(source,'face-geometry-check','exec'),ns)
report=ns['report']
(root/'work/face_visibility_validation.json').write_text(json.dumps(report,indent=2))
print('VISIBLE_EYES',sum(r['pass'] for r in report),'/',len(report),flush=True)
assert all(r['pass'] for r in report)
