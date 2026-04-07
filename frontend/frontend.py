from flask import Flask, jsonify
from flask import jsonify #for json response
import requests
app = Flask(__name__)
CATALOG_URL = "http://catalog:5000"
ORDER_URL = "http://order:5001"
@app.route("/search/<topic>")
def search(topic):
    res = requests.get(f"{CATALOG_URL}/search/{topic}")
    return jsonify(res.json())
@app.route("/info/<int:item_id>")
def info(item_id):
    res = requests.get(f"{CATALOG_URL}/info/{item_id}")
    return jsonify(res.json())
@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):
    res = requests.post(f"{ORDER_URL}/purchase/{item_id}")
    return jsonify(res.json())
if __name__ == "__main__":
    app.run(port=5002, debug=True,host="0.0.0.0")