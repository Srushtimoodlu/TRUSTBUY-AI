# TRUSTBUY AI - Backend API Documentation

Base URL: http://127.0.0.1:5000

## 1. General APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Check backend |
| GET | /health | Health status |
| GET | /products | Get all products |
| GET | /product?product_id=P004 | Get one product |
| GET | /products/count | Count products |
| GET | /categories | Get categories |
| GET | /price-range | Get price range |

## 2. Search and Filtering

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /search?keyword=Galaxy | Search products |
| GET | /budget?amount=20000 | Filter by budget |
| GET | /category?name=mobile | Filter by category |
| GET | /sort?order=low-to-high | Sort by price |
| GET | /products/page?page=1&limit=5 | Paginate products |

## 3. Product Information

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /stock?product_id=P004 | Check stock |
| GET | /compare?ids=P004,P005 | Compare products |
| GET | /trust-score?product_id=P004 | Get trust score |
| GET | /reviews?product_id=P004 | Get reviews |
| GET | /seller?product_id=P004 | Get seller details |

## 4. Cart APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /cart/add | Add product |
| GET | /cart | View cart |
| DELETE | /cart/remove | Remove product |

## 5. Authentication APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /register | Register user |
| POST | /login | Login user |

## Notes

- All responses use JSON.
- Query parameters are used for GET requests.
- POST and DELETE requests use JSON request bodies where required.
- The current database contains mock product, seller and review data.
- The Flask development server is for local testing.
