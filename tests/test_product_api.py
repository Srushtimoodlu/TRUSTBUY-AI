import json
from urllib.request import urlopen
from urllib.error import HTTPError

BASE_URL = "http://127.0.0.1:5000"


# Test 1: Existing product
print("\nTEST 1: Existing product")

with urlopen(BASE_URL + "/product?product_id=P004") as response:
    data = json.loads(response.read().decode("utf-8"))
    print("Status:", response.status)
    print("Product:", data["name"])


# Test 2: Invalid product ID
print("\nTEST 2: Invalid product ID")

try:
    urlopen(BASE_URL + "/product?product_id=P999")
except HTTPError as error:
    data = json.loads(error.read().decode("utf-8"))
    print("Status:", error.code)
    print("Message:", data["error"])


# Test 3: Missing product ID
print("\nTEST 3: Missing product ID")

try:
    urlopen(BASE_URL + "/product")
except HTTPError as error:
    data = json.loads(error.read().decode("utf-8"))
    print("Status:", error.code)
    print("Message:", data["error"])