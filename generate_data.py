
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

# Create the data folder
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Generate reproducible sample data
random.seed(42)

customers = ["C001", "C002", "C003", "C004", "C005"]

# Create order file
file_path = DATA_DIR / "orders.csv"

with open(file_path, "w", newline="") as file:
    writer = csv.writer(file)

    # Column names
    writer.writerow([
        "order_id",
        "customer_id",
        "order_ts",
        "status",
        "amount_inr",
        "updated_at"
    ])

    # Generate 100 orders
    for i in range(1, 101):
        order_id = f"O{i:03d}"
        customer_id = random.choice(customers)

        order_time = datetime(2026, 11, 1) + timedelta(
            minutes=random.randint(0, 5000)
        )

        status = random.choice([
            "completed",
            "cancelled",
            "pending"
        ])

        amount = round(random.uniform(100, 5000), 2)

        writer.writerow([
            order_id,
            customer_id,
            order_time.isoformat(),
            status,
            amount,
            order_time.isoformat()
        ])

print("Dataset generated successfully!")
print("File location:", file_path)
print("Total orders: 100")
