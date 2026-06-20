"""Baseline entry point for loading and printing cloud kitchen seed data."""

from copy import deepcopy
from datetime import date, datetime

from seed_data import inventory, orders, recipes, restock, status


def load_recipes():
    """Return the seeded recipe records for use in the application."""
    # Assumption to verify: importing these module-level lists directly is acceptable
    # for Task 1, and we do not yet need defensive copying or a database/file loader.
    return recipes


def print_recipes(recipe_data):
    """Print every recipe and its ingredient requirements to the console."""
    print("\n=== Recipes ===")
    for recipe in recipe_data:
        print(f"Recipe ID: {recipe['recipe_id']}")
        print(f"Name: {recipe['name']}")
        print("Ingredients:")
        for ingredient in recipe["ingredients"]:
            print(f"  - {ingredient['name']}: {ingredient['qty_grams']} grams")
        print()


def load_inventory():
    """Return the seeded inventory records for the simulation."""
    # Assumption to verify: inventory quantities are intentionally stored in grams
    # for every ingredient, including items like buns that might later use unit counts.
    return inventory


def print_inventory(inventory_data):
    """Print every inventory item with quantity and expiry information."""
    print("\n=== Inventory ===")
    for item in inventory_data:
        print(f"Ingredient: {item['ingredient']}")
        print(f"Quantity: {item['qty_grams']} grams")
        print(f"Expiry Date: {item['expiry_date']}")
        print()


def load_orders():
    """Return the seeded customer order records."""
    # Assumption to verify: order item names are expected to match recipe names exactly.
    return orders


def print_orders(order_data):
    """Print every order, including its brand and requested items."""
    print("\n=== Orders ===")
    for order in order_data:
        print(f"Order ID: {order['order_id']}")
        print(f"Brand: {order['brand']}")
        print("Items:")
        for item in order["items"]:
            print(f"  - {item['item']}: {item['qty']}")
        print()


def load_restock():
    """Return the seeded restock recommendations."""
    # Incomplete / follow-up: the seed table is still available for baseline loading
    # tests, but the live restock output is now recalculated from final inventory.
    return restock


def print_restock(restock_data):
    """Print every restock item with quantity needed and reason."""
    print("\n=== Restock ===")
    for item in restock_data:
        print(f"Item: {item['item']}")
        print(f"Quantity Needed: {item['qty_needed_grams']} grams")
        print(f"Reason: {item['reason']}")
        print()


def load_status():
    """Return the seeded delivery status records."""
    # Uncertain: it is not yet clear whether status should remain independent seed
    # data or later be derived from order fulfillment results in the simulation.
    return status


def print_status(status_data):
    """Print every order status with delivery result and remark."""
    print("\n=== Status ===")
    for entry in status_data:
        print(f"Order ID: {entry['order_id']}")
        print(f"Delivered: {entry['delivered']}")
        print(f"Remark: {entry['remark']}")
        print()


def find_recipe_by_name(recipe_data, item_name):
    """Return the recipe that matches an order item name, or None if missing."""
    # Step 1: look through the recipe table for a recipe whose name matches
    # the order item exactly so we can determine the required ingredients.
    # Assumption to verify: recipe lookup currently relies on exact name matching
    # between Orders.item and Recipes.name, with no normalization or aliases.
    for recipe in recipe_data:
        if recipe["name"] == item_name:
            return recipe
    # Assumption to verify: case-insensitive matching, trimming, or brand-specific
    # recipe variants are not needed yet for successful recipe lookup.
    return None


def calculate_ingredient_requirements(recipe, quantity):
    """Return the total grams required for each ingredient in an order item."""
    requirements = []

    # Step 2: multiply each recipe ingredient quantity by the ordered item count
    # so we know the total grams needed to prepare that order item.
    for ingredient in recipe["ingredients"]:
        requirements.append(
            {
                "name": ingredient["name"],
                "required_qty_grams": ingredient["qty_grams"] * quantity,
            }
        )

    return requirements


