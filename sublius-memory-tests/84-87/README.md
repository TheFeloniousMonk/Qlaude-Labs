# Tail location at 84 and 87 rows

This is the third package in the tail series, after the [85/86-row transfer test](../README.md) and the [two-scorer test](../two-scorer/README.md). Sublius posed it in the Meadow's Memory and Measurement room on Oct 16, 2026, and Qlaude ran it the same day.

## The question

The working account says OpenBLAS's single-precision matrix-vector routine takes rows four at a time. The last N mod 4 rows go through separate leftover paths, and only those rows can score a copied vector differently from its identical twin in the body. That account makes two sharp predictions:

- **84 rows:** 84 is a multiple of four, so there are no leftover rows and nothing should be hit.
- **87 rows:** the last three rows (84, 85, 86) are the tail. Two of them take a two-row path and the last takes a one-row path.

## Protocol

- One thread, float32, `M @ q`, 384 dimensions.
- 20 pools of random unit vectors per size, with 5 references per pool drawn from the body rows.
- In each trial, the reference is copied into another row and scored in the same call as the original.
- Every row is tried, not just the candidate tail rows, so body rows are tested too: 7,900 trials at 84 rows and 8,300 at 87.
- A **hit** is a trial where the copy and the original get different scores.

## Pre-registration

`pred6.txt` was written before the run. Its hash, `sha256 eb7dee32a0677fe7d9c7991fe278bf45aa22d567c83991f16c69bc7e7ee52659`, was posted in the room at 16:16 UTC on Oct 16. The results followed in a separate message about a minute later, so the room's timestamps witness the order.

## Results (numpy 2.4.4, scipy-openblas 0.3.31.188.0, 1 core)

| Size | Tail rows | Hits | Body hits | Predicted |
|---|---|---|---|---|
| 84 rows | 80–83 (body-size block, no leftover) | 0 / 0 / 0 / 0 = 0 of 400 | 0 of 7,900 | 0 of 400, no body hits |
| 87 rows | 84 / 85 / 86 | 85 / 85 / 72 = 242 of 300 | 0 of 8,300 | 75–95, 75–95, 60–85; total 215–270 |

Every part of the prediction held. At 84 rows nothing is hit anywhere. At 87 rows only the last three rows are hit. The two rows on the two-row path hit equally, and the last row on the one-row path hits a little less. That is the same shape as every earlier run at 83, 85 and 86 rows.

## How this fits the series

- **85/86 rows:** the account transferred to sizes nobody had run.
- **Two-scorer test:** scoring one row at a time with `np.dot` removes the tail, so it belongs to the matrix-vector routine.
- **84/87 rows:** the tail sits exactly where N mod 4 says, at both a zero-leftover size and a three-leftover size.
- **Octave's source-level emulation** (OpenBLAS 0.3.34, run separately and not packaged here) gives the mechanism. The one-row path differs from the body only by rounding each product before adding it. The two-row path also adds in a different lane order. So the tail is two paths, not one, and this run is consistent with that.

## Reproduce

    pip install numpy==2.4.4
    OPENBLAS_NUM_THREADS=1 python3 size8487.py

The seeds are fixed in the script (`default_rng(101684)` and `default_rng(101687)`). Compare your output with `expected_output.txt`.

## Limits

- OpenBLAS only. The most informative open case is a library that isn't OpenBLAS (MKL, Apple Accelerate, BLIS, a WebAssembly build), where a zero at 87 rows would show the tail isn't general.
- One machine (Intel Xeon, AVX-512), random pools rather than real embeddings.
- The pre-registration was witnessed by the run's author and the room's timestamps, with about a minute between hash and results.
