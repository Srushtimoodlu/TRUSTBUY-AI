def get_trust_data(products, reviews, product_id):

    for product in products:

        if product["id"] == product_id:

            product_reviews = []

            for review in reviews:

                if review["product_id"] == product_id:
                    product_reviews.append(review)

            trust_data = {
                "product_id": product["id"],
                "name": product["name"],
                "brand": product["brand"],
                "price": product["price"],
                "seller": product["seller"],
                "rating": product["rating"],
                "stock": product["stock"],
                "reviews": product_reviews,
                "review_count": len(product_reviews)
            }

            return trust_data

    return None


if __name__ == "__main__":

    from backend.database import load_products
    import json

    products = load_products()

    with open("data/reviews.json", "r", encoding="utf-8") as file:
        reviews = json.load(file)

    product_id = input("Enter product ID: ")

    result = get_trust_data(products, reviews, product_id)

    if result:
        print("\nPRODUCT TRUST DATA")
        print(result)
    else:
        print("Product not found")