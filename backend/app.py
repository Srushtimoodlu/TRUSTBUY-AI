from flask import Flask, jsonify, request
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
cart={}

app = Flask(__name__)


@app.route("/")
def home():

    return jsonify({
        "message": "TRUSTBUY AI Backend is running!"
    })


@app.route("/products")
def get_products():

    products = load_products()

    return jsonify(products)
@app.route("/product")
def get_product():

    product_id = request.args.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide a product ID"}), 400

    products = load_products()

    for product in products:

        if product["id"] == product_id:
            return jsonify(product)

    return jsonify({"error": "Product not found"}), 404

@app.route("/products/count")
def product_count():

    products = load_products()

    return jsonify({
        "total_products": len(products)
    })
@app.route("/categories")
def get_categories():

    products = load_products()

    categories = []

    for product in products:

        category = product["category"]

        if category not in categories:
            categories.append(category)

    return jsonify({
        "categories": sorted(categories)
    })
@app.route("/price-range")
def price_range():

    products = load_products()

    prices = []

    for product in products:
        prices.append(product["price"])

    return jsonify({
        "minimum_price": min(prices),
        "maximum_price": max(prices)
    })

@app.route("/reviews")
def get_product_reviews():

    product_id = request.args.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide a product ID"}), 400

    products = load_products()

    product_exists = False

    for product in products:
        if product["id"] == product_id:
            product_exists = True
            break

    if not product_exists:
        return jsonify({"error": "Product not found"}), 404

    reviews = load_json("reviews.json")

    result = []

    for review in reviews:
        if review["product_id"] == product_id:
            result.append(review)

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

    products = load_products()

    product_exists = False

    for product in products:
        if product["id"] == product_id:
            product_exists = True
            break

    if not product_exists:
        return jsonify({"error": "Product not found"}), 404

    sellers = load_json("sellers.json")

    for seller in sellers:
        if seller["product_id"] == product_id:
            return jsonify(seller)

    return jsonify({"error": "Seller information not found"}), 404

@app.route("/sort")
def sort_products():

    sort_order = request.args.get("order", "low-to-high")

    products = load_products()

    if sort_order == "low-to-high":

        result = sorted(
            products,
            key=lambda product: product["price"]
        )

    elif sort_order == "high-to-low":

        result = sorted(
            products,
            key=lambda product: product["price"],
            reverse=True
        )

    else:
        return jsonify({
            "error": "Invalid sort order"
        }), 400

    return jsonify(result)
@app.route("/products/page")
def get_products_page():

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)

    if page < 1 or limit < 1:
        return jsonify({
            "error": "Page and limit must be positive numbers"
        }), 400

    products = load_products()

    total_products = len(products)

    start = (page - 1) * limit
    end = start + limit

    result = products[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total_products": total_products,
        "total_pages": (total_products + limit - 1) // limit,
        "products": result
    })


@app.route("/search")
def search():

    keyword = request.args.get("keyword", "")

    products = load_products()

    result = search_products(products, keyword)

    return jsonify(result)
@app.route("/budget")
def budget_filter():

    budget = request.args.get("amount", type=int)

    if budget is None:
        return jsonify({"error": "Please provide a valid budget"}), 400

    products = load_products()

    result = filter_by_budget(products, budget)

    return jsonify(result)
@app.route("/category")
def category_filter():

    category = request.args.get("name", "")

    if not category.strip():
        return jsonify({"error": "Please provide a category"}), 400

    products = load_products()

    result = filter_by_category(products, category)

    return jsonify(result)
@app.route("/stock")
def stock_check():

    product_id = request.args.get("product_id", "")

    if not product_id:
        return jsonify({"error": "Please provide a product ID"}), 400

    products = load_products()

    result = check_stock(products, product_id)

    return jsonify({
        "product_id": product_id,
        "stock_status": result
    })
@app.route("/compare")
def product_comparison():

    ids = request.args.get("ids", "")

    if not ids.strip():
        return jsonify({"error": "Please provide product IDs"}), 400

    product_ids = ids.split(",")

    products = load_products()

    result = compare_products(products, product_ids)

    return jsonify(result)

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
        "product_name": trust_data["name"],
        "trust_score": score,
        "maximum_score": 100
    })
@app.route("/cart/add", methods=["POST"])
def add_cart_item():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Please provide cart details"}), 400

    product_id = data.get("product_id", "")
    quantity = data.get("quantity", 0)

    if not product_id or not isinstance(quantity, int) or isinstance(quantity, bool):
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

    items = view_cart(products, cart)

    total = calculate_total(products, cart)

    return jsonify({
        "cart": items,
        "total": total
    })

@app.route("/cart/remove", methods=["DELETE"])
def remove_cart_item():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Please provide product ID"}), 400

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

    data = request.get_json()

    if not data:
        return jsonify({"error": "Please provide user details"}), 400

    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")

    result = register_user(name, email, password)

    if result != "Registration successful":
        return jsonify({"message": result}), 400

    return jsonify({
        "message": result
    }), 201
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Please provide login details"}), 400

    email = data.get("email", "")
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    result = login_user(email, password)

    if result != "Login successful":
        return jsonify({"message": result}), 401

    return jsonify({
        "message": result
    })
@app.route("/health")
def health_check():

    return jsonify({
        "status": "healthy",
        "message": "TRUSTBUY AI Backend is working!"
    })
if __name__ == "__main__":
    app.run(debug=True)