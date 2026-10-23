import json,math,numpy as np
from scipy.spatial import cKDTree
m=json.load(open('new_map_audit/before_spacing_expansion/manifest.json'));r=np.array(m['roads'][0]['center'])*[100,-100,100];h=np.array(m['roads'][0]['halfwidth'])*100;x=json.load(open('new_map_audit/spacing_expansion_flat.json'));aa,bb=np.meshgrid(np.arange(-1300,1301,200),np.arange(-1700,1701,200));best=[]
def overlap(a,b):
 ax=np.array(a['store_axes']);bx=np.array(b['store_axes']);delta=np.array(a['center'][:2])-b['center'][:2]
 for v in [*ax,*bx]:
  lim=sum(abs(v@w)*d for w,d in zip(ax,[1300,1700]))+sum(abs(v@w)*d for w,d in zip(bx,[1300,1700]))
  if abs(delta@v)>lim:return False
 return True
for f in sorted(set(s['factor'] for s in x)):
 tree=cKDTree(r[:,:2]*f);raw=[]
 for s in x:
  if s['factor']!=f:continue
  ds,i=tree.query(s['center'][:2])
  if ds<h[i]+1100:continue
  back=np.array(s['center'][:2])-r[i,:2]*f;back/=np.linalg.norm(back)
  for mode in [0,1]:
   by=back if mode==0 else np.array([back[1],-back[0]]);bx=np.array([by[1],-by[0]]);q=np.array(s['center'][:2])+aa[:,:,None]*bx+bb[:,:,None]*by;ds,ii=tree.query(q.reshape(-1,2))
   if np.any(ds<h[ii]+50):continue
   z=s.copy();z['road_index']=int(i);z['store_axes']=[bx.tolist(),by.tolist()];raw.append(z)
 sel=[]
 while raw:
  a=max(raw,key=lambda s:min([math.dist(s['center'][:2],v['center'][:2]) for v in sel],default=1e6));sel.append(a);raw=[s for s in raw if not overlap(a,s)]
 print('RECT_ROAD_CLEAR',f,len(sel))
 if len(sel)>=20:json.dump({'factor':f,'shops':sel[:20]},open('new_map_audit/spacing_expansion_selected.json','w'));break
