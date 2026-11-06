
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
