# Overview
In this assignment, you will use AI as a coding assistant to build, test, debug, and refine a Python-based inventory simulation for a cloud kitchen.

A cloud kitchen is a delivery-only food business where multiple virtual restaurant brands share the same kitchen, staff, equipment, and ingredients. This creates operational challenges because the same ingredients may be used across many menu items and brands. If one ingredient runs out or expires, several menu items may become unavailable at the same time.

Your task is to use AI-assisted coding practices to build a simulation that processes customer orders, checks recipe-linked inventory, updates delivery status, deducts ingredient quantities, tracks expiry risk, and creates a restock plan.

The purpose of this assignment is not just to produce working code. You must also demonstrate that you can guide AI effectively, inspect AI-generated code critically, test it, debug it, and document your decisions.

## Files Provided
You will receive the following files from your instructor:
- `AI-Assisted Cloud Kitchen Inventory Simulation.pdf`
- `seed_data-1.pyDownload seed_data-1.py`
- `main.py`
- `test_main.py`

You will need to create your own files,
- `PROJECT_SPEC.md`

## Learning Objectives
By completing this assignment, you will be able to:
- Use AI tools to plan, implement, test, and debug a Python program.
- Break a software problem into small implementation tasks.
- Maintain a project specification file to reduce context drift when using AI.
- Evaluate AI-generated code instead of accepting it uncritically.
- Write and run unit tests for AI-generated functions.
- Implement rule-based business logic in Python.
- Explain the difference between AI-assisted coding and autonomous AI decision-making.
- Reflect on the strengths and limitations of using AI as a programming partner.

## Business Scenario
A cloud kitchen operates multiple virtual brands from one shared kitchen. Each menu item is linked to a recipe, and each recipe consumes ingredients from a shared inventory.

The kitchen faces several operational problems:

- Ingredients may run out mid-shift.
- Orders may be accepted for menu items the kitchen cannot fulfill.
- Expired or soon-to-expire ingredients may create waste or quality risk.
- Restocking may be inefficient if the kitchen lacks visibility into ingredient usage.
- Manual menu and inventory updates can cause errors.

You will build a Python simulation that models these problems and creates a more reliable inventory workflow.

## Role of AI in This Assignment
You are expected to use AI as a coding assistant, but you are responsible for the final result.

Think of AI as a fast but unreliable junior developer. It can generate code quickly, but it may misunderstand requirements, invent assumptions, duplicate logic, or produce code that only appears correct.

Throughout the assignment, you will play three roles:
**Navigator**: You define the goal, break the work into tasks, and decide what to ask the AI to do.
**Reviewer**: You inspect AI-generated code, identify assumptions, check outputs, and look for errors.
**Decision-Maker**: You decide what to accept, reject, revise, test, or refactor.

You may use AI tools to help write code, debug errors, generate tests, and improve explanations. However, your submitted work must show your own understanding.

## Required Development Practice
You must use an incremental AI-assisted development workflow.

For each major task:
- Ask AI for a plan or task breakdown.
- Ask AI to implement only one small task at a time.
- Review the generated code.
- Ask AI to identify assumptions, uncertainty, and incomplete sections.
- Write or generate unit tests.
- Run the tests.
- Debug failures before moving on.
- Update your project specification file.
- Do not ask AI to build the entire project in one prompt.

## Required Project Files
Your final submission should include:
```
main.py
seed_data.py
test_main.py
PROJECT_SPEC.md
AI_USAGE_LOG.md
```
You may add additional files if useful.

`main.py`
This file should contain your main simulation logic.

`seed_data.py`
This file contains the starting data for recipes, inventory, orders, restock records, and delivery status.

`test_main.py`
This file should contain your unit tests.

`PROJECT_SPEC.md`
This file is your external memory for the project. It should summarize:

- What you are building
- Current components and their status
- Important design decisions
- Business rules
- Constraints
- Current task and next task
- Known issues or assumptions

`AI_USAGE_LOG.md`
This file should document how you used AI. For each major interaction, include:
- The task you were working on
- The prompt you gave the AI
- A short summary of the AI’s response
- What you accepted, changed, or rejected
- Any issues you found in the AI output
- You do not need to include every minor prompt, but you should include enough evidence to show that you used AI thoughtfully and critically.

