
#import csv
#from pathlib import Path
import csv
from pathlib import Path
from datetime import datetime
import sys
import hashlib
import os
from partition_utils import get_existing_order_ids
import uuid
# 0. Track pipeline execution

run_id = str(uuid.uuid4())

pipeline_start_time = datetime.now()

print("Run ID:", run_id)
print("Pipeline start time:", pipeline_start_time)
def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

# 1. Define the input file
#INPUT_FILE = Path("data/orders.csv")
INPUT_FILE = Path(os.environ.get("PIPELINE_INPUT_FILE", "data/orders.csv"))
#INPUT_FILE = Path("data/orders_test_invalid.csv")
#INPUT_FILE = Path("data/orders_test.csv")
#INPUT_FILE = Path("data/orders_test2.csv")
#INPUT_FILE = Path("data/orders_late.csv")
#INPUT_FILE = Path("data/orders_copy.csv")
#INPUT_FILE = Path("data/orders.csv")
#INPUT_FILE = Path("data/orders_late_new.csv")
# 2. Define output folders

RAW_FOLDER = Path("data/raw")
VALID_FOLDER = Path("data/validated")
CURATED_FOLDER = Path("data/curated")
# 2.1 Define metadata file
METADATA_FILE = Path("data/metadata/processed_files.csv")
RUN_HISTORY_FILE = Path("data/metadata/pipeline_runs.csv")
def record_pipeline_run(input_count, valid_count, rejected_count, duplicate_count, status):
    pipeline_end_time = datetime.now()

    RUN_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = RUN_HISTORY_FILE.exists()

    fieldnames = [
        "run_id",
        "input_file",
        "start_time",
        "end_time",
        "duration_seconds",
        "input_count",
        "valid_count",
        "rejected_count",
        "duplicate_count",
        "status"
    ]

    with open(RUN_HISTORY_FILE, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists or RUN_HISTORY_FILE.stat().st_size == 0:
            writer.writeheader()

        writer.writerow({
            "run_id": run_id,
            "input_file": INPUT_FILE.name,
            "start_time": pipeline_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": pipeline_end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": (pipeline_end_time - pipeline_start_time).total_seconds(),
            "input_count": input_count,
            "valid_count": valid_count,
            "rejected_count": rejected_count,
            "duplicate_count": duplicate_count,
            "status": status
        })

    print("Pipeline run history saved with status:", status)
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

# 3.1 Read previously processed file hashes


# 3.1 Read previously processed file hashes

METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

if not METADATA_FILE.exists():

    with open(METADATA_FILE, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "file_name",
                "processed_at",
                "record_count",
                "file_hash"
            ]
        )

        writer.writeheader()

processed_hashes = []

with open(METADATA_FILE, "r", newline="") as file:

    reader = csv.DictReader(file)

    for row in reader:

        file_hash = row.get("file_hash", "")

        if file_hash:
            processed_hashes.append(file_hash)

print("Previously processed file hashes:", processed_hashes)

# 3.2 Calculate hash of the current input file

if not INPUT_FILE.exists():
    print("Input file does not exist:", INPUT_FILE)

    record_pipeline_run(0, 0, 0, 0, "FAILED_MISSING_FILE")

    sys.exit()

input_file_hash = calculate_file_hash(INPUT_FILE)

# 3.3 Check whether the file content was already processed
if input_file_hash in processed_hashes:

    print("Duplicate file content detected.")
    print("This file has already been processed.")

    record_pipeline_run(0, 0, 0, 0, "DUPLICATE_FILE")

    sys.exit()




# 4. Read the source data
with open(INPUT_FILE, "r", newline="") as file:

    reader = csv.DictReader(file)

    orders = list(reader)

    columns = reader.fieldnames

print("Total orders read:", len(orders))

# 4.1 Handle empty input
if not orders:
    print("Input file contains no data records.")

    record_pipeline_run(0, 0, 0, 0, "FAILED_EMPTY_INPUT")

    sys.exit()
# 4.2 Validate required and unexpected columns
required_columns = {
    "order_id",
    "customer_id",
    "order_ts",
    "status",
    "amount_inr",
    "updated_at"
}

expected_columns = {
    "order_id",
    "customer_id",
    "order_ts",
    "status",
    "amount_inr",
    "updated_at"
}

actual_columns = set(columns or [])

# Check missing required columns
missing_columns = required_columns - actual_columns

if missing_columns:
    print("Missing required columns:", sorted(missing_columns))

    record_pipeline_run(
        len(orders), 0, 0, 0, "FAILED_MISSING_COLUMNS"
    )

    sys.exit()

# Check unexpected columns
unexpected_columns = actual_columns - expected_columns

if unexpected_columns:
    print("Unexpected columns detected:", sorted(unexpected_columns))
    print("Input schema does not match expected schema.")

    record_pipeline_run(
        len(orders), 0, 0, 0, "FAILED_UNEXPECTED_COLUMNS"
    )

    sys.exit()

print("Schema validation passed!")




# 5. Save original data in raw zone
#raw_file = RAW_FOLDER / "orders_raw.csv"

with open(raw_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(orders)



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

    # Validate order timestamp
    order_ts = order["order_ts"].strip()

    try:
        datetime.fromisoformat(order_ts)

    except (ValueError, TypeError):
        order["reject_reason"] = "Invalid order timestamp"
        rejected_orders.append(order)
        continue

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
    seen_order_ids.add(order_id)
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

curated_file = CURATED_FOLDER / "orders_curated.csv"

with open(curated_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=orders[0].keys()
    )

    writer.writeheader()
    writer.writerows(valid_orders)


# 9. Create date-partitioned curated output

PARTITIONED_FOLDER = CURATED_FOLDER / "partitioned"

# Load existing order IDs only once
existing_order_ids = get_existing_order_ids(PARTITIONED_FOLDER)

for order in valid_orders:

    order_date = order["order_ts"][:10]

    partition_folder = PARTITIONED_FOLDER / f"order_date={order_date}"

    partition_folder.mkdir(parents=True, exist_ok=True)

    partition_file = partition_folder / "orders.csv"
    # Skip duplicate order IDs across all partitions
    if order["order_id"] in existing_order_ids:

        print("Order already exists:", order["order_id"])
        continue

    file_exists = partition_file.exists()

    with open(partition_file, "a", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=orders[0].keys()
        )

        if not file_exists or partition_file.stat().st_size == 0:
            writer.writeheader()

        writer.writerow(order)
        existing_order_ids.add(order["order_id"])

print("Date-partitioned curated data saved!")


# 10. Save processed file metadata

METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

file_exists = METADATA_FILE.exists()

with open(METADATA_FILE, "a", newline="") as file:

    fieldnames = [
        "file_name",
        "processed_at",
        "record_count",
        "file_hash"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    if not file_exists or METADATA_FILE.stat().st_size == 0:
        writer.writeheader()

    writer.writerow({
        "file_name": INPUT_FILE.name,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "record_count": len(orders),
        "file_hash": input_file_hash
    })

print("Processed file metadata saved!")
# 11. Record pipeline end time

pipeline_end_time = datetime.now()

print("Pipeline end time:", pipeline_end_time)

print("Pipeline duration:", pipeline_end_time - pipeline_start_time)
# 12. Save pipeline run history
record_pipeline_run(
    len(orders),
    len(valid_orders),
    len(rejected_orders),
    len(duplicate_orders),
    "SUCCESS"
)