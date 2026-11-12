import json
from pathlib import Path

DATA_FOLDER = Path(__file__).resolve().parent.parent / "data"


def load_json(filename):
    file_path = DATA_FOLDER / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_trust_data(products, reviews, product_id, sellers=None):

    product = None

    for item in products:
        if item["id"] == product_id:
            product = item
            break

    if product is None:
        return None

    product_reviews = []

    for review in reviews:
        if review["product_id"] == product_id:
            product_reviews.append(review)

    seller_data = None

    if sellers is not None:
        for seller in sellers:
            if seller["product_id"] == product_id:
                seller_data = seller
                break

    trust_data = {
        "product_id": product["id"],
        "name": product["name"],
        "brand": product["brand"],
        "category": product["category"],
        "price": product["price"],
        "seller": product["seller"],
        "stock": product["stock"],
        "product_rating": product["rating"],
        "seller_data": seller_data,
        "reviews": product_reviews,
        "review_count": len(product_reviews)
    }

    return trust_data


if __name__ == "__main__":

    products = load_json("products.json")
    reviews = load_json("reviews.json")
    sellers = load_json("sellers.json")

    product_id = input("Enter product ID: ")

    result = get_trust_data(
        products, reviews, product_id, sellers
    )

    if result:
        print("\nProduct Trust Information:")
        print(json.dumps(result, indent=4))
    else:
        print("Product not found.")