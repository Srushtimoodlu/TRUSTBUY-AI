
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.database import load_products
from backend.search import search_products
from backend.filters import filter_by_budget
from backend.category import filter_by_category
from backend.inventory import check_stock
from backend.comparison import compare_products

from backend.trust_score import (
    load_json,
    get_trust_data,
    calculate_trust_score
)

from backend.cart import (
    add_to_cart,
    remove_from_cart,
    view_cart,
    calculate_total
)

from backend.auth import register_user, login_user

try:
    from agents.shopping_agent import shopping_agent
    AGENT_AVAILABLE = True
except ImportError as error:
    print("Shopping agent unavailable:", error)
    shopping_agent = None
    AGENT_AVAILABLE = False

app = Flask(__name__)
CORS(app)

cart = {}


@app.route("/")
def home():
    return jsonify({
        "message": "TRUSTBUY AI Backend is running!",
        "status": "Running"
    })


@app.route("/products")
def get_products():
    return jsonify(load_products())


@app.route("/product")
def get_product():
    product_id = request.args.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide a product ID"}), 400

    for product in load_products():
        if product["id"] == product_id:
            return jsonify(product)

    return jsonify({"error": "Product not found"}), 404


@app.route("/products/count")
def product_count():
    return jsonify({"total_products": len(load_products())})


@app.route("/categories")
def get_categories():
    products = load_products()
    categories = sorted(set(p["category"] for p in products))
    return jsonify({"categories": categories})


@app.route("/price-range")
def price_range():
    products = load_products()

    if not products:
        return jsonify({"error": "No products available"}), 404

    prices = [p["price"] for p in products]

    return jsonify({
        "minimum_price": min(prices),
        "maximum_price": max(prices)
    })


@app.route("/reviews")
def get_product_reviews():
    product_id = request.args.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide a product ID"}), 400

    if not any(p["id"] == product_id for p in load_products()):
        return jsonify({"error": "Product not found"}), 404

    reviews = load_json("reviews.json")
    result = [r for r in reviews if r["product_id"] == product_id]

    return jsonify({
        "product_id": product_id,
        "review_count": len(result),
        "reviews": result
    })


@app.route("/seller")
def get_seller():
    product_id = request.args.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide a product ID"}), 400

    if not any(p["id"] == product_id for p in load_products()):
        return jsonify({"error": "Product not found"}), 404

    sellers = load_json("sellers.json")

    for seller in sellers:
        if seller["product_id"] == product_id:
            return jsonify(seller)

    return jsonify({"error": "Seller information not found"}), 404


@app.route("/sort")
def sort_products():
    order = request.args.get("order", "low-to-high")
    products = load_products()

    if order == "low-to-high":
        result = sorted(products, key=lambda p: p["price"])
    elif order == "high-to-low":
        result = sorted(
            products,
            key=lambda p: p["price"],
            reverse=True
        )
    else:
        return jsonify({"error": "Invalid sort order"}), 400

    return jsonify(result)


@app.route("/products/page")
def get_products_page():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)

    if page < 1 or limit < 1:
        return jsonify({"error": "Invalid page or limit"}), 400

    products = load_products()
    total = len(products)
    start = (page - 1) * limit

    return jsonify({
        "page": page,
        "limit": limit,
        "total_products": total,
        "total_pages": (total + limit - 1) // limit,
        "products": products[start:start + limit]
    })


@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")
    return jsonify(search_products(load_products(), keyword))


@app.route("/budget")
def budget_filter():
    budget = request.args.get("amount", type=int)

    if budget is None or budget < 0:
        return jsonify({"error": "Invalid budget"}), 400

    return jsonify(filter_by_budget(load_products(), budget))


@app.route("/category")
def category_filter():
    category = request.args.get("name", "")

    if not category.strip():
        return jsonify({"error": "Please provide a category"}), 400

    return jsonify(filter_by_category(load_products(), category))


