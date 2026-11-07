# Data Dictionary

## Dataset Overview

- Dataset: Orders
- Source: CSV input files
- Data grain: One record per order
- Order identifier: order_id
- Currency: Indian Rupees (INR)
- Timestamp format: ISO-compatible timestamp strings

## Input Schema

| Column | Data Type | Description | Validation |
|---|---|---|---|
| order_id | String | Unique identifier for an order | Required; duplicate IDs are detected |
| customer_id | String | Identifier of the customer placing the order | Required |
| order_ts | Timestamp string | Date and time when the order was placed | Must be parseable by datetime.fromisoformat |
| status | String | Current order status | Must be completed, cancelled, or pending |
| amount_inr | Decimal-like numeric string | Order amount in Indian Rupees | Must convert to float and be greater than zero |
| updated_at | Timestamp string | Date and time when the order record was updated | Column is required; timestamp value is not currently validated |

## Keys and Duplicate Handling

- order_id identifies an order.
- Duplicate order IDs within an input file are separated into duplicate records.
- Existing order IDs in date-based curated partitions are checked before writing.
- The pipeline uses order_ts to determine the partition date.

## Partitioning

Curated orders are partitioned by the date portion of order_ts.

Example:

data/curated/partitioned/order_date=2026-11-01/orders.csv

## Assumptions

- Each order should have an order_id and customer_id.
- Order timestamps should be ISO-compatible.
- Valid order statuses are completed, cancelled, and pending.
- Order amounts must be numeric and greater than zero.
- The pipeline currently does not validate the updated_at timestamp value.
- Duplicate order IDs are treated as duplicates rather than separate orders.
- The current pipeline uses CSV files for local storage.

## Known Limitations

- updated_at value validation is not implemented.
- The pipeline uses local CSV storage rather than cloud object storage.
- Performance measurements are based on a small local sample.
