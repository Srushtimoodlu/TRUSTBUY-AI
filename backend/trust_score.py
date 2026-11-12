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

def calculate_trust_score(trust_data):

    product_score = (trust_data["product_rating"] / 5) * 30

    seller_score = (trust_data["seller_data"]["rating"] / 5) * 25

    verification_score = 20 if trust_data["seller_data"]["verified"] else 0

    if trust_data["reviews"]:
        total_rating = 0

        for review in trust_data["reviews"]:
            total_rating += review["rating"]

        average_rating = total_rating / len(trust_data["reviews"])

        review_score = (average_rating / 5) * 15
    else:
        review_score = 0

    stock_score = 10 if trust_data["stock"] > 0 else 0

    total_score = (
        product_score
        + seller_score
        + verification_score
        + review_score
        + stock_score
    )

    return round(total_score, 2)
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
    
        trust_score = calculate_trust_score(result)
    
        print("\nProduct Trust Score:", trust_score, "/ 100")
    
    else:
        print("Product not found.")