def check_inventory_availability(inventory_data, requirements):
    """Check whether inventory contains every required ingredient in enough quantity."""
    inventory_lookup = {item["ingredient"]: item for item in inventory_data}
    availability_results = []
    all_available = True

    # Step 3: compare each required ingredient against the inventory table to see
    # whether it exists and whether the available grams are sufficient.
    for requirement in requirements:
        inventory_item = inventory_lookup.get(requirement["name"])
        available_qty = inventory_item["qty_grams"] if inventory_item else 0
        is_available = inventory_item is not None and available_qty >= requirement["required_qty_grams"]

        availability_results.append(
            {
                "ingredient": requirement["name"],
                "required_qty_grams": requirement["required_qty_grams"],
                "available_qty_grams": available_qty,
                "is_available": is_available,
            }
        )

        if not is_available:
            all_available = False

    return {"all_available": all_available, "details": availability_results}


def combine_requirements(requirement_groups):
    """Merge repeated ingredient requirements into a single total per ingredient."""
    combined_requirements = {}

    # Step 2: combine ingredient demand across all items in the same order so
    # fulfillment is checked against the total grams needed for the entire order.
    for requirements in requirement_groups:
        for requirement in requirements:
            ingredient_name = requirement["name"]
            combined_requirements.setdefault(ingredient_name, 0)
            combined_requirements[ingredient_name] += requirement["required_qty_grams"]

    return [
        {"name": ingredient_name, "required_qty_grams": required_qty}
        for ingredient_name, required_qty in combined_requirements.items()
    ]


def deduct_inventory(inventory_data, requirements):
    """Subtract the used ingredient grams from inventory after a successful order."""
    inventory_lookup = {item["ingredient"]: item for item in inventory_data}

    # Step 4: deduct only after the full order passes the availability check so
    # we do not partially consume stock for orders that cannot be delivered.
    # Assumption to verify: partial stock should not be deducted for failed orders;
    # inventory changes only when the entire order is considered deliverable.
    for requirement in requirements:
        inventory_lookup[requirement["name"]]["qty_grams"] -= requirement["required_qty_grams"]


def apply_final_inventory_snapshot(inventory_data, final_inventory_data):
    """Copy the final cumulative inventory quantities back into the main table."""
    final_inventory_lookup = {
        item["ingredient"]: item["qty_grams"] for item in final_inventory_data
    }

    # Step 6: update the final inventory table only after all orders have been
    # processed so the printed inventory reflects the true remaining stock.
    for item in inventory_data:
        if item["ingredient"] in final_inventory_lookup:
            item["qty_grams"] = final_inventory_lookup[item["ingredient"]]


def update_status_entry(status_data, order_id, delivered, remark):
    """Update or create a status-table entry for a processed order."""
    for entry in status_data:
        if entry["order_id"] == order_id:
            entry["delivered"] = delivered
            entry["remark"] = remark
            return

    # Incomplete / follow-up: if later tasks formalize a stricter schema, we may
    # want to prevent new status rows and require every order to exist up front.
    status_data.append({"order_id": order_id, "delivered": delivered, "remark": remark})


def calculate_restock_needs(inventory_data, reference_date=None):
    """Build restock recommendations from final inventory using the Task 5 rules."""
    if reference_date is None:
        # Assumption to verify: when no simulation date is passed in, the code uses
        # Python's date.today() from the local runtime environment as "today."
        # Please verify this matches the intended simulation date basis.
        reference_date = date.today()

    restock_recommendations = []

    for item in inventory_data:
        expiry_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d").date()
        days_until_expiry = (expiry_date - reference_date).days
        restock_reason = None
        qty_needed_grams = 0

        # Rule 1: ingredients expiring within the next 5 days are restocked to a
        # full 10,000 grams, and this rule takes priority over the stock rules below.
        # Assumption to verify: an ingredient cannot be labeled with both "Expiring soon"
        # and "Running low on stock" at the same time in the output; expiry takes
        # priority because these checks are evaluated in order with elif branches.
        if 0 <= days_until_expiry <= 5:
            restock_reason = "Expiring soon"
            qty_needed_grams = 10000
        # Rule 2: if the final stock reaches exactly 0 grams, mark it out of stock
        # and request a full 10,000-gram refill.
        elif item["qty_grams"] == 0:
            restock_reason = "Out of stock"
            qty_needed_grams = 10000
        # Rule 3: if stock is low but not empty, request only the grams needed to
        # bring the ingredient back up to the 10,000-gram target.
        elif item["qty_grams"] <= 1000:
            restock_reason = "Running low on stock"
            qty_needed_grams = 10000 - item["qty_grams"]

        if restock_reason is not None:
            restock_recommendations.append(
                {
                    "item": item["ingredient"],
                    "qty_needed_grams": qty_needed_grams,
                    "reason": restock_reason,
                }
            )

    return restock_recommendations


