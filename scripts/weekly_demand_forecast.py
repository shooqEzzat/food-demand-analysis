from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


project_root = Path(__file__).resolve().parents[1]
raw_dir = project_root / "data" / "raw"
reports_dir = project_root / "reports"
figures_dir = reports_dir / "figures"
train_path = raw_dir / "train.csv"
test_path = raw_dir / "test.csv"

if not train_path.is_file() or not test_path.is_file():
    raise FileNotFoundError("Expected data/raw/train.csv and data/raw/test.csv.")

train = pd.read_csv(train_path)
test = pd.read_csv(test_path)
required_train_columns = {
    "week",
    "center_id",
    "meal_id",
    "checkout_price",
    "base_price",
    "emailer_for_promotion",
    "homepage_featured",
    "num_orders",
}
feature_columns = [
    "center_id",
    "meal_id",
    "week",
    "checkout_price",
    "base_price",
    "emailer_for_promotion",
    "homepage_featured",
]
missing_train = required_train_columns - set(train.columns)
missing_test = set(feature_columns) - set(test.columns)
if missing_train:
    raise ValueError(f"train.csv is missing required columns: {sorted(missing_train)}")
if missing_test:
    raise ValueError(f"test.csv is missing required feature columns: {sorted(missing_test)}")

print("train.csv schema:", {column: str(dtype) for column, dtype in train.dtypes.items()})
print("test.csv schema:", {column: str(dtype) for column, dtype in test.dtypes.items()})
print("train.csv missing values:", train.isna().sum().to_dict())
print("test.csv missing values:", test.isna().sum().to_dict())
print(f"Exact duplicate rows: train={int(train.duplicated().sum()):,}; test={int(test.duplicated().sum()):,}")
if train[list(required_train_columns)].isna().any().any():
    raise ValueError("Required training fields contain missing values; no rows were dropped or imputed.")
if test[feature_columns].isna().any().any():
    raise ValueError("Required test features contain missing values; no rows were dropped or imputed.")
if not np.isfinite(train[feature_columns + ["num_orders"]].to_numpy(dtype=float)).all():
    raise ValueError("Training features and target must be finite numeric values.")
if not np.isfinite(test[feature_columns].to_numpy(dtype=float)).all():
    raise ValueError("Test features must be finite numeric values.")

train_row_count = len(train)
total_orders = int(train["num_orders"].sum())
print(f"Training rows before weekly aggregation: {train_row_count:,}")
print(f"Training num_orders before weekly aggregation: {total_orders:,}")

weekly_actual = (
    train.groupby("week", as_index=False)["num_orders"]
    .sum()
    .rename(columns={"num_orders": "actual_orders"})
    .sort_values("week")
    .reset_index(drop=True)
)
if int(weekly_actual["actual_orders"].sum()) != total_orders:
    raise AssertionError("Weekly aggregation does not reconcile to training num_orders.")
print(f"Weekly aggregates: {len(weekly_actual):,} chronologically sorted observed weeks.")
print(f"Training num_orders after weekly aggregation: {int(weekly_actual['actual_orders'].sum()):,}")

if len(weekly_actual) < 11:
    raise ValueError(
        "At least 11 observed weeks are required to hold out the latest 10 and retain earlier training weeks."
    )

holdout_weeks = weekly_actual["week"].tail(10).tolist()
first_holdout_week = holdout_weeks[0]
fit_rows = train.loc[train["week"] < first_holdout_week].copy()
holdout_rows = train.loc[train["week"].isin(holdout_weeks)].copy()
if fit_rows.empty or holdout_rows.empty:
    raise AssertionError("The chronological split must contain training and holdout rows.")
if fit_rows["week"].max() >= min(holdout_weeks):
    raise AssertionError("Temporal leakage detected: a holdout week appears in model training.")

categorical_features = ["center_id", "meal_id"]
numeric_features = [
    "week",
    "checkout_price",
    "base_price",
    "emailer_for_promotion",
    "homepage_featured",
]

linear_preprocessor = ColumnTransformer(
    [
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("numeric", StandardScaler(), numeric_features),
    ]
)
forest_preprocessor = ColumnTransformer(
    [
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("numeric", "passthrough", numeric_features),
    ]
)
models = {
    "LinearRegression": Pipeline(
        [
            ("preprocess", linear_preprocessor),
            ("regressor", LinearRegression()),
        ]
    ),
    "RandomForestRegressor": Pipeline(
        [
            ("preprocess", forest_preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=32,
                    max_depth=10,
                    min_samples_leaf=10,
                    random_state=42,
                    n_jobs=2,
                ),
            ),
        ]
    ),
}

weekly_predictions = weekly_actual.loc[
    weekly_actual["week"].isin(holdout_weeks), ["week", "actual_orders"]
].copy()
score_rows = []
for model_name, model in models.items():
    model.fit(fit_rows[feature_columns], fit_rows["num_orders"])
    row_predictions = np.maximum(model.predict(holdout_rows[feature_columns]), 0)
    predictions_by_week = (
        pd.DataFrame({"week": holdout_rows["week"].to_numpy(), "prediction": row_predictions})
        .groupby("week")["prediction"]
        .sum()
        .reindex(holdout_weeks)
    )
    if predictions_by_week.isna().any():
        raise AssertionError(f"{model_name} did not produce predictions for every holdout week.")
    weekly_predictions[f"{model_name}_predicted_orders"] = predictions_by_week.to_numpy()
    score_rows.append(
        {
            "model": model_name,
            "weekly_total_mae": mean_absolute_error(
                weekly_predictions["actual_orders"], predictions_by_week.to_numpy()
            ),
            "holdout_weeks": len(holdout_weeks),
            "first_holdout_week": holdout_weeks[0],
            "last_holdout_week": holdout_weeks[-1],
            "training_rows": len(fit_rows),
        }
    )

