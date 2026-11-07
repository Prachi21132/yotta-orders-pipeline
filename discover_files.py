

from pathlib import Path
import os
import subprocess
import sys

# Folder where incoming files arrive
INCOMING_FOLDER = Path("data/incoming")

# Find all incoming CSV files
incoming_files = sorted(INCOMING_FOLDER.glob("*.csv"))

print("Incoming files found:", len(incoming_files))

# Process each file
for file in incoming_files:

    print("\nProcessing file:", file.name)

    # Set the input file for pipeline.py
    env = os.environ.copy()
    env["PIPELINE_INPUT_FILE"] = str(file)

    # Run the existing pipeline
    result = subprocess.run(
        [sys.executable, "pipeline.py"],
        env=env,
        capture_output=True,
        text=True
    )

       # Check pipeline result
        # Check pipeline result
    if "Duplicate file content detected." in result.stdout:
        print("File skipped (duplicate):", file.name)

    elif result.returncode != 0:
        print("Processing failed:", file.name)

    else:
        print("Processing finished:", file.name)
