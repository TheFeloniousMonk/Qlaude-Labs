import os; os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
def unit(a): return (a/np.linalg.norm(a,axis=-1,keepdims=True)).astype(np.float32)
D,POOLS,REFS=384,20,5
for N in (84,87):
    rng=np.random.default_rng(1016*100+N)
    hits=np.zeros(N,int); trials=np.zeros(N,int)
    for _ in range(POOLS):
        M=unit(rng.standard_normal((N,D))); q=unit(rng.standard_normal(D))
        for r in rng.choice(N-4,REFS,replace=False):
            for p in range(N):
                if p==r: continue
                X=M.copy(); X[p]=X[r]; s=X@q
                trials[p]+=1; hits[p]+=int(s[p]!=s[r])
    tail=range(4*(N//4)-4 if N%4==0 else 4*(N//4), N) if N%4 else range(80,84)
    print(f"N={N}: tail rows {list(tail)} hits {[int(hits[i]) for i in tail]} of {[int(trials[i]) for i in tail]}; body hits {int(hits[:min(tail)].sum())}/{int(trials[:min(tail)].sum())}; any hit rows {[i for i in range(N) if hits[i]]}")
print("numpy",np.__version__)
