# AI_USAGE_LOG.md — How AI Was Used 🎓

This log documents how I used an AI coding assistant (Claude Code) on this assignment. It records the genuine, major interactions of the working session in which I completed the module — the task, the prompt/intent, a summary of the AI response, and **what I accepted, changed, or rejected** as the reviewer and decision-maker. Trivial prompts are omitted.

I worked in three roles throughout: **Navigator** (set goals, decided what to ask), **Reviewer** (inspected generated code and assumptions), and **Decision-Maker** (chose what to accept, revise, or reject).

---

## Interaction 1 — Assess the assignment and existing code
- **Task:** Understand the full scope and decide an approach for full credit.
- **Prompt (intent):** "Look at module 3 and assess how to approach it so we get full credit." (Planning prompt pattern.)
- **AI response (summary):** Read `ASSIGNMENT.md` and the provided `main.py`, `test_main.py`, and `seed_data-1.py`. Reported that the provided code already implemented Requirements 1–7, but (a) imports were broken because the data file was named `seed_data-1.py` while the code imports `seed_data`, and (b) several rubric gaps remained. It mapped every rubric line to a status and proposed a plan.
- **What I accepted:** the gap analysis and incremental plan.
- **What I reviewed critically:** I verified the "all 20 tests pass once renamed" claim by running the suite in a scratch copy rather than trusting it.
- **Decisions I made:** chose to (1) copy rather than rename the seed file, (2) log AI usage going forward (this file), and (3) add optional enhancements A, C, and D.

## Interaction 2 — Fix the import blocker
- **Task:** Make the project importable and runnable (Requirement 1 / Task 1).
- **Prompt (intent):** "Create `seed_data.py` and confirm the baseline tests pass."
- **AI response:** Copied `seed_data-1.py` → `seed_data.py`; ran `pytest` → 20 passed.
- **What I accepted:** the copy approach (a duplicate is acceptable for this project).
- **Issue found:** none, but I confirmed the run rather than assuming.

## Interaction 3 — Restock & expiry logic (Requirement 6)
- **Task:** Restock logic that preserves multiple reasons and reports current quantity + expiry info, with thresholds as named constants.
- **Prompt (intent):** "The brief says preserve *all* restock reasons and include current quantity and expiry info; the current code uses `elif` and keeps only one reason, and the thresholds are magic numbers. Refactor it."
- **AI response (summary):** Added `PAR_LEVEL_GRAMS`, `LOW_STOCK_THRESHOLD_GRAMS`, and `EXPIRY_WINDOW_DAYS` constants; rewrote `calculate_restock_needs` to collect a `reasons` list and emit `current_qty_grams`, `expiry_date`, and `days_until_expiry`.
- **What I changed/rejected:** The first version only flagged *expiring soon* (`0 ≤ days ≤ 5`) and **missed already-expired stock**, even though Requirement 6 says "expired **or** expiring soon." I rejected that and added an explicit "Expired" branch for `days < 0`.
- **Decision I made:** for expired/expiring stock, order a **full par level** (treat on-hand as unusable) instead of only the shortfall — documented in `PROJECT_SPEC.md §7`. I updated the affected tests to match this deliberate rule.

## Interaction 4 — Business summary (Requirement 7 / Task 9)
- **Task:** A non-technical summary: delivered/not-delivered counts, reasons, final inventory, restock recommendations, and expiry concerns.
- **Prompt (intent):** "Add a `build_business_summary` + `print_business_summary` for a kitchen manager."
- **AI response:** Aggregated processed orders into counts and a `delivery_issues` list, plus final inventory and restock data.
- **What I reviewed:** confirmed partial orders are counted separately and not double-counted as delivered.

## Interaction 5 — Optional enhancements A, C, D
- **Task:** Partial fulfillment, dynamic menu disabling, and a Markdown report.
- **Prompt (intent):** "Add optional A (partial), C (menu disabling), and D (Markdown report) without breaking the tested base path."
- **AI response:** Added a `partial_fulfillment=False` flag to `process_orders` (base path untouched), `find_unavailable_menu_items`, and `generate_markdown_report`.
- **What I insisted on:** keeping the base all-or-nothing path and its tests unchanged; partial behavior lives behind an opt-in flag and its own tests.
- **Decision:** menu disabling flags only *out-of-stock/expired* ingredients (not merely low/expiring), since low items can still be cooked.

