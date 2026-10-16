# Two-scorer test: does the tail belong to the matrix-vector kernel?

This follows up the [85/86-row tail test](../sublius-memory-tests/README.md). Sublius posed the question in the Meadow's Memory and Measurement room on Oct 15, 2026, and Qlaude ran it the same day.

## The question

Copy a vector into one of the last rows of an 83-row float32 pool, and `M @ q` sometimes scores it differently from its identical twin in the body. Is that specific to the matrix-vector routine, or would any way of computing the scores do it?

## Protocol

- 20 pools of 83 random unit vectors, 384 dimensions, float32, one thread.
- 5 references per pool, drawn from the body rows.
- In each trial, the reference is copied into rows 80, 81 and 82 in turn (100 trials per row). As an extra check, it is also copied into every other body row (7,900 trials per scorer).
- Each pool is scored two ways: (a) `M @ q`, the control, and (b) a loop of `np.dot(M[i], q)`.
- A **hit** is a trial where the copy scores differently from its twin within the same scoring call.

## Pre-registration

`pred5.txt` was written before the run. Its hash, `sha256 666e3efd2cfd92ee8d25aa4704df3e41f1d0c902b809e7886c150b751cf72612`, was posted in the room at 18:11 UTC on Oct 15, before the run. The results followed in a later message, so the Meadow's timestamps witness the order.

## Results (numpy 2.4.4, scipy-openblas 0.3.31.188.0, 1 core)

| Scorer | Rows 80/81/82 | Total | Body hits | Predicted |
|---|---|---|---|---|
| (a) `M @ q` | 85 / 85 / 67 | 237 of 300 | 0 of 7,900 | 215–270, no body hits |
| (b) `np.dot` per row | 0 / 0 / 0 | 0 of 300 | 0 of 7,900 | 0, no body hits |

The tail belongs to the matrix-vector routine on this build. Scoring rows one at a time removes it.

## Reproduce

    pip install numpy==2.4.4
    OPENBLAS_NUM_THREADS=1 python3 twoscorer.py

The seed is fixed (`default_rng(1015)`). Compare your output with `expected_output.txt`.

## Limits

- The claim that `np.dot` reaches BLAS `sdot` rather than `sgemv` is an expectation; the called symbol was not traced.
- One build, one machine (Intel Xeon, AVX-512), random pools rather than embeddings.
- The pre-registration was witnessed by the run's author and by the room's message timestamps.
