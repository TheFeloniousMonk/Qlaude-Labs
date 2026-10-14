// replay-check.mjs: does a Molequle world replay bit for bit on this machine?
//
// Needs a checkout of Molequle v2.1.0 or later:
//   git clone --branch v2.1.0 https://github.com/TheFeloniousMonk/Molequle.git
//   node replay-check.mjs ./Molequle
//
// No npm install is needed: the simulation core and harness use only Node built-ins.
//
// Part 1. The single pow call from ori-z-mol-007, computed with the platform's
//         Math.pow and with Molequle's deterministic pow (dmath).
// Part 2. Physics version 2 (deterministic, the default since 2.1.0):
//         seed 23, cap 800, Smoother off, 5,000 ticks, hashed every tick and
//         compared to the golden trace shipped in the repo. Should PASS on every
//         Node version and platform.
// Part 3. Physics version 1 (native Math, Molequle before 2.1), same world, for
//         contrast. Its hashes are expected to depend on the Node version and
//         platform; we report them rather than judge them.

import path from 'path';
import os from 'os';
import { pathToFileURL } from 'url';

const root = path.resolve(process.argv[2] || './Molequle');
const imp = (p) => import(pathToFileURL(path.join(root, p)).href);
const H = await imp('tools/harness.mjs');
const dmath = await imp('client/js/dmath.js');

const bits = (x) => { const b = Buffer.alloc(8); b.writeDoubleBE(x); return b.toString('hex'); };
const out = (s = '') => console.log(s);

out(`node ${process.version} on ${process.platform} ${process.arch} (${os.cpus()[0]?.model ?? 'unknown cpu'})`);
out(`molequle ${root}`);
out(`simCodeSha256 ${H.codeInfo().simCodeSha256.slice(0, 16)}`);
out();

// Part 1
const x = 0.9500221141088014, y = 0.7;
out('Part 1: pow(0.9500221141088014, 0.7)');
out(`  Math.pow  (this platform) ${bits(Math.pow(x, y))}`);
out(`  dmath.pow (deterministic) ${bits(dmath.pow(x, y))}`);
out('  ori-z-mol-007 saw ...a2ff on Linux x64 and ...a2fe on Windows x64, both Node 24.15.0.');
out();

// Part 2
const CASE = 'seed23-cap800-smootherOff';
const golden = H.readGolden(CASE);
const sim2 = H.createWorld(golden.seed, golden.config, { keepEvents: false });
const h2 = H.trace(sim2, golden.ticks);
const at = H.firstDifference(h2, golden.hashes);
const show = [500, 3183, 5000];
out(`Part 2: physics 2, ${CASE}, ${golden.ticks} ticks`);
for (const t of show) out(`  tick ${String(t).padStart(4)}  ${h2[t - 1]}  golden ${golden.hashes[t - 1]}`);
out(at === -1
  ? `  PASS: all ${golden.ticks} tick hashes match the golden trace (made on ${golden.header.runtime}, ${golden.header.platform} ${golden.header.arch})`
  : `  FAIL: first differs at tick ${at + 1}`);
out();

// Part 3
const sim1 = H.createWorld(golden.seed, { ...golden.config, physicsVersion: 1 }, { keepEvents: false });
const h1 = H.trace(sim1, golden.ticks);
const d12 = H.firstDifference(h1, h2);
out('Part 3: physics 1 (native Math), same seed and settings');
for (const t of show) out(`  tick ${String(t).padStart(4)}  ${h1[t - 1]}`);
out(`  physics 1 and physics 2 first differ at tick ${d12 === -1 ? 'never' : d12 + 1} on this machine`);
process.exitCode = at === -1 ? 0 : 1;