def refresh_restock_table(restock_data, inventory_data, reference_date=None):
    """Replace the live restock table with recommendations from final inventory."""
    # Step 7: rebuild the restock table after all orders have been processed so it
    # reflects the final inventory state instead of intermediate order failures.
    # Incomplete / follow-up: this replaces the whole restock table each run, so it
    # does not preserve historical/manual restock notes outside the current simulation.
    restock_data.clear()
    restock_data.extend(calculate_restock_needs(inventory_data, reference_date))


def process_orders(
    recipe_data,
    inventory_data,
    order_data,
    status_data,
    restock_data,
    reference_date=None,
):
    """Process orders, update fulfillment status, deduct inventory, and add restocks."""
    processed_orders = []
    working_inventory = deepcopy(inventory_data)

    # Step 0: use a working inventory snapshot during processing so each order is
    # checked against stock remaining after previous successful orders, while the
    # final inventory table is only updated once the full order list is complete.
    # Assumption to verify: working_inventory is a deep copy, not a shared reference,
    # so interim deductions during processing do not immediately mutate inventory_data.
    # Incomplete / follow-up: this remains an in-memory simulation only; later tasks
    # may need transaction handling or persistence if inventory state is stored externally.

    for order in order_data:
        order_result = {
            "order_id": order["order_id"],
            "brand": order["brand"],
            "items": [],
            "order_requirements": [],
            "inventory_check": None,
            "fulfilled": False,
            "reason": "",
        }
        requirement_groups = []
        missing_recipe_items = []

        for item in order["items"]:
            # Step 1: find the recipe for the ordered menu item.
            recipe = find_recipe_by_name(recipe_data, item["item"])

            if recipe is None:
                # If an order item has no matching recipe, we do not stop the program
                # or attempt substitution. We record recipe_found=False, skip demand
                # calculation and inventory checking for that item, and continue.
                # Incomplete / follow-up: later tasks may convert this into a formal
                # rejection reason, validation error, or fulfillment status update.
                order_result["items"].append(
                    {
                        "item": item["item"],
                        "qty": item["qty"],
                        "recipe_found": False,
                        "requirements": [],
                    }
                )
                missing_recipe_items.append(item["item"])
                continue

            # Step 2: calculate the total ingredient grams needed for this order item.
            requirements = calculate_ingredient_requirements(recipe, item["qty"])
            requirement_groups.append(requirements)

            order_result["items"].append(
                {
                    "item": item["item"],
                    "qty": item["qty"],
                    "recipe_found": True,
                    "requirements": requirements,
                }
            )

        order_requirements = combine_requirements(requirement_groups)
        order_result["order_requirements"] = order_requirements

        # Step 3: check the inventory table against the total ingredient demand for
        # the whole order, not just individual items, before deciding fulfillment.
        # Because this uses working_inventory, Order 2 is checked against whatever
        # stock remains after Order 1 was successfully served.
        # If two orders compete for the same ingredient, the earlier successful order
        # consumes from working_inventory first, and the later order is evaluated
        # against the reduced quantity that remains.
        inventory_check = check_inventory_availability(working_inventory, order_requirements)
        order_result["inventory_check"] = inventory_check

        missing_ingredients = [
            detail for detail in inventory_check["details"] if not detail["is_available"]
        ]

        if missing_recipe_items:
            reason_parts = [
                "No matching recipe for item(s): " + ", ".join(missing_recipe_items)
            ]
            if missing_ingredients:
                reason_parts.append(
                    "Missing or insufficient ingredients: "
                    + ", ".join(detail["ingredient"] for detail in missing_ingredients)
                )

            order_result["fulfilled"] = False
            order_result["reason"] = " | ".join(reason_parts)
            update_status_entry(status_data, order["order_id"], False, order_result["reason"])
        elif inventory_check["all_available"]:
            # Step 4: when every required ingredient is available, mark the order as
            # delivered and deduct the used grams from the working inventory only.
            deduct_inventory(working_inventory, order_requirements)
            order_result["fulfilled"] = True
            order_result["reason"] = "Delivered"
            update_status_entry(status_data, order["order_id"], True, "Delivered")
        else:
            # Step 5: when any ingredient is missing or insufficient, do not deduct
            # inventory. Mark the order as not delivered, record the reason, and add
            # the shortage reason to status. The final restock table is rebuilt later
            # from ending inventory according to the Task 5 expiry/stock rules.
            # Assumption to verify: this flow rejects the full order rather than
            # allowing partial fulfillment of the items that do have enough stock.
            missing_names = ", ".join(detail["ingredient"] for detail in missing_ingredients)
            order_result["fulfilled"] = False
            order_result["reason"] = f"Missing or insufficient ingredients: {missing_names}"
            update_status_entry(status_data, order["order_id"], False, order_result["reason"])

        processed_orders.append(order_result)

    apply_final_inventory_snapshot(inventory_data, working_inventory)
    refresh_restock_table(restock_data, inventory_data, reference_date)

    return processed_orders


