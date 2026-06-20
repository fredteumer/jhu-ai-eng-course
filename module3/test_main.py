"""Unit tests for the baseline seed-data loading functions."""

from copy import deepcopy
from datetime import date
import unittest

from main import (
    calculate_ingredient_requirements,
    calculate_restock_needs,
    find_recipe_by_name,
    load_inventory,
    load_orders,
    load_recipes,
    load_restock,
    load_status,
    process_orders,
)


class TestLoadFunctions(unittest.TestCase):
    """Verify the Task 1 data-loading helpers return the expected seed tables."""

    def test_loads_all_five_tables_successfully(self):
        """Each load function should return a non-empty list from seed_data."""
        # Assumption to verify: Task 1 considers a successful import equivalent to
        # each loader returning the seeded module-level list without raising errors.
        self.assertIsInstance(load_recipes(), list)
        self.assertIsInstance(load_inventory(), list)
        self.assertIsInstance(load_orders(), list)
        self.assertIsInstance(load_restock(), list)
        self.assertIsInstance(load_status(), list)

        self.assertGreater(len(load_recipes()), 0)
        self.assertGreater(len(load_inventory()), 0)
        self.assertGreater(len(load_orders()), 0)
        self.assertGreater(len(load_restock()), 0)
        self.assertGreater(len(load_status()), 0)

    def test_record_counts_match_seed_data(self):
        """Each load function should return the expected number of seed records."""
        self.assertEqual(len(load_recipes()), 5)
        self.assertEqual(len(load_inventory()), 14)
        self.assertEqual(len(load_orders()), 5)
        self.assertEqual(len(load_restock()), 5)
        self.assertEqual(len(load_status()), 5)

    def test_recipe_key_field_types(self):
        """Recipe records should expose the expected identifier and ingredient types."""
        recipe = load_recipes()[0]
        ingredient = recipe["ingredients"][0]

        self.assertIsInstance(recipe["recipe_id"], int)
        self.assertIsInstance(recipe["name"], str)
        self.assertIsInstance(recipe["ingredients"], list)
        self.assertIsInstance(ingredient["name"], str)
        self.assertIsInstance(ingredient["qty_grams"], (int, float))

    def test_inventory_key_field_types(self):
        """Inventory records should provide valid quantity and expiry field types."""
        item = load_inventory()[0]

        self.assertIsInstance(item["ingredient"], str)
        self.assertIsInstance(item["qty_grams"], (int, float))
        self.assertIsInstance(item["expiry_date"], str)

    def test_order_key_field_types(self):
        """Order records should expose valid identifiers, brands, and quantities."""
        order = load_orders()[0]
        item = order["items"][0]

        self.assertIsInstance(order["order_id"], int)
        self.assertIsInstance(order["brand"], str)
        self.assertIsInstance(order["items"], list)
        self.assertIsInstance(item["item"], str)
        self.assertIsInstance(item["qty"], int)

    def test_restock_key_field_types(self):
        """Restock records should provide an item name, numeric quantity, and reason."""
        item = load_restock()[0]

        self.assertIsInstance(item["item"], str)
        self.assertIsInstance(item["qty_needed_grams"], (int, float))
        self.assertIsInstance(item["reason"], str)

    def test_status_key_field_types(self):
        """Status records should provide order linkage and delivery state types."""
        item = load_status()[0]

        self.assertIsInstance(item["order_id"], int)
        self.assertIsInstance(item["delivered"], bool)
        self.assertIsInstance(item["remark"], str)
        # Incomplete / follow-up: if the project later formalizes a status enum or
        # richer state machine, these tests should be expanded beyond simple types.


class TestOrderRecipeLookup(unittest.TestCase):
    """Verify order items can be matched to recipes and scaled correctly."""

    def test_find_recipe_by_name_returns_matching_recipe(self):
        """A valid order item should return its matching recipe record."""
        recipe = find_recipe_by_name(load_recipes(), "Chicken Burger")

        self.assertIsNotNone(recipe)
        self.assertEqual(recipe["recipe_id"], 2)
        self.assertEqual(recipe["name"], "Chicken Burger")

    def test_find_recipe_by_name_handles_missing_recipe_gracefully(self):
        """A missing order item should return None instead of raising an error."""
        recipe = find_recipe_by_name(load_recipes(), "Paneer Wrap")

        self.assertIsNone(recipe)

    def test_calculate_ingredient_requirements_scales_for_quantity_two(self):
        """Ingredient requirements should double when the order quantity is two."""
        recipe = find_recipe_by_name(load_recipes(), "Margherita Pizza")
        requirements = calculate_ingredient_requirements(recipe, 2)

        expected_requirements = [
            {"name": "Flour", "required_qty_grams": 600},
            {"name": "Tomato Sauce", "required_qty_grams": 200},
            {"name": "Mozzarella Cheese", "required_qty_grams": 300},
        ]

        self.assertEqual(requirements, expected_requirements)


