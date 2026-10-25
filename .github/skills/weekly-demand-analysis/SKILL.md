---
name: weekly-demand-analysis
description: "Use when analyzing weekly food demand, week-over-week fluctuations, or ranking meals by order volume. Covers data validation, aggregation, interpretation, and evidence-based reporting."
---

# Weekly Demand Analysis

Analyze weekly food demand and rank meals by observed order volume without assuming a dataset schema or inventing results.

## Use when

- Summarizing weekly demand or changes between weeks.
- Identifying demand fluctuations or ranking meals by orders.
- Preparing verified weekly findings for a client report.

## Procedure

1. Confirm the available input files and inspect column names, data types, missing values, and duplicates before analysis. Do not assume date, meal, or order columns exist; identify and validate the appropriate fields first.
2. Keep source files in `data/raw/` unchanged. Perform analysis on in-memory data or derived files outside that directory.
3. Parse the validated date field, report invalid or missing dates, and define the week boundary and time zone if relevant. Do not silently discard records that cannot be assigned to a week; document their handling.
4. Before and after any join or row deletion, print and compare row counts and total `num_orders` when applicable. Validate join keys and investigate unexpected changes. Document cleaning decisions and reasons in `docs/decisions_cleaning.md`.
5. Aggregate `num_orders` by the validated week and meal identifier. State whether the weekly measure is a sum or another explicitly justified statistic. Sort meal rankings by the chosen measure and define how ties are handled.
6. Quantify week-over-week changes only for comparable weeks and state the formula and comparison period. Distinguish absolute changes from percentage changes; do not calculate percentages when the baseline is zero.
7. Check for incomplete weeks, missing observations, duplicate records, and other limitations that could affect comparisons. Describe observed patterns without presenting them as causes.
8. Save reproducible calculations and charts in `notebooks/analysis.ipynb` and appropriate figures in `reports/figures/`. Ensure every reported number can be traced to notebook output. Do not invent values, dates, meals, or business context.

## Expected output

- A weekly demand summary and meal ranking, with the aggregation and ranking criteria stated.
- A description of material fluctuations, supported by calculated values.
- Relevant limitations and a clear distinction between observations, interpretations, and recommendations.
