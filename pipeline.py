
#import csv
#from pathlib import Path
import csv
from pathlib import Path
from datetime import datetime
import sys

# 1. Define the input file
#INPUT_FILE = Path("data/orders.csv")
#INPUT_FILE = Path("data/orders_test_invalid.csv")
#INPUT_FILE = Path("data/orders_test.csv")
#INPUT_FILE = Path("data/orders_test2.csv")
INPUT_FILE = Path("data/orders_late.csv")
# 2. Define output folders

RAW_FOLDER = Path("data/raw")
VALID_FOLDER = Path("data/validated")
CURATED_FOLDER = Path("data/curated")
# 2.1 Define metadata file
METADATA_FILE = Path("data/metadata/processed_files.csv")
# 2.2 Create output filenames based on input filename

file_name = INPUT_FILE.stem

raw_file = RAW_FOLDER / f"{file_name}_raw.csv"

valid_file = VALID_FOLDER / f"{file_name}_valid.csv"

reject_file = VALID_FOLDER / f"{file_name}_rejected.csv"

duplicate_file = VALID_FOLDER / f"{file_name}_duplicates.csv"

curated_file = CURATED_FOLDER / f"{file_name}_curated.csv"

# 3. Create folders
RAW_FOLDER.mkdir(parents=True, exist_ok=True)
VALID_FOLDER.mkdir(parents=True, exist_ok=True)
CURATED_FOLDER.mkdir(parents=True, exist_ok=True)
# 3.1 Read previously processed files

processed_files = []

with open(METADATA_FILE, "r", newline="") as file:

    reader = csv.DictReader(file)

    for row in reader:
        processed_files.append(row["file_name"])

print("Previously processed files:", processed_files)
# 3.2 Check whether the input file was already processed

input_file_name = INPUT_FILE.name

if input_file_name in processed_files:

    print("Duplicate file detected:", input_file_name)
    print("This file has already been processed.")

    sys.exit()

# 4. Read the source data
with open(INPUT_FILE, "r", newline="") as file:

    reader = csv.DictReader(file)

    orders = list(reader)


print("Total orders read:", len(orders))


# 5. Save original data in raw zone
#raw_file = RAW_FOLDER / "orders_raw.csv"

with open(raw_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(orders)


# 6. Validate orders

# 6. Validate orders and detect duplicates

# 6. Validate orders and detect duplicates

valid_orders = []
rejected_orders = []
duplicate_orders = []

seen_order_ids = set()

for order in orders:

    order_id = order["order_id"].strip()
    customer_id = order["customer_id"].strip()
    status = order["status"].strip().lower()
    amount_value = order["amount_inr"].strip()

    # Check duplicate order ID
    if order_id and order_id in seen_order_ids:
        duplicate_orders.append(order)
        continue

    # Check required fields
    if not order_id:
        order["reject_reason"] = "Missing order_id"
        rejected_orders.append(order)
        continue

    if not customer_id:
        order["reject_reason"] = "Missing customer_id"
        rejected_orders.append(order)
        continue

    # Remember order ID after required fields pass
    seen_order_ids.add(order_id)

    # Validate status
    if status not in ["completed", "cancelled", "pending"]:
        order["reject_reason"] = "Invalid status"
        rejected_orders.append(order)
        continue

    # Validate amount
    try:
        amount = float(amount_value)

        if amount <= 0:
            order["reject_reason"] = "Amount must be greater than zero"
            rejected_orders.append(order)
            continue

    except (ValueError, TypeError):
        order["reject_reason"] = "Amount is not numeric"
        rejected_orders.append(order)
        continue

    # If all checks pass
    valid_orders.append(order)


print("Validation completed!")
print("Valid orders:", len(valid_orders))
print("Rejected orders:", len(rejected_orders))
print("Duplicate orders:", len(duplicate_orders))






# 7. Save validated orders
#valid_file = VALID_FOLDER / "orders_valid.csv"

with open(valid_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(valid_orders)


# 8. Save rejected orders

# 8. Save rejected orders

#reject_file = VALID_FOLDER / "orders_rejected.csv"

#reject_fields = list(orders[0].keys()) + ["reject_reason"]
reject_fields = [
    field for field in orders[0].keys()
    if field != "reject_reason"
]

reject_fields.append("reject_reason")
with open(reject_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=reject_fields
    )

    writer.writeheader()
    writer.writerows(rejected_orders)


# 8.1 Save duplicate orders

#duplicate_file = VALID_FOLDER / "orders_duplicates.csv"

with open(duplicate_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(duplicate_orders)



# 9. Create curated output
#curated_file = CURATED_FOLDER / "orders_curated.csv"

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

# 11. Record successfully processed file

with open(METADATA_FILE, "a", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=["file_name", "processed_at", "record_count"]
    )

    writer.writerow({
        "file_name": INPUT_FILE.name,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "record_count": len(orders)
    })

print("File processing history updated!")


