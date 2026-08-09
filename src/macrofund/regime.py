from __future__ import annotations
import numpy as np, pandas as pd
FEATURES=["growth","inflation","liquidity","risk"]

def _kmeans(x:np.ndarray,k:int=4,seed:int=42,n_init:int=6,max_iter:int=80):
    if len(x)<k: raise ValueError("Need at least k observations")
    best=None; best_inertia=np.inf; rng=np.random.default_rng(seed)
    for _ in range(n_init):
        centers=[x[rng.integers(0,len(x))]]
        while len(centers)<k:
            d2=np.min(np.stack([np.sum((x-c)**2,axis=1) for c in centers],axis=1),axis=1); total=float(d2.sum())
            centers.append(x[rng.integers(0,len(x))] if total<=0 else x[rng.choice(len(x),p=d2/total)])
        centers=np.asarray(centers,float); labels=np.zeros(len(x),dtype=int)
        for _ in range(max_iter):
            dist=np.sum((x[:,None,:]-centers[None,:,:])**2,axis=2); new_labels=dist.argmin(axis=1); new_centers=centers.copy()
            for j in range(k):
                members=x[new_labels==j]
                if len(members): new_centers[j]=members.mean(axis=0)
            if np.array_equal(new_labels,labels) and np.allclose(new_centers,centers): labels=new_labels; centers=new_centers; break
            labels,centers=new_labels,new_centers
        inertia=float(np.sum((x-centers[labels])**2))
        if inertia<best_inertia: best_inertia=inertia; best=(centers,labels)
    return best

def semantic_regime(growth:float,inflation:float)->str:
    if growth>=0 and inflation<0:return "Goldilocks"
    if growth>=0 and inflation>=0:return "Reflation"
    if growth<0 and inflation>=0:return "Stagflation"
    return "Deflation"

def expanding_regimes(features:pd.DataFrame,warmup:int=60,k:int=4,refit_every:int=3)->pd.DataFrame:
    clean=features[FEATURES].dropna().copy(); result=pd.DataFrame(index=clean.index,columns=["cluster","confidence","regime"]); centers=None
    for i in range(len(clean)):
        row=clean.iloc[i].to_numpy(float)
        if i<warmup: result.iloc[i]=[np.nan,np.nan,semantic_regime(row[0],row[1])]; continue
        if centers is None or (i-warmup)%refit_every==0: centers,_=_kmeans(clean.iloc[:i+1].to_numpy(float),k=k)
        d=np.sqrt(np.sum((centers-row)**2,axis=1)); order=np.argsort(d); nearest,second=float(d[order[0]]),float(d[order[1]])
        conf=float(np.clip(1-nearest/(second+1e-9),0,1)); result.iloc[i]=[int(order[0]),conf,semantic_regime(row[0],row[1])]
    result["cluster"]=pd.to_numeric(result["cluster"],errors="coerce"); result["confidence"]=pd.to_numeric(result["confidence"],errors="coerce"); return result

def current_regime(features:pd.DataFrame,regimes:pd.DataFrame)->dict:
    valid=features[FEATURES].dropna(); date=valid.index[-1]; reg=regimes.reindex(valid.index).loc[date]; row=valid.loc[date]
    return {"date":date.strftime("%Y-%m-%d"),"regime":str(reg["regime"]),"cluster":None if pd.isna(reg["cluster"]) else int(reg["cluster"]),"confidence":None if pd.isna(reg["confidence"]) else round(float(reg["confidence"]),4),"growth":round(float(row["growth"]),3),"inflation":round(float(row["inflation"]),3),"liquidity":round(float(row["liquidity"]),3),"risk":round(float(row["risk"]),3)}
