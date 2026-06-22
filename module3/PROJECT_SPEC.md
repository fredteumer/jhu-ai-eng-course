# PROJECT_SPEC.md — Cloud Kitchen Inventory Simulation 🎓

> External memory for the project. Updated throughout the assignment to reduce
> context drift when working with AI.

## 1. Project Purpose
Build a Python simulation for a delivery-only **cloud kitchen** that shares one
inventory across multiple virtual brands. The simulation processes customer
orders against recipe-linked inventory, updates delivery status, deducts
ingredients cumulatively, tracks expiry risk, and produces a restock plan and a
business-friendly summary.

The grade rewards not just working code but evidence of **navigating, reviewing,
and deciding** on AI-assisted output (see `AI_USAGE_LOG.md`).

## 2. Data Structures (from `seed_data.py`)
Five module-level lists of dicts. The code inspects the provided schema rather
than inventing one.

| Table | Shape (key fields) |
| :--- | :--- |
| `recipes` | `recipe_id:int`, `name:str`, `ingredients:[{name:str, qty_grams:int}]` |
| `inventory` | `ingredient:str`, `qty_grams:int`, `expiry_date:str "YYYY-MM-DD"` |
| `orders` | `order_id:int`, `brand:str`, `items:[{item:str, qty:int}]` |
| `restock` | `item:str`, `qty_needed_grams:int`, `reason:str` (legacy seed schema) |
| `status` | `order_id:int`, `delivered:bool`, `remark:str` |

> Note: `seed_data.py` is a copy of the instructor file `seed_data-1.py` (the
> code imports `seed_data`). The duplicate is intentional and harmless.

## 3. Business Rules
- **Ingredient matching:** exact name match between `orders[].items[].item` and
  `recipes[].name`, and between recipe ingredient names and `inventory[].ingredient`.
  No normalization/aliases (documented assumption).
- **Quantity scaling:** required grams = recipe grams × ordered qty; multiple
  items in one order are summed per ingredient.
- **Fulfillment policy (base):** **all-or-nothing**. An order is delivered only if
  *every* required ingredient is available in sufficient quantity; otherwise nothing
  is deducted and the order is marked not delivered with a reason.
- **Cumulative deduction:** orders are processed in sequence against a single
  working inventory; later orders see stock left by earlier delivered orders.
- **Restock thresholds (module constants in `main.py`):**
  - `PAR_LEVEL_GRAMS = 10000` — target top-up level.
  - `LOW_STOCK_THRESHOLD_GRAMS = 1000` — `≤ this` (and `> 0`) = "Running low".
  - `EXPIRY_WINDOW_DAYS = 5` — within 5 days of the reference date = "Expiring soon".
- **Restock reasons are additive:** an ingredient can carry *multiple* reasons
  (e.g. low **and** expiring); reasons are stored in a `reasons` list and never
  overwritten.
- **Expiry handling:** already-expired stock (`days_until_expiry < 0`) → "Expired";
  within window → "Expiring soon". Expired/expiring stock is treated as **unusable**,
  so a full par level is ordered for it (design decision — see §7).

## 4. Components & Status
| Function | Requirement | Status |
| :--- | :--- | :--- |
| `load_*` / `print_*` (5 tables) | R1 Load & display | ✅ |
| `find_recipe_by_name` | R2 Recipe lookup | ✅ |
| `calculate_ingredient_requirements` | R2 Quantity scaling | ✅ |
| `combine_requirements` | R2 Per-order totals | ✅ |
| `check_inventory_availability` | R3 Availability | ✅ |
| `deduct_inventory` / `apply_final_inventory_snapshot` | R4 Deduction | ✅ |
| `update_status_entry` | R4 Status updates | ✅ |
| `process_orders` | R4/R5 Fulfillment + cumulative | ✅ |
| `calculate_restock_needs` / `refresh_restock_table` | R6 Restock & expiry | ✅ |
| `build_business_summary` / `print_business_summary` | R7 Summary | ✅ |
| `find_unavailable_menu_items` | Optional C | ✅ |
| `generate_markdown_report` | Optional D (`REPORT.md`) | ✅ |
| `process_orders(partial_fulfillment=True)` | Optional A | ✅ |

## 5. Implementation Plan (incremental)
1. ✅ Fix import (`seed_data.py`), confirm baseline tests.
2. ✅ Restock: constants + multiple reasons + current qty/expiry fields + expired stock.
3. ✅ Business summary function + report.
4. ✅ Optional enhancements A (partial), C (menu disabling), D (Markdown report).
5. ✅ Tests for all new behavior; full suite green.
6. ⬜ Docs: this file, `AI_USAGE_LOG.md`, written response + reflection.

## 6. Testing Plan
`unittest` in `test_main.py`, run with `python3 -m unittest` or `pytest`.
Coverage: data-loading types/counts, recipe lookup (hit/miss/scaling),
availability, fulfillment (success/fail/deduction/no-deduction), cumulative
processing, restock rules (out/low/threshold/expiring/expired/multi-reason/adequate),
business summary counts, partial fulfillment, menu availability.
**Current: 27 tests passing.**

## 7. Open Questions / Assumptions
- **Reference date:** `main()` uses `date.today()` (2026-06-22 at authoring), so many
  seed ingredients read as already expired. Tests pin an explicit `reference_date`
  for determinism.
- **Quantity-needed for expiry:** decision to order a *full par level* for
  expired/expiring stock (treat on-hand as unusable) rather than only the shortfall.
  Defensible operationally; revisit if instructor wants shortfall-only.
- **Exact name matching** only — no fuzzy/alias matching.
- Simulation is **in-memory**; no persistence layer.
