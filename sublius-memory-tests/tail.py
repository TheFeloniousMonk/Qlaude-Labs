import numpy as np, os
os.environ['OPENBLAS_NUM_THREADS']='1'
def unit(a): return (a/np.linalg.norm(a,axis=-1,keepdims=True)).astype(np.float32)
def q12(a): return (np.round(a*2048)/2048).astype(np.float32)  # 12-bit signed grid -> exact products
def run(N, exact=False, pools=40, refs=5, seed=0):
    rng=np.random.default_rng(seed+N*10+exact)
    hits=np.zeros(N,int); trials=np.zeros(N,int)
    for _ in range(pools):
        M=unit(rng.standard_normal((N,384))); q=unit(rng.standard_normal(384))
        if exact: M=q12(M); q=q12(q)
        for r in rng.choice(N-4, refs, replace=False):
            for p in range(N):
                if p==r: continue
                X=M.copy(); X[p]=X[r]; s=X@q
                trials[p]+=1; hits[p]+= s[p]!=s[r]
    return hits,trials
for N,ex in [(85,False),(86,False),(85,True),(83,False)]:
    h,t=run(N,ex); hit_rows={i:int(h[i]) for i in range(N) if h[i]}
    print(f'N={N} exact={ex}: hit rows {hit_rows}  (trials per row ~{int(np.median(t))})')
