# Bazar.com Lab 2 — Replication, Caching, and Consistency

This project extends the original Bazar.com multi-tier online bookstore from Lab 1 by adding:

- Service replication
- Frontend load balancing
- In-memory caching
- Cache invalidation
- Replica synchronization
- Performance measurement

The system is implemented using **Python Flask**, **SQLite**, and **Docker Compose**.

---

## 1. Project Overview

Bazar.com is a small online bookstore system built using a multi-tier microservices architecture.

The system contains:

- A **Frontend Server** that receives client requests.
- Two **Catalog Server replicas** that store book information.
- Two **Order Server replicas** that process purchase requests.
- An **in-memory cache** inside the frontend to speed up repeated `info` requests.

The goal of Lab 2 is to improve request latency and availability by using replication and caching while maintaining consistency when data is updated.

---

## 2. System Architecture

```text
Client
  |
  v
Frontend Server :5002
  |
  |-- Read requests: /info, /search
  |       |
  |       |-- Round-robin load balancing
  |       v
  |    Catalog Replica 1 :5000
  |    Catalog Replica 2 :5003
  |
  |-- Write requests: /purchase
          |
          |-- Round-robin load balancing
          v
       Order Replica 1 :5001
       Order Replica 2 :5004
          |
          |-- Updates both catalog replicas
          v
       Catalog Replica 1
       Catalog Replica 2
```
