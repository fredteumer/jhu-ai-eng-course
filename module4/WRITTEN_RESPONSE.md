# Module 4 — Goal-Based & Utility-Based Agents

**Notebook:** `notebook.ipynb`  ·  **Scenario:** commercial travel office booking employee travel from Paris to Berlin for a 2-night trip.

> Reproducibility note: the notebook is built to run in Google Colab, in a local Jupyter environment, or fully offline. Because the flight/hotel searches require paid SerpAPI + LLM keys, the notebook defaults to `RUN_LIVE = False` and evaluates a cached, representative dataset so every result below is deterministic and can be re-graded without credentials. Setting `RUN_LIVE = True` with valid keys restores the live agent calls. For a **local** live run, copy `.env.example` to `.env` and populate `serp_api` and `GL_OpenAI`; in **Google Colab**, add those same two secrets via the Secrets panel instead.

## Task 1: Original Notebook Workflow
The original notebook wires together five components:

- **Flight agent** — a `CodeAgent` given a single tool, `search_flights`, which queries SerpAPI's `google_flights` engine for an origin, destination, date, and trip type. Its system prompt tells it to return a clean flight dictionary (airline, times, duration, price, etc.). In short, it turns a natural-language flight request into a structured flight record.
- **Hotel agent** — a second `CodeAgent` with the `search_hotel` tool, which queries SerpAPI's `google_hotels` engine for a location and check-in/check-out dates. Its system prompt asks for a structured hotel dictionary (name, star rating, price per night, distance, amenities).
- **Manager agent** — a `CodeAgent` that does not search directly. It holds the flight and hotel agents as `managed_agents` (plus a `WebSearchTool`) and orchestrates them: it reads the user's combined request, delegates the flight portion to the flight agent and the hotel portion to the hotel agent, and returns one merged result containing both `flights` and `hotels`.
- **Goal-based evaluator** — the `goal_checker` tool wrapped in its own agent. Its *goal* is "stay within an airfare budget." For each flight it parses the price and compares it to a budget: flights within budget earn a positive score based on the savings (discounted by a penalty factor), and flights over budget earn a negative score based on the overage. It is a binary, single-objective check: within budget or over budget.
- **Utility-based evaluator** — the `utility_checker` tool wrapped in its own agent. Instead of one pass/fail goal, it assigns each hotel a *utility score* by combining two preferences: it adds points for a desirable star rating (5 stars) and adds points for being within a nightly budget, and subtracts points otherwise. The result is a graded score (in multiples of 50) reflecting overall value rather than a single yes/no.

The key difference between the two evaluators: the **goal-based** agent asks "did we meet the goal (budget)?" while the **utility-based** agent asks "how good is this option overall, weighing several attributes?"

On the cached dataset, the original evaluators produce: flights scored A = +63 (within the $200 budget), B = −1, C = −14; hotels scored X (Airport North Inn) = 0, Z (Berlin Mitte) = −100, Y (City Center Grand) = 0. Price-only, this points to **Flight A** (cheapest airfare) and **Hotel X** (cheapest nightly rate). Notably, the coarse utility scoring cannot even separate X from Y — both score 0 — which is a hint that price + stars alone is too blunt.

## Task 2: Limitation of Listed-Price Optimization
Choosing the lowest sticker price ignores the employee's paid time, which is a real company cost. Two examples from the dataset (employee rate $75/hr):

- **Flight:** Option A has the lowest airfare at $130, but it has 2 stops and ~8 effective travel hours, so its labor cost is 8 × $75 = $600, giving a total business cost of $730. Option C costs $340 up front but is nonstop (~1.83 hrs), so its labor cost is only ~$137.50 and its total is $477.50 — cheaper overall by ~$250, despite the higher ticket price.
- **Hotel:** Hotel X is cheapest per night at $94 ($188 lodging), but its 1.5-hour daily commute adds 1.5 × 2 days × $75 = $225 of commute labor, for a total of $413. Hotel Z at $140/night ($280 lodging) has a shorter 0.8-hour commute ($120 labor) and a total of $400 — lower total business cost even though it is more expensive per night.

In both cases the cheapest *listed* option is not the cheapest *total* option, because listed price omits the largest hidden cost: paid employee time.

## Task 3: Labor Cost Parameters
All labor assumptions are grouped in one cell so the whole evaluation can be re-run by changing a single value:

