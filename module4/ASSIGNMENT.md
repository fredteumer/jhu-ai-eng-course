# Overview
In this assignment, you will work with a Jupyter notebook that demonstrates an agentic AI orchestration workflow using the smolagents package. The notebook simulates a commercial travel office where AI agents search for flight and hotel options, then evaluate those options using goal-based and utility-based criteria.

The current notebook identifies the least expensive and most expensive airfare options and evaluates hotel options based on price and quality. Your task is to extend this workflow so that the agentic system considers the true business cost of travel, not just the listed price of flights and hotels.

In real business travel, the cheapest listed option is not always the cheapest option overall. A low-cost flight with multiple layovers may require many more paid employee hours. A cheaper hotel outside the city center may create additional commute time that increases labor cost and reduces productivity. Your job is to modify the notebook so that the agents can account for these hidden labor costs.

# Files Provided
You will be provided with: `Goal_Based_&_Utility_Based_Agent (1)-1.ipynb`

You are responsible for running the notebook, understanding the existing workflow, and modifying the code to complete the assignment tasks.

# Learning Objectives
By completing this assignment, you will be able to:

- Explain how agentic AI orchestration can be used for business decision-making.
- Describe the difference between goal-based and utility-based agents.
- Read and modify an existing agentic AI workflow.
- Extend an AI agent’s decision criteria beyond simple price comparison.
- Incorporate labor cost into travel optimization.
- Evaluate whether an AI-generated recommendation is actually aligned with business value.
- Reflect on risks and limitations of agentic AI in operational decision-making.

# Business Scenario
You are working with a commercial travel office that books employee travel. The existing agentic AI workflow can search for flights and hotels and identify options based on airfare, hotel price, and hotel quality.

However, the current workflow does not account for the employee’s paid time during travel.

For example:

- A flight with two layovers may have a lower airfare, but if the employee spends six additional hours traveling, the company pays for that time.
- A hotel outside the city center may have a lower nightly rate, but if the employee spends extra time commuting each day, that commute time has a labor cost.
- The best business option may not be the cheapest listed airfare or the cheapest hotel. It may be the option with the lowest total business cost.

Your task is to modify the agentic workflow so that it accounts for these hidden costs.

# Setup Instructions
Open the provided Jupyter notebook and run the initial setup cells.

The notebook uses the smolagents package and external APIs for LLM and travel search functionality. Depending on your environment, you may need to install packages and configure credentials.

The notebook may include setup code similar to:
```
!pip install smolagents[toolkit] google-search-results google-serp-api
```

You will also need credentials for:

- An LLM endpoint
- SerpAPI or another travel search API, if required by the notebook
- Do not submit API keys, secret tokens, or private credentials.

If you use Google Colab secrets, confirm that your secrets are available to the notebook. If you use a local environment, you may need to modify the credential-loading code.

# Credential Safety Requirement
Your API keys or credentials must never appear in:

- Submitted notebook outputs
- Screenshots
- Written responses
- Markdown cells
- Code comments
- Shared files
- Before submitting your work, clear or verify any output cells that may expose secrets.

# Existing Notebook Workflow
The provided notebook demonstrates an agentic travel workflow with several major parts:

1. LLM setup
2. Flight search agent
3. Hotel search agent
4. Manager agent that orchestrates the workflow
5. Goal-based flight evaluation
6. Utility-based hotel evaluation

The current workflow evaluates travel options primarily using listed prices and basic quality criteria. Your assignment is to extend the workflow so that employee labor time is included in the cost calculation.

# Key Concept: Total Business Cost
For this assignment, you will calculate a more complete cost estimate.

## Flight Total Business Cost
A flight’s total business cost should include:
```
Total Flight Business Cost = Airfare + Labor Cost During Travel
```

Where:
```
Labor Cost During Travel = Total Travel Time in Hours × Employee Hourly Rate
```

