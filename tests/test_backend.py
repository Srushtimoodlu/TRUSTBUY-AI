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
from backend.cart import (
    add_to_cart,
    remove_from_cart,
    view_cart,
    calculate_total
)

from backend.auth import register_user, login_user


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
    def test_trust_score_missing_seller(self):

        reviews = load_json("reviews.json")

        result = get_trust_data(
            self.products, reviews, "P004", []
        )

        score = calculate_trust_score(result)

        self.assertIsNone(result["seller_data"])
        self.assertEqual(score, 49.3)
    def test_trust_score_no_reviews(self):

        sellers = load_json("sellers.json")

        result = get_trust_data(
            self.products, [], "P004", sellers
        )

        score = calculate_trust_score(result)

        self.assertEqual(result["review_count"], 0)
        self.assertEqual(score, 78.3)
    def test_add_to_cart(self):

        cart = {}

        result = add_to_cart(
            self.products,
            cart,
            "P004",
            1
        )

        self.assertEqual(result, "Product added to cart")
        self.assertEqual(cart["P004"], 1)
    def test_remove_from_cart(self):

        cart = {"P004": 1}

        result = remove_from_cart(cart, "P004")

        self.assertEqual(result, "Product removed from cart")
        self.assertNotIn("P004", cart)
    def test_view_cart(self):

        cart = {"P004": 2}

        result = view_cart(self.products, cart)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Galaxy M15")
        self.assertEqual(result[0]["quantity"], 2)
    def test_calculate_cart_total(self):

        cart = {"P004": 2}

        result = calculate_total(self.products, cart)

        self.assertEqual(result, 31998)
    def test_add_to_cart_exceeds_stock(self):

        cart = {}

        result = add_to_cart(
            self.products,
            cart,
            "P012",
            1
        )

        self.assertEqual(result, "Not enough stock available")
        self.assertNotIn("P012", cart)
    def test_add_to_cart_invalid_quantity(self):

        cart = {}

        result = add_to_cart(
            self.products,
            cart,
            "P004",
            0
        )

        self.assertEqual(result, "Invalid quantity")
        self.assertEqual(cart, {})
    def test_remove_missing_product(self):

        cart = {}

        result = remove_from_cart(cart, "P004")

        self.assertEqual(result, "Product not found in cart")
        self.assertEqual(cart, {})

    def test_register_invalid_password(self):

        result = register_user(
            "Test User",
            "testuser@example.com",
            "123"
        )

        self.assertEqual(
            result,
            "Enter valid details and a password of at least 8 characters"
        )
    def test_register_empty_name(self):

        result = register_user(
            "",
            "emptyname@example.com",
            "password123"
        )

        self.assertEqual(
            result,
            "Enter valid details and a password of at least 8 characters"
        )
    def test_register_empty_email(self):

        result = register_user(
            "Test User",
            "",
            "password123"
        )

        self.assertEqual(
            result,
            "Enter valid details and a password of at least 8 characters"
        )
    def test_successful_login(self):

        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        with TemporaryDirectory() as temp_dir:

            test_file = Path(temp_dir) / "users.json"
            test_file.write_text("[]", encoding="utf-8")

            with patch("backend.auth.DATA_FILE", test_file):

                register_result = register_user(
                    "Test User",
                    "login_test@example.com",
                    "password123"
                )

                login_result = login_user(
                    "login_test@example.com",
                    "password123"
                )

                self.assertEqual(register_result, "Registration successful")
                self.assertEqual(login_result, "Login successful")

    def test_incorrect_password(self):

        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        with TemporaryDirectory() as temp_dir:

            test_file = Path(temp_dir) / "users.json"
            test_file.write_text("[]", encoding="utf-8")

            with patch("backend.auth.DATA_FILE", test_file):

                register_user(
                    "Test User",
                    "wrongpass_test@example.com",
                    "password123"
                    )

                result = login_user(
                    "wrongpass_test@example.com",
                    "wrongpassword"
                )

                self.assertEqual(result, "Incorrect password")
    def test_login_unknown_user(self):

        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        with TemporaryDirectory() as temp_dir:

            test_file = Path(temp_dir) / "users.json"
            test_file.write_text("[]", encoding="utf-8")

            with patch("backend.auth.DATA_FILE", test_file):

                result = login_user(
                    "unknown@example.com",
                    "password123"
                )

                self.assertEqual(result, "User not found")


if __name__ == "__main__":
    unittest.main()