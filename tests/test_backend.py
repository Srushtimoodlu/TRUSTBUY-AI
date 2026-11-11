import unittest
from backend.database import load_products
from backend.search import search_products
from backend.filters import filter_by_budget
from backend.category import filter_by_category
from backend.inventory import check_stock
from backend.comparison import compare_products
from backend.trust_score import get_trust_data


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


if __name__ == "__main__":
    unittest.main()