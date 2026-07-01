# Overview
In this assignment, you will use a Jupyter notebook to explore prompt optimization and evaluation using DSPy. The notebook is executable, but your task is not simply to run it from top to bottom. You must demonstrate that you can read, understand, use, evaluate, and modify the code.

You will work with a product review classification task. The notebook uses a gold dataset for prompt optimization and a test dataset for evaluation. You will configure access to an LLM, run the notebook, inspect the results, and complete several coding and analysis tasks that demonstrate your understanding of prompt optimization.

# Files Provided
You will be given the following files:
- `Prompt_Optimization_and_Evaluation.ipynb`
- `gold_reviews.csvDownload gold_reviews.csv`
- `test_reviews.csvDownload test_reviews.csv`

You are responsible for creating your own `config.json` file containing your LLM credentials.

# Learning Objectives
By completing this assignment, you will be able to:
- Explain the purpose of prompt optimization and evaluation.
- Run and inspect a DSPy-based prompt optimization workflow.
- Understand how gold and test datasets are used differently.
- Interpret evaluation results before and after optimization.
- Modify notebook code to test a new prompt, metric, or evaluation condition.
- Reflect on the limitations of prompt optimization and automated evaluation.

# Setup Instructions
Place the following files in the same working directory:
- `Prompt_Optimization_and_Evaluation.ipynb`
- `gold_reviews.csv`
- `test_reviews.csv`
- `config.json`

Create a file named `config.json` with your own LLM access credentials. The exact values will depend on the provider or endpoint you are using. Use the format below as a starting point:
```
{
  "API_KEY": "your_api_key_here",
  "OPENAI_API_BASE": "your_base_url_here"
}
```

Do not submit your `config.json` file. It contains private credentials.

If you are using Google Colab, you may need to upload the notebook and CSV files into the Colab runtime. If the notebook uses paths such as `/content/gold_reviews.csv` and `/content/test_reviews.csv`, make sure the files are uploaded to that location. If you are running locally, you may need to update the file paths to:
```
gold_dataset_path = "gold_reviews.csv"
test_dataset_path = "test_reviews.csv"
```

# Important Credential Safety Requirement
Your API key or LLM credentials must never appear in your submitted notebook, screenshots, write-up, or code comments. Keep credentials only in `config.json`, and do not submit that file.

Before submitting, check that your notebook does not reveal your API key in any cell output.

# Assignment Tasks
## Task 1: Run the Notebook Successfully
Run the notebook from beginning to end.

Your notebook should demonstrate that you can:
- Load the gold and test datasets.
- Configure the LLM connection.
- Run the baseline prompt or baseline classifier.
- Run the DSPy optimization workflow.
- Evaluate the optimized prompt or program on the test dataset.

If the notebook does not run successfully on the first attempt, debug it. You may need to fix file paths, install packages, or update configuration values.

In your written response, briefly describe any setup or debugging steps you had to complete.

## Task 2: Explain the Dataset Roles
In your own words, explain the purpose of each dataset:
- What is `gold_reviews.csv` used for?
- What is `test_reviews.csv` used for?
- Why should the test dataset not be used to directly optimize the prompt?

Your answer should show that you understand the difference between optimization data and evaluation data.

## Task 3: Explain the Baseline Workflow
Identify the part of the notebook that runs the baseline prompt or baseline classification workflow.

In your written response, explain:
- What input the model receives.
- What output the model is expected to produce.
- What metric or evaluation logic is used to judge the output.
- What the baseline results show before optimization.

Include relevant code cells or screenshots in your submitted notebook or PDF export.

## Task 4: Explain the DSPy Optimization Workflow
Identify the part of the notebook that uses DSPy for prompt optimization.

In your written response, explain:
- What DSPy is optimizing.
- What examples are used during optimization.
- What metric or scoring function guides the optimization.
- How the optimized version differs from the baseline version.

Do not simply paste code. Explain what the code is doing in plain language.

## Task 5: Compare Baseline and Optimized Performance
Compare the model’s performance before and after prompt optimization.

Your comparison should include:
- Baseline performance.
- Optimized performance.
- Whether performance improved, declined, or stayed about the same.
- At least one possible reason for the result.

If the optimized prompt performs worse than expected, that is acceptable. Your job is to analyze the outcome, not force a perfect result.

## Task 6: Inspect Individual Predictions
Choose at least three examples from the test dataset and inspect the model’s predictions.

For each example, provide:
- The product or review example you selected.
- The expected output or label.
- The model’s output.
- Whether the output was correct or incorrect.
- A brief explanation of why the example was easy, difficult, ambiguous, or error-prone.