## Core Data Structures
Your simulation will use five core data structures from `seed_data.py`:
```
Recipes
Inventory
Orders
Restock
Status
```
The exact format will be provided in the data file. Your code should inspect and use the provided structure rather than assuming a completely different schema.

## Functional Requirements
Your program must implement the following functionality.

### Requirement 1: Load and Display Data
Create functions that import and display all major data structures from `seed_data.py`.

Your program should be able to show:
- Recipes
- Inventory
- Orders
- Restock records
- Delivery status records

You should use this step to confirm that your program can access all required data.

### Requirement 2: Process Orders Against Recipes
For each order, your program should:
- Identify the menu item or items ordered.
- Look up the corresponding recipe.
- Calculate the total ingredient quantity required.
- Handle item quantities correctly.
- Handle missing or unknown recipes gracefully.

For example, if an order contains quantity 2 of a menu item, the required ingredient quantities should be doubled.

### Requirement 3: Check Inventory Availability
Before fulfilling an order, your program should check whether the required ingredients are available in sufficient quantity.

The check should account for:
- Ingredient name
- Quantity required
- Quantity available
- Expiry status, if expiry dates are included in the inventory data

The function should return clear information about whether the order can be fulfilled and, if not, what is missing or unavailable.

### Requirement 4: Fulfill Orders and Deduct Inventory
If all required ingredients are available, your program should:
- Mark the order as Delivered
- Deduct the used ingredient quantities from inventory

If required ingredients are missing or unavailable, your program should:
- Mark the order as Not Delivered
- Record the reason
- Add missing or unavailable ingredients to the restock list

Your code should clearly define whether failed orders deduct any partial inventory. For the base assignment, use all-or-nothing fulfillment unless your instructor states otherwise.

### Requirement 5: Make Inventory Deduction Cumulative
Inventory deduction must be cumulative.

This means:
- `Order 1` consumes inventory.
- `Order 2` checks against the inventory remaining after `Order 1`.
- `Order 3` checks against the inventory remaining after `Orders 1` and `2`.
- The final inventory table should reflect all delivered orders.

Do not reset inventory between orders unless you are running a separate test case.

### Requirement 6: Apply Restock and Expiry Rules
After processing orders, apply restock logic.

Your program should identify ingredients that meet any of the following conditions:
- Ingredient is out of stock.
- Ingredient is running low.
- Ingredient is expired or expiring soon.

Unless your instructor provides different values, use these rules:
- Running low threshold: quantity ≤ 1,000g
- Par level: 10,000g
- Expiring soon window: within 5 days of the simulation date

Your restock output should include:
- Ingredient name
- Current quantity
- Reason for restock
- Quantity needed to reach par level
- Any relevant expiry information

If an ingredient qualifies for more than one reason, your code should preserve all relevant reasons instead of silently overwriting them.

### Requirement 7: Produce a Business-Friendly Summary
At the end of the simulation, produce a clear summary that includes:
- Number of orders delivered
- Number of orders not delivered
- Final inventory levels
- Restock recommendations
- Any ingredients that are low, out of stock, expired, or expiring soon
- Any orders that could not be fulfilled and why

This output should be understandable to a non-technical kitchen manager.

## Required AI Prompt Templates
Use the following prompt patterns during the assignment.

### Planning Prompt
Use this before building a major component.
```
I want to build [COMPONENT OR FEATURE]. Before writing any code, give me a high-level plan. What components do I need and what should I build first?
```

### Task Breakdown Prompt
Use this after you have a plan.

```
Here is component [COMPONENT NAME] from our plan. Break it into individual implementation tasks. Keep each task small enough to implement in a single prompt.
```

### Implementation Prompt
Use this for one task at a time.
```
Implement Task [N]: [DESCRIPTION]. Use Python. Keep the code simple and add comments explaining each section. Do not implement any other tasks yet.
Validation Hook Prompt
```
Use this after AI generates code.

After generating the code, add inline comments or notes that identify:
1. Any assumptions you made that I should verify
2. Any parts you are uncertain about
3. Any sections that are incomplete or require follow-up

### Debugging Prompt
Use this when code fails or results are unexpected.
```
Here is the code and the error it produces: [PASTE CODE] / [PASTE ERROR]. Explain what is wrong and why. Then provide a corrected version with comments explaining what was changed and why.
```

