import json,numpy as np
from pathlib import Path
from scipy.ndimage import gaussian_filter1d,map_coordinates
p=Path('compact_city/monserrate_path.json');d=json.loads(p.read_text());q=np.array(d['points']);raw=np.load('compact_city/original_terrain_heights_2m.npy')
for sig in [4,6,8,10,12,16]:
 xy=gaussian_filter1d(q[:,:2],sig,axis=0,mode='nearest');xy[:5]=q[:5,:2];xy[-5:]=q[-5:,:2];ds=np.linalg.norm(np.diff(xy,axis=0),axis=1);t=np.gradient(xy,axis=0);angles=np.unwrap(np.arctan2(t[:,1],t[:,0]));curv=abs(np.gradient(angles)/np.maximum(np.linalg.norm(t,axis=1),1e-6));radius=1/np.maximum(curv,1e-8);nat=map_coordinates(raw,[(xy[:,1]+50000)/200,(xy[:,0]+40000)/200],order=1);z=gaussian_filter1d(q[:,2],sig);z[0]=0
 for i in range(1,len(z)):z[i]=min(z[i],z[i-1]+.25*ds[i-1])
 for i in range(len(z)-2,-1,-1):z[i]=min(z[i],z[i+1]+.25*ds[i])
 print(sig,'radius1%',np.percentile(radius[20:-20],1)/100,'min',min(radius[20:-20])/100,'cut',max(abs(z-nat))/100,'length',sum(ds)/100)