last_training_week = fit_rows["week"].max()
last_training_week_total = int(
    weekly_actual.loc[weekly_actual["week"].eq(last_training_week), "actual_orders"].iloc[0]
)
weekly_predictions["last_training_week_baseline"] = last_training_week_total
baseline_mae = mean_absolute_error(
    weekly_predictions["actual_orders"], weekly_predictions["last_training_week_baseline"]
)
score_rows.append(
    {
        "model": "Last training week baseline",
        "weekly_total_mae": baseline_mae,
        "holdout_weeks": len(holdout_weeks),
        "first_holdout_week": holdout_weeks[0],
        "last_holdout_week": holdout_weeks[-1],
        "training_rows": len(fit_rows),
    }
)
model_scores = pd.DataFrame(score_rows)
ml_scores = model_scores.loc[model_scores["model"].isin(models)]
selected_model_name = ml_scores.sort_values("weekly_total_mae").iloc[0]["model"]
selected_model = models[selected_model_name]

reports_dir.mkdir(parents=True, exist_ok=True)
figures_dir.mkdir(parents=True, exist_ok=True)
model_scores.to_csv(reports_dir / "weekly_demand_forecast_model_comparison.csv", index=False)
weekly_predictions.to_csv(reports_dir / "weekly_demand_holdout_predictions.csv", index=False)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    weekly_predictions["week"],
    weekly_predictions["actual_orders"],
    marker="o",
    linewidth=2.2,
    label="Actual weekly orders",
)
for model_name in models:
    ax.plot(
        weekly_predictions["week"],
        weekly_predictions[f"{model_name}_predicted_orders"],
        marker="o",
        linewidth=1.6,
        label=f"{model_name} forecast",
    )
ax.plot(
    weekly_predictions["week"],
    weekly_predictions["last_training_week_baseline"],
    linestyle="--",
    linewidth=1.6,
    label="Last training week baseline",
)
ax.set(
    title="Actual vs. Predicted Weekly Demand: Final 10 Training Weeks",
    xlabel="Observed week identifier",
    ylabel="Total num_orders",
)
ax.grid(True, alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(figures_dir / "weekly_demand_forecast_holdout.png", dpi=160)
plt.close(fig)

selected_mae = float(
    model_scores.loc[model_scores["model"].eq(selected_model_name), "weekly_total_mae"].iloc[0]
)
print("\nHoldout evaluation (weekly total MAE; lower is better):")
print(model_scores[["model", "weekly_total_mae"]].to_string(index=False, formatters={"weekly_total_mae": "{:,.2f}".format}))
print(
    f"\nSelected machine-learning model: {selected_model_name} "
    f"(holdout weekly MAE {selected_mae:,.2f} orders, weeks {holdout_weeks[0]}–{holdout_weeks[-1]})."
)
print(
    f"Naive baseline weekly MAE: {baseline_mae:,.2f} orders "
    f"(repeats week {int(last_training_week)} total for each holdout week)."
)

selected_model.fit(train[feature_columns], train["num_orders"])
test_predictions = np.maximum(selected_model.predict(test[feature_columns]), 0)
if len(test_predictions) != len(test):
    raise AssertionError("Test prediction count does not match test row count.")

row_output_columns = ["id", "week", "center_id", "meal_id"]
missing_output_columns = set(row_output_columns) - set(test.columns)
if missing_output_columns:
    raise ValueError(f"test.csv is missing output identifier columns: {sorted(missing_output_columns)}")
row_forecasts = test[row_output_columns].copy()
row_forecasts["predicted_num_orders"] = test_predictions
row_forecasts.to_csv(reports_dir / "weekly_demand_test_predictions.csv", index=False)
test_weekly_forecasts = (
    row_forecasts.groupby("week", as_index=False)["predicted_num_orders"]
    .sum()
    .sort_values("week")
    .reset_index(drop=True)
)
test_weekly_forecasts.to_csv(reports_dir / "weekly_demand_test_weekly_totals.csv", index=False)

if "num_orders" in test.columns:
    test_weekly_actual = (
        test.groupby("week", as_index=False)["num_orders"]
        .sum()
        .sort_values("week")
    )
    test_weekly_scored = test_weekly_actual.merge(
        test_weekly_forecasts, on="week", how="inner", validate="one_to_one"
    )
    test_mae = mean_absolute_error(
        test_weekly_scored["num_orders"], test_weekly_scored["predicted_num_orders"]
    )
    print(f"Test-file weekly MAE: {test_mae:,.2f} across {len(test_weekly_scored):,} weeks.")
else:
    print("test.csv has no num_orders column; no test-file MAE was calculated.")

print(
    f"Saved {len(row_forecasts):,} row-level test forecasts "
    f"({len(test_weekly_forecasts):,} weeks) to reports/weekly_demand_test_predictions.csv."
)
print("Saved holdout comparison, holdout weekly predictions, test weekly totals, and holdout chart under reports/.")
