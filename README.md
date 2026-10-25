# Food Demand Analysis

## Project overview

This project prepares and explores meal-order data to describe demand patterns across observed weeks, meals, and fulfilment centers. It also summarizes price and promotion associations and presents findings in charts and a concise client report. The analyses are descriptive and do not establish causal effects.

## Problem statement

The project addresses these questions using the available order records:

- How does total meal demand vary by observed week?
- Which meal categories and individual meals account for most recorded orders?
- How do recorded orders vary across fulfilment-center types and individual centers?
- How are order counts associated with email promotion, homepage featuring, and signed price reductions?
- Which meals have the highest total demand or the greatest relative week-to-week variability?

The files do not identify actual calendar dates or establish geographic representativeness, so the analysis does not infer either. The project has two distinct forecasts: a weekly-total workflow and a row-level meal-center-week workflow. The latter predicts `num_orders` for each `test.csv` row, compares LinearRegression and RandomForestRegressor on a chronological holdout, and selects by row-level MAE.

## Key findings

- Five categories account for **81.40%** of recorded orders; the top 22 meals account for **81.18%**.
- The prepared training data contains **119,557,485** orders across **145** observed weeks. Week 48 has the highest observed weekly total: **1,303,457**.
- Email-promotion and homepage-featured observations have higher mean order counts in the within-meal-center descriptive comparisons, but repeated observations and confounding prevent causal conclusions.

## Tools and methods

The project uses Python, Pandas, NumPy, Matplotlib, SciPy, scikit-learn, and Jupyter notebooks. Preparation validates source schemas, missing values, duplicates, join keys, and merge integrity. Exploratory work aggregates weekly, category, center, and meal demand; calculates estimated revenue and signed discount rates; uses Mann–Whitney U and Spearman rank correlation for exploratory association tests; and visualizes results with Matplotlib. Forecast models compare weekly MAE with a last-observed-week baseline. Meal demand volatility is summarized by the coefficient of variation across observed meal-weeks without imputing missing combinations as zero.

## Project structure

```text
.
├── data/
│   ├── raw/                 # Original CSV inputs; excluded from Git
│   └── processed/           # Prepared training data
├── docs/                    # Cleaning decisions and data-quality log
├── notebooks/               # Data preparation, analysis, and visualization
├── reports/
│   ├── figures/             # PNG charts
│   ├── report_client/       # Reserved directory (currently empty)
│   ├── report_client.md     # Client-facing report
│   └── *.csv                # Reusable analysis summaries
├── .github/
│   ├── instructions/        # Workspace Copilot instructions
│   └── skills/              # Project analysis skills
├── AGENTS.md                # Project-wide analysis rules
├── README.md
└── requirements.txt         # Python dependencies
```

Place the original `train.csv`, `test.csv`, `meal_info.csv`, and `fulfilment_center_info.csv` files in `data/raw/`. The test set has no `num_orders`; it is used only to generate forecasts, not to calculate actual demand or test-set accuracy. The row-level meal-center-week prediction output is `reports/meal_center_demand_predictions.csv`.

## How to reproduce the analysis

From the project root in PowerShell, create and activate a virtual environment, then install the declared dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the notebooks in order, using the same environment as their Jupyter kernel:

```powershell
$env:PYTHONUTF8 = '1'
python -m nbconvert --to notebook --execute --inplace notebooks/data_preparation.ipynb
python -m nbconvert --to notebook --execute --inplace notebooks/analysis.ipynb
python -m nbconvert --to notebook --execute --inplace notebooks/visualizations.ipynb
python -m nbconvert --to notebook --execute --inplace notebooks/forecasting.ipynb
```

The UTF-8 mode setting preserves non-ASCII notebook text and generated documentation when executing from Windows PowerShell.

The preparation notebook reads the raw files without changing them and writes `data/processed/prepared_train.csv` and `docs/decisions_cleaning.md`. The analysis and visualization notebooks then use that prepared dataset and the resulting summaries.
The forecasting notebook separately validates and enriches the raw training and test rows, performs a chronological model comparison, and writes its forecasts and validation chart. It does not overwrite the descriptive analysis outputs or the separate weekly-total forecast.

## Outputs

- Client-facing findings: [`reports/report_client.md`](reports/report_client.md)
- Cleaning decisions and data-quality results: [`docs/decisions_cleaning.md`](docs/decisions_cleaning.md)
- Reusable aggregate CSV files: `reports/*.csv`
- PNG visualizations: `reports/figures/*.png`
- Prepared training dataset: `data/processed/prepared_train.csv`
- Meal-center-week demand forecasts: `reports/meal_center_demand_predictions.csv`
- Forecast comparison, assumptions, and client guidance: `reports/forecasting_summary.md`
- Validation actual-versus-predicted chart: `reports/figures/forecast_validation_actual_vs_predicted.png`

## Use of AI

AI assistance was used in drafting and reviewing notebook code, debugging execution issues, and preparing project documentation and findings. The analysis and visualization notebooks were executed, and generated summary tables and chart files were checked against their inputs. These checks support reproducibility but are not a claim that AI independently verified every result or that every business interpretation was manually audited.

## Limitations

The data contains week numbers, not actual calendar dates. Missing meal-week records do not show whether a meal was offered, so they are not treated as zero orders. Revenue calculated from recorded checkout prices and order counts is an estimate, not audited revenue. Center comparisons are not adjusted for operating area or meal mix. Promotion tests pool repeated weekly observations, which violates the independence assumption of an ordinary Mann–Whitney U test; their p-values are exploratory. The observed discount-demand correlation may also reflect promotions, homepage placement, or time-related factors.

## Responsible interpretation

Observed differences, statistical significance, and correlations do not establish causation. Promotion and discount findings should be treated as associations, not as proof that a price or promotion change caused demand to change. Further controlled evaluation would be needed to estimate causal effects.