def print_order_processing_results(processed_orders):
    """Print recipe lookup, ingredient demand, inventory checks, and fulfillment."""
    print("\n=== Order Processing ===")
    for order in processed_orders:
        print(f"Order ID: {order['order_id']}")
        print(f"Brand: {order['brand']}")

        for item in order["items"]:
            print(f"Item: {item['item']}")
            print(f"Quantity Ordered: {item['qty']}")
            print(f"Recipe Found: {item['recipe_found']}")

            if not item["recipe_found"]:
                print("Inventory Check: Skipped because the recipe was not found.")
                print()
                continue

            print("Required Ingredients:")
            for requirement in item["requirements"]:
                print(
                    f"  - {requirement['name']}: "
                    f"{requirement['required_qty_grams']} grams required"
                )

            print()

        print("Combined Order Requirements:")
        for requirement in order["order_requirements"]:
            print(f"  - {requirement['name']}: {requirement['required_qty_grams']} grams required")

        print(f"All Ingredients Available: {order['inventory_check']['all_available']}")
        print("Inventory Details:")
        for detail in order["inventory_check"]["details"]:
            print(
                f"  - {detail['ingredient']}: "
                f"required={detail['required_qty_grams']} grams, "
                f"available={detail['available_qty_grams']} grams, "
                f"enough={detail['is_available']}"
            )

        print(f"Fulfilled: {order['fulfilled']}")
        print(f"Reason: {order['reason']}")
        print()


def main():
    """Load seed tables, process fulfillment, and print the updated results."""
    # Assumption to verify: we process working copies of mutable tables so the seed
    # definitions stay unchanged across runs and tests.
    # Incomplete / follow-up: this script still prints results directly to the console
    # and does not yet persist updated inventory, restock, or status tables anywhere.
    recipe_data = load_recipes()
    inventory_data = deepcopy(load_inventory())
    order_data = load_orders()
    # Step 8: start with an empty live restock table because recommendations are
    # now generated from final inventory after all orders have been processed.
    restock_data = []
    status_data = deepcopy(load_status())
    processed_orders = process_orders(
        recipe_data,
        inventory_data,
        order_data,
        status_data,
        restock_data,
    )

    print_recipes(recipe_data)
    print_orders(order_data)
    print_order_processing_results(processed_orders)
    print_inventory(inventory_data)
    print_restock(restock_data)
    print_status(status_data)


if __name__ == "__main__":
    main()
