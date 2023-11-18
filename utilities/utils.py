import os
import subprocess

def get_repo(sshAddress):
    try:
        # Use subprocess.check_output to capture the command's output
        result = subprocess.check_output(["git", "ls-remote", "--heads", sshAddress], text=True)

        # Process the output to extract branch names
        branches = []
        for line in result.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].startswith('refs/heads/'):
                branch_name = parts[1].split('/')[-1]  # Extract the branch name
                branches.append(branch_name)

        return '\n'.join(branches)  # Join branch names into a single string
    except subprocess.CalledProcessError as e:
        # Handle errors in command execution
        return str(e)

def clone_repo(ssh_address, branch, clone_directory, depth=1):

    repo_name = ssh_address.split('/')[-1].replace('.git', '')
    full_clone_path = os.path.join(clone_directory, repo_name)

    try:
        os.system('rm -rf '+full_clone_path)
    except subprocess.CalledProcessError as e:
        # Handle error
        print(f"An error occurred: {e}")


    try:
        # Clone the specified branch with the given depth into the full clone path
        subprocess.run(["git", "clone", "-b", branch, "--depth", str(depth), ssh_address, full_clone_path], check=True)
        print(f"Repository cloned successfully into {full_clone_path}")
    except subprocess.CalledProcessError as e:
        # Handle error
        print(f"An error occurred: {e}")