#!/usr/bin/env python3
"""Run the ops/ci unittest suite across every CPU, so CI bills fewer minutes.

The suite takes about 5 minutes on one core. Two modules take three quarters of
that, so modules run in parallel processes and those slow ones are split per
test class or method. Each chunk is a separate `python -m unittest` process,
which keeps module state isolated exactly as in a serial run. Exits non-zero
if any chunk fails or if the chunk inventory misses a discovered test.
"""
import os
import re
import subprocess
import sys
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# The serial run imports modules alphabetically in one process, and earlier test
# modules add these roots to sys.path that later ones rely on. Give every chunk
# the same roots up front.
PATHS = [str(ROOT / 'web/scripts/pipeline'), str(HERE), str(ROOT / 'ops/evaluation'), str(ROOT / 'web/tests'), str(ROOT)]
sys.path[:0] = PATHS
ENV = dict(os.environ, PYTHONPATH=os.pathsep.join(PATHS + [p for p in [os.environ.get('PYTHONPATH')] if p]))
# Modules slow enough to split per test (measured seconds on one core, 2026-11-06).
SPLIT = {'test_cyera_primary_capture': 156, 'test_prnewswire_primary_capture': 71}


def tests_of(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from tests_of(item)
        else:
            yield item


def chunks():
    loader = unittest.TestLoader()
    suite = loader.discover(str(HERE), pattern='test_*.py', top_level_dir=str(HERE))
    ids, failures = [], []
    for test in tests_of(suite):
        ids.append(test.id())
        if type(test).__name__ in ('_FailedTest', 'ModuleImportFailure'):
            failures.append(test.id())
    if failures:
        raise SystemExit('Import failures: ' + ', '.join(failures))
    work = {}
    # A TestCase class imported into another test module is discovered twice with
    # the same id; running each module once still runs it, as the serial run does.
    ids = list(dict.fromkeys(ids))
    for test_id in ids:
        module = test_id.split('.')[0]
        key = test_id if module in SPLIT else module
        work.setdefault(key, []).append(test_id)
    # Slow modules first, so the long tail starts early.
    order = sorted(work, key=lambda k: (k.split('.')[0] not in SPLIT, k))
    return ids, [(key, work[key]) for key in order]


def run(chunk):
    key, test_ids = chunk
    started = time.monotonic()
    target = [key] if key.count('.') == 0 else test_ids
    result = subprocess.run([sys.executable, '-m', 'unittest', *target], cwd=ROOT, env=ENV,
                            capture_output=True, text=True)
    return key, result.returncode, result.stderr, time.monotonic() - started, len(test_ids)


def main():
    ids, work = chunks()
    assert sum(len(t) for _, t in work) == len(ids) == len(set(ids)), 'Chunk inventory differs from discovery'
    workers = int(os.environ.get('SUITE_WORKERS') or os.cpu_count() or 2)
    started = time.monotonic()
    failed, ran = [], 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for key, code, err, seconds, count in pool.map(run, work):
            print(f'{"ok  " if code == 0 else "FAIL"} {seconds:6.1f}s {count:4d} tests  {key}', flush=True)
            found = re.search(r'^Ran (\d+) tests? in', err, re.M)
            ran += int(found.group(1)) if found else 0
            if code != 0 or not found:
                failed.append(key)
                print(err[-20000:], flush=True)
    print(f'{ran} tests ran ({len(ids)} distinct) in {len(work)} chunks on {workers} workers, {time.monotonic() - started:.0f}s; '
          f'{len(failed)} chunks failed', flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
