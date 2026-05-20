import requests
import time
import statistics

BASE      = "http://localhost:5002"
BOOK_ID   = 2          
ROUNDS    = 20        
def avg_ms(times):
    return round(statistics.mean(times) * 1000, 2)

def median_ms(times):
    return round(statistics.median(times) * 1000, 2)

def measure_info(label, book_id=BOOK_ID, n=ROUNDS):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        requests.get(f"{BASE}/info/{book_id}")
        times.append(time.perf_counter() - t0)
    print(f"  {label}: avg={avg_ms(times)} ms | median={median_ms(times)} ms | "
          f"min={round(min(times)*1000,2)} ms | max={round(max(times)*1000,2)} ms")
    return times

def measure_purchase(book_id=BOOK_ID, n=5):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        requests.post(f"{BASE}/purchase/{book_id}")
        times.append(time.perf_counter() - t0)
    print(f"  purchase: avg={avg_ms(times)} ms | median={median_ms(times)} ms")
    return times

def reset_cache(book_id=BOOK_ID):
    """Force cache miss by sending invalidate directly."""
    requests.post(f"{BASE}/invalidate/{book_id}")
print("\n" + "="*60)
print("EXPERIMENT 1: Cache MISS vs HIT response time")
print("="*60)
print(f"\n[a] Cold requests (cache MISS) — {ROUNDS} calls, clearing cache before each:")
miss_times = []
for i in range(ROUNDS):
    reset_cache(BOOK_ID)
    t0 = time.perf_counter()
    requests.get(f"{BASE}/info/{BOOK_ID}")
    miss_times.append(time.perf_counter() - t0)
print(f"  MISS avg={avg_ms(miss_times)} ms | median={median_ms(miss_times)} ms | "
      f"min={round(min(miss_times)*1000,2)} ms | max={round(max(miss_times)*1000,2)} ms")
print(f"\n[b] Warm requests (cache HIT) — {ROUNDS} calls after warm-up:")
requests.get(f"{BASE}/info/{BOOK_ID}")   # warm-up
hit_times = measure_info("HIT ", book_id=BOOK_ID, n=ROUNDS)

speedup = round(avg_ms(miss_times) / avg_ms(hit_times), 1) if avg_ms(hit_times) > 0 else "N/A"
print(f"\n  --> Cache speedup: {speedup}x faster with cache")
print("\n" + "="*60)
print("EXPERIMENT 2: Purchase response time (book id=5, qty=80)")
print("="*60)
purchase_times = measure_purchase(book_id=5, n=5)
print("\n" + "="*60)
print("EXPERIMENT 3: Cache consistency — invalidation overhead")
print("="*60)

requests.get(f"{BASE}/info/{BOOK_ID}")
print(f"\n[a] Cache populated for book_id={BOOK_ID}")
inv_times = []
for _ in range(ROUNDS):
    # re-populate first
    requests.get(f"{BASE}/info/{BOOK_ID}")
    t0 = time.perf_counter()
    requests.post(f"{BASE}/invalidate/{BOOK_ID}")
    inv_times.append(time.perf_counter() - t0)

print(f"  Invalidation avg={avg_ms(inv_times)} ms | "
      f"median={median_ms(inv_times)} ms")
print(f"\n[b] First request after invalidation (should be MISS):")
miss_after = []
for _ in range(ROUNDS):
    reset_cache(BOOK_ID)
    t0 = time.perf_counter()
    requests.get(f"{BASE}/info/{BOOK_ID}")
    miss_after.append(time.perf_counter() - t0)
print(f"  Post-invalidation MISS avg={avg_ms(miss_after)} ms")
print("\n" + "="*60)
print("PERFORMANCE SUMMARY TABLE")
print("="*60)
print(f"{'Scenario':<35} {'Avg (ms)':>10} {'Median (ms)':>12}")
print("-"*60)
print(f"{'Info - Cache MISS (cold)':<35} {avg_ms(miss_times):>10} {median_ms(miss_times):>12}")
print(f"{'Info - Cache HIT (warm)':<35} {avg_ms(hit_times):>10} {median_ms(hit_times):>12}")
print(f"{'Purchase (write)':<35} {avg_ms(purchase_times):>10} {median_ms(purchase_times):>12}")
print(f"{'Cache Invalidation':<35} {avg_ms(inv_times):>10} {median_ms(inv_times):>12}")
print(f"{'Post-invalidation MISS':<35} {avg_ms(miss_after):>10} {median_ms(miss_after):>12}")
print("-"*60)
print(f"  Cache speedup: {speedup}x")

print("\n[Cache Stats from server]")
r = requests.get(f"{BASE}/cache/stats")
print(" ", r.json())

print("\nDone. Copy the table above into docs/output.txt\n")
