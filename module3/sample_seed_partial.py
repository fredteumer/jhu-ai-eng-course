# Sample seed data for demonstrating PARTIAL fulfillment (Optional Enhancement A).
#
# Run it with:
#   python3 main.py -f sample_seed_partial.py -p
#
# It is deliberately small and rigged so that Order 1 can only be *partially*
# delivered: the kitchen has enough stock for the Veggie Wraps but not enough
# Steak for the Steak Plate. Order 2 delivers in full, and Order 3 contains an
# item with no matching recipe, so you can see every outcome in one run.

# 1. Recipes
recipes = [
    {
        "recipe_id": 1,
        "name": "Veggie Wrap",
        "ingredients": [
            {"name": "Tortilla", "qty_grams": 100},
            {"name": "Lettuce", "qty_grams": 50},
        ],
    },
    {
        "recipe_id": 2,
        "name": "Steak Plate",
        "ingredients": [
            {"name": "Steak", "qty_grams": 300},
        ],
    },
]

# 2. Inventory — note Steak is short (only 100 g, but a Steak Plate needs 300 g).
inventory = [
    {"ingredient": "Tortilla", "qty_grams": 1000, "expiry_date": "2026-12-31"},
    {"ingredient": "Lettuce", "qty_grams": 500, "expiry_date": "2026-12-31"},
    {"ingredient": "Steak", "qty_grams": 100, "expiry_date": "2026-12-31"},
]

# 3. Orders
orders = [
    {
        # Partial: 2 Veggie Wraps are makeable; the Steak Plate is short on Steak.
        "order_id": 1,
        "brand": "Demo Diner",
        "items": [
            {"item": "Veggie Wrap", "qty": 2},
            {"item": "Steak Plate", "qty": 1},
        ],
    },
    {
        # Fully delivered.
        "order_id": 2,
        "brand": "Demo Diner",
        "items": [{"item": "Veggie Wrap", "qty": 1}],
    },
    {
        # Not delivered: no matching recipe for the ordered item.
        "order_id": 3,
        "brand": "Demo Diner",
        "items": [{"item": "Unicorn Steak", "qty": 1}],
    },
]

# 4. Restock — starts empty; recalculated from final inventory after processing.
restock = []

# 5. Status — starts empty; populated as orders are processed.
status = []
