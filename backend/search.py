def search_products(products, keyword):

    result = []

    for product in products:

        if keyword.lower() in product["name"].lower():

            result.append(product)

    return result


if __name__ == "__main__":
    from backend.database import load_products

    products = load_products()

    keyword = input("Enter product name: ")

    result = search_products(products, keyword)

    if result:
        for product in result:
            print(product["name"], "-", product["price"])
    else:
        print("No products found")