You may use the flight duration provided by the notebook. If the result includes layover time or number of stops, you should incorporate that information in your calculation or explain your assumptions.

For example:
```
Airfare: $300
Total travel time: 7 hours
Employee hourly rate: $80/hour

Labor cost = 7 × 80 = $560
Total flight business cost = 300 + 560 = $860
```

## Hotel Total Business Cost

A hotel’s total business cost should include:
```
Total Hotel Business Cost = Lodging Cost + Commute Labor Cost
```

Where:
```
Lodging Cost = Price Per Night × Number of Nights
Commute Labor Cost = Daily Commute Time in Hours × Number of Travel Days × Employee Hourly Rate
```

For example:
```
Hotel price: $120/night
Stay length: 2 nights
Daily commute time: 1.5 hours
Employee hourly rate: $80/hour

Lodging cost = 120 × 2 = $240
Commute labor cost = 1.5 × 2 × 80 = $240
Total hotel business cost = 240 + 240 = $480
```

## Required Assumptions
Because travel APIs may return inconsistent fields, you must define and document your assumptions.

At minimum, your notebook must include clearly stated assumptions for:
- Employee hourly rate
- Number of hotel nights
- Whether travel time counts as paid labor time
- How layovers or number of stops are handled
- How commute time from hotel to business location or city center is estimated
- How missing or ambiguous travel data is handled

You may choose your own reasonable values, unless your instructor provides specific values.

For example, you may use:
```
EMPLOYEE_HOURLY_RATE = 75
HOTEL_NIGHTS = 2
DEFAULT_COMMUTE_MINUTES = 30
LAYOVER_PENALTY_HOURS = 1.5
```
You may use different values, but you must justify them.

## Assignment Tasks

### Task 1: Run and Understand the Original Notebook
Run the original notebook and inspect the outputs.

In your written response, explain:
```
What the flight agent does.
What the hotel agent does.
What the manager agent does.
What the goal-based evaluator does.
What the utility-based evaluator does.
```

Your explanation should be in your own words. Do not simply copy code from the notebook.

### Task 2: Identify the Limitation in the Existing Workflow
Explain why selecting the cheapest airfare or cheapest hotel may not minimize total business cost.

Your answer should include at least one flight example and one hotel example.

For example:
- A cheaper flight with longer travel time may cost more after labor is included.
- A cheaper hotel farther from the business destination may cost more after commute labor is included.

### Task 3: Add Employee Labor Cost Parameters
Modify the notebook to include configurable labor cost parameters.

At minimum, add variables for:
```
EMPLOYEE_HOURLY_RATE
HOTEL_NIGHTS
DEFAULT_COMMUTE_MINUTES
LAYOVER_PENALTY_HOURS
```

You may add additional parameters if useful.

Your code should make it easy to change the hourly rate and rerun the evaluation.

In your written response, explain why you chose your hourly rate and other assumptions.

### Task 4: Modify Flight Evaluation
Modify or extend the flight evaluation logic so that each flight option includes a total business cost.

Your modified flight evaluation should calculate:
- Airfare
- Estimated travel time in hours
- Estimated labor cost during travel
- Total flight business cost
- Whether the option is still attractive after labor cost is included

Your output should make it clear whether the flight with the lowest airfare is also the flight with the lowest total business cost.

You may create a new function, such as:

```
calculate_flight_business_cost(flight, employee_hourly_rate)
```

Or you may modify the existing goal-checking function.

Your code should include comments explaining the calculation.

### Task 5: Modify Hotel Evaluation
Modify or extend the hotel evaluation logic so that each hotel option includes a total business cost.

Your modified hotel evaluation should calculate:
- Price per night
- Number of nights
- Lodging cost
- Estimated commute time
- Commute labor cost
- Total hotel business cost
- Whether the hotel is still attractive after commute labor cost is included

You may create a new function, such as:
```
calculate_hotel_business_cost(hotel, employee_hourly_rate, hotel_nights)
```

Or you may modify the existing utility-checking function.

