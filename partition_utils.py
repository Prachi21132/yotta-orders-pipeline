import csv


def get_existing_order_ids(partitioned_folder):

    existing_order_ids = set()

    if partitioned_folder.exists():

        for folder in partitioned_folder.iterdir():

            existing_file = folder / "orders.csv"

            if existing_file.exists():

                with open(existing_file, "r", newline="") as file:

                    reader = csv.DictReader(file)

                    for row in reader:
                        existing_order_ids.add(row["order_id"])

    return existing_order_ids