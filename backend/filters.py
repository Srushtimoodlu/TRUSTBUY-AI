def filter_by_budget(products, budget):

    result = []

    for product in products:

        if product["price"] <= budget:

            result.append(product)

    return result


if __name__ == "__main__":
    from backend.database import load_products

    products = load_products()

    budget = int(input("Enter your budget: "))

    result = filter_by_budget(products, budget)

    if result:
        print("\nProducts within your budget:")

        for product in result:
            print(product["name"], "-", product["price"])
    else:
        print("No products available within your budget.")