class TestOrderFulfillment(unittest.TestCase):
    """Verify fulfillment updates status, restock, and inventory correctly."""

    def test_process_orders_marks_delivered_when_ingredients_are_available(self):
        """An order with sufficient stock should be marked as delivered."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        status_data = deepcopy(load_status())
        restock_data = deepcopy(load_restock())
        order_data = [
            {
                "order_id": 101,
                "brand": "Test Kitchen",
                "items": [{"item": "Chicken Burger", "qty": 1}],
            }
        ]

        processed_orders = process_orders(
            recipe_data, inventory_data, order_data, status_data, restock_data
        )

        self.assertTrue(processed_orders[0]["fulfilled"])
        self.assertEqual(processed_orders[0]["reason"], "Delivered")
        self.assertEqual(status_data[-1]["order_id"], 101)
        self.assertTrue(status_data[-1]["delivered"])
        self.assertEqual(status_data[-1]["remark"], "Delivered")

    def test_process_orders_marks_not_delivered_and_adds_missing_item_to_restock(self):
        """An order with a missing ingredient should fail and log the shortage."""
        recipe_data = [
            {
                "recipe_id": 1,
                "name": "Test Wrap",
                "ingredients": [
                    {"name": "Chicken Breast", "qty_grams": 200},
                    {"name": "Bun", "qty_grams": 100},
                ],
            }
        ]
        inventory_data = [
            {"ingredient": "Chicken Breast", "qty_grams": 500, "expiry_date": "2026-12-31"},
            {"ingredient": "Bun", "qty_grams": 0, "expiry_date": "2026-12-31"},
        ]
        order_data = [
            {"order_id": 202, "brand": "Test Kitchen", "items": [{"item": "Test Wrap", "qty": 1}]}
        ]
        status_data = []
        restock_data = []

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=date(2026, 6, 3),
        )

        self.assertFalse(processed_orders[0]["fulfilled"])
        self.assertIn("Missing or insufficient ingredients: Bun", processed_orders[0]["reason"])
        self.assertEqual(status_data[0]["order_id"], 202)
        self.assertFalse(status_data[0]["delivered"])
        self.assertIn("Bun", status_data[0]["remark"])
        bun_restock = next(item for item in restock_data if item["item"] == "Bun")
        self.assertEqual(bun_restock["qty_needed_grams"], 10000)
        self.assertEqual(bun_restock["reason"], "Out of stock")

    def test_process_orders_deducts_inventory_after_successful_delivery(self):
        """A delivered order should reduce inventory by the required grams."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        status_data = []
        restock_data = []
        order_data = [
            {
                "order_id": 303,
                "brand": "Test Kitchen",
                "items": [{"item": "Margherita Pizza", "qty": 2}],
            }
        ]

        original_flour_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour"
        )
        original_sauce_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Tomato Sauce"
        )
        original_cheese_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Mozzarella Cheese"
        )

        process_orders(recipe_data, inventory_data, order_data, status_data, restock_data)

        updated_flour_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour"
        )
        updated_sauce_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Tomato Sauce"
        )
        updated_cheese_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Mozzarella Cheese"
        )

        self.assertEqual(updated_flour_qty, original_flour_qty - 600)
        self.assertEqual(updated_sauce_qty, original_sauce_qty - 200)
        self.assertEqual(updated_cheese_qty, original_cheese_qty - 300)


