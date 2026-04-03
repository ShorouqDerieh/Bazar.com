from flask import Flask, jsonify
from flask import jsonify #for json response
import sqlite3
import requests

app = Flask(__name__)
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

CATALOG_URL = "http://127.0.0.1:5000"
@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):
    res = requests.get(f"{CATALOG_URL}/info/{item_id}")
    if res.status_code != 200:
        return jsonify({"error": "Book not found"}), 404
    book = res.json()
    if book["quantity"] <= 0:
        return jsonify({"error": "Out of stock"}), 400
    update_res = requests.put(
        f"{CATALOG_URL}/update/{item_id}",
        json={"quantity": -1}
    )
    if update_res.status_code != 200:
        return jsonify({"error": "Failed to update catalog"}), 500
    conn = sqlite3.connect("orders.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO orders (item_id) VALUES (?)", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Purchase successful"})