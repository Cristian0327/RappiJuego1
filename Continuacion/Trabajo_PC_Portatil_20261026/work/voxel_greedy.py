from collections import defaultdict

def emit(vox,q):
    layers=defaultdict(set)
    for p,(mat,bone) in vox.items():
        for axis in range(3):
            for sign in [-1,1]:
                n=list(p);n[axis]+=sign
                other=vox.get(tuple(n))
                if other and other[1]==bone:continue
                uv=[a for a in range(3) if a!=axis]
                layers[(axis,sign,p[axis]+(sign>0),mat,bone)].add((p[uv[0]],p[uv[1]]))
    V=[];F=[];M=[];B=[]
    for (axis,sign,plane,mat,bone),cells in layers.items():
        uv=[a for a in range(3) if a!=axis]
        while cells:
            u,v=min(cells);w=1
            while (u+w,v) in cells:w+=1
            h=1
            while all((u+i,v+h) in cells for i in range(w)):h+=1
            for j in range(h):
                for i in range(w):cells.remove((u+i,v+j))
            points=[]
            for a,b in [(u,v),(u+w,v),(u+w,v+h),(u,v+h)]:
                p=[0,0,0];p[axis]=plane*q;p[uv[0]]=a*q;p[uv[1]]=b*q;points.append(tuple(p))
            # u cross v points positive X, negative Y, positive Z.
            if sign != (1 if axis!=1 else -1):points.reverse()
            first=len(V);V.extend(points);F.append(tuple(range(first,first+4)));M.append(mat);B.extend([bone]*4)
    return V,F,M,B
