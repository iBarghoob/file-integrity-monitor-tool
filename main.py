import os
import time
import json 
import hashlib
import datetime
import logging
import sys

"""
A pyhton script to monitor a directory for file integrity

calculates sha256 hashes of each file in directory and stores in hashes.json
with each interval it recalculates hashes and compares with old values to detect changes
ignores temp and irrelevant files
logs output to log.txt

run >python main.py 
can specify interval for time between scans
>python main.py 10 (10 seconds between each scan)

Replace variable MONITOR_DIRECTORY with path to the directory you want to monitor
"""

# directory to scan, (replace with path to the directory to monitor)
MONITOR_DIRECTORY = r"monitor_directory"

# file to stores known hashes of each file
HASH_FILE = "hashes.json"
INTERVAL = 5 # by default scan every 5 seconds

def calculate_hash(filepath):
  sha256 = hashlib.sha256()
  try:
    # read file in 8kb chunks and feed each one to hash function
    with open(filepath, "rb") as f:
      while True:
        chunk = f.read(8192)
        if not chunk:
          break 
        sha256.update(chunk)
  except FileNotFoundError:
    return None 
  return sha256.hexdigest()

# load known hashes from file which will be used to compare with new hashes
def load_known_hashes():
  if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r") as f:
      return json.load(f)
  return {}

# save new file hashes (only used when any change occurs) 
def save_hashes(updated_hashes):
  with open(HASH_FILE, "w") as f:
    json.dump(updated_hashes, f, indent=2)

def should_ignore(filename):
  return (
    filename.startswith("~$") or
    filename.endswith(".tmp") or
    filename.endswith(".bak")
    ) 
  
# scan all items in directory and return the {filepath : filehash} dictionary
def scan_directory(path):
  file_hashes = {}
  # scan all files nested in subdirectories within the monitor directory
  for root, dirs, files in os.walk(path):
    for file in files:
      # ignore temp files
      if should_ignore(file):
        continue

      filepath = os.path.join(root, file)
      file_hash = calculate_hash(filepath)
      if file_hash:
        file_hashes[filepath] = file_hash

  return file_hashes

def timestamp():
  return datetime.datetime.now().strftime("%H:%M:%S")

# logger
logging.basicConfig(
    filename="log.txt",
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO
)

def log(msg):
  timestamped = f"{timestamp()} {msg}"
  print(timestamped)
  logging.info(msg)

def monitor():
  baseline = load_known_hashes()
  log(f"{timestamp()} Initial baseline loaded")

  while True:
    # scan dir to compare with previous state
    current_hashes = scan_directory(MONITOR_DIRECTORY)
    changes_detected = False

    # check for any changes after the new scan comparing with the previous baseline
    # when a file is modified in any way, the corresponding hash for the filepath will be completely different
    for filepath, filehash in current_hashes.items():
      if filepath not in baseline:
        log(f"[NEW FILE CREATED] {filepath}")
        changes_detected = True
      elif baseline[filepath] != filehash:
        log(f"[FILE MODIFIED] {filepath}")
        changes_detected = True

    for filepath in baseline:
      if filepath not in current_hashes:
        log(f"[FILE DELETED] {filepath}")
        changes_detected = True

    # if any changes then override current hashes file with the updates
    if changes_detected:
      log(f"Changes detected. Updating hashes...")
      save_hashes(current_hashes)
      baseline = current_hashes.copy()
    else:
      log(f"No changes detected.")

    log(f"... SCAN COMPLETED SLEEPING ...\n")
    time.sleep(INTERVAL)

if __name__ == "__main__":
    if len(sys.argv) > 1 :
      INTERVAL = int(sys.argv[1])
    else:
      INTERVAL = 5

    log(f"Monitoring '{MONITOR_DIRECTORY}' for changes every {INTERVAL} seconds...  (Ctrl^C to stop)\n")
    try:
      monitor()
    except KeyboardInterrupt:
      log("Monitoring stopped by user.")
