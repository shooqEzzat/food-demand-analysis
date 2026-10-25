"""Train and evaluate row-level meal-center demand forecasts."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def find_project_root() -> Path:
    candidates = [Path.cwd(), *Path.cwd().parents]
    for candidate in candidates:
        if (candidate / "data" / "raw" / "train.csv").is_file():
            return candidate
    raise FileNotFoundError("Could not locate data/raw/train.csv from the current directory.")


def inspect_source(name: str, frame: pd.DataFrame) -> None:
    print(f"\n{name}: rows={len(frame):,}, columns={len(frame.columns)}")
    print("Columns:", list(frame.columns))
    print("Data types:", frame.dtypes.astype(str).to_dict())
    print("Missing values:", frame.isna().sum().to_dict())
    print("Exact duplicate rows:", int(frame.duplicated().sum()))
    if frame.isna().any().any():
        raise ValueError(f"{name} contains missing values; resolve them before modeling.")
    if frame.duplicated().any():
        raise ValueError(f"{name} contains duplicate rows; investigate before modeling.")


def enrich_rows(
    frame: pd.DataFrame,
    meal_info: pd.DataFrame,
    center_info: pd.DataFrame,
    name: str,
    has_target: bool,
) -> pd.DataFrame:
    """Enrich rows using dimensions with unique keys, checking each merge."""
    result = frame.copy()
    result["_row_order"] = np.arange(len(result))

    for dimension, key, label in (
        (center_info, "center_id", "fulfilment-center metadata"),
        (meal_info, "meal_id", "meal metadata"),
    ):
        if not dimension[key].is_unique:
            raise ValueError(f"{label} key {key} is not unique.")
        unmatched = set(result[key].unique()) - set(dimension[key].unique())
        if unmatched:
            raise ValueError(f"{name} has {len(unmatched)} unmatched {key} values.")

        rows_before = len(result)
        orders_before = int(result["num_orders"].sum()) if has_target else None
        result = result.merge(
            dimension,
            on=key,
            how="left",
            validate="many_to_one",
            sort=False,
        )
        result = result.sort_values("_row_order", kind="stable").reset_index(drop=True)
        rows_after = len(result)
        orders_after = int(result["num_orders"].sum()) if has_target else None
        print(
            f"{name} + {label}: rows {rows_before:,}->{rows_after:,}; "
            f"num_orders {orders_before if has_target else 'n/a'}"
            f"->{orders_after if has_target else 'n/a'}"
        )
        if rows_after != rows_before or orders_after != orders_before:
            raise AssertionError(f"{label} merge changed {name} row count or target sum.")
        if result[list(dimension.columns.drop(key))].isna().any().any():
            raise ValueError(f"{label} merge produced missing metadata.")

    return result


def build_pipeline(
    categorical_features: list[str],
    numeric_features: list[str],
    estimator: object,
) -> Pipeline:
    preprocessing = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            ("numeric", "passthrough", numeric_features),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("regressor", estimator),
        ]
    )


def write_summary(
    output_path: Path,
    metrics: pd.DataFrame,
    selected_name: str,
    validation_first_week: int,
    validation_last_week: int,
    validation_rows: int,
    test_rows: int,
    train_first_week: int,
    train_last_week: int,
    test_first_week: int,
    test_last_week: int,
) -> None:
    linear_mae = metrics.loc[metrics["model"] == "LinearRegression", "mae"].iloc[0]
    forest_mae = metrics.loc[metrics["model"] == "RandomForestRegressor", "mae"].iloc[0]
    baseline_mae = metrics.loc[
        metrics["model"] == "Previous-week meal-center baseline", "mae"
    ].iloc[0]
    comparison_rows = int(metrics["n_validation_rows"].iloc[0])
    report = f"""# Meal-center demand forecasts

## Validation results

The chronological holdout uses weeks {validation_first_week}–{validation_last_week} ({validation_rows:,} meal-center-week rows). Models were fitted only on earlier weeks. All methods are compared on the same {comparison_rows:,} rows for which the same meal-center combination has an observed order count in the previous week. The last-week baseline uses the actual previous week's orders; for validation weeks after the first, this is a rolling one-week-ahead reference. MAE is the average absolute difference between a prediction and actual demand, in orders per evaluated row.

| Model | Validation MAE (orders per row) |
| --- | ---: |
| Previous-week meal-center baseline | {baseline_mae:,.2f} |
| LinearRegression | {linear_mae:,.2f} |
| RandomForestRegressor | {forest_mae:,.2f} |

