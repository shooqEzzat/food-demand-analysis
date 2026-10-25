# قرارات تجهيز البيانات وجودتها

أُنشئ هذا الجدول من نتائج تشغيل `notebooks/data_preparation.ipynb`. لم تُعدّل ملفات `data/raw/`، ولم تُحذف أو تُصحح سجلات من التدريب. النسب محسوبة من المقام الموضح في فحص كل مشكلة.

| المشكلة | طريقة الكشف | عدد السجلات المتأثرة | النسبة | القرار | السبب | الأثر / القيود |
| --- | --- | --- | --- | --- | --- | --- |
| Missing values: train.csv.id | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: train.csv.week | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: train.csv.center_id | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: train.csv.meal_id | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: train.csv.checkout_price | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: train.csv.base_price | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: train.csv.emailer_for_promotion | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: train.csv.homepage_featured | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: train.csv.num_orders | isna() by column | 0 / 456,548 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Exact duplicate rows: train.csv | DataFrame.duplicated() | 0 / 456,548 | 0.00% | Retain and investigate if present; no automatic removal. | A repeated row may be a valid observation or a data issue; confirm its meaning first. | Duplicates can overweight records and inflate aggregates. |
| Missing values: fulfilment_center_info.csv.center_id | isna() by column | 0 / 77 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: fulfilment_center_info.csv.city_code | isna() by column | 0 / 77 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: fulfilment_center_info.csv.region_code | isna() by column | 0 / 77 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: fulfilment_center_info.csv.center_type | isna() by column | 0 / 77 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: fulfilment_center_info.csv.op_area | isna() by column | 0 / 77 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Exact duplicate rows: fulfilment_center_info.csv | DataFrame.duplicated() | 0 / 77 | 0.00% | Retain and investigate if present; no automatic removal. | A repeated row may be a valid observation or a data issue; confirm its meaning first. | Duplicates can overweight records and inflate aggregates. |
| Missing values: meal_info.csv.meal_id | isna() by column | 0 / 51 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: meal_info.csv.category | isna() by column | 0 / 51 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Missing values: meal_info.csv.cuisine | isna() by column | 0 / 51 | 0.00% | Retain; no imputation or deletion. Flag if present. | Missingness must be understood before any value is inferred. | Could reduce usable observations or leave joined metadata unavailable. |
| Exact duplicate rows: meal_info.csv | DataFrame.duplicated() | 0 / 51 | 0.00% | Retain and investigate if present; no automatic removal. | A repeated row may be a valid observation or a data issue; confirm its meaning first. | Duplicates can overweight records and inflate aggregates. |
| Duplicate training business keys (week, center_id, meal_id) | Rows belonging to repeated business-key groups; groups=0 | 0 / 456,548 | 0.00% | Retain and investigate if present; no automatic removal. | The combination should identify a weekly meal-center observation, but repetition alone does not establish which row is wrong. | Repeated keys may make aggregation ambiguous or double-count demand. |
| checkout_price > base_price | checkout_price greater than base_price | 116,101 / 456,548 | 25.43% | Keep and flag; do not rewrite either price. | The available fields do not establish whether the difference is a promotion, price change, or other business rule. | Price comparisons should not be interpreted as discounts without additional context. |
| num_orders statistical outliers | IQR rule: Q1=54, Q3=324, IQR=270, fences=[-351, 729] | 32,937 / 456,548 | 7.21% | Keep and flag; do not delete or cap. | The IQR rule flags unusual values, not necessarily errors; no independent evidence justifies changing orders. | Extreme demand observations can influence means and models; report robust summaries or sensitivity checks later. |
| Missing meal-week pairs in observed week range | Cartesian meal x contiguous observed week range 1-145; missing pairs do not prove offer availability | 222 / 7,395 | 3.00% | Retain; flag as unobserved, not as zero demand. | The files do not show whether a meal was offered in every week. | Treating absent rows as zero would bias demand summaries if the meal was not offered. |
| Non-numeric values in numeric training fields | to_numeric(errors=coerce), excluding existing nulls | 0 / 456,548 | 0.00% | Retain and flag if present; do not coerce silently. | Automatic conversion could obscure malformed source values. | Affected fields may not support numeric comparison or aggregation. |
| Non-finite values in numeric training fields | isfinite across numeric training fields | 0 / 456,548 | 0.00% | Retain and investigate if present. | Infinite values are not valid measurements. | Can distort summaries and downstream calculations. |
| Non-positive training id | Domain validation | 0 / 456,548 | 0.00% | Retain and flag if present; no inferred correction. | A record identifier should be positive. | Invalid values could affect identifiers, filters, or demand calculations. |
| Non-positive week | Domain validation | 0 / 456,548 | 0.00% | Retain and flag if present; no inferred correction. | Observed week identifiers should be positive. | Invalid values could affect identifiers, filters, or demand calculations. |
| Negative num_orders | Domain validation | 0 / 456,548 | 0.00% | Retain and flag if present; no inferred correction. | Negative order counts are not valid demand counts. | Invalid values could affect identifiers, filters, or demand calculations. |
| Non-integer num_orders | Domain validation | 0 / 456,548 | 0.00% | Retain and flag if present; no inferred correction. | Order counts are expected to be integer-valued. | Invalid values could affect identifiers, filters, or demand calculations. |
| Non-positive checkout_price | Domain validation | 0 / 456,548 | 0.00% | Retain and flag if present; no inferred correction. | Prices are expected to be positive. | Invalid values could affect identifiers, filters, or demand calculations. |
| Non-positive base_price | Domain validation | 0 / 456,548 | 0.00% | Retain and flag if present; no inferred correction. | Prices are expected to be positive. | Invalid values could affect identifiers, filters, or demand calculations. |
| Invalid emailer_for_promotion flag | Domain validation | 0 / 456,548 | 0.00% | Retain and flag if present; no inferred correction. | Promotion indicator is expected to be binary. | Invalid values could affect identifiers, filters, or demand calculations. |
| Invalid homepage_featured flag | Domain validation | 0 / 456,548 | 0.00% | Retain and flag if present; no inferred correction. | Featured indicator is expected to be binary. | Invalid values could affect identifiers, filters, or demand calculations. |
| Training center keys absent from center dimension | train.center_id not in center_info.center_id | 0 / 456,548 | 0.00% | Preserve rows in left join; flag missing center metadata. | Only keys present in the dimension can be enriched. | Missing attributes limit center-level analysis. |
| Training meal keys absent from meal dimension | train.meal_id not in meal_info.meal_id | 0 / 456,548 | 0.00% | Preserve rows in left join; flag missing meal metadata. | Only keys present in the dimension can be enriched. | Missing attributes limit meal-category analysis. |
| Center merge validation | left many-to-one on center_id; matched rows=456548 | 0 / 456,548 | 0.00% | Keep left-joined observations; inspect unmatched keys. | Center key unique=True; source unmatched keys=0, rows=0. | Rows 456,548->456,548; num_orders 119,557,485->119,557,485; multiplication=0; dropped=0. |
| Meal merge validation | left many-to-one on meal_id; matched rows=456548 | 0 / 456,548 | 0.00% | Keep left-joined observations; inspect unmatched keys. | Meal key unique=True; source unmatched keys=0, rows=0. | Rows 456,548->456,548; num_orders 119,557,485->119,557,485; multiplication=0; dropped=0. |

