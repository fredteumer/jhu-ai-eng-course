# Module 5: Prompt Optimization and Evaluation with DSPy

Notebook: `Prompt_Optimization_and_Evaluation.ipynb`

## Task 1: Run the Notebook Successfully 
I had to make the following changes to get a successful e2e:
- Set up a `.venv` and run jupyter. 
- Edited notebook to point to `gold_reviews.csv` and `test_reviews.csv` without the `/content/` folder prepend.
- Create and populate `config.json`
- Reconfigure the notebook to use `gemini-flash-lite-latest` over `gpt-4o-mini`
- Raised the DSPy program's `max_tokens` from `1024` to `8192` so the model's structured JSON output wouldn't get truncated mid-answer (which had caused a DSPy parse error).

I ran the notebook headless in the terminal to achieve this. 

## Task2: Explain the Dataset Roles 
>Note: To increase readability, I loaded both into a [Google Sheet](https://docs.google.com/spreadsheets/d/16Zx-p7FIehkMsdnPTtFLcSNZ71OtuAyOamfqRAee4RA/)

### What is `gold_reviews.csv` used for?
`gold_reviews.csv` is the "practice" set: the data the optimizer is allowed to learn from. The system runs the starting prompt on these 12 products, looks at where the AI's summaries fall short, and automatically rewrites the prompt's instructions to do better. These are the products the prompt gets to study and improve on.

### What is `test_reviews.csv` used for?
`test_reviews.csv` is the "final exam": a separate set of 8 products the optimizer never sees while it's improving the prompt. Once the prompt has been tuned on the practice set, both the original prompt and the improved prompt are run on these unseen products, and a separate grader model scores the summaries. It exists only to measure, honestly, whether the improved prompt actually got better on data it could not have memorized.

### Why should the test dataset not be used to directly optimize the prompt? 
If you tune the prompt using the same products you later grade it on the LLM is essentially just memorizing those specific answers rather than genuinely getting better at summarizing reviews in general. That makes the final score meaningless. Holding the test set back until the very end is the only way to tell whether the improvement is real (it works on new products) rather than fake (it just memorized the practice set). 

## Task 3: Explain the Baseline Workflow
The baseline workflow runs in Phase 3, applying the original v1.0 prompt to every product before any optimization. 

**Input**: For each product the model receives the metadata (name, category, number of reviews, average rating) plus the full block of customer reviews, along with fixed rules telling it to stay honest, only use claims the reviews support, reflect the true sentiment balance, and return strict JSON. 

**Output**: A single JSON object with five fields: a 2–3 sentence balanced summary, top positives, top complaints, feature requests, and an overall sentiment label. 

**How it's judged**: There's no answer key: separate grader models score each summary. A stability check (consistent when asked twice?), a faithfulness/balance/hallucination check (is every claim backed by the reviews?), and a relevance/clarity/actionability check (useful to a product manager?) blended into a single per-product score from 0 to 1. 

**Baseline result**: Across the 12 products the original prompt scored a mean of `0.374`, with individual products ranging from `0.30` to `0.63`. Notably, most products sat right at the `0.30` floor, which suggests the baseline summaries were consistently marked down by the graders and left clear room for improvement, exactly what the optimization step then targeted.

## Task 4: Explain the DSPy Optimization Workflow
Optimization lives in Phase 7 and is a DSPy program. GEPA is run on it with the `auto="light"` budget. 

The 12 gold products are the training examples GEPA scores candidate prompts against. An interesting note: GEPA tuned and graded on the same 12 products (no separate validation set) so it increases the risk of overfitting the prompt to that product set.

GEPA rewrites the instructions and never touches the actual reviews or the required output fields. It evolves the wording of the rules themselves: 4 short honesty rules and it's up to GEPA to find a better performing version of the original input text. 

The grader models in Phase 5 and 6 take the candidate prompts and grade them on a score from 0 to 1 and provide written feedback. GEPA hands that feedback to the "coach" model which determines failures and proposes a revised prompt. It tries to raise the score and discards the weaker ones until the budget runs out. 

The optimized version differs from the baseline in that we have moved from an honesty prompt to a rigid specification. It ensures that the wording adheres to a set of more specific directives: never mention the product name unless a reviewer does (a leakage guard), "zero inference / no narrative" (report "Software: Application crashes," not "the software is unreliable"), a required favorable-vs-non-favorable ratio in every summary, an exact fixed format for the sentiment label, and a `[Component]: [Specific Failure]` ticket format for complaints and feature requests. It essentially converted a general honesty prompt into a structured, ticket-style extraction spec.

## Task 5: Compare Baseline and Optimized Performance
**Baseline**: On the 12 gold products, the original scored a mean of 0.374 with a range from 0.30-0.63

**Optimized Performance**: After GEPA, mean raises to 0.494 (+0.12) showing improvement on 9/12 products. 2 products regressed and one stayed unchanged. With the held-out test set, the optimized prompt held ~0.49 (0.45–0.50), and every product passed the confidence gate (70.5–87.5 out of 100).

**Did it improve?**: On average, yes. Most products showed improvement, but the gain is relatively shallow. Nearly every optimized product landed at 0.50. GEPA mostly just helped to raise the floor but, more notably, capped the ceiling. The already strong product (Ergodesk Chair) dropped in rating to 0.50. 

**Possible Reasons**: The near consistent and flat 0.50 is the tell. GEPA converged a rigid, format-enforcing prompt so it lifts the bottom but capst the top. It's also likely the metric is fairly coarse (scores cluster at 0.30 / 0.50), so the "+0.12" partly reflects products snapping up to a 0.50 plateau rather than a smooth per-product quality gain. 

Encouragingly, the same ~0.49 appears on the unseen test set, so the optimized prompt did generalize (it didn't collapse on new products) but it generalized to the same flat plateau, reinforcing that the improvement is real yet limited.

## Task 6: Inspect Individual Predictions



## Task 7: Modify the Notebook

## Task 8: Reflection
