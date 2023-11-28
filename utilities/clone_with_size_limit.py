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

def monitor_size(path, size_limit, process, result_dict):
    while process.poll() is None:
        size = get_dir_size(path) / (1024 * 1024)  # Size in MB
        print(f"Current size: {size} MB")
        if size > size_limit:
            process.terminate()
            print("Clone aborted due to size limit.")
            result_dict["size_limit_exceeded"] = True
            break
        time.sleep(1)  # Wait for 1 second before next check



        
def repo_cloning(repo_url, target_path, size_limit):
    if os.path.exists(target_path):
        os.system('rm -rf '+target_path)

    process = subprocess.Popen(["git", "clone", "--filter=blob:limit=0", "--no-checkout", repo_url, target_path])
    result_dict = {"size_limit_exceeded": False}
    monitor = threading.Thread(target=monitor_size, args=(target_path, size_limit, process, result_dict))
    monitor.start()
    process.wait()
    monitor.join()

    if result_dict["size_limit_exceeded"]:
        raise SizeLimitExceededError("Repo exceeded size limit")
    elif process.returncode != 0:
        raise InvalidSSHAddressError("Invalid ssh address")





class SizeLimitExceededError(Exception):
    pass

class InvalidSSHAddressError(Exception):
    pass