Your code should include comments explaining the calculation.

### Task 6: Update the Agent Prompt or Evaluation Criteria
Modify at least one agent prompt, system prompt, or evaluation task so that the agent explicitly considers total business cost.

For example, you might update the manager agent task so that it asks for:
```
Do not rank options only by listed price. Estimate total business cost by including employee labor cost during travel and commuting.
```

Or you might update the evaluator prompt so that the agent returns:
```
airfare, travel labor cost, total business cost, and recommendation
```

Your written response should identify the exact prompt or evaluation instruction you changed and explain why.

### Task 7: Compare Original and Modified Recommendations
Compare the original recommendation with your modified cost-aware recommendation.

Your comparison should answer:
- Which flight looked best before labor cost was included?
- Which flight looks best after labor cost is included?
- Did the recommendation change? Why or why not?
- Which hotel looked best before commute labor cost was included?
- Which hotel looks best after commute labor cost is included?
- Did the recommendation change? Why or why not?

If your recommendation does not change, explain what would need to be different for it to change.

TODO: HERE
### Task 8: Add a Sensitivity Analysis
Run your modified evaluation using at least three different employee hourly rates.

For example:
```
$40/hour
$75/hour
$125/hour
```
For each hourly rate, report the recommended flight and hotel.

Your goal is to show whether the recommendation changes as employee time becomes more expensive.

You may present your results in a table.

Example format:

| Employee Hourly Rate | Recommended Flight | Flight Total Business Cost | Recommended Hotel |Hotel Total Business Cost |
|----------------------|--------------------|----------------------------|-------------------|--------------------------|
| $40/hour | Option A | $___ | Hotel X | $___ |
| $75/hour | Option B | $___ | Hotel Y | $___
$125/hour | Option B | $___ | Hotel Z | $___

### Task 9: Explain the Role of Agentic AI
Write a short explanation of how this workflow demonstrates agentic AI orchestration.

Your answer should discuss:
- Why this is more than a single LLM prompt.
- How tools are used by agents.
- How the manager agent coordinates other agents.
- How goal-based and utility-based evaluation support decision-making.
- What changed when you introduced labor-aware utility calculations.

### Task 10: Reflect on Business and AI Engineering Implications
Write a 300–500 word reflection addressing the following questions:
- Why can optimizing for listed price produce poor business decisions?
- How does adding labor cost change the objective function?
- What risks exist when using agentic AI for travel procurement?
- What data quality issues could affect the recommendation?
- What additional constraints would you add before using this in a real company?

Examples of additional constraints might include:
- Maximum number of layovers
- Maximum total travel time
- Required arrival window
- Hotel safety rating
- Cancellation flexibility
- Traveler preference
- Carbon emissions
- Accessibility needs
- Company travel policy

## Deliverables
Submit the following:
1. Completed Jupyter notebook: Submit your modified `.ipynb` file with all relevant cells run and outputs visible.
2. Written response: Submit a PDF, Word document, or Markdown file answering Tasks 1–10.
3. Optional notebook export: You may also submit an HTML or PDF export of the notebook if Canvas does not render notebook outputs clearly.

Do not submit:
- API keys
- Secret tokens
- Private credentials
- Any file containing live credentials

## Suggested Written Response Structure
Use the following headings:
```
Task 1: Original Notebook Workflow
Task 2: Limitation of Listed Price Optimization
Task 3: Labor Cost Parameters
Task 4: Modified Flight Evaluation
Task 5: Modified Hotel Evaluation
Task 6: Prompt or Evaluation Criteria Update
Task 7: Original vs. Modified Recommendations
Task 8: Sensitivity Analysis
Task 9: Agentic AI Orchestration
Task 10: Reflection
```

