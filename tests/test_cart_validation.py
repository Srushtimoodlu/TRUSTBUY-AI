import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

url = "http://127.0.0.1:5000/cart/add"

data = {
    "product_id": "P012",
    "quantity": 1
}

request = Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urlopen(request) as response:
        print("Status Code:", response.status)
        print(response.read().decode("utf-8"))

except HTTPError as error:
    print("Status Code:", error.code)
    print(error.read().decode("utf-8"))