## سلامة الدمج

- الصفوف: 456,548 قبل الدمج و456,548 بعده.
- مجموع `num_orders`: 119,557,485 قبل الدمج و119,557,485 بعده.
- ملف البيانات المجهزة: `data/processed/prepared_train.csv` (456,548 صفًا).
- بقيت ملاحظات الجودة غير المحسومة معلّمة في الدفتر والجدول؛ غياب صف وجبة-أسبوع لا يثبت أن الوجبة كانت معروضة أو أن طلبها صفر.

## قرارات تجهيز بيانات التنبؤ الأسبوعي

- حُسب الطلب الأسبوعي بجمع `num_orders` لكل صفوف الوجبات ومراكز التوزيع داخل `week`. هذا هو إجمالي الطلب المرصود، وليس متوسط الطلب لكل مركز أو وجبة.
- قيم `week` هي معرّفات زمنية مرتبة وليست تواريخ تقويمية؛ لا يمكن استنتاج تواريخ فعلية أو حدود أسبوع/منطقة زمنية من هذه الملفات.
- لم تُحذف سجلات أو تُملأ قيم مفقودة للتنبؤ. فُحصت الأعمدة والأنواع والقيم المفقودة والتكرارات في `train.csv` و`test.csv` قبل التحليل. لا يحتوي ملف الاختبار على `num_orders`، لذلك لا يُحسب له MAE.
- قُيّمت النماذج على الأسابيع العشرة الأخيرة الموجودة في التدريب، بعد التدريب على الأسابيع الأسبق فقط. حُسب MAE على مجموع التوقعات الصفية في كل أسبوع مقابل إجمالي `num_orders` الفعلي للأسبوع.
- استُخدمت `center_id` و`meal_id` كمتغيرات فئوية مشفّرة، مع الأسبوع والسعرين ومؤشري الترويج والظهور في الصفحة الرئيسية كميزات. استُبعد `id` لأنه معرّف سجل وليس إشارة طلب معروفة.
- بعد اختيار النموذج بناءً على MAE في فترة الحجز، أُعيد تدريبه على جميع سجلات التدريب وأُنتج توقع لكل صف في ملف الاختبار. قد تكون قيم الأسعار والترويج معروفة في ملف الاختبار، لكن توقع الطلب الناتج لا يثبت أن الطلب سيحدث.
- لا تتضمن الميزات سجل الطلب الفعلي السابق للوجبة/المركز ولا تواريخ أو متغيرات خارجية. كما أن تقييم مجموع الطلب الأسبوعي عبر 10 أسابيع لا يثبت دقة توقع كل صف أو صلاحية النموذج خارج نطاق البيانات المرصودة.

