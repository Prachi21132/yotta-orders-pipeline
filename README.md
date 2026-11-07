\# YottaFlex AI – Data Engineering Code Challenge



\## Project Overview



This project implements a Python-based CSV data ingestion and processing pipeline. It simulates an order-processing data engineering workflow with raw data ingestion, validation, duplicate detection, curated outputs, date-based partitioning, and processing metadata.



The pipeline also supports processing multiple incoming CSV files, including late-arriving data files.



\## Key Features



1\. \*\*CSV Ingestion:\*\* Reads order data from CSV files and stores the original records in a raw data layer.

2\. \*\*File-Level Duplicate Detection:\*\* Uses SHA-256 hashing to identify files that have already been processed.

3\. \*\*Data Validation:\*\* Checks required fields, valid order statuses, and positive numeric order amounts.

4\. \*\*Record-Level Duplicate Detection:\*\* Identifies repeated order IDs within an input file.

5\. \*\*Rejected Records:\*\* Separates invalid records and records the reason for rejection.

6\. \*\*Curated Data:\*\* Stores validated records in a curated CSV file.

7\. \*\*Date-Based Partitioning:\*\* Organizes curated records into folders based on the order date.

8\. \*\*Cross-Partition Duplicate Detection:\*\* Checks existing date partitions to prevent previously stored order IDs from being added again.

9\. \*\*Metadata Tracking:\*\* Stores the input filename, processing timestamp, record count, and SHA-256 hash.

10\. \*\*Incoming File Discovery:\*\* Automatically discovers CSV files in the incoming folder when the discovery script is executed.



\## Project Structure



```text

yotta-orders-pipeline/

│

├── data/

│   ├── incoming/          # Incoming CSV files

│   ├── raw/               # Original ingested data

│   ├── validated/         # Valid, rejected and duplicate records

│   ├── curated/           # Curated output

│   │   └── partitioned/   # Date-wise partitioned data

│   ├── metadata/          # Processed file metadata

│   └── orders.csv         # Default input file

│

├── tests/

│   └── test\_pipeline.py   # Automated tests

│

├── pipeline.py            # Main ETL pipeline

├── partition\_utils.py     # Cross-partition duplicate lookup

├── discover\_files.py      # Incoming file discovery

├── generate\_data.py       # Sample data generator

├── generate\_late\_data.py  # Late-arriving data generator

├── requirements.txt       # Python dependencies

└── README.md

```



\## Technologies Used



\- Python

\- CSV

\- SHA-256 hashing

\- Pytest

\- Git and GitHub



\## Data Processing Workflow



```text

Incoming CSV Files

&#x20;       |

&#x20;       v

File Discovery

&#x20;       |

&#x20;       v

File-Level Duplicate Check

&#x20;       |

&#x20;       v

Raw Data Ingestion

&#x20;       |

&#x20;       v

Data Validation

&#x20;       |

&#x20;       +------------------+

&#x20;       |                  |

&#x20;       v                  v

&#x20;  Valid Records      Rejected Records

&#x20;       |

&#x20;       v

Record-Level Duplicate Check

&#x20;       |

&#x20;       v

Curated Data

&#x20;       |

&#x20;       v

Date-Based Partitioning

&#x20;       |

&#x20;       v

Metadata Tracking

```



\## Data Validation Rules



The pipeline applies the following validation rules:



| Field | Validation |

|---|---|

| order\_id | Must not be empty |

| customer\_id | Must not be empty |

| status | Must be completed, cancelled, or pending |

| amount\_inr | Must be numeric and greater than zero |



Invalid records are stored in the rejected output with a `reject\_reason` field.



Repeated order IDs within an input file are stored separately as duplicate records.



\## Installation



\### 1. Clone the repository



```bash

git clone https://github.com/Prachi21132/yotta-orders-pipeline.git

cd yotta-orders-pipeline

```



\### 2. Create a virtual environment



```bash

python -m venv venv

```



\### 3. Activate the virtual environment



Windows PowerShell:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



\### 4. Install dependencies



```bash

pip install -r requirements.txt

```



\## Running the Pipeline



\### Process the default input file



```bash

python pipeline.py

```



By default, the pipeline processes:



```text

data/orders.csv

```



\### Process a specific input file



Windows PowerShell:



```powershell

$env:PIPELINE\_INPUT\_FILE="data/incoming/orders\_late\_new.csv"

python pipeline.py

```



\### Discover and process incoming files



```bash

python discover\_files.py

```



The discovery script finds CSV files in `data/incoming/` and executes the pipeline for each file.



It can be run again when new files arrive. It is not a continuously running folder-monitoring service.



\## Output Files



| Folder | Description |

|---|---|

| `data/raw/` | Original input records |

| `data/validated/` | Validated, rejected, and duplicate records |

| `data/curated/` | Curated output records |

| `data/curated/partitioned/` | Date-wise partitioned records |

| `data/metadata/` | Previously processed file hashes and metadata |



Example partition structure:



```text

data/curated/partitioned/

&#x20;   order\_date=2026-11-01/

&#x20;       orders.csv

&#x20;   order\_date=2026-11-02/

&#x20;       orders.csv

```



\## Running Automated Tests



Execute the test suite using:



```bash

python -m pytest -v

```



The test suite currently contains eight tests covering:



\- Successful pipeline execution

\- Valid record count

\- Rejected record count

\- Duplicate record count

\- Curated record count

\- Invalid amount rejection reason

\- Date-based partitioning

\- Cross-date duplicate ID lookup



\*\*Latest local test result:\*\* 8 passed.



The cross-date duplicate test independently verifies the partition lookup helper using temporary test data.

## Performance Measurement and Optimization

### Performance Measurement

The pipeline was tested locally using a sample input containing 100 orders.

| Metric | Result |
|---|---:|
| Input records | 100 |
| Valid records | 99 |
| Rejected records | 1 |
| Pipeline execution time | 0.057801 seconds |
| Automated test suite execution time | 0.772829 seconds |
| Automated tests passed | 8 |

The pipeline execution time was recorded in the pipeline run history. The automated test suite runtime was measured separately using PowerShell's `Measure-Command`.

These measurements represent a small local test and are not a large-scale performance benchmark.

### Optimization

The original partition duplicate-checking logic loaded existing order IDs repeatedly while processing orders.

The optimized implementation loads existing order IDs from the date-based partitions once before processing the valid orders.

A set is used for duplicate lookup, and newly written order IDs are added to the set.

This avoids repeatedly scanning partition files for every order and improves duplicate-checking efficiency.

### Performance Considerations

- The current performance measurement uses a small sample dataset.
- Larger datasets should be tested to evaluate scalability.
- Partition lookup and file processing can be further optimized for larger workloads.

\## Future Improvements



\- Add structured logging and detailed error reporting.

\- Improve automated test isolation using temporary directories.

\- Optimize duplicate detection for larger datasets.

\- Add schema validation and configurable validation rules.

\- Add continuous monitoring for incoming files.



\## Author



Developed as part of the YottaFlex AI Data Engineering Code Challenge.
