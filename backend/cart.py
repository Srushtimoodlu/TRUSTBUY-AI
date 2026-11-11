def add_to_cart(products, cart, product_id, quantity):

    if quantity <= 0:
        return "Invalid quantity"

    for product in products:

        if product["id"] == product_id:

            current_quantity = cart.get(product_id, 0)

            if current_quantity + quantity > product["stock"]:
                return "Not enough stock available"

            cart[product_id] = current_quantity + quantity

            return "Product added to cart"

    return "Product not found"


def remove_from_cart(cart, product_id):

    if product_id in cart:
        del cart[product_id]
        return "Product removed from cart"

    return "Product not found in cart"


def view_cart(products, cart):

    result = []

    for product in products:

        if product["id"] in cart:

            item = {
                "name": product["name"],
                "price": product["price"],
                "quantity": cart[product["id"]],
                "subtotal": product["price"] * cart[product["id"]]
            }

            result.append(item)

    return result


def calculate_total(products, cart):

    total = 0

    for product in products:

        if product["id"] in cart:

            total += product["price"] * cart[product["id"]]

    return total


if __name__ == "__main__":

    from backend.database import load_products

    products = load_products()
    cart = {}

    product_id = input("Enter product ID: ")
    quantity = int(input("Enter quantity: "))

    approval = input("Do you approve adding this product? (yes/no): ")

    if approval.lower() == "yes":

        message = add_to_cart(products, cart, product_id, quantity)
        print(message)

        if message == "Product added to cart":

            print("\nYOUR CART")

            for item in view_cart(products, cart):
                print(item)

            print("Total:", calculate_total(products, cart))

    else:
        print("Product was not added.")