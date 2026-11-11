def compare_products(products, product_ids):

    result = []

    for product in products:

        if product["id"] in product_ids:

            result.append(product)

    return result


if __name__ == "__main__":
    from backend.database import load_products

    products = load_products()

    ids = input("Enter product IDs separated by commas: ")

    product_ids = ids.split(",")

    result = compare_products(products, product_ids)

    if result:
        print("\nPRODUCT COMPARISON")

        for product in result:
            print("--------------------")
            print("Name:", product["name"])
            print("Brand:", product["brand"])
            print("Price:", product["price"])
            print("RAM:", product["ram"])
            print("Storage:", product["storage"])
            print("Rating:", product["rating"])
            print("Stock:", product["stock"])
    else:
        print("No matching products found.")