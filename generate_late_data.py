import csv
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

file_path = DATA_DIR / "orders_late_new.csv"

late_orders = [
    [
        "O101",
        "C001",
        "2026-11-01T10:00:00",
        "completed",
        1500.00,
        "2026-11-03T09:00:00"
    ],
    [
        "O102",
        "C002",
        "2026-11-01T11:00:00",
        "pending",
        2500.00,
        "2026-11-03T09:30:00"
    ],
    [
        "O103",
        "C003",
        "2026-11-02T12:00:00",
        "completed",
        3200.00,
        "2026-11-03T10:00:00"
    ]
]

with open(file_path, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "order_id",
        "customer_id",
        "order_ts",
        "status",
        "amount_inr",
        "updated_at"
    ])

    writer.writerows(late_orders)

print("Late-arriving dataset created!")
print("File location:", file_path)
print("Total orders:", len(late_orders))