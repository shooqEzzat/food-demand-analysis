# Meal-center demand forecasts

## Validation results

The chronological holdout uses weeks 136–145 (32,821 meal-center-week rows). Models were fitted only on earlier weeks. All methods are compared on the same 31,245 rows for which the same meal-center combination has an observed order count in the previous week. The last-week baseline uses the actual previous week's orders; for validation weeks after the first, this is a rolling one-week-ahead reference. MAE is the average absolute difference between a prediction and actual demand, in orders per evaluated row.

| Model | Validation MAE (orders per row) |
| --- | ---: |
| Previous-week meal-center baseline | 81.78 |
| LinearRegression | 126.57 |
| RandomForestRegressor | 89.51 |

Selected model: **RandomForestRegressor**, chosen as the lower-MAE result between LinearRegression and RandomForestRegressor. The previous-week baseline is a reference, not a candidate for selecting the final estimator.

The validation chart compares actual and predicted orders for each held-out meal-center-week row.

## Forecast output

`meal_center_demand_predictions.csv` contains 32,573 row-level forecasts with the original `id`, `week`, `center_id`, and `meal_id` identifiers, plus `predicted_num_orders`. Predictions are non-negative and retain the input row order. Test weeks are 146–155, beyond the training range of 1–145.

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
- The validation is a single chronological holdout, not a guarantee of future accuracy. Test weeks 146–155 are outside the training range, so the output requires temporal extrapolation. Week values do not identify calendar dates.
- Forecasts support inventory and staffing decisions; they do not replace operational judgment. Monitor realized demand and update plans as actual results become available.
