from __future__ import annotations

import os
import pickle
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db' / 'return_tracker.db'
MODELS_DIR = BASE_DIR / 'models'

RETURN_MODEL_PATH = MODELS_DIR / 'return_classifier.pkl'
REASON_MODEL_PATH = MODELS_DIR / 'reason_nlp.pkl'


def today_iso_date() -> str:
    return datetime.now().strftime('%Y-%m-%d')


def load_return_bundle(path: Path):
    with open(path, 'rb') as f:
        bundle = pickle.load(f)
    return bundle


def predict_return_prob(df_features: pd.DataFrame, bundle: dict) -> float:
    """Prepare features to match training columns and return probability for class 1."""

    model = bundle['model']
    scaler = bundle['scaler']
    train_columns = bundle['train_columns']
    num_cols = bundle['num_cols']
    cat_cols = bundle['cat_cols']

    # One-hot encode
    X_dum = pd.get_dummies(df_features, columns=cat_cols, drop_first=False)

    # Align columns
    X_dum = X_dum.reindex(columns=train_columns, fill_value=0)

    # Scale numeric cols using scaler
    X_final = X_dum.copy()
    # train_columns includes both numeric and dummy cols; but numeric columns names must exist
    X_final[num_cols] = scaler.transform(X_dum[num_cols])

    prob = model.predict_proba(X_final)[:, 1][0]
    return float(prob)


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))

    try:
        # Load models
        return_bundle = load_return_bundle(RETURN_MODEL_PATH)
        with open(REASON_MODEL_PATH, 'rb') as f:
            reason_nlp = pickle.load(f)

        # Query delivered orders
        delivered_df = pd.read_sql(
            "SELECT order_id, vendor, item, category, price, order_date, delivery_date, status FROM Orders WHERE status = 'delivered'",
            conn,
        )

        # 5) Likely-return notifications based on ML probability
        reminders_fired = 0
        for _, row in delivered_df.iterrows():
            df_features = row.to_frame().T
            prob = predict_return_prob(df_features, return_bundle)

            if prob > 0.6:
                conn.execute(
                    "INSERT INTO Notifications (order_id, message, created_date, is_read) VALUES (?, ?, ?, ?)",
                    (
                        row['order_id'],
                        'Likely return — decide keep or return before window closes.',
                        today_iso_date(),
                        0,
                    ),
                )
                reminders_fired += 1

        # 6) Urgent notifications for windows closing soon
        urgent_rows = conn.execute(
            """
            SELECT rw.order_id, rw.days_left
            FROM Return_Windows rw
            JOIN Orders o ON o.order_id = rw.order_id
            WHERE rw.days_left <= 3 AND o.status = 'delivered'
            """
        ).fetchall()

        for (order_id, days_left) in urgent_rows:
            conn.execute(
                "INSERT INTO Notifications (order_id, message, created_date, is_read) VALUES (?, ?, ?, ?)",
                (
                    order_id,
                    f'URGENT: Return window closes in {days_left} days. Start return process now.',
                    today_iso_date(),
                    0,
                ),
            )
            reminders_fired += 1

        # 7) Classify missing reason_category
        reasons_rows = conn.execute(
            """
            SELECT reason_id, order_id, reason_text
            FROM Return_Reasons
            WHERE reason_category IS NULL AND reason_text IS NOT NULL
            """
        ).fetchall()

        reasons_classified = 0
        for reason_id, order_id, reason_text in reasons_rows:
            pred = reason_nlp.predict([str(reason_text)])[0]
            conn.execute(
                "UPDATE Return_Reasons SET reason_category = ? WHERE reason_id = ?",
                (pred, reason_id),
            )
            reasons_classified += 1

        # 8) Commit
        conn.commit()

        # 9) Print
        print(f'Reminders fired: {reminders_fired} | Reasons classified: {reasons_classified}')

    finally:
        conn.close()


if __name__ == '__main__':
    main()

