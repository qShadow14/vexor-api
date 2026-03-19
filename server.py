"""
╔══════════════════════════════════════════╗
║   VEXOR ORDER API  —  server.py          ║
║   Run this alongside main.py             ║
║   pip install flask flask-cors           ║
╚══════════════════════════════════════════╝

Your website POSTs to:  http://localhost:5050/order
The dashboard reads:    vexor_orders.json  (same folder)
"""

import json
import os
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allows your GitHub Pages site to POST here

ORDERS_FILE = "vexor_orders.json"


def load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)


# ── Health check ──────────────────────────────────
@app.route("/ping", methods=["GET"])
def ping():
    orders = load_orders()
    return jsonify({
        "status": "online",
        "total_orders": len(orders),
        "server": "Vexor Order API v1.0"
    })


# ── Receive a new order from the website ─────────
@app.route("/order", methods=["POST"])
def receive_order():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON body"}), 400

        orders = load_orders()

        order = {
            "id":       f"web_{int(datetime.datetime.now().timestamp())}",
            "date":     datetime.date.today().isoformat(),
            "time":     datetime.datetime.now().strftime("%H:%M"),
            "product":  str(data.get("product",  "Unknown")),
            "customer": str(data.get("name",     data.get("customer", "Anonymous"))),
            "email":    str(data.get("email",    "")),
            "discord":  str(data.get("discord",  "")),
            "amount":   float(data.get("amount", data.get("total", 0))),
            "category": str(data.get("category", data.get("order_type", "Other"))),
            "payment":  str(data.get("payment",  data.get("payment_method", "Other"))),
            "note":     str(data.get("note",     data.get("notes", ""))),
            "source":   "website",
        }

        orders.append(order)
        save_orders(orders)

        print(f"[✦] New order: {order['product']} — ${order['amount']:.2f} from {order['customer']}")
        return jsonify({"status": "ok", "id": order["id"]}), 200

    except Exception as e:
        print(f"[!] Error: {e}")
        return jsonify({"error": str(e)}), 500


# ── Get all orders (optional, for debugging) ──────
@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(load_orders())


# ── Get revenue summary ───────────────────────────
@app.route("/summary", methods=["GET"])
def summary():
    orders = load_orders()
    today  = datetime.date.today().isoformat()
    week   = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    month  = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

    return jsonify({
        "today":  {
            "revenue": sum(o["amount"] for o in orders if o.get("date") == today),
            "orders":  sum(1           for o in orders if o.get("date") == today),
        },
        "week": {
            "revenue": sum(o["amount"] for o in orders if o.get("date","") >= week),
            "orders":  sum(1           for o in orders if o.get("date","") >= week),
        },
        "month": {
            "revenue": sum(o["amount"] for o in orders if o.get("date","") >= month),
            "orders":  sum(1           for o in orders if o.get("date","") >= month),
        },
        "all_time": {
            "revenue": sum(o["amount"] for o in orders),
            "orders":  len(orders),
        },
    })


if __name__ == "__main__":
    print("=" * 44)
    print("  ✦  VEXOR ORDER API")
    print("  Listening on http://localhost:5050")
    print("  Orders saved to: vexor_orders.json")
    print("=" * 44)
    app.run(host="0.0.0.0", port=5050, debug=False)
