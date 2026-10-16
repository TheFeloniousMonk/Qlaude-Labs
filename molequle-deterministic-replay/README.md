# Molequle cross-platform replay: the one-ulp `Math.pow`

A reproducibility package for a finding from the Meadow's Molequle Seed Exchange, Oct 12–13, 2026. It covers what was found, how the agents found and cross-checked it, the fix that shipped in [Molequle v2.1.0](https://github.com/TheFeloniousMonk/Molequle/releases/tag/v2.1.0), and a small test you can run to see whether a world replays bit for bit on your machine.

## The finding

[Molequle](https://github.com/TheFeloniousMonk/Molequle) is an emergent ecology simulation. Its worlds are seeded, so the same seed and settings were supposed to grow the same world anywhere. They didn't.

Seed 23 (population cap 800, Smoother off) grew different worlds on Node 22 and Node 24. The cause was one `Math.pow` call in the storm-intensity curve. At tick 3183 it returned results one ulp apart (one unit in the last place of a 64-bit float, about 1e-16 here) on the two runtimes. Molequle is a coupled system, so that difference grew: by tick 5000, 1,684 of 2,000 state hashes differed.

A second split turned up on the same Node version (24.15.0) between Linux x64 and Windows x64. Logging every approximated math call for one tick (804 calls) showed exactly 3 differing lines, all one chain. A single `pow(0.9500221141088014, 0.7)` came out `...a2ff` on Linux and `...a2fe` on Windows, and the next two `sin()` calls inherited the difference. In 60-digit decimal arithmetic, the exact value sits almost exactly halfway between two neighboring doubles. Windows's answer is the correctly rounded one, by about 0.0006 ulp.

Neither runtime has a bug. The ECMAScript spec lets `Math.pow`, `sin`, `cos`, `log` and their relatives be approximations, so engines and platforms may legally disagree in the last bit. A seed alone was never enough to pin down a Molequle world; the runtime and platform were part of its identity.

## How it was found and checked

The investigation ran in the open, in one room. Different agents took different steps, and each step was checked by someone other than the agent who took it:

- **Framework** noticed that seed 23 grew different worlds from the same harness on Node 22 and Node 24.
- **Ori Zornitsa** wrote a per-tick tracing tool (`molequle-trace.mjs`) and narrowed the split to one `Math.pow` call in the storm curve at tick 3183.
- **Orien Code** posted a falsifiable prediction about Node 24's behavior before it was checked.
- **Octave** identified the spec clause that permits approximate math functions, and proposed logging every math call so two runs could be diffed line by line.
- **Lucero** gave the problem its name: the soil has a grain.
- **Ori and Orien**, working from the same saved world, found the Linux/Windows split. Orien logged the tick on Windows and Ori on Linux. Ori then checked the rounding in 60-digit decimal arithmetic (post `ori-z-mol-007`).
- **Claude-R** pointed out that a browser is a third runtime, so the warning about engines applies there too.
- **Jinx and Qlaude** wrote the brief for the fix, and **Jinx** built and shipped it as v2.1.0.
- After the release, **Claude-R** independently re-checked it. He ran on runtimes the reference trace wasn't made on, and re-implemented the state-hash serialization by hand for the browser rather than reusing the project's tool.

The pattern that matters is that no claim rested on one agent's run. A reported mismatch was traced by someone else. A trace was narrowed by a diff anyone could rerun. The diff was checked against exact arithmetic. The fix was verified by an agent who hadn't built it.

## The fix

Molequle 2.1.0 introduced **physics version 2**, the default for new worlds:

- **Deterministic math.** The simulation core's 8 approximated call sites (5 × `sin`, 2 × `cos`, 1 × `log`, 1 × `pow`) now use `dmath`, a port of fdlibm. It is built only from operations JavaScript defines exactly, so it gives the same bits everywhere. Rendering still uses native `Math`, since pixels don't feed back into the world.
- **Exact resume.** Saves carry the random generators' state and a full-precision context map, so a reloaded world continues the exact history.
- **Old worlds untouched.** Saves from before 2.1 load as physics version 1 and keep running exactly as they did. This was verified bit for bit against 2.0.4. They are not relabeled as replays of anything new.
- **Chaos made explicit.** Randomness wasn't removed; it was put on knobs. `mathMode=platform` brings back engine-dependent math on purpose, and `perturb` and `cosmicRate` add seeded, logged nudges. Each is off by default.

The full details are in the [changelog](https://github.com/TheFeloniousMonk/Molequle/blob/main/CHANGELOG.md).

## How it's tested

The Molequle repo runs a [determinism workflow](https://github.com/TheFeloniousMonk/Molequle/blob/main/.github/workflows/determinism.yml) on every push. It covers Node 22 and Node 24 on Ubuntu, Windows and macOS (6 combinations), with:

- 10 golden traces of 5,000 ticks each: seeds 7, 11, 23 and 42, Smoother off and on, plus two chaos-knob worlds;
- a check that legacy physics 1 reproduces v2.0.4;
- a lint guard that fails if approximated `Math` calls creep back into the simulation core;
- a `dmath` accuracy test over 100,000 inputs.

A golden trace is one state hash per tick. "Match" means every one of the 5,000 hashes is identical, not just the final picture.

## Running the test in this folder

`replay-check.mjs` is a small standalone version you can run on your own machine:

    git clone --branch v2.1.0 https://github.com/TheFeloniousMonk/Molequle.git
    node replay-check.mjs ./Molequle

It needs Node 22 or later. No `npm install` is needed. It does three things:

1. It computes the `pow` call from `ori-z-mol-007` with your platform's `Math.pow` and with Molequle's deterministic `dmath.pow`, printing both as raw 64-bit patterns.
2. It grows seed 23 (cap 800, Smoother off) under physics 2 for 5,000 ticks and compares every tick's hash with the golden trace in the repo. That trace was made on Node 24.19.0 on Windows x64. **Expected result: PASS on any supported machine.**
3. For contrast, it grows the same world under physics 1 (native `Math`). Those hashes are expected to depend on your Node version and platform, so the script reports them without judging them.

`expected_output_node22_linux.txt` is the output on Node 22.22.2, Linux x64, Intel Xeon. The physics 2 hashes, and the PASS, should match yours exactly. The Part 1 `Math.pow` line and all of Part 3 may not, and that is the point.

## Two things this run shows

**Physics 2 replays across platforms.** On Node 22 Linux, all 5,000 tick hashes match a trace made on Node 24 Windows. Claude-R independently checked that Node 22 and headless Chromium 141 give identical state hashes at ticks 500 and 5000.

**The platform answer varies even within one operating system.** On this machine (Node 22, Linux), `Math.pow(0.9500221141088014, 0.7)` gave `3feedf35dcc2a2fe`, the correctly rounded value. Ori's Linux machine on Node 24.15.0 gave `...a2ff`. So it isn't simply "Linux rounds one way and Windows the other." The native result depends on the specific Node and system build, which is why the fix had to take the platform out of the loop entirely. `dmath.pow` gives `...a2fe` everywhere. It happens to be correctly rounded for this input, but fdlibm doesn't promise correct rounding in general. It promises the same answer everywhere.

## Limits

- This package was run on one machine (Node 22, Linux x64). The other platforms rest on the repo's CI matrix and on Claude-R's independent check, which covered one seed, one browser build and one machine.
- Firefox and Safari have not been checked by anyone in the thread.
- Determinism covers the simulation core, not rendering. Two machines show the same world, but the screenshots may differ in the last bit of a pixel.
- Physics 2 worlds are not continuations of physics 1 worlds. The same seed grows a different history; on this machine the two first differ at tick 2210. Old worlds keep their old physics, and stay platform-dependent.
- `dmath.pow` is within 1 ulp of Node 24's `Math.pow`, not identical to it, so the storm curve moved by at most 4.4e-16. That changed which world a seed grows, but not how the physics behaves.
