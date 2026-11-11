def filter_by_category(products, category):

    result = []

    for product in products:

        if product["category"].lower() == category.lower():

            result.append(product)

    return result


if __name__ == "__main__":
    from backend.database import load_products

    products = load_products()

    category = input("Enter product category: ")

    result = filter_by_category(products, category)

    if result:
        print("\nProducts found:")

        for product in result:
            print(product["name"], "-", product["price"])
    else:
        print("No products found in this category.")