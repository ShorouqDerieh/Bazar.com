# Bazar.com — Lab 2: Replication, Caching & Consistency

> Distributed and Operating Systems — Spring 2019 / Fall 2020

---

## Project Structure

```
bazar_lab2/
├── frontend/
│   ├── frontend.py        # Frontend server (cache + load balancer)
│   └── Dockerfile
├── catalog1/
│   ├── catalog.py         # Catalog replica 1
│   └── Dockerfile
├── catalog2/
│   ├── catalog.py         # Catalog replica 2
│   └── Dockerfile
├── order1/
│   ├── order.py           # Order replica 1
│   └── Dockerfile
├── order2/
│   ├── order.py           # Order replica 2
│   └── Dockerfile
├── docker-compose.yml
├── measure.py             # Performance measurement script
├── test_client.py         # Functional test client
└── docs/
    ├── output.txt         # Sample program output + performance table
    └── design_document.md # Full design description
```

---

## How to Run

### Requirements
- Docker Desktop installed and running
- Python 3.x (for running the test/measure clients on host)
- `requests` library: `pip install requests`

### Step 1 — Start all services
```bash
cd bazar_lab2
docker compose up --build
```

This starts 5 containers:
| Container | Port (host) | Role |
|-----------|-------------|------|
| frontend  | 5002        | Frontend server with cache |
| catalog1  | 5010        | Catalog replica 1 |
| catalog2  | 5011        | Catalog replica 2 |
| order1    | 5020        | Order replica 1 |
| order2    | 5021        | Order replica 2 |

### Step 2 — Run functional tests
```bash
python test_client.py
```

### Step 3 — Run performance measurements
```bash
python measure.py
```

### Step 4 — Manual curl examples
```bash
# Search books by topic
curl "http://localhost:5002/search/distributed%20systems"
curl "http://localhost:5002/search/undergraduate%20school"

# Get book info (first call = MISS, second call = HIT)
curl http://localhost:5002/info/2
curl http://localhost:5002/info/2

# Purchase a book
curl -X POST http://localhost:5002/purchase/2

# View current cache contents
curl http://localhost:5002/cache

# View cache hit/miss statistics
curl http://localhost:5002/cache/stats
```

### Stop all services
```bash
docker compose down
```

---

## Architecture Overview

```
         Client
           |
           v
     ┌─────────────────────────────┐
     │  Frontend  (port 5002)      │
     │  - In-memory Cache          │
     │  - Round-Robin Load Balancer│
     └──────┬──────────────┬───────┘
            |              |
     ┌──────┴──┐      ┌────┴────┐
     │Catalog 1│ <--> │Catalog 2│   (replica sync)
     │port 5000│      │port 5000│
     └─────────┘      └─────────┘

     ┌──────────┐      ┌─────────┐
     │ Order 1  │ <--> │ Order 2 │  (replica sync)
     │ port 5001│      │port 5001│
     └──────────┘      └─────────┘
```

---

## Cache Behavior

| Request Type | Cache Used? | Notes |
|---|---|---|
| `/info/<id>` | YES | HIT returns instantly; MISS fetches from catalog |
| `/search/<topic>` | NO | Results depend on stock levels |
| `/purchase/<id>` | NO | Write operation, always goes to order server |

### Cache Consistency Flow
```
purchase(book_id)
    → Order Server decrements stock in Catalog
        → Catalog sends POST /invalidate/<book_id> to Frontend
            → Frontend removes book_id from cache
                → Next /info call fetches fresh data (MISS)
```

---

## REST API Reference

### Frontend Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search/<topic>` | Search books by topic |
| GET | `/info/<id>` | Get book details (cached) |
| POST | `/purchase/<id>` | Buy a book |
| POST | `/invalidate/<id>` | Invalidate cache entry (called by catalog) |
| GET | `/cache` | View cache contents (debug) |
| GET | `/cache/stats` | View hit/miss statistics |

### Catalog Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search/<topic>` | Query by topic |
| GET | `/info/<id>` | Query by item ID |
| PUT | `/update/<id>` | Update price or quantity |

### Order Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/purchase/<id>` | Process a purchase |
| POST | `/sync_order` | Sync order to peer replica |
| GET | `/orders` | List all orders |

---

## Book Catalog

| ID | Title | Topic | Price | Qty |
|----|-------|-------|-------|-----|
| 1 | How to get a good grade in DOS in 40 minutes a day | distributed systems | $20 | 100 |
| 2 | RPCs for Noobs | distributed systems | $50 | 200 |
| 3 | Xen and the Art of Surviving Undergraduate School | undergraduate school | $30 | 150 |
| 4 | Cooking for the Impatient Undergrad | undergraduate school | $20 | 100 |
| 5 | How to finish Project 3 on time *(new)* | distributed systems | $25 | 80 |
| 6 | Why theory classes are so hard *(new)* | undergraduate school | $15 | 120 |
| 7 | Spring in the Pioneer Valley *(new)* | undergraduate school | $10 | 60 |

---

## Performance Summary

| Scenario | Avg (ms) | Median (ms) |
|---|---|---|
| Info — Cache MISS (cold) | ~18 | ~18 |
| Info — Cache HIT (warm)  | ~1  | ~1  |
| Purchase (write)         | ~35 | ~34 |
| Cache Invalidation       | ~2  | ~2  |
| Post-invalidation MISS   | ~19 | ~18 |

**Cache speedup: ~15x faster for repeated reads.**

Full results and analysis: `docs/output.txt`

---

## Team Responsibilities

| Person | Responsibilities |
|--------|-----------------|
| Person 1 | docker-compose, catalog/order replicas, replica sync, load balancing |
| Person 2 | Frontend cache, cache hit/miss logs, cache invalidation, measure.py, docs, README |
