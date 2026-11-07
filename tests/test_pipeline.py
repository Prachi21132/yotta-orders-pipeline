
import csv
import subprocess
import sys
from pathlib import Path
import os
from partition_utils import get_existing_order_ids


# Project root folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_pipeline_runs_successfully():

    result = subprocess.run(
        [sys.executable, "pipeline.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0


def test_valid_orders_count():

    file_path = PROJECT_ROOT / "data/validated/orders_valid.csv"

    with open(file_path, "r", newline="") as file:

        reader = csv.DictReader(file)
        orders = list(reader)

    assert len(orders) == 100


def test_rejected_orders_count():

    file_path = PROJECT_ROOT / "data/validated/orders_rejected.csv"

    with open(file_path, "r", newline="") as file:

        reader = csv.DictReader(file)
        orders = list(reader)

    assert len(orders) == 0


def test_duplicate_orders_count():

    file_path = PROJECT_ROOT / "data/validated/orders_duplicates.csv"

    with open(file_path, "r", newline="") as file:

        reader = csv.DictReader(file)
        orders = list(reader)

    assert len(orders) == 0


def test_curated_orders_count():

    file_path = PROJECT_ROOT / "data/curated/orders_curated.csv"

    with open(file_path, "r", newline="") as file:

        reader = csv.DictReader(file)
        orders = list(reader)

    assert len(orders) == 100


def test_invalid_amount_rejection_reason():

    test_input = PROJECT_ROOT / "data/orders_test_invalid.csv"

    # Set the input file through an environment variable
    env = os.environ.copy()
    env["PIPELINE_INPUT_FILE"] = str(test_input)

    # Run the pipeline
    result = subprocess.run(
        [sys.executable, "pipeline.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env
    )

    assert result.returncode == 0

    # Read rejected orders
    reject_file = (
        PROJECT_ROOT
        / "data/validated/orders_test_invalid_rejected.csv"
    )

    with open(reject_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        rejected_orders = list(reader)

    # Check rejection
    assert len(rejected_orders) == 1
    assert rejected_orders[0]["order_id"] == "O001"
    assert rejected_orders[0]["reject_reason"] == "Amount is not numeric"

def test_date_partitioned_curated_orders():

    partition_folder = (
        PROJECT_ROOT / "data/curated/partitioned"
    )

    partition_files = list(
        partition_folder.glob("order_date=*/orders.csv")
    )

    assert len(partition_files) > 0

    total_orders = 0

    for partition_file in partition_files:

        with open(partition_file, "r", newline="") as file:
            reader = csv.DictReader(file)
            orders = list(reader)

        total_orders += len(orders)

        partition_date = partition_file.parent.name.replace(
            "order_date=", ""
        )

        for order in orders:
            assert order["order_ts"].startswith(partition_date)

    assert total_orders == 106

def test_duplicate_order_id_across_different_dates(tmp_path):

    partitioned_folder = tmp_path / "partitioned"

    # Existing order in the first date partition
    first_partition = (
        partitioned_folder / "order_date=2026-11-01"
    )

    first_partition.mkdir(parents=True)

    with open(first_partition / "orders.csv", "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=["order_id", "order_ts"]
        )

        writer.writeheader()

        writer.writerow({
            "order_id": "O001",
            "order_ts": "2026-11-01T10:00:00"
        })

    # Check IDs across all partitions
    existing_ids = get_existing_order_ids(partitioned_folder)

    # Same ID arriving on a different date must be detected
    new_order = {
        "order_id": "O001",
        "order_ts": "2026-11-02T10:00:00"
    }

    assert new_order["order_id"] in existing_ids