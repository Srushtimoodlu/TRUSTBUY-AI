import json
from urllib.request import Request, urlopen

url = "http://127.0.0.1:5000/cart/add"

data = {
    "product_id": "P004",
    "quantity": 1
}

request = Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

    print("Status Code:", response.status)
    print("Response:")
    print(json.dumps(result, indent=4))