| Parameter | Value | Justification |
|---|---|---|
| `EMPLOYEE_HOURLY_RATE` | $75/hr | A "fully loaded" cost (salary + benefits + payroll tax + overhead) for a ~$120–150k/yr professional across ~2,080 working hours is roughly $70–80/hr; $75 is a defensible midpoint and matches the assignment's suggested value. |
| `HOTEL_NIGHTS` | 2 | The trip books a 2-night stay. |
| `TRAVEL_DAYS` | 2 | One commute cycle per on-site working day; kept separate from nights so a non-working travel day could be modeled without changing lodging math. |
| `DEFAULT_COMMUTE_MINUTES` | 30 | A conservative city-center commute used only when a hotel record has no usable commute field, so missing data is handled transparently rather than dropped. |
| `LAYOVER_PENALTY_HOURS` | 1.0 | A modest lost-productivity penalty added per stop on top of the elapsed duration (boarding, security re-checks, dead time). 1.0 hr/stop is intentionally conservative to avoid over-penalizing connections. |

Stated assumptions (also printed by the notebook): travel time counts as fully paid labor time; layovers are captured via penalty × number of stops; commute time is the hotel-to-business-district daily round trip; missing or ambiguous data falls back to the documented defaults above.

## Task 4: Modified Flight Evaluation
`calculate_flight_business_cost(flight, employee_hourly_rate)` computes, per flight: airfare (parsed from a string like `"$130"`), effective travel hours (`estimate_travel_hours` = elapsed duration + stops * `LAYOVER_PENALTY_HOURS`), travel labor cost (travel hours * rate), and total business cost (airfare + labor). At $75/hr:

| Flight | Airfare | Travel Hrs | Labor Cost | Total Business Cost |
|---|---|---|---|---|
| Option A | $130 | 8.0 | $600.00 | **$730.00** |
| Option B | $210 | 4.5 | $337.50 | **$547.50** |
| Option C | $340 | 1.83 | $137.50 | **$477.50** ← lowest total |

The lowest-airfare flight (A) is **not** the lowest-total flight (C); the notebook prints this conclusion explicitly.

## Task 5: Modified Hotel Evaluation
`calculate_hotel_business_cost(hotel, employee_hourly_rate, hotel_nights, travel_days)` computes, per hotel: price per night, lodging cost (price × nights), estimated daily commute hours (`estimate_commute_hours`), commute labor cost (commute hours × travel days × rate), and total business cost (lodging + commute labor). At $75/hr:

| Hotel | $/Night | Lodging | Commute Labor | Total Business Cost |
|---|---|---|---|---|
| Airport North Inn | $94 | $188 | $225.00 | **$413.00** |
| Berlin Mitte | $140 | $280 | $120.00 | **$400.00** ← lowest total |
| City Center Grand | $200 | $400 | $45.00 | **$445.00** |

The cheapest nightly rate (Airport North Inn) is **not** the lowest total; commute labor changes the winner to Berlin Mitte.

## Task 6: Prompt or Evaluation Criteria Update
The change is to the goal-based evaluator's instruction. **Before**, it was told to "evaluate flight options based on price … mark Within Budget or Over Budget." **After**, it is replaced by `labor_aware_evaluation_prompt`, a Business-Cost Evaluator instruction that explicitly requires estimating total business cost — spelling out the flight formula (`airfare + travel_hours * rate`, with `travel_hours = duration + stops * LAYOVER_PENALTY_HOURS`) and the hotel formula (`lodging + commute_hours * travel_days * rate`) and instructs the agent to "recommend the single option with the lowest total business cost" and to "never recommend an option solely because it has the lowest sticker price." The Task 4/5 cost functions are also wrapped as agent tools (`flight_business_cost_tool`, `hotel_business_cost_tool`) so a live agent can actually call them, and the manager task was rewritten to demand total-business-cost ranking. I made this change because the original prompt hard-codes price as the only objective; to change the *behavior*, the agent's stated objective has to change, not just the downstream math.

## Task 7: Original vs. Modified Recommendations
| Category | Price-only pick | Labor-aware pick ($75/hr) | Changed? |
|---|---|---|---|
| Flight | Option A (cheapest airfare) | **Option C** (lowest total) | **Yes** |
| Hotel | Airport North Inn (cheapest/night) | **Berlin Mitte** (lowest total) | **Yes** |