At least one of your examples should be a case where the model made an error or produced an imperfect response. If your model produces no errors, choose the most ambiguous or challenging example and explain why it could have been difficult.

## Task 7: Modify the Notebook
Modify the notebook in one meaningful way. Your modification must require you to understand and change the code, not just rerun an existing cell.

Choose one of the following options:

### Option A: Modify the prompt or DSPy signature
Change the wording, structure, or instructions used by the model. Then rerun the relevant cells and compare results.

### Option B: Modify the evaluation metric
Change or extend the evaluation logic. For example, you might make the metric stricter, more lenient, or more informative.

### Option C: Add an error analysis table
Create a table showing examples where the model was incorrect, including the input, expected output, model output, and your explanation of the likely cause.

### Option D: Add a small custom test set
Create at least three new examples of your own and evaluate the baseline or optimized prompt on them.

### Option E: Compare two LLM configurations
If you have access to more than one model or endpoint, compare results across two configurations.

In your written response, describe:
- What you changed.
- Why you made that change.
- What happened after the change.
- What you learned from the result.

## Task 8: Reflect on Prompt Optimization
Write a short reflection of 300–500 words addressing the following questions:
- What did prompt optimization improve?
- What did it not improve?
- What risks or limitations did you observe?
- How would you decide whether an optimized prompt is ready for production use?
- What additional evaluation would you want before deploying this workflow?

Your reflection should connect the technical results to real-world AI engineering practice.

# Deliverables
Submit the following:
- Your completed Jupyter notebook
- Submit the `.ipynb` file with all cells run and outputs visible.
- A short written response
- This may be submitted as a PDF, Word document, or Markdown file. It should answer Tasks 2–8.
- Optional: HTML or PDF export of the notebook

This is helpful if notebook outputs do not render correctly in Canvas.

Do not submit:
- `config.json`
- API keys
- Secret tokens
- Private endpoint credentials
- Suggested Submission Structure

Your written response should use the following headings:
```
Task 1: Notebook Setup and Execution
Task 2: Dataset Roles
Task 3: Baseline Workflow
Task 4: DSPy Optimization Workflow
Task 5: Baseline vs. Optimized Performance
Task 6: Individual Prediction Inspection
Task 7: Notebook Modification
Task 8: Reflection
```

# Grading Rubric
Total: 100 points

## 1. Notebook Execution and Setup — 15 points
Full credit requires:
- Notebook runs successfully from beginning to end.
- Required files are loaded correctly.
- LLM configuration works through config.json.
- Outputs are visible.
- Student does not expose credentials.

Partial credit may be awarded if the notebook runs only partially but the student clearly documents and explains the issue.

## 2. Understanding of Dataset Roles — 10 points
Full credit requires a clear explanation of:
- The purpose of the gold dataset.
- The purpose of the test dataset.
- Why test data should be held out from optimization.

## 3. Baseline Workflow Explanation — 10 points
Full credit requires the student to correctly explain:
- The baseline prompt or model workflow.
- Inputs and outputs.
- Evaluation logic.
- Baseline results.

## 4. DSPy Optimization Explanation — 15 points
Full credit requires the student to explain:
- What DSPy is optimizing.
- How training examples are used.
- How the metric guides optimization.
- How the optimized version differs from the baseline.

## 5. Performance Comparison — 10 points
Full credit requires:
- A comparison of baseline and optimized performance.
- Correct interpretation of whether performance improved.
- A reasonable explanation for the observed result.

## 6. Individual Prediction Analysis — 15 points
Full credit requires:
- At least three inspected examples.
- Expected and actual outputs.
- Correctness judgment.
- Meaningful explanation of errors, ambiguity, or difficulty.

## 7. Notebook Modification — 15 points
Full credit requires:
- A meaningful code or prompt modification.
- Evidence that the modified workflow was run.
- Explanation of what changed and why.
- Analysis of the result.

## 8. Reflection — 10 points
Full credit requires a thoughtful 300–500 word reflection that discusses:
- Benefits of prompt optimization.
- Limitations and risks.
- Production readiness.
- Additional evaluation needed before deployment.

# Academic Integrity and Responsible AI Use
You may use AI tools to help understand errors, explain code, or brainstorm improvements. However, your submitted work must show your own understanding. Do not submit AI-generated explanations that you cannot personally explain.

You are responsible for all code, analysis, and claims in your submission.

# Final Checklist Before Submission
Before submitting, confirm that:
- The notebook runs.
- The notebook outputs are visible.
- `gold_reviews.csv` and `test_reviews.csv` are loaded successfully.
- Your written response answers all required tasks.
- Your notebook includes your modification from Task 7.
- No API key or credential appears anywhere in your submission.
- You did not submit `config.json`.
