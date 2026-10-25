---
description: "Use when analyzing food-demand data, transforming or joining datasets, cleaning data, or preparing client reports. Covers data integrity and evidence-based reporting."
applyTo: "**"
---

# Rule 1: Data Integrity and Code Quality

- Never modify, overwrite, or delete files inside `data/raw/`.
- Before and after every data join or row deletion, print and compare the row count and total `num_orders`, where applicable.
- Validate join keys and investigate unexpected changes in row counts or order totals.
- Do not remove outliers or missing values without documenting the reason and decision in `docs/decisions_cleaning.md`.

# Rule 2: Evidence-Based Reporting

- Every numerical claim in the client report must be traceable to a calculation or result in `notebooks/analysis.ipynb`.
- Never claim that a promotion or discount causes higher demand based on association or correlation alone.
- Report statistical test results, effect sizes, and sample sizes where applicable.
- Include a limitations section in the client report and distinguish observed results from interpretations and recommendations.
- Never invent results, dates, cities, or business facts.
