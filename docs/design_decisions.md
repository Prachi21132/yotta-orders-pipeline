\# Design Decisions



\## 1. Local CSV Storage



\### Decision

The pipeline uses CSV files and the local filesystem for input, processing, and output.



\### Reason

This keeps the project simple to run and test without requiring cloud infrastructure.



\### Trade-off

Local CSV storage is suitable for this challenge but does not provide the scalability or distributed processing capabilities of a cloud data lake.



\## 2. File-Level Duplicate Detection



\### Decision

The pipeline uses SHA-256 hashing to identify previously processed file contents.



\### Reason

A file hash helps identify identical file deliveries even when the filename changes.



\### Trade-off

Files with identical contents are treated as duplicate deliveries. The hash does not determine whether two different files contain overlapping order records.



\## 3. Record-Level Duplicate Detection



\### Decision

The pipeline uses order\_id to identify duplicate orders.



Duplicate IDs within an input file are separated into duplicate records. Existing order IDs are also checked against curated date partitions.



\### Reason

This helps prevent the same order from being added repeatedly.



\### Trade-off

The current design assumes order\_id identifies an order uniquely. It does not implement an update or merge strategy for an existing order.



\## 4. Date-Based Partitioning



\### Decision

Curated orders are organized into folders using the date portion of order\_ts.



\### Reason

Date-based partitioning makes records easier to organize and locate by order date.



\### Trade-off

The current implementation uses local folders and CSV files rather than a distributed partitioned storage system.



\## 5. Duplicate Lookup Optimization



\### Decision

Existing order IDs are loaded into a set before processing valid orders.



Newly written order IDs are added to the set.



\### Reason

This avoids repeatedly scanning partition files for every order and allows efficient set membership checks.



\### Trade-off

The set must fit in memory. A larger dataset may require a different storage or lookup strategy.



\## 6. Late-Arriving Data



\### Decision

The pipeline supports processing additional incoming CSV files through the discovery script or configured input path.



\### Reason

This allows new files to be processed after earlier pipeline runs.



\### Current Behavior

The discovery script is manually executed and is not a continuously running file-monitoring service.



The pipeline uses order\_ts to determine the partition date.



\### Limitation

The current design does not implement a complete order update or merge process for records that already exist.



\## 7. Pipeline Run Tracking



\### Decision

The pipeline records execution metadata, including run identifiers, timestamps, record counts, processing duration, and status.



\### Reason

Run history helps investigate successful and failed executions.



\### Trade-off

The metadata is stored in local CSV files and does not provide centralized monitoring or alerting.



\## 8. Reconciliation



\### Decision

The pipeline compares the total input record count with the combined valid, rejected, and duplicate record counts.



\### Reason

This helps detect records that were not accounted for during validation.



\### Limitation

Reconciliation checks record counts. It does not independently verify every field or the correctness of every output record.



\## 9. Testing



\### Decision

The project uses pytest for automated testing.



\### Reason

Automated tests help verify pipeline behavior and reduce the risk of regressions.



\### Current Coverage

The documented test suite contains eight tests covering successful execution, record counts, rejection behavior, partitioning, and duplicate lookup.



\## 10. Performance



\### Decision

The project measures pipeline execution time and automated test suite runtime separately.



\### Optimization

Existing partition order IDs are loaded once rather than repeatedly scanned for each order.



\### Limitation

The current measurement uses a small local dataset and is not a large-scale benchmark.



