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

def repo_cloning(repo_url, target_path, size_limit):

    if os.path.exists(target_path):
        os.system('rm -rf '+target_path)

    process = subprocess.Popen(["git", "clone","--filter=blob:limit=0","--no-checkout" , repo_url, target_path])
    monitor = threading.Thread(target=monitor_size, args=(target_path, size_limit, process))
    monitor.start()
    process.wait()
    monitor.join()
