from flask import Flask, jsonify, request
import requests
import threading
import time

app = Flask(__name__)
CATALOG_REPLICAS = ["http://catalog1:5000", "http://catalog2:5000"]
ORDER_REPLICAS   = ["http://order1:5001",   "http://order2:5001"]
_lock        = threading.Lock()
_catalog_idx = 0
_order_idx   = 0

def pick_catalog():
    global _catalog_idx
    with _lock:
        url = CATALOG_REPLICAS[_catalog_idx % len(CATALOG_REPLICAS)]
        _catalog_idx += 1
    print(f"[LB] Catalog request -> {url}", flush=True)
    return url

def pick_order():
    global _order_idx
    with _lock:
        url = ORDER_REPLICAS[_order_idx % len(ORDER_REPLICAS)]
        _order_idx += 1
    print(f"[LB] Order request -> {url}", flush=True)
    return url
MAX_CACHE   = 50
_cache      = {}
_cache_lock = threading.Lock()
_hits   = 0
_misses = 0

def cache_get(book_id: int):
    global _hits, _misses
    with _cache_lock:
        entry = _cache.get(book_id)
    if entry:
        _hits += 1
        age = round(time.time() - entry["timestamp"], 2)
        print(f"[Cache] HIT  book_id={book_id} (age={age}s) | hits={_hits}", flush=True)
        return entry["data"]
    else:
        _misses += 1
        print(f"[Cache] MISS book_id={book_id} | misses={_misses}", flush=True)
        return None

def cache_put(book_id: int, data: dict):
    with _cache_lock:
        if len(_cache) >= MAX_CACHE:
            oldest_key = next(iter(_cache))
            del _cache[oldest_key]
            print(f"[Cache] Evicted book_id={oldest_key} (capacity={MAX_CACHE})", flush=True)
        _cache[book_id] = {"data": data, "timestamp": time.time()}
    print(f"[Cache] Stored book_id={book_id} | cache_size={len(_cache)}", flush=True)

def cache_invalidate(book_id: int):
    with _cache_lock:
        removed = _cache.pop(book_id, None)
    if removed:
        print(f"[Cache] Invalidated book_id={book_id}", flush=True)
    else:
        print(f"[Cache] Invalidate: book_id={book_id} was not in cache", flush=True)
@app.route("/search/<string:topic>")
def search(topic):
    catalog = pick_catalog()
    print(f"[Frontend] search topic='{topic}'", flush=True)
    res = requests.get(f"{catalog}/search/{topic}", timeout=5)
    return jsonify(res.json()), res.status_code


@app.route("/info/<int:item_id>")
def info(item_id):
    cached = cache_get(item_id)
    if cached:
        return jsonify(cached)
    catalog = pick_catalog()
    print(f"[Frontend] info id={item_id} -> {catalog}", flush=True)
    res = requests.get(f"{catalog}/info/{item_id}", timeout=5)
    if res.status_code == 200:
        cache_put(item_id, res.json())
    return jsonify(res.json()), res.status_code


@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):
    cache_invalidate(item_id)

    order = pick_order()
    print(f"[Frontend] purchase id={item_id} -> {order}", flush=True)
    res = requests.post(f"{order}/purchase/{item_id}", timeout=5)
    return jsonify(res.json()), res.status_code

@app.route("/invalidate/<int:book_id>", methods=["POST"])
def invalidate(book_id):
    cache_invalidate(book_id)
    return jsonify({"message": f"Cache invalidated for book {book_id}"})

@app.route("/cache")
def show_cache():
    with _cache_lock:
        snapshot = {k: v["data"] for k, v in _cache.items()}
    return jsonify(snapshot)


@app.route("/cache/stats")
def cache_stats():
    total = _hits + _misses
    rate  = round(_hits / total * 100, 1) if total > 0 else 0
    return jsonify({
        "hits":       _hits,
        "misses":     _misses,
        "total":      total,
        "hit_rate":   f"{rate}%",
        "cache_size": len(_cache)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
