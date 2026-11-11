import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "products.json"
)

def load_products():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    products = load_products()

    for product in products:
        print(product["name"], product["price"])