Selected model: **{selected_name}**, chosen as the lower-MAE result between LinearRegression and RandomForestRegressor. The previous-week baseline is a reference, not a candidate for selecting the final estimator.

The validation chart compares actual and predicted orders for each held-out meal-center-week row.

## Forecast output

`meal_center_demand_predictions.csv` contains {test_rows:,} row-level forecasts with the original `id`, `week`, `center_id`, and `meal_id` identifiers, plus `predicted_num_orders`. Predictions are non-negative and retain the input row order. Test weeks are {test_first_week}–{test_last_week}, beyond the training range of {train_first_week}–{train_last_week}.

There are no actual `num_orders` values in `test.csv`, so test MAE cannot be calculated.

## How to use the forecasts

- **Portions:** use each meal-center-week forecast as an estimate of portions to prepare, then apply the client's waste, safety-stock, and rounding policies.
- **Purchasing and inventory:** combine forecast portions with ingredient-per-meal recipes, existing stock, supplier lead times, and spoilage constraints to plan purchases. This dataset contains no recipe or ingredient-consumption rates, so forecasts cannot be converted to ingredient quantities by themselves.
- **Kitchen capacity and staffing:** compare center-level weekly meal forecasts with available equipment, prep stations, shift hours, and staffing capacity; schedule resources around the expected workload.
- **Monitoring:** review meal-center combinations with large forecasts or material changes against recent operational context, and investigate shortages, waste, and forecast errors as actual orders become available.

## Assumptions and limitations

