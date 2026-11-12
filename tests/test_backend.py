import unittest
from backend.database import load_products
from backend.search import search_products
from backend.filters import filter_by_budget
from backend.category import filter_by_category
from backend.inventory import check_stock
from backend.comparison import compare_products
from backend.trust_score import (
    get_trust_data,
    calculate_trust_score,
    load_json
)


class TestBackend(unittest.TestCase):

    def setUp(self):
        self.products = load_products()

    def test_database_loading(self):
        self.assertGreater(len(self.products), 0)

    def test_product_search(self):
        result = search_products(self.products, "Laptop A")
        self.assertTrue(any(p["id"] == "P001" for p in result))

    def test_budget_filter(self):
        result = filter_by_budget(self.products, 45000)
        self.assertTrue(all(p["price"] <= 45000 for p in result))

    def test_category_filter(self):
        result = filter_by_category(self.products, "laptop")
        self.assertTrue(all(p["category"].lower() == "laptop" for p in result))

    def test_stock_available(self):
        self.assertEqual(check_stock(self.products, "P001"), "Available")

    def test_stock_unavailable(self):
        self.assertEqual(check_stock(self.products, "P002"), "Out of stock")

    def test_product_not_found(self):
        self.assertEqual(check_stock(self.products, "P999"), "Product not found")

    def test_product_comparison(self):
        result = compare_products(self.products, ["P001", "P002"])
        found_ids = [p["id"] for p in result]
        self.assertIn("P001", found_ids)
        self.assertIn("P002", found_ids)

    def test_trust_data(self):
        import json
        from pathlib import Path

        reviews_file = Path(__file__).resolve().parent.parent / "data" / "reviews.json"

        with open(reviews_file, "r", encoding="utf-8") as file:
            reviews = json.load(file)

        result = get_trust_data(self.products, reviews, "P001")
        self.assertIsNotNone(result)
        self.assertEqual(result["product_id"], "P001")
    def test_trust_score_p004(self):

        reviews = load_json("reviews.json")
        sellers = load_json("sellers.json")

        result = get_trust_data(
            self.products, reviews, "P004", sellers
        )

        score = calculate_trust_score(result)

        self.assertEqual(score, 91.8)


    def test_trust_score_p012(self):

        reviews = load_json("reviews.json")
        sellers = load_json("sellers.json")

        result = get_trust_data(
            self.products, reviews, "P012", sellers
        )

        score = calculate_trust_score(result)

        self.assertEqual(score, 53.5)


    def test_trust_score_invalid_product(self):

        reviews = load_json("reviews.json")
        sellers = load_json("sellers.json")

        result = get_trust_data(
            self.products, reviews, "P999", sellers
        )

        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()