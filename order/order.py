from flask import Flask, jsonify
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
CATALOG_URL = "http://catalog:5000"
@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):
    print(f"Order: received purchase request for book {item_id}")
    res = requests.get(f"{CATALOG_URL}/info/{item_id}")
    print(f"Order: requesting book info from Catalog")

    if res.status_code != 200:
        print(f"Order: book {item_id} not found")
        return jsonify({"error": "Book not found"}), 404

    book = res.json()

    if book["quantity"] <= 0:
        print(f"Order: book {item_id} out of stock")
        return jsonify({"error": "Out of stock"}), 400

    print(f"Order: updating Catalog (decreasing quantity)")
    update_res = requests.put(
        f"{CATALOG_URL}/update/{item_id}",
        json={"quantity": -1}
    )

    if update_res.status_code != 200:
        print(f"Order: failed to update catalog")
        return jsonify({"error": "Failed to update catalog"}), 500

    print(f"Order: saving order in database")
    conn = sqlite3.connect("orders.db", check_same_thread=False)
    c = conn.cursor()

    c.execute("INSERT INTO orders (item_id) VALUES (?)", (item_id,))
    conn.commit()
    conn.close()
    
    print(f"Order: purchase completed for book {item_id}")
    return jsonify({"message": "Purchase successful"})
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