- **Flight:** best before = Option A ($130 airfare). Best after = Option C ($477.50 total vs A's $730). It changed because A's low fare is outweighed by ~8 hours of paid travel time; C's nonstop speed makes it cheapest overall.
- **Hotel:** best before = Airport North Inn ($94/night; note the original utility could not distinguish it from City Center Grand). Best after = Berlin Mitte ($400 total vs X's $413). It changed because X's long daily commute adds more labor than the nightly savings.

Both recommendations changed at $75/hr. Where a recommendation does *not* change at a given rate, it would only flip once the hourly rate is high enough that time savings outweigh the price gap — which is exactly what the sensitivity analysis demonstrates.

## Task 8: Sensitivity Analysis
Re-running the labor-aware evaluation at three employee hourly rates:

| Employee Hourly Rate | Recommended Flight | Flight Total Business Cost | Recommended Hotel | Hotel Total Business Cost |
|---|---|---|---|---|
| $40/hr | Option B | $390.00 | Airport North Inn | $308.00 |
| $75/hr | Option C | $477.50 | Berlin Mitte | $400.00 |
| $125/hr | Option C | $569.16 | City Center Grand | $475.00 |

Interpretation: as employee time gets more expensive, both recommendations shift toward faster and more central options. The flight recommendation moves B → C → C (never the cheapest-airfare Option A), and the hotel recommendation moves through all three options X → Z → Y. At a low $40/hr the cheapest-sticker options look best; by $125/hr the highest-sticker, lowest-time-cost options (nonstop flight, city-center hotel) win. This shows the "right" choice is a function of how much the company values employee time; a single fixed ranking by price cannot capture that.

## Task 9: Agentic AI Orchestration
This workflow is more than a single LLM prompt because the work is decomposed across specialized agents that use external tools and are coordinated by a manager. A single prompt would have to imagine flight and hotel data; here, the flight and hotel agents call real search tools (`search_flights`, `search_hotel`) to fetch grounded data, and the evaluator agents call scoring tools to compute decisions. Tools are how agents act on the world and on structured data rather than only generating text. The **manager agent** coordinates the others: it interprets the combined request, routes the flight and hotel sub-tasks to the appropriate managed agents, and assembles their structured outputs into one result — a division of labor that keeps each agent focused and its prompt simple. The **goal-based** and **utility-based** evaluators support decision-making in complementary ways: the goal-based agent enforces a hard constraint (budget), while the utility-based agent produces a graded preference score across multiple attributes. Introducing **labor-aware utility** changed the objective the agents optimize: instead of ranking by listed price, the evaluator now ranks by total business cost, the cost functions became callable tools, and the manager task explicitly asks for time-inclusive ranking. The orchestration structure stayed the same; what changed was the *criterion*, which is exactly the kind of business-logic change agentic systems are meant to accommodate.

## Task 10: Reflection
Optimizing for listed price can produce poor business decisions because the sticker price is only part of what a trip actually costs the company. A flight's fare ignores the paid hours an employee spends in transit, and a hotel's nightly rate ignores the paid hours lost to commuting. When those hours are cheap, price is a fine proxy; when they are expensive, price becomes actively misleading. In this assignment the cheapest airfare (Option A, $130) was the most expensive option once labor was included ($730), and the cheapest hotel was beaten by a pricier but closer one. Optimizing the visible number optimized the wrong thing.

Adding labor cost changes the objective function from "minimize price" to "minimize price plus the monetary value of employee time." That single change turns a one-dimensional comparison into a trade-off between money and time, and it makes the optimal choice depend on a parameter: the hourly rate; rather than being fixed. The sensitivity analysis makes this concrete: the recommended flight and hotel both shift as the rate rises, because the relative weight of time versus fare changes.

Several risks come with using agentic AI for travel procurement. The agents depend on live search APIs and an LLM, so results vary run to run and can silently degrade if a field is missing or an API changes. The cost model encodes assumptions (hourly rate, layover penalty, commute defaults) that, if wrong or gamed, produce confidently wrong recommendations. And an autonomous booking agent acting on a flawed estimate could commit real money. Data-quality issues are central: prices arrive as inconsistent strings, durations as free text, commute times may be absent, and star ratings are noisy. All of which the parsers must normalize, with documented defaults for missing values so nothing is silently dropped.

Before using this in a real company I would add guardrails beyond total cost: a maximum number of layovers and maximum total travel time, a required arrival window, a minimum hotel safety rating, cancellation flexibility, and adherence to company travel policy and per-diem limits. I would also surface traveler preferences and accessibility needs, log every assumption used, and keep a human approval step for any booking above a threshold. Total business cost is a much better objective than listed price, but it is still a model, and a responsible deployment treats its recommendation as a decision aid rather than a final answer.
