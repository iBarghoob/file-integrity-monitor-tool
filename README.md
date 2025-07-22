# File Integrity Monitor

A Python script to monitor a directory/folder for file integrity.

## Features

The script generates a sha256 hash for each file in the monitor directory and stores it as a key value pair in the `hashes.json` file. After the interval it recalculates the hash value and compares it with the previously created hash. If it is different, then it logs that a change has occurred, whether the file was changed, deleted, or a new file was added.

- Detects file changes, additions, and deletions
- Logs events to `log.txt` with timestamps
- Stores known sha256 file hashes in `hashes.json`  

## Usage

1. **Set the directory to monitor**

   Edit the `MONITOR_DIRECTORY` variable in `main.py` to the directory you want to monitor.

2. **Run the script**

   ```sh
   python main.py
   ```

   Optionally, set the scan interval (in seconds):

   ```sh
   python main.py 10 
   ```

## Output

- **log.txt**: Logs all detected changes with timestamps.
- **hashes.json**: Stores known sha256 hashes for each file for comparison.