class TestCumulativeInventoryDeduction(unittest.TestCase):
    """Verify inventory is consumed cumulatively across sequential orders."""

    def test_two_orders_consuming_same_ingredient_use_combined_deduction(self):
        """Two delivered orders should deduct the combined shared ingredient total."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        status_data = []
        restock_data = []
        order_data = [
            {"order_id": 401, "brand": "Test Kitchen", "items": [{"item": "Margherita Pizza", "qty": 1}]},
            {"order_id": 402, "brand": "Test Kitchen", "items": [{"item": "Chocolate Cake", "qty": 1}]},
        ]

        original_flour_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour"
        )

        processed_orders = process_orders(
            recipe_data, inventory_data, order_data, status_data, restock_data
        )

        updated_flour_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour"
        )

        self.assertTrue(processed_orders[0]["fulfilled"])
        self.assertTrue(processed_orders[1]["fulfilled"])
        self.assertEqual(updated_flour_qty, original_flour_qty - 550)

    def test_later_order_fails_after_prior_order_consumes_remaining_stock(self):
        """A later order should fail if an earlier order uses the remaining shared stock."""
        recipe_data = [
            {
                "recipe_id": 1,
                "name": "First Dish",
                "ingredients": [{"name": "Cheese", "qty_grams": 600}],
            },
            {
                "recipe_id": 2,
                "name": "Second Dish",
                "ingredients": [{"name": "Cheese", "qty_grams": 500}],
            },
        ]
        inventory_data = [
            {"ingredient": "Cheese", "qty_grams": 1000, "expiry_date": "2026-12-31"}
        ]
        order_data = [
            {"order_id": 501, "brand": "Test Kitchen", "items": [{"item": "First Dish", "qty": 1}]},
            {"order_id": 502, "brand": "Test Kitchen", "items": [{"item": "Second Dish", "qty": 1}]},
        ]
        status_data = []
        restock_data = []

        processed_orders = process_orders(
            recipe_data,
            inventory_data,
            order_data,
            status_data,
            restock_data,
            reference_date=date(2026, 6, 3),
        )

        self.assertTrue(processed_orders[0]["fulfilled"])
        self.assertFalse(processed_orders[1]["fulfilled"])
        self.assertIn("Cheese", processed_orders[1]["reason"])
        self.assertEqual(status_data[1]["order_id"], 502)
        self.assertFalse(status_data[1]["delivered"])
        self.assertEqual(restock_data[0]["item"], "Cheese")
        self.assertEqual(restock_data[0]["qty_needed_grams"], 9600)
        self.assertEqual(restock_data[0]["reason"], "Running low on stock")

    def test_final_inventory_matches_expected_remaining_quantities(self):
        """Final inventory should reflect all successful cumulative deductions."""
        recipe_data = deepcopy(load_recipes())
        inventory_data = deepcopy(load_inventory())
        status_data = []
        restock_data = []
        order_data = [
            {"order_id": 601, "brand": "Test Kitchen", "items": [{"item": "Margherita Pizza", "qty": 2}]},
            {"order_id": 602, "brand": "Test Kitchen", "items": [{"item": "Chocolate Cake", "qty": 1}]},
        ]

        process_orders(recipe_data, inventory_data, order_data, status_data, restock_data)

        flour_qty = next(item["qty_grams"] for item in inventory_data if item["ingredient"] == "Flour")
        sauce_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Tomato Sauce"
        )
        cheese_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Mozzarella Cheese"
        )
        chocolate_qty = next(
            item["qty_grams"] for item in inventory_data if item["ingredient"] == "Chocolate"
        )
        sugar_qty = next(item["qty_grams"] for item in inventory_data if item["ingredient"] == "Sugar")

        self.assertEqual(flour_qty, 9150)
        self.assertEqual(sauce_qty, 9800)
        self.assertEqual(cheese_qty, 9700)
        self.assertEqual(chocolate_qty, 9850)
        self.assertEqual(sugar_qty, 9900)


class TestRestockRules(unittest.TestCase):
    """Verify the Task 5 rule-based restock calculations."""

    def test_expiring_soon_sets_full_restock_quantity(self):
        """Ingredients expiring within 5 days should be marked as expiring soon."""
        inventory_data = [
            {"ingredient": "Cream", "qty_grams": 7000, "expiry_date": "2026-06-06"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=date(2026, 6, 3))

        self.assertEqual(
            restock_data,
            [{"item": "Cream", "qty_needed_grams": 10000, "reason": "Expiring soon"}],
        )

    def test_out_of_stock_sets_full_restock_quantity(self):
        """Zero final stock should be marked as out of stock with 10,000 grams needed."""
        inventory_data = [
            {"ingredient": "Bun", "qty_grams": 0, "expiry_date": "2026-12-31"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=date(2026, 6, 3))

        self.assertEqual(
            restock_data,
            [{"item": "Bun", "qty_needed_grams": 10000, "reason": "Out of stock"}],
        )

    def test_running_low_calculates_amount_needed_to_reach_ten_thousand(self):
        """Low stock should request only the amount needed to reach 10,000 grams."""
        inventory_data = [
            {"ingredient": "Chicken Breast", "qty_grams": 500, "expiry_date": "2026-12-31"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=date(2026, 6, 3))

        self.assertEqual(
            restock_data,
            [
                {
                    "item": "Chicken Breast",
                    "qty_needed_grams": 9500,
                    "reason": "Running low on stock",
                }
            ],
        )

    def test_adequate_stock_without_expiry_issue_is_not_flagged(self):
        """Adequate stock with no near-expiry condition should not appear in restock."""
        inventory_data = [
            {"ingredient": "Tomato Sauce", "qty_grams": 7000, "expiry_date": "2026-12-31"}
        ]

        restock_data = calculate_restock_needs(inventory_data, reference_date=date(2026, 6, 3))

        self.assertEqual(restock_data, [])


if __name__ == "__main__":
    unittest.main()