## Required Tasks

### Task 1: Set Up the Project
Create or organize the following files:
```
main.py
seed_data.py
test_main.py
PROJECT_SPEC.md
AI_USAGE_LOG.md
```
Run a simple import test to confirm that `main.py` can access data from `seed_data.py`.

In your written response, explain:
- How your project is organized.
- How to run your program.
- How to run your tests.
- Any setup issues you encountered.

### Task 2: Create `PROJECT_SPEC.md`
Create a project specification file that documents your current understanding of the project.

It should include:
- Project purpose
- Data structures
- Business rules
- Implementation plan
- Testing plan
- Open questions or assumptions

Update this file throughout the assignment.

### Task 3: Load and Inspect Seed Data
Write functions that load and print or return the five main data structures.

Your code should show that you can access:
- Recipes
- Inventory
- Orders
- Restock
- Status

Write unit tests that verify:
- All required data structures are present.
- Each data structure has the expected type.
- Each data structure contains records.
- Key fields are present.

### Task 4: Implement Recipe Lookup
Write a function that looks up a recipe for an ordered item.

Your function should:
- Accept an item name or order line.
- Return the required ingredients and quantities.
- Handle missing recipes gracefully.

Write unit tests for:
- A valid item with a matching recipe.
- An invalid item with no matching recipe.
- A quantity greater than 1.

### Task 5: Implement Inventory Availability Check
Write a function that checks whether inventory can fulfill an order.

Your function should:
- Compare required ingredients against available stock.
- Identify missing ingredients.
- Identify ingredients with insufficient quantity.
- Identify expired or unusable ingredients, if expiry data is available.

Write unit tests for:
- All ingredients available.
- One ingredient missing.
- One ingredient with insufficient quantity.
- One expired or invalid ingredient, if applicable.

### Task 6: Implement Fulfillment Logic
Write a function that processes an order.

If the order can be fulfilled:
- Mark it as delivered.
- Deduct ingredients from inventory.

If the order cannot be fulfilled:
- Mark it as not delivered.
- Record the reason.
- Add missing or unavailable ingredients to restock recommendations.

Write unit tests for:
- Successful delivery.
- Failed delivery due to missing stock.
- Correct inventory deduction after delivery.
- No unintended deduction after failed delivery.

### Task 7: Implement Cumulative Order Processing
Write a function that processes all orders in sequence.

Your function should ensure that each order uses the inventory remaining after previous delivered orders.

Write unit tests for:
- Two orders consuming the same ingredient.
- An order that fails because an earlier order used the remaining stock.
- Final inventory matching expected values.

### Task 8: Implement Restock and Expiry Rules
Write or update a function that generates restock recommendations.

Your logic should account for:
- Out-of-stock ingredients
- Low-stock ingredients
- Expiring soon ingredients
- Multiple restock reasons for the same ingredient

Write unit tests for:
- Ingredient with zero stock
- Ingredient below or equal to the low-stock threshold
- Ingredient above the threshold
- Ingredient expiring soon
- Ingredient with multiple restock reasons

### Task 9: Generate Final Business Summary
Create a final output that summarizes the simulation for a business user.

The summary should include:
- Delivered orders
- Not delivered orders
- Reasons for non-delivery
- Final inventory
- Restock recommendations
- Expiry concerns

The output may be printed to the console, returned as a dictionary, or written to a text or Markdown file.

### Task 10: Refactor and Review
After completing the core functionality, review your code for:
- Duplicate logic
- Hard-coded values that should be constants
- Unclear function names
- Missing comments
- Weak error handling
- Functions that do too much

Use AI to help identify possible refactoring opportunities, but you decide what to change.

Document at least two improvements you made during refactoring.

### Task 11: Reflection on AI-Assisted Coding
Write a 400–600 word reflection addressing the following questions:
- How did AI help you move faster?
- Where did AI make mistakes or questionable assumptions?
- How did testing help you evaluate AI-generated code?
- What did you change or reject from the AI’s suggestions?
- How did `PROJECT_SPEC.md` help maintain context?
- What would you do differently in a future AI-assisted coding project?

## Optional Enhancement
Choose one optional enhancement if you want to go beyond the base requirements.

