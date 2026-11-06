
import csv
from pathlib import Path


# 1. Define the input file
INPUT_FILE = Path("data/orders.csv")


# 2. Define output folders
RAW_FOLDER = Path("data/raw")
VALID_FOLDER = Path("data/validated")
CURATED_FOLDER = Path("data/curated")


# 3. Create folders
RAW_FOLDER.mkdir(parents=True, exist_ok=True)
VALID_FOLDER.mkdir(parents=True, exist_ok=True)
CURATED_FOLDER.mkdir(parents=True, exist_ok=True)


# 4. Read the source data
with open(INPUT_FILE, "r", newline="") as file:

    reader = csv.DictReader(file)

    orders = list(reader)


print("Total orders read:", len(orders))


# 5. Save original data in raw zone
raw_file = RAW_FOLDER / "orders_raw.csv"

with open(raw_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(orders)


# 6. Validate orders

# 6. Validate orders and detect duplicates

valid_orders = []
rejected_orders = []
duplicate_orders = []

seen_order_ids = set()

for order in orders:

    order_id = order["order_id"].strip()

    # Check duplicate order ID
    if order_id in seen_order_ids:

        duplicate_orders.append(order)
        continue

    # Remember this order ID
    seen_order_ids.add(order_id)

    # Validate required fields
    if not order_id or not order["customer_id"].strip():

        rejected_orders.append(order)
        continue

    # Validate status
    if order["status"] not in [
        "completed",
        "cancelled",
        "pending"
    ]:

        rejected_orders.append(order)
        continue

    # Validate amount safely
    try:
        amount = float(order["amount_inr"])

        if amount <= 0:
            rejected_orders.append(order)
            continue

    except (ValueError, TypeError):
        rejected_orders.append(order)
        continue

    # If all checks pass
    valid_orders.append(order)


print("Validation completed!")
print("Valid orders:", len(valid_orders))
print("Rejected orders:", len(rejected_orders))
print("Duplicate orders:", len(duplicate_orders))




# 7. Save validated orders
valid_file = VALID_FOLDER / "orders_valid.csv"

with open(valid_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(valid_orders)


# 8. Save rejected orders
reject_file = VALID_FOLDER / "orders_rejected.csv"

with open(reject_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(rejected_orders)

# 8.1 Save duplicate orders

duplicate_file = VALID_FOLDER / "orders_duplicates.csv"

with open(duplicate_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(duplicate_orders)



# 9. Create curated output
curated_file = CURATED_FOLDER / "orders_curated.csv"

with open(curated_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(valid_orders)


# 10. Print pipeline summary
print("Pipeline completed successfully!")

print("Raw orders:", len(orders))
print("Valid orders:", len(valid_orders))
print("Rejected orders:", len(rejected_orders))
print("Duplicate orders:", len(duplicate_orders))
print("Duplicate file:", duplicate_file)

print("Raw file:", raw_file)
print("Validated file:", valid_file)
print("Curated file:", curated_file)

