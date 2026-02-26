import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

regions = {
    "North America": ["United States", "Canada", "Mexico"],
    "Europe": ["Germany", "France", "United Kingdom", "Spain", "Italy"],
    "Asia Pacific": ["Japan", "Australia", "China", "India", "South Korea"],
    "Latin America": ["Brazil", "Argentina", "Colombia", "Chile"],
}

categories = {
    "Electronics": ["Laptops", "Smartphones", "Tablets", "Accessories", "Audio"],
    "Furniture": ["Chairs", "Desks", "Shelving", "Cabinets", "Lighting"],
    "Office Supplies": ["Paper", "Pens", "Notebooks", "Binders", "Organizers"],
    "Clothing": ["Shirts", "Pants", "Shoes", "Jackets", "Accessories"],
}

segments = ["Consumer", "Corporate", "Home Office", "Small Business"]

price_ranges = {
    "Laptops": (800, 2500), "Smartphones": (400, 1200), "Tablets": (300, 900),
    "Accessories": (20, 150), "Audio": (50, 500), "Chairs": (100, 800),
    "Desks": (150, 1200), "Shelving": (80, 400), "Cabinets": (200, 900),
    "Lighting": (30, 300), "Paper": (5, 50), "Pens": (5, 30),
    "Notebooks": (5, 40), "Binders": (5, 25), "Organizers": (10, 60),
    "Shirts": (20, 120), "Pants": (30, 150), "Shoes": (50, 300),
    "Jackets": (60, 400), "Accessories": (10, 80),
}

records = []
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)

for i in range(10000):
    order_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    region = random.choice(list(regions.keys()))
    country = random.choice(regions[region])
    category = random.choice(list(categories.keys()))
    subcategory = random.choice(categories[category])
    segment = random.choice(segments)
    quantity = random.randint(1, 20)
    low, high = price_ranges.get(subcategory, (10, 200))
    unit_price = round(random.uniform(low, high), 2)
    revenue = round(quantity * unit_price, 2)
    cost_pct = random.uniform(0.45, 0.75)
    cost = round(revenue * cost_pct, 2)
    profit = round(revenue - cost, 2)
    profit_margin = round((profit / revenue) * 100, 2)

    records.append({
        "order_id": f"ORD-{i+1:05d}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "year": order_date.year,
        "quarter": f"Q{(order_date.month - 1) // 3 + 1}",
        "month": order_date.month,
        "month_name": order_date.strftime("%B"),
        "region": region,
        "country": country,
        "category": category,
        "subcategory": subcategory,
        "customer_segment": segment,
        "quantity": quantity,
        "unit_price": unit_price,
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "profit_margin": profit_margin,
    })

df = pd.DataFrame(records)
df.to_csv("global_retail_sales.csv", index=False)
print(f"Dataset generated: {len(df)} records")
print(df.head())