## قرارات إعداد التنبؤ

- تُستخدم سجلات التدريب الأصلية دون حذف أو تغيير. فُحصت المخططات والقيم المفقودة والتكرارات قبل النمذجة؛ وأُدرجت خصائص الوجبة والمركز بدمجين من نوع many-to-one مع التحقق من تفرد المفاتيح وتطابقها، ومقارنة عدد الصفوف ومجموع `num_orders` قبل الدمج وبعده.
- هدف التنبؤ هو `num_orders` لكل صف في `test.csv`؛ لا يحتوي الاختبار على العمود المستهدف، وتُحفظ معرفات الصفوف وترتيبها كما وردت.
- لا تُملأ أسابيع أو توليفات وجبة-مركز غائبة بصفر، ولا تُستخدم ميزات الطلب التاريخي أو `id`. تستخدم النماذج الأسبوع والسعر والترويج والخصائص الوصفية المتاحة، مع ترميز one-hot للفئات.
- يُدرّب التحقق على الأسابيع السابقة ويُقيّم على آخر عشرة أسابيع تدريبية. ويُعاد تدريب النموذج الفائز وفق MAE على كامل بيانات التدريب قبل التنبؤ.
- أسابيع الاختبار أحدث من نطاق التدريب؛ لذلك فالنتائج استقراء زمني، ولا يمكن قياس MAE للاختبار لغياب قيم `num_orders` الفعلية. توثّق [ملخصات التنبؤ](../reports/forecasting_summary.md) الأداء والافتراضات والقيود الفعلية.
