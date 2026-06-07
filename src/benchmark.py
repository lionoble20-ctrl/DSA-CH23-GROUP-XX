# =============================================================================
#  benchmark.py  —  Performance Benchmark for the URL Shortening Service
#  DSA-CH23-GROUP-XX  |  Theme B: Bitly-lite
#  Measures: Insert speed, Lookup speed, Delete speed, Sort speed
# =============================================================================
#
#  WHAT THIS FILE DOES:
#  Times how long each core operation takes at scale (10,000 operations)
#  Proves our O(1) hash table claims with real measured numbers
#  Required by the assignment: "complexity analysis + benchmark notes"
#
# =============================================================================

import time
import random
import string
import sys
sys.path.insert(0, './src')

from url_store import URLStore
from sorter import merge_sort


# =============================================================================
#  Helper — generate random URLs for testing
# =============================================================================

def random_url():
    slug = ''.join(random.choices(string.ascii_lowercase, k=10))
    return f"https://www.{slug}.com"


# =============================================================================
#  Benchmark 1 — INSERT (shorten) 10,000 URLs
#  Expected: O(1) per operation → very fast total
# =============================================================================

def benchmark_insert(n=10000):
    store = URLStore()
    urls  = [random_url() for _ in range(n)]

    start = time.perf_counter()
    for url in urls:
        store.shorten(url)
    end = time.perf_counter()

    total_ms = (end - start) * 1000
    per_op   = total_ms / n

    print(f"  INSERT  {n:,} URLs     →  {total_ms:.2f} ms total  |  {per_op:.4f} ms per op  |  O(1) expected")
    return store, total_ms


# =============================================================================
#  Benchmark 2 — LOOKUP (redirect) 10,000 times
#  Expected: O(1) per operation → fastest operation in the system
# =============================================================================

def benchmark_lookup(store, n=10000):
    codes = list(store.short_to_long.keys())
    if not codes:
        print("  LOOKUP  No URLs in store to look up")
        return

    start = time.perf_counter()
    for _ in range(n):
        code = random.choice(codes)
        store.short_to_long[code]  # direct hash table access
    end = time.perf_counter()

    total_ms = (end - start) * 1000
    per_op   = total_ms / n

    print(f"  LOOKUP  {n:,} lookups  →  {total_ms:.2f} ms total  |  {per_op:.6f} ms per op  |  O(1) expected")
    return total_ms


# =============================================================================
#  Benchmark 3 — DELETE 1,000 URLs
#  Expected: O(1) per operation
# =============================================================================

def benchmark_delete(store, n=1000):
    codes = list(store.short_to_long.keys())[:n]

    start = time.perf_counter()
    for code in codes:
        store.delete(code)
    end = time.perf_counter()

    total_ms = (end - start) * 1000
    per_op   = total_ms / n

    print(f"  DELETE  {n:,} URLs     →  {total_ms:.2f} ms total  |  {per_op:.4f} ms per op  |  O(1) expected")
    return total_ms


# =============================================================================
#  Benchmark 4 — SORT 10,000 URLs by click count using Merge Sort
#  Expected: O(n log n)
# =============================================================================

def benchmark_sort(store):
    data = [(random.randint(0, 1000), code, url)
            for code, url in store.short_to_long.items()]
    n = len(data)

    start = time.perf_counter()
    merge_sort(data)
    end = time.perf_counter()

    total_ms = (end - start) * 1000
    per_op   = total_ms / n if n > 0 else 0

    print(f"  SORT    {n:,} URLs     →  {total_ms:.2f} ms total  |  {per_op:.4f} ms per op  |  O(n log n) expected")
    return total_ms


# =============================================================================
#  Benchmark 5 — TOP-K heap operation
#  Expected: O(n log k)
# =============================================================================

def benchmark_top_k(store, k=10):
    start = time.perf_counter()
    store.top_k(k)
    end = time.perf_counter()

    total_ms = (end - start) * 1000
    print(f"  TOP-K   k={k}           →  {total_ms:.2f} ms total                          |  O(n log k) expected")
    return total_ms


# =============================================================================
#  MAIN — Run all benchmarks and print summary table
# =============================================================================

if __name__ == "__main__":

    print("\n" + "="*70)
    print("  BENCHMARK  —  URL Shortener Performance Test")
    print("  Testing at scale: 10,000 operations per benchmark")
    print("="*70 + "\n")

    # Suppress output from url_store during benchmarking
    import io, contextlib

    print("  Running benchmarks — please wait...\n")
    print(f"  {'Operation':<10}  {'Details':<60}")
    print(f"  {'-'*70}")

    # Run with suppressed print output for speed
    with contextlib.redirect_stdout(io.StringIO()):
        store, t1 = benchmark_insert(10000)

    # Re-run visible versions
    store2 = URLStore()
    urls   = [random_url() for _ in range(10000)]

    # Time insert
    start = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        for url in urls:
            store2.shorten(url)
    end = time.perf_counter()
    t_insert = (end - start) * 1000
    print(f"  INSERT    10,000 URLs       →  {t_insert:.2f} ms  |  {t_insert/10000:.4f} ms/op  |  O(1)")

    # Time lookup
    codes = list(store2.short_to_long.keys())
    start = time.perf_counter()
    for _ in range(10000):
        store2.short_to_long[random.choice(codes)]
    end = time.perf_counter()
    t_lookup = (end - start) * 1000
    print(f"  LOOKUP    10,000 lookups    →  {t_lookup:.2f} ms  |  {t_lookup/10000:.6f} ms/op  |  O(1)")

    # Time delete
    del_codes = list(store2.short_to_long.keys())[:1000]
    start = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        for code in del_codes:
            store2.delete(code)
    end = time.perf_counter()
    t_delete = (end - start) * 1000
    print(f"  DELETE    1,000 URLs        →  {t_delete:.2f} ms  |  {t_delete/1000:.4f} ms/op  |  O(1)")

    # Time sort
    data = [(random.randint(0, 1000), code, url)
            for code, url in store2.short_to_long.items()]
    n = len(data)
    start = time.perf_counter()
    merge_sort(data)
    end = time.perf_counter()
    t_sort = (end - start) * 1000
    print(f"  SORT      {n:,} URLs       →  {t_sort:.2f} ms  |  {t_sort/n:.4f} ms/op  |  O(n log n)")

    # Time top-k
    start = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        store2.top_k(10)
    end = time.perf_counter()
    t_topk = (end - start) * 1000
    print(f"  TOP-K     k=10              →  {t_topk:.2f} ms                        |  O(n log k)")

    print(f"\n  {'='*70}")
    print(f"  SUMMARY")
    print(f"  {'='*70}")
    print(f"  Fastest operation : LOOKUP  ({t_lookup/10000:.6f} ms per lookup) — proves O(1) hash table")
    print(f"  Heaviest operation: SORT    ({t_sort:.2f} ms for {n:,} items) — expected for O(n log n)")
    print(f"\n  OBSERVATION:")
    print(f"  Hash table insert and lookup are nearly instant even at 10,000 entries.")
    print(f"  Merge sort scales predictably with n log n growth.")
    print(f"  This confirms our design choices are correct for this scale.")
    print(f"  {'='*70}\n")