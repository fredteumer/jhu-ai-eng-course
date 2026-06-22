"""Baseline entry point for loading and printing cloud kitchen seed data."""

import argparse
import importlib.util
import os
from copy import deepcopy
from datetime import date, datetime

from seed_data import inventory, orders, recipes, restock, status

# --- Business-rule constants (Requirement 6) -------------------------------
# Pulled out of the restock logic so the kitchen's thresholds live in one
# obvious place and can be tuned without hunting through the code.
PAR_LEVEL_GRAMS = 10000          # Target stock level we restock back up to.
LOW_STOCK_THRESHOLD_GRAMS = 1000  # At or below this (but > 0) = "running low".
EXPIRY_WINDOW_DAYS = 5            # Within this many days of today = "expiring soon".


def load_recipes():
    """Return the seeded recipe records for use in the application."""
    # Assumption to verify: importing these module-level lists directly is acceptable
    # for Task 1, and we do not yet need defensive copying or a database/file loader.
    return recipes


def print_recipes(recipe_data):
    """Print every recipe and its ingredient requirements to the console."""
    print("\n🍽️  === Recipes ===")
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
    print("\n📦 === Inventory ===")
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
    print("\n🧾 === Orders ===")
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
    """Print every restock item with current stock, quantity needed, and reasons."""
    print("\n🔧 === Restock ===")
    for item in restock_data:
        print(f"Item: {item['item']}")
        # Seed-data restock rows use the legacy single 'reason'/no-current-qty
        # schema; recalculated rows use the richer Requirement 6 schema. Support both.
        if "current_qty_grams" in item:
            print(f"Current Quantity: {item['current_qty_grams']} grams")
        print(f"Quantity Needed: {item['qty_needed_grams']} grams")
        reasons = item.get("reasons") or [item.get("reason", "")]
        print(f"Reason(s): {', '.join(reasons)}")
        if "expiry_date" in item:
            print(f"Expiry Date: {item['expiry_date']} (in {item['days_until_expiry']} days)")
        print()


def load_status():
    """Return the seeded delivery status records."""
    # Uncertain: it is not yet clear whether status should remain independent seed
    # data or later be derived from order fulfillment results in the simulation.
    return status


