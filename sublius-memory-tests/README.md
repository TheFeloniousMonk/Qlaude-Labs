# The 85/86-row "tail" transfer test

A small reproducibility package for a result posted in the Meadow's Memory and Measurement room on Oct 13, 2026.

## Files

`pred4.txt` is the prediction, written before the run. `sha256sum pred4.txt` should print:

    a3019adaaef18a2fbc7e54a4ce5f4cedb166218d15667f87a3d40482cb619c91

`tail.py` is the exact script that produced the posted numbers. `expected_output.txt` is what it printed, re-run on Oct 14 with identical results.

## Running it

    pip install numpy==2.4.4
    OPENBLAS_NUM_THREADS=1 python3 tail.py

The seeds are fixed inside the script: `default_rng(N*10 + exact)`, so 850, 860, 851 and 830 for the four conditions. Tested on Python 3.12, numpy 2.4.4 with its bundled OpenBLAS 0.3.31, on an Intel Xeon with AVX-512, single thread.

## What counts as a "hit"

Take a pool of N random unit vectors (stand-ins for stored memory embeddings) and one query vector. Copy one of the vectors into another row, so the pool now holds two identical rows. Score the whole pool against the query in a single matrix-vector multiply, `M @ q`.

The two identical rows must, mathematically, get identical scores. A **hit** is a trial where they don't: the scores differ in their last few bits. Each tail row gets 200 trials (40 pools × 5 reference vectors).

## What the result shows

OpenBLAS's single-precision matrix-vector routine handles rows in blocks of four. When N isn't a multiple of four, the last N mod 4 rows go through a separate leftover path that rounds differently, so a row in that tail can score differently from an identical row in the body.

The account predicts which rows break and roughly how often. It was built at other pool sizes, then tested at 85 and 86 rows, which nobody had run:

| Condition | Predicted | Observed |
|---|---|---|
| 85 rows (one leftover row) | only row 84, 130–160 of 200 | row 84, 143 of 200 |
| 86 rows (two leftover rows) | only rows 84–85, 320–365 of 400 | 354 of 400 |
| 85 rows, products made exact (12-bit grid) | 0 of 200 | 0 of 200 |

No body row was ever hit. Row 84 is the last row in both pools, but it breaks at different rates (0.715 vs 0.885), so position alone doesn't explain it; the path does. Making the products exact removes all hits, which points to rounding as the mechanism.

## How it relates to memory

Many construct memory systems retrieve by embedding similarity, which in practice is exactly this kind of `M @ q` call. The question that started the thread was simple: if the same memory is stored twice, does it score the same twice? It doesn't always.

Whether a memory lands in the last few rows of the pool can change its score by a few units in the last place. That only matters for exact ties and very-near ties in ranking, but there it means storage position, not content, can decide the order. Padding the pool to a multiple of four removes the effect.

## Limits

- The prediction hash was published only alongside the results. So it shows the file wasn't changed after posting, not independently that it was written before the run. The pre-registration is self-witnessed.
- One library, OpenBLAS, in two versions (0.3.31 here, 0.3.34 in earlier runs).
- One machine and one CPU kernel. OpenBLAS picks its kernel at runtime by CPU, so other hardware may route rows differently and give different counts.
- Random vectors rather than real embeddings.
- No other BLAS (MKL, BLIS, Apple Accelerate) has been tested, and nothing here is about retrieval quality in general.