@app.route("/stock")
def stock_check():
    product_id = request.args.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide a product ID"}), 400

    return jsonify({
        "product_id": product_id,
        "stock_status": check_stock(load_products(), product_id)
    })


@app.route("/compare")
def product_comparison():
    ids = request.args.get("ids", "")

    if not ids.strip():
        return jsonify({"error": "Please provide product IDs"}), 400

    return jsonify(compare_products(load_products(), ids.split(",")))


@app.route("/trust-score")
def product_trust_score():
    product_id = request.args.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide a product ID"}), 400

    products = load_json("products.json")
    reviews = load_json("reviews.json")
    sellers = load_json("sellers.json")

    trust_data = get_trust_data(
        products, reviews, product_id, sellers
    )

    if trust_data is None:
        return jsonify({"error": "Product not found"}), 404

    score = calculate_trust_score(trust_data)

    return jsonify({
        "product_id": product_id,
        "name": trust_data["name"],
        "product_name": trust_data["name"],
        "trust_score": score,
        "maximum_score": 100
    })


@app.route("/cart/add", methods=["POST"])
def add_cart_item():
    data = request.get_json(silent=True) or {}

    product_id = data.get("product_id", "")
    quantity = data.get("quantity", 0)

    if (
        not product_id
        or not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return jsonify({"error": "Invalid product ID or quantity"}), 400

    products = load_products()
    result = add_to_cart(products, cart, product_id, quantity)

    if result != "Product added to cart":
        return jsonify({"message": result}), 400

    return jsonify({
        "message": result,
        "cart": view_cart(products, cart),
        "total": calculate_total(products, cart)
    })


@app.route("/cart", methods=["GET"])
def get_cart():
    products = load_products()

    return jsonify({
        "cart": view_cart(products, cart),
        "total": calculate_total(products, cart)
    })


@app.route("/cart/remove", methods=["DELETE"])
def remove_cart_item():
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide product ID"}), 400

    result = remove_from_cart(cart, product_id)

    if result != "Product removed from cart":
        return jsonify({"message": result}), 404

    products = load_products()

    return jsonify({
        "message": result,
        "cart": view_cart(products, cart),
        "total": calculate_total(products, cart)
    })


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    result = register_user(
        data.get("name", ""),
        data.get("email", ""),
        data.get("password", "")
    )

    if result != "Registration successful":
        return jsonify({"message": result}), 400

    return jsonify({"message": result}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "")
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    result = login_user(email, password)

    if result != "Login successful":
        return jsonify({"message": result}), 401

    return jsonify({"message": result})



@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Enter shopping requirements"}), 400

    import re

    # Extract budget from user query
    match = re.search(r'(\d[\d,]*)', query)

    budget = None
    if match:
        budget = int(match.group(1).replace(",", ""))

    # Detect category
    query_lower = query.lower()

    category = None

    if "laptop" in query_lower:
        category = "laptop"
    elif "mobile" in query_lower or "phone" in query_lower:
        category = "mobile"

    # Load actual products
    all_products = load_products()

    # Filter matching products
    recommendations = []

    for product in all_products:

        product_category = str(
            product.get("category", "")
        ).lower()

        product_name = str(
            product.get("name", "")
        ).lower()

        if category and category not in product_category and category not in product_name:
            continue

        try:
            price = float(product.get("price", 0))
        except (ValueError, TypeError):
            continue

        if budget is not None and price > budget:
            continue

        recommendations.append(product)

    # Sort by price
    recommendations.sort(
        key=lambda p: float(p.get("price", 0))
    )

    return jsonify({
        "agent": "TRUSTBUY-AI",
        "user_query": query,
        "budget": budget,
        "category": category,
        "status": "AI analysis successful",
        "total_found": len(recommendations),
        "recommendations": recommendations[:5]
    })


@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "TRUSTBUY AI Backend is working!",
        "agent_available": AGENT_AVAILABLE
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