## Minimum Technical Requirements
Your modified notebook must include:
- A configurable employee hourly rate.
- A total business cost calculation for flights.
- A total business cost calculation for hotels.
- At least one modified prompt, task, or evaluator instruction.
- A comparison of recommendations before and after labor cost is included.
- A sensitivity analysis using at least three hourly rates.
- Clear comments explaining your changes.
- Output cells showing that your modified code was run.

## Recommended Implementation Guidance
You may find it helpful to add helper functions such as:
```
def parse_price(price_value):
    """Convert a price string such as '$1,250' into a float."""
    pass
```
```
def estimate_travel_hours(flight):
    """Estimate total travel hours from flight duration and stops."""
    pass
```
```
def calculate_flight_business_cost(flight, employee_hourly_rate):
    """Calculate airfare, labor cost, and total business cost for a flight."""
    pass
```
```
def estimate_commute_hours(hotel):
    """Estimate commute hours from hotel distance or travel-time fields."""
    pass
```
```
def calculate_hotel_business_cost(hotel, employee_hourly_rate, hotel_nights):
    """Calculate lodging cost, commute labor cost, and total hotel business cost."""
    pass
```
You do not have to use these exact function names, but your code should be organized, readable, and easy to evaluate.

## Handling Missing or Messy Data
Travel search results may not always contain clean or consistent fields. Your code should handle common issues such as:
- Prices formatted as strings, such as `"$350"` or `"$1,200"`
- Missing hotel distance values
- Duration written in natural language, such as `"5 hours and 30 minutes"`
- Flights with stops or layovers
- Hotels with distance but no commute time
- Unexpected or incomplete API responses

When data is missing, you may use a documented default assumption. Do not silently ignore missing data.

## Grading Rubric
Total: 100 points

### 1. Original Workflow Understanding — 10 points
Full credit requires a clear explanation of the flight agent, hotel agent, manager agent, goal-based evaluator, and utility-based evaluator.

### 2. Business Problem Framing — 10 points
Full credit requires a clear explanation of why listed price alone is insufficient for business travel decisions, including both flight and hotel examples.

### 3. Labor Cost Parameters — 10 points
Full credit requires configurable parameters for employee hourly rate, hotel nights, commute assumptions, and layover assumptions, with a clear explanation of chosen values.

### 4. Flight Business Cost Modification — 15 points
Full credit requires working code that calculates airfare, travel labor cost, and total flight business cost, with clear output and comments.

### 5. Hotel Business Cost Modification — 15 points
Full credit requires working code that calculates lodging cost, commute labor cost, and total hotel business cost, with clear output and comments.

### 6. Agent Prompt or Evaluation Update — 10 points
Full credit requires at least one meaningful modification to an agent prompt, system prompt, or evaluation instruction so that the agent considers total business cost.

### 7. Recommendation Comparison — 10 points
Full credit requires a clear comparison of original and modified recommendations, including whether and why recommendations changed.

### 8. Sensitivity Analysis — 10 points
Full credit requires evaluation at three different employee hourly rates and a clear interpretation of the results.

### 9. Code Quality and Robustness — 5 points
Full credit requires readable, organized code that handles messy or missing data using documented assumptions.

### 10. Reflection — 5 points
Full credit requires a thoughtful 300–500 word reflection connecting the assignment to real-world AI engineering and business decision-making.

## Academic Integrity and Responsible AI Use
You may use AI tools to help understand errors, debug code, or brainstorm implementation approaches. However, your submitted work must demonstrate your own understanding. You are responsible for all code, calculations, assumptions, and explanations in your submission.

Do not submit AI-generated explanations that you cannot explain in your own words.

## Final Checklist Before Submission
Before submitting, confirm that:
- Your notebook runs.
- Your modified code cells have been executed.
- Your outputs are visible.
- Your notebook includes labor-aware flight cost calculations.
- Your notebook includes labor-aware hotel cost calculations.
- Your notebook includes a sensitivity analysis using three hourly rates.
- Your written response answers all required tasks.
- Your assumptions are clearly documented.
- No credentials, API keys, or secret tokens appear in your submission.