## Interaction 6 — Prettier, business-friendly output
- **Task:** Make the manager-facing output easier to read.
- **Prompt (intent):** "The output format isn't strictly defined — emojify it and make it prettier."
- **AI response:** Confirmed Task 9 leaves the format open, then added EMOJIDICT-consistent icons and per-ingredient status markers (✅ healthy, ⚠️ low/expiring, ❌ out/expired) to the console summary and Markdown report, with thousands-separated quantities.
- **What I reviewed:** confirmed the icons are derived from the actual restock reasons rather than hard-coded.

## Interaction 7 — Tests and verification
- **Task:** Cover the new behavior and re-run everything.
- **AI response:** Added tests for multiple restock reasons, expired stock, the threshold edge, business-summary counts, partial fulfillment, and menu availability; updated tests whose expected values changed by design.
- **Result:** full suite **27 passing** (`python3 -m pytest test_main.py`).

## Interaction 8 — Command-line interface
- **Task:** Make the simulation configurable from the command line, including a way to actually see partial fulfillment (Enhancement A) in a normal run.
- **Prompt (intent):** "Add an `argparse` CLI with `--help/-h`, `--file/-f` (custom seed file, defaults to seed_data.py), `--partial/-p`, and `--date/-d`. Emojify the help text and write good descriptions for each option."
- **AI response (summary):** Refactored `main()` to take `seed_file`, `partial`, and `reference_date` parameters; added `load_seed_module` (dynamic import via `importlib` so `--file` can point at any compatible seed file), `_valid_date` (an argparse type that validates `YYYY-MM-DD`), and `build_arg_parser` with emojified descriptions and usage examples. `argparse` supplies `-h/--help` automatically.
- **What I changed/insisted on:** the first version let a bad `--file` path raise a raw traceback; I had it catch `FileNotFoundError`/`AttributeError` and exit with a clean `❌` message and non-zero status. I also had `load_seed_module` validate that the file actually defines the required tables rather than failing later with a confusing attribute error.
- **What I verified:** `--help` renders the emojified text, an invalid date is rejected with a friendly message, a missing seed file exits cleanly (exit code 1), `--partial` switches the fulfillment banner, and a custom `-f seed_data.py` loads. Full suite still **29 passing** — the CLI wraps `main()` and did not require changing any test.

## Interaction 9 — Demo seed file for partial fulfillment
- **Task:** Provide a seed file that actually exercises partial fulfillment so the `--file` loader and Enhancement A can be demonstrated together (the bundled seed has every order succeed, so partial mode never visibly triggers).
- **Prompt (intent):** "Create a partial seed file so we can test both the file feeding and the extra-credit work."
- **AI response (summary):** Added `sample_seed_partial.py` — a small, commented seed rigged so Order 1 is partially fulfillable (enough Tortilla/Lettuce for Veggie Wraps but only 100 g of the 300 g Steak needed), Order 2 fully delivers, and Order 3 has no matching recipe. Added `TestCustomSeedFile` with four tests covering the loader, a missing-file error, the partial-mode outcome, and the all-or-nothing contrast (verifying the failed order deducts no Tortilla).
- **What I verified:** `python3 main.py -f sample_seed_partial.py -p` shows 1 delivered / 1 partial / 1 not delivered, while the same file without `-p` shows 1 delivered / 0 partial / 2 not delivered — proving both the policy switch and the custom-seed path. Full suite now **33 passing**.

---

## Overall reviewer notes
- The AI's biggest miss was the **already-expired** case in restock — a requirement it skipped until I pushed back. This is exactly the "fast but unreliable junior" behavior the assignment warns about.
- I rejected one suggestion to change the base fulfillment to partial by default; the brief specifies all-or-nothing for the base, so partial is opt-in only.
- Every code change was confirmed by running the test suite, not by trusting the model's claim that it worked.
