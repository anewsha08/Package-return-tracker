"""Synthetic data generator for Package Return Tracker.

Generates 3000 realistic fake orders as a CSV with columns:
order_id, vendor, item, category,
price, discount_pct, multiple_sizes_ordered,
order_date, delivery_date, returned

The 'returned' label is generated with realistic heuristics:
- Clothing: multiple sizes + higher price increases return probability.
- Electronics: higher price + higher damage likelihood increases return probability.
- Other categories have lower base return rates.
- Added noise so it isn't trivially perfect.

Run:
  python data/generate_data.py
"""

from __future__ import annotations

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np


SEED = 42
random.seed(SEED)
np.random.seed(SEED)


CATEGORIES = ["clothing", "electronics", "home", "books", "shoes"]
VENDORS = [
    "Amazon",
    "BestBuy",
    "Target",
    "Walmart",
    "IKEA",
    "Etsy",
    "Newegg",
    "Kobo",
    "Zappos",
]

ITEMS_BY_CATEGORY = {
    "clothing": [
        "Cotton T-shirt",
        "Denim jacket",
        "Sweater",
        "Running shorts",
        "Casual hoodie",
    ],
    "electronics": [
        "Wireless earbuds",
        "Smart watch",
        "Noise cancelling headphones",
        "Bluetooth speaker",
        "4K streaming stick",
    ],
    "home": [
        "Kitchen blender",
        "Air purifier",
        "Desk lamp",
        "Vacuum cleaner",
        "Storage organizer set",
    ],
    "books": [
        "Paperback thriller",
        "Science textbook",
        "Cooking guide",
        "Business strategy book",
        "Fantasy novel",
    ],
    "shoes": [
        "Leather sneakers",
        "Running shoes",
        "Chelsea boots",
        "Sandals",
        "Winter boots",
    ],
}


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def gen_order_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    days = random.randint(0, max(0, delta.days))
    return start + timedelta(days=days)


def gen_delivery_date(order_date: datetime) -> datetime:
    # delivery window between 2 and 14 days
    lead_days = weighted_choice(
        list(range(2, 15)),
        [
            10,  # 2
            10,  # 3
            9,  # 4
            9,  # 5
            8,  # 6
            8,  # 7
            7,  # 8
            6,  # 9
            5,  # 10
            5,  # 11
            4,  # 12
            3,  # 13
            2,  # 14
        ],
    )
    return order_date + timedelta(days=lead_days)


def gen_price_and_discount(category: str) -> tuple[float, float]:
    if category == "clothing":
        price = np.random.lognormal(mean=np.log(35), sigma=0.35)  # ~20-70
    elif category == "shoes":
        price = np.random.lognormal(mean=np.log(55), sigma=0.35)  # ~30-110
    elif category == "electronics":
        price = np.random.lognormal(mean=np.log(120), sigma=0.5)  # ~40-300+
    elif category == "home":
        price = np.random.lognormal(mean=np.log(70), sigma=0.45)  # ~30-180
    else:  # books
        price = np.random.lognormal(mean=np.log(18), sigma=0.3)  # ~8-30

    price = float(clamp(price, 6.99, 399.99))

    # discount distribution by category
    if category in ("electronics", "home"):
        disc = np.random.beta(2.2, 6.0) * 45  # mostly small-to-mid discounts
    elif category in ("clothing", "shoes"):
        disc = np.random.beta(1.8, 5.0) * 55
    else:
        disc = np.random.beta(1.6, 7.0) * 35

    # occasional bigger discounts
    if random.random() < 0.08:
        disc += random.uniform(10, 25)

    discount_pct = float(clamp(disc, 0.0, 80.0))
    return round(price, 2), round(discount_pct, 2)


def gen_multiple_sizes(category: str) -> int:
    if category not in ("clothing", "shoes"):
        return 0

    # clothing/shoes shoppers sometimes order multiple sizes
    base = 0.18 if category == "clothing" else 0.22
    # higher chance when discount is high
    # (we approximate later, so just do base + noise)
    return 1 if random.random() < base + np.random.normal(0, 0.03) else 0


def gen_electronics_damage_flag() -> int:
    # higher chance for expensive electronics and longer delivery.
    # we'll create a base probability.
    return 1 if random.random() < 0.12 + np.random.normal(0, 0.02) else 0


def compute_return_probability(
    category: str,
    price: float,
    discount_pct: float,
    multiple_sizes_ordered: int,
    electronics_damage: int,
) -> float:
    # baseline by category
    base = {
        "clothing": 0.06,
        "shoes": 0.07,
        "electronics": 0.10,
        "home": 0.05,
        "books": 0.015,
    }[category]

    p = base

    # Clothing + multiple sizes + price > 60 => higher probability
    if category in ("clothing", "shoes"):
        if multiple_sizes_ordered == 1:
            p += 0.14
        if price > 60:
            p += 0.10
        if discount_pct > 30:
            p += 0.04

    # Electronics: damaged increases probability
    if category == "electronics":
        if electronics_damage == 1:
            p += 0.22
        if price > 150:
            p += 0.08
        if discount_pct > 25:
            p += 0.03

    # Other categories: smaller bumps
    if category in ("home",):
        if price > 120:
            p += 0.06
        if discount_pct > 35:
            p += 0.03

    if category == "books":
        # mostly low returns; discount might slightly increase.
        if discount_pct > 20:
            p += 0.01

    # add noise so it isn't deterministic
    p += np.random.normal(0, 0.035)

    # keep within [0.01, 0.95]
    return float(clamp(p, 0.01, 0.95))


def main(n_orders: int = 3000) -> None:
    out_path = Path(__file__).resolve().parent / "orders.csv"

    start = datetime(2024, 1, 1)
    end = datetime(2025, 1, 1)

    header = [
        "order_id",
        "vendor",
        "item",
        "category",
        "price",
        "discount_pct",
        "multiple_sizes_ordered",
        "order_date",
        "delivery_date",
        "returned",
    ]

    rows = []

    for _ in range(n_orders):
        category = random.choice(CATEGORIES)
        vendor = random.choice(VENDORS)
        item = random.choice(ITEMS_BY_CATEGORY[category])

        price, discount_pct = gen_price_and_discount(category)
        multiple_sizes_ordered = gen_multiple_sizes(category)

        order_date = gen_order_date(start, end)
        delivery_date = gen_delivery_date(order_date)

        electronics_damage = gen_electronics_damage_flag() if category == "electronics" else 0

        p_return = compute_return_probability(
            category=category,
            price=price,
            discount_pct=discount_pct,
            multiple_sizes_ordered=multiple_sizes_ordered,
            electronics_damage=electronics_damage,
        )

        returned = 1 if random.random() < p_return else 0

        order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"

        rows.append(
            {
                "order_id": order_id,
                "vendor": vendor,
                "item": item,
                "category": category,
                "price": f"{price:.2f}",
                "discount_pct": f"{discount_pct:.2f}",
                "multiple_sizes_ordered": int(multiple_sizes_ordered),
                "order_date": order_date.strftime("%Y-%m-%d"),
                "delivery_date": delivery_date.strftime("%Y-%m-%d"),
                "returned": int(returned),
            }
        )

    # Write CSV
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {n_orders} orders -> {out_path}")


if __name__ == "__main__":
    main(3000)