def print_status(status_data):
    """Print every order status with delivery result and remark."""
    print("\n🚚 === Delivery Status ===")
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
    """Build restock recommendations from final inventory using the Requirement 6 rules.

    Each ingredient is checked against ALL three conditions (out of stock, running
    low, expiring soon) and every condition that applies is preserved in a
    ``reasons`` list -- we never let one condition silently overwrite another.
    The output also reports the current quantity and expiry information so a
    kitchen manager can see why a restock was recommended.
    """
    if reference_date is None:
        # Assumption to verify: when no simulation date is passed in, the code uses
        # Python's date.today() from the local runtime environment as "today."
        reference_date = date.today()

    restock_recommendations = []

    for item in inventory_data:
        current_qty = item["qty_grams"]
        expiry_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d").date()
        days_until_expiry = (expiry_date - reference_date).days

        # Collect every reason that applies instead of stopping at the first one.
        reasons = []

        # Stock condition: 0 grams is "out of stock"; anything above 0 but at or
        # below the low-stock threshold is "running low". These two are mutually
        # exclusive (you cannot be both empty and merely low), so we use elif here.
        if current_qty == 0:
            reasons.append("Out of stock")
        elif current_qty <= LOW_STOCK_THRESHOLD_GRAMS:
            reasons.append("Running low on stock")

        # Expiry condition is independent of the stock level: a fully stocked but
        # soon-to-expire ingredient still needs attention, and a low-stock item that
        # is ALSO expiring soon keeps both reasons. We flag both already-expired
        # stock (negative days) and stock expiring within the window.
        is_expiry_flagged = days_until_expiry <= EXPIRY_WINDOW_DAYS
        if days_until_expiry < 0:
            reasons.append("Expired")
        elif days_until_expiry <= EXPIRY_WINDOW_DAYS:
            reasons.append("Expiring soon")

        if not reasons:
            continue

        # Quantity needed tops the ingredient back up to the par level. Expired or
        # soon-to-expire stock will be discarded, so it does not count as usable on
        # hand -- in that case we order a full par level. Otherwise we order only the
        # shortfall against current stock ("quantity needed to reach par level").
        usable_qty = 0 if is_expiry_flagged else current_qty
        qty_needed_grams = max(0, PAR_LEVEL_GRAMS - usable_qty)

        restock_recommendations.append(
            {
                "item": item["ingredient"],
                "current_qty_grams": current_qty,
                "qty_needed_grams": qty_needed_grams,
                "reasons": reasons,
                "expiry_date": item["expiry_date"],
                "days_until_expiry": days_until_expiry,
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
    partial_fulfillment=False,
):
    """Process orders, update fulfillment status, deduct inventory, and add restocks.

    ``partial_fulfillment`` selects the fulfillment policy:
      * False (default, base assignment): all-or-nothing. An order is delivered only
        if every required ingredient is available; otherwise nothing is deducted.
      * True (Optional Enhancement A): each line item is fulfilled independently, so
        the items that CAN be made are delivered and only the rest are rejected.
    """
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
            "partially_fulfilled": False,
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

        if partial_fulfillment:
            # Optional Enhancement A: fulfill each line item on its own so an order
            # is not lost just because one of its items is short. Items are evaluated
            # in order and deduct from working_inventory as they succeed, so earlier
            # items in the same order get first claim on shared stock.
            delivered_items = []
            rejected_items = []

            for item_result in order_result["items"]:
                if not item_result["recipe_found"]:
                    rejected_items.append(f"{item_result['item']} (no matching recipe)")
                    item_result["delivered"] = False
                    continue

                item_check = check_inventory_availability(
                    working_inventory, item_result["requirements"]
                )
                if item_check["all_available"]:
                    deduct_inventory(working_inventory, item_result["requirements"])
                    item_result["delivered"] = True
                    delivered_items.append(item_result["item"])
                else:
                    item_result["delivered"] = False
                    shortages = ", ".join(
                        detail["ingredient"]
                        for detail in item_check["details"]
                        if not detail["is_available"]
                    )
                    rejected_items.append(f"{item_result['item']} (short: {shortages})")

            if delivered_items and not rejected_items:
                order_result["fulfilled"] = True
                order_result["reason"] = "Delivered"
                update_status_entry(status_data, order["order_id"], True, "Delivered")
            elif delivered_items and rejected_items:
                order_result["partially_fulfilled"] = True
                order_result["reason"] = (
                    "Partially delivered. Delivered: "
                    + ", ".join(delivered_items)
                    + ". Not delivered: "
                    + "; ".join(rejected_items)
                )
                update_status_entry(
                    status_data, order["order_id"], False, order_result["reason"]
                )
            else:
                order_result["reason"] = "Not delivered: " + "; ".join(rejected_items)
                update_status_entry(
                    status_data, order["order_id"], False, order_result["reason"]
                )

            processed_orders.append(order_result)
            continue

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
    print("\n🔍 === Order Processing ===")
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


def find_unavailable_menu_items(recipe_data, inventory_data, reference_date=None):
    """Return menu items that cannot be offered (Optional Enhancement C).

    A menu item is "unavailable" when any required ingredient is missing, out of
    stock (0 grams), or already expired as of the reference date. Items that are
    merely low or expiring soon are still offerable, so they are not disabled here.
    """
    if reference_date is None:
        reference_date = date.today()

    inventory_lookup = {item["ingredient"]: item for item in inventory_data}
    unavailable_items = []

    for recipe in recipe_data:
        blockers = []
        for ingredient in recipe["ingredients"]:
            stock = inventory_lookup.get(ingredient["name"])
            if stock is None or stock["qty_grams"] <= 0:
                blockers.append(f"{ingredient['name']} (out of stock)")
                continue
            expiry_date = datetime.strptime(stock["expiry_date"], "%Y-%m-%d").date()
            if expiry_date < reference_date:
                blockers.append(f"{ingredient['name']} (expired)")

        if blockers:
            unavailable_items.append({"item": recipe["name"], "blocked_by": blockers})

    return unavailable_items


def build_business_summary(
    processed_orders, inventory_data, restock_data, unavailable_menu_items=None
):
    """Build a kitchen-manager-friendly summary of the simulation (Requirement 7)."""
    delivered = [o for o in processed_orders if o["fulfilled"]]
    partial = [o for o in processed_orders if o.get("partially_fulfilled")]
    not_delivered = [
        o
        for o in processed_orders
        if not o["fulfilled"] and not o.get("partially_fulfilled")
    ]

    # Surface the not-fully-delivered orders (both partial and failed) with reasons.
    delivery_issues = [
        {"order_id": o["order_id"], "brand": o["brand"], "reason": o["reason"]}
        for o in (partial + not_delivered)
    ]

    return {
        "orders_delivered": len(delivered),
        "orders_partially_delivered": len(partial),
        "orders_not_delivered": len(not_delivered),
        "delivery_issues": delivery_issues,
        "final_inventory": [
            {
                "ingredient": item["ingredient"],
                "qty_grams": item["qty_grams"],
                "expiry_date": item["expiry_date"],
            }
            for item in inventory_data
        ],
        "restock_recommendations": restock_data,
        "unavailable_menu_items": unavailable_menu_items or [],
    }


def _inventory_status_icon(ingredient_name, restock_recommendations):
    """Pick a status icon for an ingredient based on its restock reasons (if any)."""
    # Cross-reference the restock plan so the icon matches why an item was flagged:
    # ❌ for out-of-stock/expired, ⚠️ for low/expiring soon, ✅ for healthy stock.
    for entry in restock_recommendations:
        if entry["item"] != ingredient_name:
            continue
        reasons = entry.get("reasons") or [entry.get("reason", "")]
        if any(reason in ("Out of stock", "Expired") for reason in reasons):
            return "❌"
        return "⚠️"
    return "✅"


def print_business_summary(summary):
    """Print the business summary in plain language for a non-technical manager."""
    restock = summary["restock_recommendations"]

    print("\n🎯 ===== KITCHEN DAILY SUMMARY ===== 🎯")
    print(f"✅ Orders delivered in full:   {summary['orders_delivered']}")
    print(f"⚠️  Orders partially delivered: {summary['orders_partially_delivered']}")
    print(f"❌ Orders not delivered:       {summary['orders_not_delivered']}")

    if summary["delivery_issues"]:
        print("\n🔍 Orders needing attention:")
        for issue in summary["delivery_issues"]:
            print(f"   • Order {issue['order_id']} ({issue['brand']}): {issue['reason']}")

    print("\n📦 Final inventory levels:")
    for item in summary["final_inventory"]:
        icon = _inventory_status_icon(item["ingredient"], restock)
        print(
            f"   {icon} {item['ingredient']}: {item['qty_grams']:,} g "
            f"(expires {item['expiry_date']})"
        )

    print("\n🔧 Restock recommendations:")
    if not restock:
        print("   ✅ None — stock levels and expiry dates are all healthy.")
    for item in restock:
        reasons = ", ".join(item.get("reasons") or [item.get("reason", "")])
        print(f"   • {item['item']}: order {item['qty_needed_grams']:,} g  ({reasons})")

    if summary["unavailable_menu_items"]:
        print("\n🛑 Menu items to disable (ingredient unavailable):")
        for menu_item in summary["unavailable_menu_items"]:
            print(f"   • {menu_item['item']} — blocked by {', '.join(menu_item['blocked_by'])}")
    print()


def generate_markdown_report(summary, file_path="REPORT.md"):
    """Write the business summary to a polished Markdown file (Optional Enhancement D)."""
    restock = summary["restock_recommendations"]
    lines = ["# 🎓 Cloud Kitchen — Daily Report", ""]
    lines.append("## 🎯 Order Outcomes")
    lines.append(f"- ✅ **Delivered in full:** {summary['orders_delivered']}")
    lines.append(f"- ⚠️ **Partially delivered:** {summary['orders_partially_delivered']}")
    lines.append(f"- ❌ **Not delivered:** {summary['orders_not_delivered']}")
    lines.append("")

    if summary["delivery_issues"]:
        lines.append("## 🔍 Orders Needing Attention")
        lines.append("| Order | Brand | Reason |")
        lines.append("| :--- | :--- | :--- |")
        for issue in summary["delivery_issues"]:
            lines.append(f"| {issue['order_id']} | {issue['brand']} | {issue['reason']} |")
        lines.append("")

    lines.append("## 📦 Final Inventory")
    lines.append("| | Ingredient | Quantity (g) | Expiry |")
    lines.append("| :---: | :--- | ---: | :--- |")
    for item in summary["final_inventory"]:
        icon = _inventory_status_icon(item["ingredient"], restock)
        lines.append(
            f"| {icon} | {item['ingredient']} | {item['qty_grams']:,} | {item['expiry_date']} |"
        )
    lines.append("")

    lines.append("## 🔧 Restock Recommendations")
    if not restock:
        lines.append("_✅ None — stock levels and expiry dates are all healthy._")
    else:
        lines.append("| Ingredient | Current (g) | Order (g) | Reason(s) |")
        lines.append("| :--- | ---: | ---: | :--- |")
        for item in restock:
            reasons = ", ".join(item.get("reasons") or [item.get("reason", "")])
            current = item.get("current_qty_grams", "—")
            current = f"{current:,}" if isinstance(current, int) else current
            lines.append(
                f"| {item['item']} | {current} | {item['qty_needed_grams']:,} | {reasons} |"
            )
    lines.append("")

    if summary["unavailable_menu_items"]:
        lines.append("## 🛑 Menu Items To Disable")
        for menu_item in summary["unavailable_menu_items"]:
            lines.append(f"- **{menu_item['item']}** — blocked by {', '.join(menu_item['blocked_by'])}")
        lines.append("")

    with open(file_path, "w", encoding="utf-8") as report_file:
        report_file.write("\n".join(lines))

    return file_path


def load_seed_module(seed_file):
    """Import a seed-data file from an arbitrary path and return the module.

    Lets the CLI's --file option point at any seed file with the same structure
    (recipes, inventory, orders, restock, status) instead of the bundled one.
    """
    if not os.path.exists(seed_file):
        raise FileNotFoundError(f"Seed file not found: {seed_file}")

    spec = importlib.util.spec_from_file_location("custom_seed", seed_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Fail loudly if the chosen file is missing any of the five required tables.
    required = ["recipes", "inventory", "orders", "status"]
    missing = [name for name in required if not hasattr(module, name)]
    if missing:
        raise AttributeError(
            f"Seed file '{seed_file}' is missing required table(s): {', '.join(missing)}"
        )
    return module


def main(seed_file=None, partial=False, reference_date=None):
    """Load seed tables, process fulfillment, and print the updated results.

    Args:
        seed_file: optional path to a seed-data file; defaults to the bundled
            seed_data.py imported at module load.
        partial: when True, use Optional Enhancement A (partial fulfillment).
        reference_date: optional date used as "today" for expiry calculations;
            defaults to the real current date inside the processing functions.
    """
    # Assumption to verify: we process working copies of mutable tables so the seed
    # definitions stay unchanged across runs and tests.
    if seed_file:
        seed = load_seed_module(seed_file)
        recipe_data = deepcopy(seed.recipes)
        inventory_data = deepcopy(seed.inventory)
        order_data = deepcopy(seed.orders)
        status_data = deepcopy(seed.status)
        print(f"📂 Using seed data from: {seed_file}")
    else:
        recipe_data = load_recipes()
        inventory_data = deepcopy(load_inventory())
        order_data = load_orders()
        status_data = deepcopy(load_status())

    if partial:
        print("🧩 Fulfillment mode: PARTIAL (deliver available items individually)")
    else:
        print("📦 Fulfillment mode: ALL-OR-NOTHING (base policy)")

    # Step 8: start with an empty live restock table because recommendations are
    # now generated from final inventory after all orders have been processed.
    restock_data = []
    processed_orders = process_orders(
        recipe_data,
        inventory_data,
        order_data,
        status_data,
        restock_data,
        reference_date=reference_date,
        partial_fulfillment=partial,
    )

    # Optional Enhancement C: flag menu items that can no longer be offered.
    unavailable_menu_items = find_unavailable_menu_items(
        recipe_data, inventory_data, reference_date
    )
    summary = build_business_summary(
        processed_orders, inventory_data, restock_data, unavailable_menu_items
    )

    print_recipes(recipe_data)
    print_orders(order_data)
    print_order_processing_results(processed_orders)
    print_inventory(inventory_data)
    print_restock(restock_data)
    print_status(status_data)
    print_business_summary(summary)

    # Optional Enhancement D: also write a polished Markdown report to disk.
    report_path = generate_markdown_report(summary)
    print(f"\n📝 Markdown report written to {report_path}")


def _valid_date(value):
    """argparse type: parse a YYYY-MM-DD string into a date, or raise a clear error."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"❌ Invalid date '{value}'. Use the format YYYY-MM-DD (e.g. 2026-06-22)."
        )


def build_arg_parser():
    """Build the emojified command-line interface for the simulation."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="🎓 Cloud Kitchen Inventory Simulation — process orders against a "
        "shared, recipe-linked inventory, then report deliveries, restock needs, and "
        "expiry risk for a delivery-only kitchen.",
        epilog="✨ Examples:\n"
        "  python3 main.py                     ▶️  run with the bundled seed data\n"
        "  python3 main.py -p                  🧩 run with partial fulfillment\n"
        "  python3 main.py -d 2026-06-03       📅 pin the simulation date\n"
        "  python3 main.py -f my_seed.py -p    📂 custom seed file + partial mode\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="seed_file",
        metavar="PATH",
        default=None,
        help="📂 Path to a seed-data file (recipes, inventory, orders, restock, "
        "status). Defaults to the bundled seed_data.py.",
    )
    parser.add_argument(
        "-p",
        "--partial",
        action="store_true",
        help="🧩 Enable partial fulfillment (Enhancement A): deliver the items an "
        "order can satisfy and reject only the rest. Default is all-or-nothing.",
    )
    parser.add_argument(
        "-d",
        "--date",
        dest="reference_date",
        metavar="YYYY-MM-DD",
        type=_valid_date,
        default=None,
        help="📅 Simulation 'today' used for expiry checks (low/expiring/expired). "
        "Defaults to the real current date.",
    )
    return parser


if __name__ == "__main__":
    import sys

    args = build_arg_parser().parse_args()
    try:
        main(
            seed_file=args.seed_file,
            partial=args.partial,
            reference_date=args.reference_date,
        )
    except (FileNotFoundError, AttributeError) as error:
        # Turn seed-file problems into a clean message instead of a raw traceback.
        sys.exit(f"❌ {error}")
