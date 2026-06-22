# Written Response — Cloud Kitchen Inventory Simulation 🎓

## Project Setup
The project lives in `module3/` with the required files: `main.py` (simulation logic), `seed_data.py` (starting data — a copy of the provided `seed_data-1.py`), `test_main.py` (unit tests), plus `PROJECT_SPEC.md`, `AI_USAGE_LOG.md`, and this written response. `main.py` imports the five seed tables from `seed_data.py`.

- **Run the program:** `python3 main.py` (prints all tables, order processing, the business summary, and writes `REPORT.md`).
- **Run the tests:** `python3 -m unittest` or `python3 -m pytest test_main.py`.
- **Setup issue encountered:** the provided code imports `seed_data`, but the data file ships as `seed_data-1.py`, so imports failed until I created `seed_data.py`. For speed purposes, I copied over the original file into this new file.

## Data Loading
`load_recipes`, `load_inventory`, `load_orders`, `load_restock`, and `load_status` return the five seed tables; matching `print_*` helpers display them. Tests verify each table is a non-empty list, has the expected record count, and exposes the expected key field types (R1 / Task 3).

## Recipe Lookup
`find_recipe_by_name` returns the matching recipe or `None` for an unknown item. `calculate_ingredient_requirements` scales recipe grams by ordered quantity, and `combine_requirements` sums per-ingredient demand across all items in an order (R2 / Task 4). Tests cover a valid item, a missing item, and quantity > 1.

## Inventory Availability
`check_inventory_availability` compares combined order requirements against current stock and returns per-ingredient detail (`required`, `available`, `is_available`) plus an overall `all_available` flag, distinguishing missing from insufficient ingredients (R3 / Task 5).

## Order Fulfillment
`process_orders` uses **all-or-nothing** fulfillment: if every ingredient is available it marks the order delivered and deducts stock; otherwise it records a reason and deducts nothing. Status is updated via `update_status_entry`, and failed/short ingredients flow into the recalculated restock plan (R4 / Task 6).

## Cumulative Processing
Orders are processed sequentially against one working inventory (a deep copy), so each order sees the stock remaining after prior delivered orders. The final inventory snapshot is written back only after all orders complete (R5 / Task 7). Tests confirm combined deduction, a later order failing once stock is exhausted, and exact final quantities.

## Restock and Expiry Logic
`calculate_restock_needs` checks every ingredient against all conditions and keeps **all** applicable reasons in a `reasons` list: "Out of stock", "Running low on stock", "Expired", and "Expiring soon". Thresholds are module constants (`PAR_LEVEL_GRAMS`, `LOW_STOCK_THRESHOLD_GRAMS`, `EXPIRY_WINDOW_DAYS`). Output includes current quantity, quantity needed to reach par, reasons, and expiry info (R6 / Task 8). Expired/expiring stock is treated as unusable, so a full par level is ordered for it.

## Business Summary
`build_business_summary` / `print_business_summary` report delivered, partially delivered, and not-delivered counts, the reasons for each issue, final inventory, restock recommendations, and unavailable menu items — in plain language for a non-technical manager, with status icons (✅/⚠️/❌) for quick scanning (R7 / Task 9).

## Refactoring Notes
Two concrete improvements made during review:
1. **Replaced magic numbers with named constants** for the par level, low-stock threshold, and expiry window, so the business rules live in one obvious place.
2. **Replaced `elif`-chained single-reason restock with an additive `reasons` list**, fixing a real defect where an ingredient that was both low and expiring silently lost one reason — exactly what Requirement 6 forbids.

## Optional Enhancements
- **A — Partial fulfillment:** an opt-in `partial_fulfillment=True` flag delivers the items an order *can* satisfy and rejects only the rest; the base path is unchanged.
- **C — Dynamic menu disabling:** `find_unavailable_menu_items` flags menu items whose ingredients are out of stock or expired.
- **D — Improved reporting:** `generate_markdown_report` writes a polished `REPORT.md` business report. All three are tested.

## AI Usage Summary
See `AI_USAGE_LOG.md`. I used AI to assess the brief, refactor the restock logic, build the summary and enhancements, and generate tests — reviewing every output, running the suite after each change, and rejecting the AI's initial restock logic that missed already-expired stock.

## Reflection
Working with an AI coding assistant on this simulation changed *where* my effort went more than *how much* effort it took. The AI moved me faster mainly on mechanical, well-specified work: scaffolding the business-summary and Markdown-report functions, generating boilerplate unit tests, and translating a requirement I had already understood into idiomatic Python. Tasks that would have been twenty minutes of careful typing became a quick prompt plus a review. It was also fast at the "reading" half of the job — surveying the provided files and mapping each rubric line to a status — which let me plan before writing anything.

The mistakes were instructive. The clearest was the restock logic: the AI initially flagged only ingredients *expiring soon* and silently ignored stock that was *already expired*, even though Requirement 6 explicitly says "expired or expiring soon." It read plausibly and even passed its own first tests, which is precisely the trap the assignment warns about — code that looks correct because the tests were written to the same flawed assumption. It also tended to want to "improve" things I hadn't asked about, such as making partial fulfillment the default, which would have violated the base specification.

Testing was the single most valuable check on the AI's work. Because the failure modes were quiet (a dropped reason, a missed expiry branch), reading the code was not enough; I had to run scenarios. Writing a test for an ingredient that was *both* low and expiring immediately exposed the overwriting bug, and a test pinned to a fixed reference date made the expiry behavior deterministic and reviewable. I treated a green suite, not the model's assurance, as the definition of "done," and I ran the suite after every change.

I changed or rejected several suggestions: I kept the base all-or-nothing policy and pushed partial fulfillment behind an opt-in flag; I rejected the expired-stock omission and added an explicit branch; and I made a deliberate design call — ordering a full par level for expired stock rather than only the shortfall — and documented it rather than letting the AI's default stand unexamined.

`PROJECT_SPEC.md` was what kept the collaboration coherent. Each time I returned to the AI, the spec re-anchored the data shapes, the exact thresholds, and the open decisions, so I never had to re-explain context or risk the model drifting toward a different schema. It also forced me to make my assumptions explicit, which is where several near-misses surfaced.

Next time I would write the spec and the tests *before* asking the AI to implement, so the AI is constrained by my acceptance criteria from the first prompt instead of inheriting its own assumptions. I would also ask, as a standard step, "what conditions does this logic *not* handle?" — the question that would have caught the expired-stock gap immediately. The overall lesson is that AI is a genuine accelerator for implementation, but the navigation, the skepticism, and the verification have to stay firmly with me.
