# Alerts / Reminders Runner

This script generates return-related notifications and classifies missing return reasons using the trained ML models.

## Script
- `run_reminders.py`

## What it does
1. Connects to SQLite database: `db/return_tracker.db`
2. Loads models:
   - `models/return_classifier.pkl` (return likelihood)
   - `models/reason_nlp.pkl` (NLP pipeline for `reason_category`)
3. Queries all delivered orders from `Orders`
4. For each delivered order:
   - prepares features matching training (one-hot `category` + `vendor`, scale `price` + `discount_pct`)
   - runs `return_classifier.predict_proba`
   - if `P(return) > 0.6`, inserts into `Notifications`:
     - `message`: `Likely return — decide keep or return before window closes.`
     - `created_date`: today (YYYY-MM-DD)
     - `is_read`: 0
5. Queries return windows closing soon from `Return_Windows` joined with `Orders`:
   - `days_left <= 3` and `Orders.status = 'delivered'`
   - inserts urgent `Notifications`:
     - `message`: `URGENT: Return window closes in X days. Start return process now.`
     - `created_date`: today
     - `is_read`: 0
6. Classifies missing return reasons:
   - selects from `Return_Reasons` where `reason_category IS NULL` and `reason_text IS NOT NULL`
   - predicts `reason_category` using `reason_nlp`
   - updates rows in-place
7. Commits and prints:
   - `Reminders fired: X | Reasons classified: Y`

## Run
From the project root:
```bash
py package-return-tracker/alerts/run_reminders.py
```

## Notes / Assumptions
- Model bundles are expected at:
  - `package-return-tracker/models/return_classifier.pkl`
  - `package-return-tracker/models/reason_nlp.pkl`
- The classifier bundle is expected to include:
  - `model`, `scaler`, `train_columns`, `cat_cols`, `num_cols`
- Table schemas must match what’s used in the script (`Orders`, `Return_Windows`, `Return_Reasons`, `Notifications`).

