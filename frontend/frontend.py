from flask import Flask, jsonify
import requests
import os
import itertools
app = Flask(__name__)
CATALOG_REPLICAS = os.getenv(
    "CATALOG_REPLICAS",
    "http://catalog1:5000,http://catalog2:5000"
).split(",")

ORDER_REPLICAS = os.getenv(
    "ORDER_REPLICAS",
    "http://order1:5001,http://order2:5001"
).split(",")

catalog_cycle = itertools.cycle(CATALOG_REPLICAS)
order_cycle = itertools.cycle(ORDER_REPLICAS)
""" CATALOG_URL = "http://catalog:5000"
ORDER_URL = "http://order:5001" """
def get_next_catalog():
    selected = next(catalog_cycle)
    print(f"Frontend: selected catalog replica -> {selected}", flush=True)
    return selected


def get_next_order():
    selected = next(order_cycle)
    print(f"Frontend: selected order replica -> {selected}", flush=True)
    return selected
@app.route("/search/<topic>")
def search(topic):
    print(f"Frontend: received search request for topic '{topic}'", flush=True)

    catalog_url = get_next_catalog()
    response = requests.get(f"{catalog_url}/search/{topic}")

    return jsonify(response.json()), response.status_code


@app.route("/info/<int:item_id>")
def info(item_id):
    print(f"Frontend: received info request for book {item_id}", flush=True)

    catalog_url = get_next_catalog()
    response = requests.get(f"{catalog_url}/info/{item_id}")

    return jsonify(response.json()), response.status_code


@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):
    print(f"Frontend: received purchase request for book {item_id}", flush=True)

    order_url = get_next_order()
    response = requests.post(f"{order_url}/purchase/{item_id}")

    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(port=5002, debug=True,host="0.0.0.0")