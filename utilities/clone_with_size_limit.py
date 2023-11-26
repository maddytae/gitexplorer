import os
import subprocess
import threading
import time

def get_dir_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def monitor_size(path, size_limit, process):
    while process.poll() is None:
        size = get_dir_size(path) / (1024 * 1024) # Size in MB
        print(f"Current size: {size} MB")
        if size > size_limit:
            process.terminate()
            print("Clone aborted due to size limit.")
            break
        time.sleep(1) # Wait for 1 second before next check

def clone_repo(repo_url, target_path, size_limit):
    process = subprocess.Popen(["git", "clone", repo_url, target_path])
    monitor = threading.Thread(target=monitor_size, args=(target_path, size_limit, process))
    monitor.start()
    process.wait()
    monitor.join()

repo_url = 'git@github.com:pandas-dev/pandas.git'  # Replace with actual repo URL
target_path = 'target_repo'  # Path where the repo is to be cloned
size_limit = 100  # Size limit in MB
clone_repo(repo_url, target_path, size_limit)