- One row represents the target for one `id` and its `week`, `center_id`, and `meal_id`; metadata dimensions have unique keys and are joined many-to-one without changing row counts.
- Features are restricted to values present in both train and test: week, price and promotion fields, meal and center identifiers, and meal/center metadata. The row `id` is excluded. Categorical values are one-hot encoded. No lag or rolling-demand features are used, so no future target values can enter a feature; absent meal-week rows are not assumed to mean zero demand.
- Price and promotion fields are useful only if their test values are known at the time a forecast is made. If operational plans change, forecasts should be refreshed using the updated inputs.
- The validation is a single chronological holdout, not a guarantee of future accuracy. Test weeks {test_first_week}–{test_last_week} are outside the training range, so the output requires temporal extrapolation. Week values do not identify calendar dates.
- Forecasts support inventory and staffing decisions; they do not replace operational judgment. Monitor realized demand and update plans as actual results become available.
"""
    output_path.write_text(report, encoding="utf-8")


def main() -> None:
    root = find_project_root()
    raw_dir = root / "data" / "raw"
    reports_dir = root / "reports"
    figure_dir = reports_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "train.csv": raw_dir / "train.csv",
        "test.csv": raw_dir / "test.csv",
        "meal_info.csv": raw_dir / "meal_info.csv",
        "fulfilment_center_info.csv": raw_dir / "fulfilment_center_info.csv",
    }
    source = {name: pd.read_csv(path) for name, path in paths.items()}
    for name, frame in source.items():
        inspect_source(name, frame)

    train = source["train.csv"]
    test = source["test.csv"]
    meal_info = source["meal_info.csv"]
    center_info = source["fulfilment_center_info.csv"]

    target = "num_orders"
    test_identifiers = ["id", "week", "center_id", "meal_id"]
    if target not in train.columns or target in test.columns:
        raise ValueError("Expected num_orders in train.csv and absent from test.csv.")
    for column in test.columns:
        if column not in train.columns:
            raise ValueError(f"Test feature {column} is not present in training data.")
    if not train["id"].is_unique or not test["id"].is_unique:
        raise ValueError("Row identifiers must be unique in both train and test.")
    for name, frame in (("train", train), ("test", test)):
        if frame.duplicated(["week", "center_id", "meal_id"]).any():
            raise ValueError(f"{name} has duplicate week-center-meal keys.")
    print(f"\nTrain target total before metadata joins: {int(train[target].sum()):,}")
    print(f"Test has actual target: {target in test.columns}")

    train_enriched = enrich_rows(train, meal_info, center_info, "train", has_target=True)
    test_enriched = enrich_rows(test, meal_info, center_info, "test", has_target=False)
    if len(train_enriched) != len(train) or len(test_enriched) != len(test):
        raise AssertionError("Metadata enrichment changed the number of source rows.")

    train_enriched = train_enriched.sort_values("week", kind="stable").reset_index(drop=True)
    train_weeks = sorted(train_enriched["week"].unique())
    test_weeks = sorted(test_enriched["week"].unique())
    train_min_week = int(train_enriched["week"].min())
    train_max_week = int(train_enriched["week"].max())
    test_min_week = int(test_enriched["week"].min())
    test_max_week = int(test_enriched["week"].max())
    print(
        f"Training weeks: {train_min_week}-{train_max_week} "
        f"({len(train_weeks)} unique); test weeks: {test_min_week}-{test_max_week} "
        f"({len(test_weeks)} unique)."
    )
    if test_min_week <= train_max_week:
        raise ValueError("Test weeks are not strictly later than all training weeks.")

    validation_week_count = min(10, len(train_weeks) - 1)
    validation_weeks = train_weeks[-validation_week_count:]
    validation_start = int(validation_weeks[0])
    fit_mask = train_enriched["week"] < validation_start
    validation_mask = train_enriched["week"].isin(validation_weeks)
    fit_rows = train_enriched.loc[fit_mask].copy()
    validation_rows = train_enriched.loc[validation_mask].copy()
    if fit_rows.empty or validation_rows.empty:
        raise ValueError("Chronological validation split produced an empty partition.")
    if fit_rows["week"].max() >= validation_rows["week"].min():
        raise AssertionError("Validation split is not chronological.")
    print(
        f"Validation split: fit weeks {fit_rows.week.min()}-{fit_rows.week.max()} "
        f"({len(fit_rows):,} rows); validation weeks "
        f"{validation_rows.week.min()}-{validation_rows.week.max()} "
        f"({len(validation_rows):,} rows)."
    )

    categorical_features = [
        "center_id",
        "meal_id",
        "category",
        "cuisine",
        "city_code",
        "region_code",
        "center_type",
    ]
    numeric_features = [
        "week",
        "checkout_price",
        "base_price",
        "emailer_for_promotion",
        "homepage_featured",
        "op_area",
    ]
    feature_columns = categorical_features + numeric_features
    if target in feature_columns or "id" in feature_columns:
        raise AssertionError("Target leakage or row identifier found in feature list.")
    if not set(feature_columns).issubset(train_enriched.columns):
        raise ValueError("One or more requested model features are missing.")
    x_fit = fit_rows[feature_columns]
    y_fit = fit_rows[target]
    x_validation = validation_rows[feature_columns]
    y_validation = validation_rows[target]

    previous_week_orders = train_enriched[
        ["week", "center_id", "meal_id", target]
    ].copy()
    previous_week_orders["week"] += 1
    previous_week_orders = previous_week_orders.rename(
        columns={target: "previous_week_orders"}
    )
    validation_with_lag = validation_rows.merge(
        previous_week_orders,
        on=["week", "center_id", "meal_id"],
        how="left",
        validate="one_to_one",
        sort=False,
    )
    comparable_mask = validation_with_lag["previous_week_orders"].notna().to_numpy()
    comparable_rows = validation_rows.loc[comparable_mask]
    comparable_targets = y_validation.loc[comparable_rows.index]
    previous_week_predictions = validation_with_lag.loc[
        comparable_mask, "previous_week_orders"
    ].to_numpy()
    if comparable_rows.empty:
        raise ValueError("No validation rows have an observed previous-week demand.")
    if len(comparable_rows) != len(previous_week_predictions):
        raise AssertionError("Previous-week baseline did not align with validation rows.")
    results = [{
        "model": "Previous-week meal-center baseline",
        "mae": mean_absolute_error(comparable_targets, previous_week_predictions),
        "n_validation_rows": len(comparable_rows),
    }]

    models = {
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=40,
            max_depth=20,
            min_samples_leaf=10,
            max_features="sqrt",
            max_samples=0.5,
            random_state=42,
            n_jobs=-1,
        ),
    }
    validation_predictions: dict[str, np.ndarray] = {}
    for name, estimator in models.items():
        pipeline = build_pipeline(categorical_features, numeric_features, estimator)
        pipeline.fit(x_fit, y_fit)
        predictions = np.maximum(pipeline.predict(x_validation), 0)
        validation_predictions[name] = predictions
        results.append(
            {
                "model": name,
                "mae": mean_absolute_error(
                    comparable_targets, predictions[comparable_mask]
                ),
                "n_validation_rows": len(comparable_rows),
            }
        )
        print(f"{name} validation MAE: {results[-1]['mae']:,.2f}")

    metrics = pd.DataFrame(results)
    metrics["note"] = [
        "Uses actual previous-week demand for the same meal and center."
        if name == "Previous-week meal-center baseline"
        else "Chronological holdout; model fitted on weeks before validation."
        for name in metrics["model"]
    ]
    print("\nValidation MAE comparison (orders per row):")
    print(
        metrics.to_string(
            index=False,
            formatters={"mae": "{:,.2f}".format},
        )
    )
    selected_name = min(
        (name for name in models),
        key=lambda name: metrics.loc[metrics["model"] == name, "mae"].iloc[0],
    )
    print(f"Selected model by validation MAE: {selected_name}")

    actual_values = comparable_targets.to_numpy()
    predicted_values = validation_predictions[selected_name][comparable_mask]
    axis_max = float(max(actual_values.max(), predicted_values.max()))
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(actual_values, predicted_values, s=8, alpha=0.2)
    ax.plot([0, axis_max], [0, axis_max], color="black", linestyle="--", label="Perfect prediction")
    ax.set(
        title=f"Validation actual vs predicted per row\n({selected_name})",
        xlabel="Actual orders per row",
        ylabel="Predicted orders per row",
        xlim=(0, axis_max),
        ylim=(0, axis_max),
    )
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    chart_path = figure_dir / "forecast_validation_actual_vs_predicted.png"
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)
    print(f"Saved validation chart: {chart_path}")

    comparison_path = reports_dir / "meal_center_validation_model_comparison.csv"
    metrics.to_csv(comparison_path, index=False)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    chart_metrics = metrics.set_index("model").loc[
        ["Previous-week meal-center baseline", "LinearRegression", "RandomForestRegressor"]
    ]
    bars = ax.bar(
        ["Previous-week\nbaseline", "Linear\nRegression", "Random\nForest"],
        chart_metrics["mae"],
        color=["#7f8c8d", "#4c78a8", "#2a9d8f"],
    )
    ax.bar_label(bars, fmt="%.1f", padding=3)
    ax.set(
        title=f"Row-level validation MAE (n={len(comparable_rows):,})",
        ylabel="MAE (orders per meal-center-week)",
    )
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    comparison_chart_path = figure_dir / "meal_center_validation_mae.png"
    fig.savefig(comparison_chart_path, dpi=180)
    plt.close(fig)
    print(f"Saved validation comparison: {comparison_path}")
    print(f"Saved validation MAE chart: {comparison_chart_path}")

    final_model = build_pipeline(
        categorical_features,
        numeric_features,
        models[selected_name],
    )
    final_model.fit(train_enriched[feature_columns], train_enriched[target])
    test_predictions = np.maximum(
        final_model.predict(test_enriched[feature_columns]),
        0,
    )
    predictions = test_enriched[test_identifiers].copy()
    predictions["predicted_num_orders"] = test_predictions

    expected_identifiers = test[test_identifiers].reset_index(drop=True)
    actual_identifiers = predictions[test_identifiers].reset_index(drop=True)
    if not actual_identifiers.equals(expected_identifiers):
        raise AssertionError("Prediction identifiers or row order do not match test.csv.")
    if len(predictions) != len(test) or predictions["predicted_num_orders"].isna().any():
        raise AssertionError("Prediction output has an unexpected row count or missing values.")
    if (predictions["predicted_num_orders"] < 0).any():
        raise AssertionError("Prediction output contains negative demand.")

    prediction_path = reports_dir / "meal_center_demand_predictions.csv"
    predictions.to_csv(prediction_path, index=False)
    print(
        f"Saved {len(predictions):,} predictions to {prediction_path}; "
        "identifier order and non-missing values verified."
    )
    if target not in test.columns:
        print("Test MAE not calculated: test.csv has no actual num_orders values.")

    summary_path = reports_dir / "forecasting_summary.md"
    write_summary(
        summary_path,
        metrics,
        selected_name,
        int(validation_rows["week"].min()),
        int(validation_rows["week"].max()),
        len(validation_rows),
        len(test),
        train_min_week,
        train_max_week,
        test_min_week,
        test_max_week,
    )
    print(f"Saved forecasting summary: {summary_path}")


if __name__ == "__main__":
    main()
