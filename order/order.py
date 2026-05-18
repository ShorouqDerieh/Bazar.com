from flask import Flask, jsonify
import sqlite3
import requests
import os
app = Flask(__name__)
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "order")
CATALOG_REPLICAS = os.getenv(
    "CATALOG_REPLICAS",
    "http://catalog1:5000,http://catalog2:5000"
).split(",")
conn = sqlite3.connect("orders.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER
)
""")

conn.commit()
conn.close()
""" CATALOG_URL = "http://catalog:5000" """
def get_book_info(item_id):
    for catalog_url in CATALOG_REPLICAS:
        try:
            print(f"{INSTANCE_NAME}: requesting book info from {catalog_url}", flush=True)
            response = requests.get(f"{catalog_url}/info/{item_id}", timeout=5)

            if response.status_code == 200:
                return response

        except requests.exceptions.RequestException as e:
            print(f"{INSTANCE_NAME}: failed to contact {catalog_url}: {e}", flush=True)

    return None
def update_all_catalog_replicas(item_id, quantity_change):
    failed_replicas = []

    for catalog_url in CATALOG_REPLICAS:
        try:
            print(
                f"{INSTANCE_NAME}: sending update to {catalog_url}, item={item_id}, quantity_change={quantity_change}",
                flush=True
            )

            response = requests.put(
                f"{catalog_url}/update/{item_id}",
                json={"quantity": quantity_change},
                timeout=5
            )

            if response.status_code != 200:
                failed_replicas.append({
                    "replica": catalog_url,
                    "status": response.status_code,
                    "response": response.text
                })

        except requests.exceptions.RequestException as e:
            failed_replicas.append({
                "replica": catalog_url,
                "error": str(e)
            })

    return failed_replicas
@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):
    print(f"{INSTANCE_NAME}: received purchase request for book {item_id}", flush=True)
    response = get_book_info(item_id)
    if response is None:
        return jsonify({"error": "Catalog service unavailable"}), 503
    book = response.json()
    if "error" in book:
        return jsonify({"error": "Book not found"}), 404
    if book["quantity"] <= 0:
        return jsonify({"error": "Out of stock"}), 400
    failed_replicas = update_all_catalog_replicas(item_id, -1)

    if failed_replicas:
        return jsonify({
            "error": "Failed to update all catalog replicas",
            "failed_replicas": failed_replicas
        }), 500
    conn = sqlite3.connect("orders.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO orders (item_id) VALUES (?)", (item_id,))
    conn.commit()
    conn.close()

    print(f"{INSTANCE_NAME}: bought book {book['title']}", flush=True)

    return jsonify({
        "message": "Purchase successful",
        "handled_by": INSTANCE_NAME,
        "item_id": item_id,
        "book_title": book["title"]
    })
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
