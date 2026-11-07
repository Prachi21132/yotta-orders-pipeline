\# Pipeline Architecture



\## Overview



The YottaFlex AI order pipeline is a local CSV-based data processing system.



It ingests order files, validates records, identifies duplicates, writes curated outputs, partitions records by order date, and tracks pipeline execution.



\## Architecture Flow



Incoming CSV Files  

↓  

File Discovery  

↓  

File-Level Duplicate Check  

↓  

Raw Data Ingestion  

↓  

Schema Validation  

↓  

Record Validation  

↓  

Valid Records / Rejected Records  

↓  

Within-File Duplicate Detection  

↓  

Curated Output  

↓  

Existing Partition Duplicate Check  

↓  

Date-Based Partitioning  

↓  

Pipeline Run Metadata



\## Processing Components



\### 1. Incoming Data



The default input file is `data/orders.csv`.



Additional CSV files can be supplied through the configured input path.



\### 2. File Discovery



The discovery script identifies CSV files in the incoming folder and executes the pipeline for each discovered file.



Discovery is manually triggered. It is not a continuously running folder-monitoring service.



\### 3. File-Level Duplicate Detection



The pipeline calculates a SHA-256 hash for the input file.



Previously processed file hashes are stored in `data/metadata/processed\_files.csv`.



\### 4. Raw Data Ingestion



Original input records are stored in the raw data layer before record validation.



\### 5. Schema and Record Validation



The pipeline checks required and unexpected columns.



Record validation checks:

\- Required order and customer identifiers

\- Valid order timestamp

\- Valid order status

\- Numeric positive order amount



Invalid records are written to rejected output with a rejection reason.



\### 6. Duplicate Detection



Duplicate order IDs within an input file are identified separately.



Before writing curated records, the pipeline checks existing date partitions for previously stored order IDs.



\### 7. Curated Data and Partitioning



Validated records are written to curated output.



Partitioned records are organized using the order date derived from `order\_ts`.



Example:



`data/curated/partitioned/order\_date=2026-11-01/orders.csv`



\### 8. Metadata and Run Tracking



The pipeline records execution information in:



\- `data/metadata/processed\_files.csv`

\- `data/metadata/pipeline\_runs.csv`



Run history includes identifiers, timestamps, processing duration, record counts, and status.



\## Storage Layers



| Layer | Purpose |

|---|---|

| Incoming | Files waiting to be processed |

| Raw | Original ingested records |

| Validated | Valid, rejected, and duplicate records |

| Curated | Processed order records |

| Partitioned | Curated records organized by order date |

| Metadata | File processing and pipeline run history |



\## Technology Stack



\- Python

\- CSV

\- pathlib

\- SHA-256

\- Pytest

\- Local filesystem



\## Design Notes



\- The implementation uses local CSV files rather than cloud object storage.

\- File hashes support duplicate delivery detection.

\- Order IDs support record-level duplicate detection.

\- Date partitioning organizes curated records by order date.

\- Existing order IDs are loaded into a set before partition processing to avoid repeated partition scans.

\- Run metadata supports execution tracking and basic failure investigation.



\## Limitations



\- File discovery is manually triggered.

\- Local CSV storage is used instead of a cloud data lake.

\- The pipeline does not currently implement a distributed processing engine.

\- Timestamp validation for `updated\_at` is not currently implemented.

\- Performance measurements use a small local sample.



