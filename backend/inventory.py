def check_stock(products, product_id):

    for product in products:

        if product["id"] == product_id:

            if product["stock"] > 0:
                return "Available"

            else:
                return "Out of stock"

    return "Product not found"


if __name__ == "__main__":
    from backend.database import load_products

    products = load_products()

    product_id = input("Enter product ID: ")

    result = check_stock(products, product_id)

    print("Stock status:", result)