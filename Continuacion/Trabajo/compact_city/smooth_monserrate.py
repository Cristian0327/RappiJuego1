import json,numpy as np,sys
from pathlib import Path
from scipy.ndimage import gaussian_filter1d,map_coordinates,distance_transform_edt
from scipy.spatial import cKDTree
from PIL import Image
C=Path('compact_city');path=C/'monserrate_path.json';d=json.loads(path.read_text());orig=np.array(d['points']);q=gaussian_filter1d(orig[:,:2],16,axis=0,mode='nearest');n=len(q);w=np.arange(n);q+=(orig[0,:2]-q[0])*np.exp(-w[:,None]/20);q+=(orig[-1,:2]-q[-1])*np.exp(-(n-1-w)[:,None]/20)
arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))];s=np.r_[np.arange(0,arc[-1],50),arc[-1]];xy=np.column_stack([np.interp(s,arc,q[:,i]) for i in range(2)]);z=np.interp(s,arc,gaussian_filter1d(orig[:,2],16));ds=np.linalg.norm(np.diff(xy,axis=0),axis=1);z[0]=0
for i in range(1,len(z)):z[i]=min(z[i],z[i-1]+.25*ds[i-1])
for i in range(len(z)-2,-1,-1):z[i]=min(z[i],z[i+1]+.25*ds[i])
raw=np.load(C/'original_terrain_heights_2m.npy');nat=map_coordinates(raw,[(xy[:,1]+50000)/200,(xy[:,0]+40000)/200],order=1);t=np.gradient(xy,axis=0);angles=np.unwrap(np.arctan2(t[:,1],t[:,0]));radius=1/np.maximum(abs(np.gradient(angles)/np.maximum(np.linalg.norm(t,axis=1),1e-6)),1e-8);pairs=cKDTree(xy).query_pairs(300);conflicts=[(a,b) for a,b in pairs if abs(s[a]-s[b])>2000];assert not conflicts,conflicts[:5]
d.update(points=np.column_stack([xy,z]).tolist(),base=[*xy[0],float(z[0])],summit=[*xy[-1],float(z[-1])],length_m=float(sum(ds)/100),maximum_grade=float(max(abs(np.diff(z))/np.maximum(ds,.001))),minimum_turn_radius_m=float(min(radius[15:-15])/100),maximum_cut_fill_m=float(max(abs(z-nat))/100),width_cm=300,player_allowed=['walk','bicycle','motorcycle'],npc_vehicles_allowed=False,cars_allowed=False)
assert d['maximum_grade']<.251 and d['maximum_cut_fill_m']<2;path.write_text(json.dumps(d,indent=2));print({k:v for k,v in d.items() if k!='points'})
