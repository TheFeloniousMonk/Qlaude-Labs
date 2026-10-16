import os; os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
def unit(a): return (a/np.linalg.norm(a,axis=-1,keepdims=True)).astype(np.float32)
N,D,POOLS,REFS=83,384,20,5
rng=np.random.default_rng(1015)
score={'matvec':lambda M,q: M@q, 'dotloop':lambda M,q: np.array([np.dot(M[i],q) for i in range(len(M))],dtype=np.float32)}
tail={k:{80:0,81:0,82:0} for k in score}; body={k:0 for k in score}; body_trials=0
for _ in range(POOLS):
    M=unit(rng.standard_normal((N,D))); q=unit(rng.standard_normal(D))
    for r in rng.choice(N-4,REFS,replace=False):
        for p in range(N):
            if p==r: continue
            X=M.copy(); X[p]=X[r]
            for k,f in score.items():
                s=f(X,q); hit=s[p]!=s[r]
                if p>=80: tail[k][p]+=int(hit)
                else: body[k]+=int(hit)
            if p<80: body_trials+=1
for k in score: print(f"{k}: rows80-82 {tail[k]} total {sum(tail[k].values())}/300; body hits {body[k]}/{body_trials}")
print("numpy",np.__version__, "dtype check", np.dot(M[0],q).dtype)