### Option A: Partial Fulfillment
Modify the logic so that if part of an order can be fulfilled, those items are delivered and only unavailable items are marked as not delivered.

### Option B: Predictive Stockout Alert
Estimate which ingredients are likely to run out soon based on observed consumption across orders.

### Option C: Dynamic Menu Item Disabling
Identify menu items that should be marked unavailable because one or more required ingredients are out of stock or unusable.

### Option D: Improved Reporting
Generate a polished business report in Markdown, CSV, or HTML format.

Optional enhancements may earn extra credit if they are working, tested, and clearly documented.

## Deliverables
Submit the following:
```
main.py
test_main.py
PROJECT_SPEC.md
AI_USAGE_LOG.md
Written reflection
Optional: any additional output files or reports
Do not submit files containing private credentials, API keys, or unrelated personal information.
```

## Suggested Written Response Structure
Use the following headings:
```
Project Setup
Data Loading
Recipe Lookup
Inventory Availability
Order Fulfillment
Cumulative Processing
Restock and Expiry Logic
Business Summary
Refactoring Notes
AI Usage Summary
Reflection
```

## Minimum Technical Requirements
Your submission must include:
- Working Python code.
- Use of the provided seed data.
- Functions for data loading, recipe lookup, inventory checking, order fulfillment, cumulative processing, restock logic, and final reporting.
- Unit tests for major functions.
- Evidence that tests were run.
- A maintained `PROJECT_SPEC.md`.
- An `AI_USAGE_LOG.md`.
- A written reflection on AI-assisted coding.

## Grading Rubric
Total: 100 points

### 1. Project Setup and Data Loading — 10 points
Full credit requires a clear project structure, successful import of seed_data.py, and working functions to access the five core data structures.

### 2. Recipe Lookup and Ingredient Calculation — 10 points
Full credit requires correct recipe lookup, quantity scaling, and graceful handling of missing recipes.

### 3. Inventory Availability Logic — 10 points
Full credit requires accurate comparison of required ingredients against available inventory, including missing or insufficient ingredients.

### 4. Fulfillment and Status Updates — 15 points
Full credit requires correct delivery status updates, inventory deduction for delivered orders, no unintended deduction for failed orders, and meaningful failure reasons.

### 5. Cumulative Inventory Processing — 10 points
Full credit requires inventory to be updated across sequential orders so later orders use remaining stock.

### 6. Restock and Expiry Logic — 10 points
Full credit requires correct handling of low stock, out-of-stock, expiring soon, and multiple restock reasons.

### 7. Unit Testing — 15 points
Full credit requires meaningful tests for major functions, including normal cases, edge cases, and failure cases. Tests must be runnable and results must be visible or documented.

### 8. AI-Assisted Development Process — 10 points
Full credit requires a useful PROJECT_SPEC.md, meaningful AI usage documentation, evidence of prompt-based iteration, and evidence that the student reviewed rather than blindly accepted AI output.

### 9. Code Quality and Refactoring — 5 points
Full credit requires readable, organized code with clear function names, constants for key thresholds, comments where useful, and reduced duplication.

### 10. Reflection — 5 points
Full credit requires a thoughtful reflection on the benefits, risks, and limitations of AI-assisted coding.

## Academic Integrity and Responsible AI Use
You are allowed and encouraged to use AI tools in this assignment. However, AI use must be documented, and you are responsible for the final work.

You may use AI to:
- Plan the project
- Break tasks into smaller steps
- Generate draft code
- Explain errors
- Suggest tests
- Suggest refactoring

You may not:
- Submit code you do not understand
- Submit AI-generated explanations you cannot explain
- Ignore failed tests
- Hide known defects
- Claim AI-generated work as fully your own without documenting your process

Your grade is based not only on whether the program works, but also on how well you demonstrate responsible, critical, and effective AI-assisted coding practice.

## Final Checklist Before Submission
Before submitting, confirm that:
- `main.py` runs.
- `test_main.py` runs.
- The program uses `seed_data.py`.
- The final inventory is cumulative.
- Restock logic handles low stock and expiry.
- Failed orders include reasons.
- Tests cover both success and failure cases.
- `PROJECT_SPEC.md` is complete and updated.
- `AI_USAGE_LOG.md` documents your AI-assisted process.
- Your reflection answers all required questions.
- You understand the code you are submitting.
