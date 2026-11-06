
import csv
import subprocess
import sys
from pathlib import Path


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
    pipeline_file = PROJECT_ROOT / "pipeline.py"

    # Read the current pipeline code
    pipeline_code = pipeline_file.read_text()

    # Temporarily use the invalid test input
    #original_input = 'INPUT_FILE = Path("data/orders.csv")'
    original_input = 'INPUT_FILE = Path("data/orders_late.csv")'
    test_input_line = 'INPUT_FILE = Path("data/orders_test_invalid.csv")'

    pipeline_file.write_text(
        pipeline_code.replace(original_input, test_input_line)
    )

    try:
        # Run the pipeline
        result = subprocess.run(
            [sys.executable, "pipeline.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Read rejected orders
        #reject_file = PROJECT_ROOT / "data/validated/orders_rejected.csv"
        reject_file = PROJECT_ROOT / "data/validated/orders_test_invalid_rejected.csv"

        with open(reject_file, "r", newline="") as file:
            reader = csv.DictReader(file)
            rejected_orders = list(reader)

        # Check rejection
        assert len(rejected_orders) == 1
        assert rejected_orders[0]["order_id"] == "O001"
        assert rejected_orders[0]["reject_reason"] == "Amount is not numeric"

    finally:
        # Restore the original pipeline input
        pipeline_file.write_text(pipeline_code)

        # Run the normal pipeline again
        subprocess.run(
            [sys.executable, "pipeline.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
