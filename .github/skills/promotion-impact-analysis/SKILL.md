---
name: promotion-impact-analysis
description: "Use when comparing demand for the same meals at the same fulfillment centers with and without promotion. Covers matched grouping, Mann–Whitney U suitability, statistical reporting, and causal limitations."
---

# Promotion Impact Analysis

Compare observed order demand for the same meals at the same fulfillment centers under promoted and non-promoted conditions. Treat results as associations unless the study design supports causal inference.

## Use when

- Comparing promoted versus non-promoted observations for the same meal and fulfillment center.
- Evaluating whether Mann–Whitney U is appropriate for a demand comparison.
- Preparing a statistically grounded, non-causal client summary.

## Procedure

1. Inspect available files, column names, data types, missing values, and duplicates before analysis. Identify and validate the meal identifier, fulfillment-center identifier, promotion indicator, and demand outcome from the actual schema; do not assume column names or meanings.
2. Keep source files in `data/raw/` unchanged. Do not infer that a promotion caused a demand difference from an observational comparison.
3. Validate promotion coding, outcome units, and join keys. Before and after every applicable join or row deletion, print and compare row counts and total `num_orders`; investigate unexpected changes. Document cleaning decisions and reasons in `docs/decisions_cleaning.md`.
4. Restrict comparisons to meal-and-center combinations with observations in both promoted and non-promoted conditions. Report how many combinations and observations are included and excluded, and why. Do not combine different meals or centers as if they were the same comparison unit.
5. Define the observation unit and assess independence. If multiple rows are repeated measurements of the same meal-center unit, or otherwise dependent, do not apply a standard independent-samples Mann–Whitney U test as though all rows were independent. Use a suitable paired, clustered, or otherwise justified method, or explain why inference is not appropriate.
6. Consider Mann–Whitney U only when comparing two independent groups with an ordinal or continuous outcome and its assumptions are reasonable. Examine group distributions and sample sizes. The test evaluates distributional differences; do not describe it as a test of medians unless distribution shapes support that interpretation.
7. If the test is appropriate, report the test variant and alternative hypothesis, sample sizes, U statistic, p-value, effect size with its definition, and uncertainty interval when available. State any multiple-comparison handling if testing many meal-center combinations. Do not invent thresholds or results.
8. Present the direction and magnitude of observed differences alongside the statistical results. A p-value alone does not establish practical importance or causality. Discuss confounding, selection, time effects, sample size, and other relevant limitations.
9. Save reproducible calculations in `notebooks/analysis.ipynb` and appropriate figures in `reports/figures/`. Trace every client-report number to notebook output and distinguish observations, interpretations, and recommendations.

## Expected output

- A clear comparison of promoted and non-promoted demand within eligible meal-center combinations.
- A justified choice of statistical method, or an explanation of why Mann–Whitney U is unsuitable.
- Statistical results, effect size, sample sizes, and limitations when inference is appropriate.
- Explicit caution that an observed association does not by itself show a promotional causal effect.
