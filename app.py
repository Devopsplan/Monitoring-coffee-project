"""
CoffeeCraft — a small Flask ecommerce demo backed by a static JSON catalog.

No database: the product catalog lives in data/products.json and the cart
lives in the browser session. This is intentionally simple so it's easy to
read, extend, or swap in a real database later.
"""
import json
import os
import uuid
from pathlib import Path

from flask import Flask, render_template, redirect, url_for, request, session, flash

BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_PATH = BASE_DIR / "data" / "products.json"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")


# ---------------------------------------------------------------------------
# Catalog helpers
# ---------------------------------------------------------------------------

def load_products():
    with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_product(product_id):
    return next((p for p in load_products() if p["id"] == product_id), None)


def roast_label(level):
    return {
        1: "Light",
        2: "Light-Medium",
        3: "Medium",
        4: "Medium-Dark",
        5: "Dark",
    }.get(level, "Medium")


# Make helpers available inside every template
app.jinja_env.globals.update(roast_label=roast_label)


# ---------------------------------------------------------------------------
# Cart helpers — cart is stored in the session as {product_id_str: qty}
# ---------------------------------------------------------------------------

def get_cart():
    return session.setdefault("cart", {})


def cart_details():
    cart = get_cart()
    products = {p["id"]: p for p in load_products()}
    items = []
    subtotal = 0.0
    for pid_str, qty in cart.items():
        product = products.get(int(pid_str))
        if not product:
            continue
        line_total = product["price"] * qty
        subtotal += line_total
        items.append({**product, "qty": qty, "line_total": line_total})
    items.sort(key=lambda i: i["name"])
    shipping = 0.0 if subtotal == 0 or subtotal >= 40 else 4.50
    total = subtotal + shipping
    return {
        "lines": items,
        "count": sum(cart.values()),
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    }


@app.context_processor
def inject_cart_count():
    return {"cart_count": sum(get_cart().values())}


# ---------------------------------------------------------------------------
# Routes — catalog
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    products = load_products()
    return render_template("index.html", products=products)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product(product_id)
    if not product:
        return render_template("404.html"), 404
    others = [p for p in load_products() if p["id"] != product_id][:3]
    return render_template("product.html", product=product, others=others)


# ---------------------------------------------------------------------------
# Routes — cart
# ---------------------------------------------------------------------------

@app.route("/cart")
def view_cart():
    return render_template("cart.html", cart=cart_details())


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = get_product(product_id)
    if not product:
        return render_template("404.html"), 404
    qty = max(1, int(request.form.get("qty", 1)))
    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    session.modified = True
    flash(f"Added {qty} \u00d7 {product['name']} to your bag.", "success")
    next_url = request.form.get("next") or url_for("index")
    return redirect(next_url)


@app.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart = get_cart()
    key = str(product_id)
    qty = int(request.form.get("qty", 0))
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session.modified = True
    return redirect(url_for("view_cart"))


# ---------------------------------------------------------------------------
# Routes — checkout (demo only: no real payment processing)
# ---------------------------------------------------------------------------

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    details = cart_details()
    if not details["lines"]:
        return redirect(url_for("index"))

    if request.method == "POST":
        order_id = uuid.uuid4().hex[:8].upper()
        session["last_order"] = {
            "id": order_id,
            "name": request.form.get("name", "").strip() or "Friend",
            "email": request.form.get("email", "").strip(),
            "lines": details["lines"],
            "subtotal": details["subtotal"],
            "shipping": details["shipping"],
            "total": details["total"],
        }
        session["cart"] = {}
        session.modified = True
        return redirect(url_for("order_confirmation"))

    return render_template("checkout.html", cart=details)


@app.route("/order-confirmation")
def order_confirmation():
    order = session.get("last_order")
    if not order:
        return redirect(url_for("index"))
    return render_template("confirmation.html", order=order)


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)